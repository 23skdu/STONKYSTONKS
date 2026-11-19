# Development

## Requirements

* Python **3.12 - 3.13** (3.13 is what the container and CI use; TensorFlow does
  not ship wheels for 3.14+ yet)
* `make` (optional, but every workflow below has a target)
* Docker (optional, for the image and the in-container test stage)

## Quick start

```bash
make setup     # creates .venv and installs the pinned dev dependencies
make check     # ruff lint + format check + unit tests
```

Without `make`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/python -m unittest discover --start-directory tests --verbose
```

All tests mock external services (`yfinance`) and heavy runtimes
(`tensorflow`, `matplotlib` windows), so the suite runs offline in a few seconds.

## Make targets

| Target          | What it does |
| --------------- | ------------ |
| `make` / `make help` | List all targets |
| `make setup`    | Create `.venv`, install `requirements-dev.txt` |
| `make venv-update` | Upgrade everything inside `.venv` |
| `make lint`     | `ruff check .` |
| `make format`   | `ruff format .` + safe auto-fixes |
| `make test`     | Run the unit test suite |
| `make check`    | Lint + format check + tests (exactly what CI runs) |
| `make audit`    | `pip-audit` against `requirements.txt` (dependency CVEs) |
| `make sast`     | `bandit` static security scan of `scripts/` |
| `make scan`     | `audit` + `sast` |
| `make docker-build` | Build the runtime image |
| `make docker-test`  | Build the `test` stage (lint/scan/test inside the image) |
| `make docker-run`   | Run a tool in the container with `--cap-drop=ALL --read-only` |
| `make clean`     | Remove `.venv`, caches, test artifacts, `data/` and `models/` |
| `make distclean` | `clean` + delete the locally built images |

## Repository layout

```
scripts/           the tools (importable package + CLI entry point)
  __main__.py      `python -m scripts <tool>` dispatcher
  marketdata.py    shared yfinance download/normalisation helper
tests/             unit tests (unittest, mocks for network/heavy deps)
docs/              documentation (this file, tool reference, container notes)
requirements.txt   pinned runtime dependencies
requirements-dev.txt  runtime + lint/security tooling
pyproject.toml     ruff configuration
Makefile           developer entry points
Dockerfile         multi-stage, non-root image (see docs/docker.md)
.github/           CI workflow + Dependabot configuration
```

## Continuous integration & dependency updates

`.github/workflows/ci.yml` runs on every push and pull request:

1. **checks** - `ruff check`, `ruff format --check`, the unit suite, `bandit`
   and `pip-audit` against the pinned requirements, on Python 3.13.
2. **container** - builds the Dockerfile's `test` stage so the image cannot ship
   code that has not been linted, scanned and tested inside the shipped
   environment.

`.github/dependabot.yml` opens weekly grouped PRs for the pip requirements, the
Docker base image and the GitHub Actions used by the workflows.
`.github/workflows/dependabot-auto-merge.yml` auto-merges **minor and patch**
Dependabot PRs once CI is green (major bumps stay manual).

> Repository setting: **Settings -> General -> Pull Requests -> Allow
> auto-merge** must be enabled for the auto-merge workflow to work.

## Dependency quirks

* **`stonky` must import `yfinance` before `tensorflow`.** Once TensorFlow's
  native libraries are loaded first, `curl_cffi` loses its browser
  impersonation and every Yahoo download fails with
  `ImpersonateError: Impersonating chromeXXX is not supported`. The import order
  is set in `scripts/stonky.py` and guarded by
  `tests/test_stonky.py::TestImportOrder` - keep it if you touch those files.
* The image is ~3.6 GB because TensorFlow is bundled; use
  `docker build --build-arg TF_EXTRAS='[and-cuda]'` only if you need the GPU
  wheels (adds several GB more).

## Security notes

* Dependencies are pinned with `==` in `requirements.txt`; bump them with
  `make venv-update` or via Dependabot PRs.
* `make scan` is the same check CI performs; run it before opening a PR.
* Never commit secrets: only `.env` (gitignored) may hold local credentials.
