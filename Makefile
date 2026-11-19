# Stonky Stonks - development, quality and security entry points.
#
#   make            # list the available targets
#   make setup      # create .venv and install the pinned dev dependencies
#   make check      # lint + tests (what CI runs)
#   make scan       # dependency audit + static security scan
#   make clean      # remove the venv, caches, test artifacts and generated data

.DEFAULT_GOAL := help

PYTHON   ?= python3
VENV     ?= .venv
VENV_BIN := $(VENV)/bin
PIP      := $(VENV_BIN)/pip
PY       := $(VENV_BIN)/python
RUFF     := $(VENV_BIN)/ruff
BANDIT   := $(VENV_BIN)/bandit
PIPAUDIT := $(VENV_BIN)/pip-audit

IMAGE    ?= stonkystonks
DOCKER   ?= docker

# Generated artifacts removed by `make clean`.
ARTIFACTS := $(VENV) .ruff_cache .pytest_cache .mypy_cache .coverage coverage.xml \
             htmlcov report.xml data models

.PHONY: help setup venv venv-update venv-clean lint lint-fix format test check \
        audit sast scan docker-build docker-test docker-run clean distclean

## help: Show this help message.
help:
	@printf '\nUsage: make <target>\n\n'
	@grep -hE '^## [a-zA-Z0-9_-]+: ' $(MAKEFILE_LIST) \
		| sed -E 's/^## //' \
		| sort \
		| awk 'BEGIN {FS = ": "} {target = $$1; description = $$0; sub(/^[^:]*: /, "", description); \
			printf "  \033[36m%-16s\033[0m %s\n", target, description}'
	@printf '\n'

## setup: Create the virtualenv and install the pinned dev dependencies.
setup: $(VENV)/.installed

## venv: Alias for `setup`.
venv: $(VENV)/.installed

$(VENV)/.installed: requirements.txt requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@touch $@

## venv-update: Upgrade the dependencies inside the virtualenv.
venv-update:
	$(PIP) install --upgrade -r requirements-dev.txt
	@touch $(VENV)/.installed

## venv-clean: Delete the virtualenv only.
venv-clean:
	rm -rf $(VENV)

## lint: Run the ruff linter.
lint: $(VENV)/.installed
	$(RUFF) check .

## lint-fix: Apply ruff's safe auto-fixes.
lint-fix: $(VENV)/.installed
	$(RUFF) check --fix .

## format: Format the codebase with ruff (then re-lint).
format: $(VENV)/.installed
	$(RUFF) format .
	$(RUFF) check --fix .

## test: Run the unit test suite.
test: $(VENV)/.installed
	$(PY) -m unittest discover --start-directory tests --verbose

## check: Run linting, formatting check and tests (the CI gate).
check: lint
	$(RUFF) format --check .
	$(PY) -m unittest discover --start-directory tests --verbose

## audit: Check the pinned dependencies against known vulnerabilities (pip-audit).
audit: $(VENV)/.installed
	$(PIPAUDIT) --requirement requirements.txt

## sast: Static application security testing on the scripts (bandit).
sast: $(VENV)/.installed
	$(BANDIT) --quiet --severity-level medium --confidence-level medium --recursive scripts

## scan: Run every security scan (audit + sast).
scan: audit sast

## docker-build: Build the runtime image.
docker-build:
	$(DOCKER) build --tag $(IMAGE) .

## docker-test: Build the test stage - lints, scans and runs the suite in the image.
docker-test:
	$(DOCKER) build --target test --tag $(IMAGE):test .

## docker-run: Run a tool, e.g. `make docker-run ARGS="stats < data/series.txt"`.
docker-run:
	$(DOCKER) run --rm -i --cap-drop=ALL --read-only --tmpfs /tmp $(IMAGE) $(ARGS)

## clean: Remove the virtualenv, caches, test artifacts and generated data/models.
clean:
	rm -rf $(ARTIFACTS)
	find . -type d \( -name '__pycache__' -o -name '*.tfmodel.100' \) -prune -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete

## distclean: `clean` plus docker images built from this repository.
distclean: clean
	-$(DOCKER) rmi $(IMAGE) $(IMAGE):test 2>/dev/null
