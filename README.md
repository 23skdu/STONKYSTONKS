# Stonky Stonks

[![CI](https://github.com/23skdu/STONKYSTONKS/actions/workflows/ci.yml/badge.svg)](https://github.com/23skdu/STONKYSTONKS/actions/workflows/ci.yml)

Small Python tools for stock-market analysis: descriptive statistics, volume/price
visualisation, a classifier benchmark and an LSTM price-prediction experiment -
all runnable locally or from a minimal, hardened container image.

## Tools

| Tool | What it does |
| ---- | ------------ |
| `stonky` | Trains a two-layer LSTM on a ticker's close price and prints 1/3/7/11/17/71-day forecasts (test RMSE included). |
| `stats` | Min/max, quartiles, Fibonacci levels, mean, median, harmonic mean, std dev, kurtosis and skew for numbers read from stdin. |
| `modeltest` | 5-fold cross-validation of Logistic Regression, Decision Tree, Random Forest and SVM on a synthetic dataset. |
| `new_volprice_ema` | Price/volume ratio with 25/50/100/200-day moving averages, plotted. |
| `ytd_volprice` | Year-to-date close price vs. volume on twin y-axes. |

Full option reference: [docs/scripts.md](docs/scripts.md).

## Quick start

### Container (recommended)

```bash
docker build -t stonkystonks .
docker run --rm -it stonkystonks --help
printf "1\n2\n3\n4\n5\n" | docker run --rm -i stonkystonks stats
docker run --rm stonkystonks ytd_volprice NVDA
```

### Local

Requires Python 3.12-3.13 (TensorFlow constraint):

```bash
make setup                 # creates .venv with the pinned dev dependencies
source .venv/bin/activate
make check                 # lint + format check + unit tests
python -m scripts stonky NVDA --epochs 20
```

Each tool also runs directly: `python scripts/stats.py < data/series.txt`.

## Quality, security and updates

```bash
make lint      # ruff
make test      # unit tests (network and TensorFlow are mocked)
make scan      # pip-audit (dependency CVEs) + bandit (SAST)
make clean     # remove .venv, caches, test artifacts, data/ and models/
```

* **CI** (`.github/workflows/ci.yml`) runs lint, formatting, tests, `bandit`,
  `pip-audit`, and builds the Dockerfile's `test` stage so the image only ships
  code that passed the suite inside the shipped environment.
* **Dependabot** (`.github/dependabot.yml`) opens weekly grouped PRs for the pip
  pins, the Docker base image and the GitHub Actions; minor/patch updates are
  auto-merged once CI is green (see
  `.github/workflows/dependabot-auto-merge.yml`).
* **The image** is multi-stage, pinned, non-root and needs no capabilities -
  see [docs/docker.md](docs/docker.md).

## Repository layout

```
scripts/            tools (importable package + `python -m scripts` CLI)
tests/              unit tests (unittest + mocks)
docs/               tool reference, development guide, container notes
requirements.txt    pinned runtime dependencies
requirements-dev.txt  + ruff, bandit, pip-audit
pyproject.toml      ruff configuration
Makefile            setup / lint / test / scan / clean targets
Dockerfile          multi-stage, non-root image with an in-build test gate
.github/            CI + Dependabot configuration
```

More documentation: [docs/scripts.md](docs/scripts.md) ·
[docs/development.md](docs/development.md) · [docs/docker.md](docs/docker.md)

## License

This project is released into the public domain under the [Unlicense](https://unlicense.org). See [LICENSE](LICENSE) for details.
