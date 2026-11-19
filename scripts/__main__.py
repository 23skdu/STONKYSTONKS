"""Unified command line interface for the Stonky Stonks tools.

Runs every tool in this package through a single entry point::

    python -m scripts --help
    python -m scripts stats < data/series.txt
    python -m scripts ytd_volprice NVDA --no-show

The container image uses this module as its entry point.
"""

from __future__ import annotations

import argparse
import importlib
from collections.abc import Sequence

__all__ = ["TOOLS", "main"]

#: CLI name -> module that provides a ``main(argv) -> int`` function.
TOOLS: dict[str, str] = {
    "modeltest": "scripts.modeltest",
    "new_volprice_ema": "scripts.new_volprice_ema",
    "stats": "scripts.stats",
    "stonky": "scripts.stonky",
    "ytd_volprice": "scripts.ytd_volprice",
}


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch ``argv`` to the requested tool, or print the tool list."""
    parser = argparse.ArgumentParser(
        prog="python -m scripts",
        description="Stock-market analysis, statistics and LSTM prediction tools.",
        epilog="Run '%(prog)s <tool> --help' for a tool's own options.",
    )
    parser.add_argument("tool", nargs="?", choices=sorted(TOOLS), help="Tool to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.tool is None:
        parser.print_help()
        return 0

    # Imported lazily so that listing the tools never loads TensorFlow or matplotlib.
    module = importlib.import_module(TOOLS[args.tool])
    result = module.main(args.args)
    return 0 if result is None else int(result)


if __name__ == "__main__":
    raise SystemExit(main())
