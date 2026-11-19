# Container image

The [`Dockerfile`](../Dockerfile) packages the tools with a multi-stage,
minimal, non-root image.

## Building

```bash
make docker-build                       # docker build -t stonkystonks .
docker build -t stonkystonks .          # same, without make
```

| Goal | Command |
| ---- | ------- |
| Runtime image | `docker build -t stonkystonks .` |
| Lint, scan & test inside the image | `docker build --target test -t stonkystonks:test .` |
| CUDA-enabled TensorFlow | `docker build --build-arg TF_EXTRAS='[and-cuda]' -t stonkystonks:gpu .` |
| SBOM + provenance attestations | `docker build --sbom=true --provenance=mode=max -t stonkystonks .` |

## Running

The entry point is the unified CLI (`python -m scripts`):

```bash
docker run --rm -it stonkystonks --help
docker run --rm stonkystonks ytd_volprice NVDA --no-show
printf "1\n2\n3\n" | docker run --rm -i stonkystonks stats
docker run --rm -v "$PWD/data:/app/data:ro" stonkystonks modeltest
```

Hardened invocation (the image needs nothing else):

```bash
docker run --rm --cap-drop=ALL --read-only --security-opt no-new-privileges --tmpfs /tmp \
  --memory 2g --cpus 2 -i stonkystonks stats < data/series.txt
```

`make docker-run ARGS="stats < data/series.txt"` runs the same hardened command
with `--cap-drop=ALL --read-only --tmpfs /tmp`.

## Image stages

```
builder  -> python:3.13.13-slim-bookworm, venv with the pinned requirements
test     -> builder + ruff/bandit/tests: build fails if lint, scans or tests fail
runtime  -> slim base + /opt/venv + scripts/ only, running as uid 10001
```

## DevSecOps posture

* **Pinned inputs** - base image (`python:3.13.13-slim-bookworm`) and every
  Python dependency (`==` in `requirements.txt`); Dependabot bumps them weekly.
* **Reproducible, cacheable build** - BuildKit pip cache mounts and a
  `requirements*.txt`-first layer order; no `apt upgrade`, no extra OS packages,
  no compiler in the final image.
* **Test gate inside the pipeline** - the `test` stage runs ruff, bandit and the
  unit suite against the exact interpreter/dependencies that ship; CI builds it
  on every push.
* **Least privilege at run time** - dedicated unprivileged user (`uid 10001`,
  non-login shell), no secrets in the image, only `scripts/` is copied in, and
  the container works with `--cap-drop=ALL --read-only`.
* **Supply chain** - OCI labels, and `--sbom=true --provenance=mode=max` builds
  an SPDX SBOM plus SLSA provenance attestation.
* **Small attack surface** - `.dockerignore` keeps `.git`, docs, virtualenvs,
  caches and generated data out of the build context.
