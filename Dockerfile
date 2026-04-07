# syntax=docker/dockerfile:1

# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Copy uv binary from the official image (always up-to-date)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# uv env: compile .pyc bytecode for faster startup, use copy link mode
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# ── Layer cache trick: install deps BEFORE copying source ──────────────────
# Only pyproject.toml + uv.lock are needed to resolve dependencies.
# This layer is only invalidated when deps change, not on every code change.
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# ── Now copy the actual source and install the project itself ──────────────
COPY src/ src/
COPY README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ── Runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="huawei-lte-exporter"
LABEL org.opencontainers.image.description="Prometheus exporter for Huawei LTE routers"
LABEL org.opencontainers.image.source="https://github.com/YOUR_GITHUB_USER/huawei-lte-exporter"
LABEL org.opencontainers.image.licenses="MIT"

# Non-root user
RUN addgroup --system exporter \
 && adduser --system --ingroup exporter exporter

WORKDIR /app

# Copy the pre-built venv from builder (no uv needed at runtime)
COPY --from=builder --chown=exporter:exporter /app /app

# Put the venv on PATH so console scripts work directly
ENV PATH="/app/.venv/bin:$PATH"

USER exporter
EXPOSE 9898

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9898/metrics')"

ENTRYPOINT ["huawei-lte-exporter"]