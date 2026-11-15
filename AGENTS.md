# AGENTS.md: PharmaTwin

Instructions for any coding agent (Cursor, Claude Code, Codex) working in this repo.

## Read first
1. `PRODUCT.md`: who it's for and why (CFO + Head of Supply Chain; sits alongside SAP IBP/Kinaxis/o9).
2. `DESIGN.md`: the visual system. Tokens are binding.
3. `CURSOR_BUILD_PROMPT.md`: the technical spec (Part B) and the step-by-step build prompts (Part C).
4. `docs/scenarios.md`: the 13 demo scenarios.

## Non-negotiables
- Every result shows **Money | Service** together, with P50/P90 and assumptions.
- Never display a number that can't be traced to simulation inputs. The copilot only reports numbers returned by tools.
- Money in Indian format (₹ lakh / crore) via `web/lib/format.ts`.
- All demo data is synthetic and labelled as such. Never fabricate customers, logos, testimonials or benchmarks.
- AI calls go through **OpenRouter** (`openai` SDK, base URL `https://openrouter.ai/api/v1`); model ids come from env vars only.
- No secrets in code or commits. `.env` is git-ignored.
- Clean-room: never copy competitor code, UI assets or text.
- Tests first (superpowers test-driven-development). Run `make test` and `make lint` before saying a task is done.

## Commands
- `make setup`: install api (uv) and web (pnpm) dependencies
- `make seed`: build the synthetic database and pre-compute cached results
- `make dev`: API on :8000, web on :3000
- `make test` · `make lint`
- `pnpm --dir web gen:api`: regenerate the TypeScript API client
