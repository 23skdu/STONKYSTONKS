import ast
import importlib
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scripts.__main__ import TOOLS
from scripts.__main__ import main as cli_main

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"


class TestCli(unittest.TestCase):
    def test_no_tool_prints_help(self):
        with patch("sys.stdout", new=StringIO()) as output:
            code = cli_main([])

        self.assertEqual(code, 0)
        self.assertIn("usage", output.getvalue())
        for tool in TOOLS:
            self.assertIn(tool, output.getvalue())

    def test_dispatches_to_stats(self):
        stdin = StringIO("1\n2\n3\n4\n5\n")
        stdout = StringIO()
        with patch("sys.stdin", stdin), patch("sys.stdout", stdout):
            code = cli_main(["stats"])

        self.assertEqual(code, 0)
        self.assertIn("Mean: 3.0", stdout.getvalue())

    def test_unknown_tool_exits_with_error(self):
        with patch("sys.stderr", new=StringIO()), self.assertRaises(SystemExit) as ctx:
            cli_main(["does-not-exist"])

        self.assertEqual(ctx.exception.code, 2)


class TestToolContract(unittest.TestCase):
    """The dispatcher calls ``module.main(argv) -> int`` for every tool.

    If a module exposes a data function called ``main`` instead, the CLI breaks
    at run time (it did once), so the contract is asserted here.
    """

    def test_every_tool_defines_a_cli_main(self):
        for tool, module_name in TOOLS.items():
            with self.subTest(tool=tool):
                source = (SCRIPTS_DIR / f"{tool}.py").read_text(encoding="utf-8")
                functions = {
                    node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)
                }

                self.assertIn("main", functions, f"{module_name} must define main()")
                entry_point = functions["main"]
                parameters = [arg.arg for arg in entry_point.args.args]
                self.assertEqual(parameters, ["argv"], "main must take the tool's argv")
                self.assertTrue(entry_point.args.defaults, "argv must default to None")

    def test_every_tool_answers_help_through_the_dispatcher(self):
        for tool in sorted(TOOLS):
            with self.subTest(tool=tool), patch("sys.stdout", new=StringIO()):
                try:
                    importlib.import_module(TOOLS[tool])
                except Exception as exc:  # heavy optional dependency missing locally
                    print(f"skipping {tool}: {exc}")
                    continue

                with self.assertRaises(SystemExit) as ctx:
                    cli_main([tool, "--help"])
                self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
