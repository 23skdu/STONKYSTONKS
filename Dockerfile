# syntax=docker/dockerfile:1.7
#
# DevSecOps-oriented image for the Stonky Stonks tools.
#
#   Build:            docker build -t stonkystonks .
#   Run a tool:       docker run --rm -i stonkystonks stats < data/series.txt
#   Run the tests:    docker build --target test -t stonkystonks:test .
#   With CUDA support: docker build --build-arg TF_EXTRAS='[and-cuda]' -t stonkystonks:gpu .
#   Supply chain:     docker build --sbom=true --provenance=mode=max -t stonkystonks .
#
# Security posture:
#   * base image pinned to an exact Python patch release and Debian suite
#   * dependencies pinned in requirements.txt (bumped by Dependabot)
#   * multi-stage build: no compiler/pip cache/test code in the final image
#   * non-root user, no extra OS packages, no secrets, read-only friendly
#   * test target re-runs the unit tests so an image cannot ship untested

ARG PYTHON_VERSION=3.13.13
ARG DEBIAN_SUITE=bookworm

# --- builder: resolve and install the pinned dependencies into a venv --------
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_SUITE} AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY requirements.txt requirements-dev.txt ./

# TF_EXTRAS allows opting into the CUDA-enabled TensorFlow wheels:
#   docker build --build-arg TF_EXTRAS='[and-cuda]' .
ARG TF_EXTRAS=""
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt "tensorflow${TF_EXTRAS}"

# --- test: lint and run the unit suite against the exact shipped deps --------
FROM builder AS test

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-dev.txt

COPY pyproject.toml ./
COPY scripts/ scripts/
COPY tests/ tests/

RUN ruff check . \
    && ruff format --check . \
    && bandit --quiet --severity-level medium --confidence-level medium --recursive scripts \
    && python -m unittest discover --start-directory tests --verbose

# --- runtime: minimal, unprivileged, tools only ------------------------------
FROM python:${PYTHON_VERSION}-slim-${DEBIAN_SUITE} AS runtime

LABEL org.opencontainers.image.title="STONKYSTONKS" \
      org.opencontainers.image.description="Stock market statistics, volume/price analysis and LSTM prediction tools" \
      org.opencontainers.image.authors="23skdu@users.noreply.github.com" \
      org.opencontainers.image.source="https://github.com/23skdu/STONKYSTONKS" \
      org.opencontainers.image.licenses="Unlicense" \
      org.opencontainers.image.base.name="docker.io/library/python:3.13.13-slim-bookworm"

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    MPLCONFIGDIR=/tmp/matplotlib \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=3

# Unprivileged, non-login user; fixed uid/gid so bind mounts stay predictable.
RUN groupadd --system --gid 10001 stonky \
    && useradd --system --uid 10001 --gid stonky --home-dir /app --create-home \
        --shell /usr/sbin/nologin stonky

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=stonky:stonky scripts/ /app/scripts/

USER 10001:10001

# The tools are a plain CLI; run them with e.g.
#   docker run --rm -i --cap-drop=ALL --read-only stonkystonks stats < data/series.txt
ENTRYPOINT ["python", "-m", "scripts"]
CMD ["--help"]
