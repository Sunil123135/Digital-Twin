# PharmaTwin: Digital Twin for Pharma Supply Chain Risk

A risk-simulation layer for pharma manufacturers and distributors. Simulate disruptions (floods, China ingredient shocks, USFDA actions, recalls, cold-chain failures, tariffs) and see the impact in **money and service** together, with recommended response plans for approval. Built to sit alongside SAP IBP, Kinaxis, o9 or Blue Yonder.

**Status:** demo build is in the repo. Data in the demo is synthetic.

## Start here
| File | What it is |
|---|---|
| [`CURSOR_BUILD_PROMPT.md`](CURSOR_BUILD_PROMPT.md) | **The build prompt.** Part A setup, Part B technical spec, Part C prompts to paste into Cursor (Day 0–7) |
| [`PRODUCT.md`](PRODUCT.md) | Users, purpose, positioning, principles |
| [`DESIGN.md`](DESIGN.md) | Visual system: tokens, typography, components, rules |
| [`docs/scenarios.md`](docs/scenarios.md) | The 13 demo scenarios and the presenter flow |
| [`docs/superpowers/specs/2026-11-15-pharmatwin-demo-design.md`](docs/superpowers/specs/2026-11-15-pharmatwin-demo-design.md) | Approved demo design |
| [`docs/research/competitor-scenarios.md`](docs/research/competitor-scenarios.md) | Public research on Kinaxis, Blue Yonder, SAP IBP, o9 and others |
| [`docs/vision/full-product-prompt.md`](docs/vision/full-product-prompt.md) | Full product vision beyond the demo (connectors, agents, pilot) |
| [`AGENTS.md`](AGENTS.md), [`.cursor/rules/`](.cursor/rules) | Rules Cursor loads automatically |

## Stack
Next.js 15 · shadcn/ui · tweakcn · Python FastAPI · NumPy · OR-Tools · SQLite (demo) · OpenRouter · Cursor

## Run the demo
1. Copy `.env.example` to `.env`. Leave `OPENROUTER_API_KEY` empty to use the app without the copilot.
2. `make setup` then `make seed` then `make dev`. API is on port 8000, the web app on port 3000. Open `/executive`.
3. On Windows without `make`: `python -m pip install uv`, then from `api` run `uv sync --all-groups` and `uv run python -m pharmatwin.seed`. Start the API with `uv run uvicorn pharmatwin.main:app --port 8000` and the web app with `pnpm dev` from `web`. Google Drive cannot store the symlinks those tools create. On this machine the API virtualenv is `%LOCALAPPDATA%\pharmatwin-venv` (`UV_LINK_MODE=copy`) and the web app runs from `%LOCALAPPDATA%\pharmatwin-web` after `pnpm install` there and a copy of `web\app`, `web\components`, and `web\lib`.
4. Presenter path: Executive → Open hero scenario (Monsoon flood + dengue) → move the flood-duration slider → Run → Compare plans → Send for approval → approve with a reason. The audit tab records the decision.
5. Deploy: web on Vercel with root directory `web` and `NEXT_PUBLIC_API_URL` pointing at the API. API on Render using `api/Dockerfile` (`PORT` is honoured). Set `DEMO_PASSWORD` to require HTTP basic auth (user `demo`). Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` on the API only.

All figures in the demo come from the synthetic network `synth-42`. They are not a real company's results.
