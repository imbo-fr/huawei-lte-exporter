# syntax=docker/dockerfile:1@sha256:572cebbc2b15e6f84c077742952674889cb63cd5e9b80abdffcbe587b6f19183

# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.15-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:a3ea1357342c1a4bf9a0c53a3deb1b55379aefa037338d8113d5771efa01774f /uv /uvx /bin/

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
FROM python:3.15-slim@sha256:63bb298d2b7b88f176f51b5189f54ce6535c997682ea70885d2132f5d473a8a5 AS runtime

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