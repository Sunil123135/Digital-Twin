.PHONY: setup seed dev test lint api web

setup:
	cd api && python -m pip install uv && uv sync --all-groups
	cd web && pnpm install

seed:
	cd api && uv run python -m pharmatwin.seed

dev:
	cd api && uv run uvicorn pharmatwin.main:app --reload --port 8000 &
	cd web && pnpm dev

test:
	cd api && uv run pytest
	cd web && pnpm test

lint:
	cd api && uv run ruff check pharmatwin tests
	cd api && uv run mypy
	cd web && pnpm exec tsc --noEmit

api:
	cd api && uv run uvicorn pharmatwin.main:app --host 0.0.0.0 --port 8000

web:
	cd web && pnpm dev
