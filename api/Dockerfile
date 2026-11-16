FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/
WORKDIR /app
COPY api/pyproject.toml api/
COPY api/pharmatwin api/pharmatwin
WORKDIR /app/api
RUN uv sync --no-dev
RUN uv run python -m pharmatwin.seed
EXPOSE 8000
CMD ["sh", "-c", "uv run uvicorn pharmatwin.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
