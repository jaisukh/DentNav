FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1

# Install dependencies from lockfile first for layer caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev --frozen

# ── runtime stage ──────────────────────────────────────────────────────────────
FROM python:3.12-slim-bookworm

WORKDIR /app

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONPATH=/app

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY data ./data
COPY scripts/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN chown -R appuser:appgroup /app /docker-entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
