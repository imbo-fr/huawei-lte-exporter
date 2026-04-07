# syntax=docker/dockerfile:1

# ── Build stage (always runs on the BUILD host, not the target platform) ──────
FROM --platform=$BUILDPLATFORM python:3.12-slim AS builder

# Pull uv for the BUILD host platform, not target (avoids arm/v7 manifest error)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Layer 1: deps only (cached unless uv.lock/pyproject.toml changes)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Layer 2: project source
COPY src/ src/
COPY README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Runtime stage (built for each TARGET platform) ────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="huawei-lte-exporter"
LABEL org.opencontainers.image.description="Prometheus exporter for Huawei LTE routers"
LABEL org.opencontainers.image.source="https://github.com/YOUR_GITHUB_USER/huawei-lte-exporter"
LABEL org.opencontainers.image.licenses="MIT"

RUN addgroup --system exporter \
 && adduser --system --ingroup exporter exporter

WORKDIR /app

COPY --from=builder --chown=exporter:exporter /app/.venv /app/.venv
COPY --from=builder --chown=exporter:exporter /app/src  /app/src

ENV PATH="/app/.venv/bin:$PATH"

USER exporter
EXPOSE 9898

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9898/metrics')"

ENTRYPOINT ["huawei-lte-exporter"]