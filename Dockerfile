# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

# ── Build stage ────────────────────────────────────────────────────────────────
FROM --platform=$BUILDPLATFORM python:3.14-slim@sha256:0741d101873c12ab927e6f8653feb8862b9bd58771177acb1b885b95141f91b4 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:f513a91fc62fe7c17567eee97230dd198e43edb8a9fbecca843714a4358fe1bc /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# COPY the lockfiles so they persist across all RUN steps
COPY pyproject.toml uv.lock ./

# Layer 1: install deps only (cached until uv.lock changes)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Layer 2: copy source, then install the project itself
COPY src/ src/
COPY README.md ./

# pyproject.toml and uv.lock are already present from the COPY above
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.14-slim@sha256:0741d101873c12ab927e6f8653feb8862b9bd58771177acb1b885b95141f91b4 AS runtime

LABEL org.opencontainers.image.title="huawei-lte-exporter"
LABEL org.opencontainers.image.description="Prometheus exporter for Huawei LTE routers"
LABEL org.opencontainers.image.source="https://github.com/YOUR_GITHUB_USER/huawei-lte-exporter"
LABEL org.opencontainers.image.licenses="MIT"

RUN addgroup --system exporter \
 && adduser --system --ingroup exporter exporter

WORKDIR /app

COPY --from=builder --chown=exporter:exporter /app/.venv /app/.venv
COPY --from=builder --chown=exporter:exporter /app/src   /app/src

ENV PATH="/app/.venv/bin:$PATH"

USER exporter
EXPOSE 9898

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9898/metrics')"

ENTRYPOINT ["huawei-lte-exporter"]