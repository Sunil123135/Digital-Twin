# PharmaTwin: Digital Twin for Pharma Supply Chain Risk

A risk-simulation layer for pharma manufacturers and distributors. Simulate disruptions (floods, China ingredient shocks, USFDA actions, recalls, cold-chain failures, tariffs) and see the impact in **money and service** together, with recommended response plans for approval. Built to sit alongside SAP IBP, Kinaxis, o9 or Blue Yonder.

**Status:** design approved; demo build not started. Data in the demo is synthetic.

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
