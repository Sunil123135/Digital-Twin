# PharmaTwin Demo: Cursor Build Prompt

This file is the complete instruction set for building the PharmaTwin demo in **Cursor**, using **OpenRouter** for AI models.

- **Part A:** one-time setup (do this yourself, 20 minutes).
- **Part B:** the technical specification. Cursor reads it when you mention `@CURSOR_BUILD_PROMPT.md`.
- **Part C:** eight prompts to paste into Cursor's Agent, one per build step (Day 0 to Day 7).

Read alongside: `PRODUCT.md` (who and why), `DESIGN.md` (visual system), `docs/scenarios.md` (the 13 scenarios), `docs/superpowers/specs/2026-11-15-pharmatwin-demo-design.md` (approved design).

---

## Part A: One-time setup

### A.1 Tools
- **Cursor** (Pro plan recommended for Agent usage limits).
- **Node.js 22 LTS** and **pnpm** (`npm i -g pnpm`).
- **Python 3.12** and **uv** (`pip install uv`).
- **Git**, with this repo cloned: `git clone https://github.com/Sunil123135/Digital-Twin.git`.
- Accounts: **OpenRouter** (add $10–20 credit), **Vercel** and **Render** (free tiers are fine for the demo).

### A.2 OpenRouter in Cursor (for building)
1. Create a key at openrouter.ai → Keys.
2. Cursor → Settings → Models → API Keys → **OpenAI API Key**: paste the OpenRouter key, switch on **Override OpenAI Base URL**: `https://openrouter.ai/api/v1`, then **Verify**.
3. Add custom model names exactly as listed on openrouter.ai/models (for example a current Anthropic Claude Sonnet or Opus model, and a cheaper fast model for small edits).
4. Choose that model in the Agent model picker.

Caveat: with a custom key, some Cursor features (Tab autocomplete, and possibly some Agent features depending on your Cursor version) keep using Cursor's own models. If a custom-key model fails in Agent mode, use Cursor's built-in models for building. The **app itself** still uses OpenRouter (section B.11), and that is independent of Cursor.

### A.3 Skills (Cursor reads `.agents/skills`)
Run in the repo root:
```bash
npx skills add https://github.com/obra/superpowers --skill brainstorming
npx skills add https://github.com/obra/superpowers --skill writing-plans
npx skills add https://github.com/obra/superpowers --skill executing-plans
npx skills add https://github.com/obra/superpowers --skill test-driven-development
npx skills add https://github.com/obra/superpowers --skill verification-before-completion
npx skills add https://github.com/mattpocock/skills --skill improve-codebase-architecture
npx skills add https://github.com/pbakaus/impeccable --skill impeccable
npx skills add https://github.com/leonxlnx/taste-skill --skill design-taste-frontend
```
Review each skill's `SKILL.md` before use; they run with full agent permissions.

### A.4 Project rules
`.cursor/rules/*.mdc` and `AGENTS.md` are already in the repo. Cursor loads them automatically.

### A.5 Secrets
Copy `.env.example` to `.env` and set `OPENROUTER_API_KEY`. Never commit `.env`.

### A.6 Optional: REA
`npx rea-agents setup` (choose Cursor). Use it only as described in `docs/vision/full-product-prompt.md` §3.3: open-source tools and your own app, never competitors' logged-in products.

---

## Part B: Technical specification

### B.1 Repository layout
```
/
├─ PRODUCT.md  DESIGN.md  AGENTS.md  CURSOR_BUILD_PROMPT.md  README.md
├─ .env.example  Makefile  docker-compose.yml
├─ api/                         # Python 3.12, FastAPI
│  ├─ pyproject.toml            # managed by uv
│  ├─ pharmatwin/
│  │  ├─ main.py                # FastAPI app factory, CORS, routers
│  │  ├─ config.py              # pydantic-settings (env vars)
│  │  ├─ db.py  models.py       # SQLAlchemy 2 (SQLite now, Postgres later)
│  │  ├─ schemas.py             # Pydantic v2 API models
│  │  ├─ seed/                  # synthetic network generator (deterministic)
│  │  ├─ engine/
│  │  │  ├─ network.py          # Network object, validation, CSV import
│  │  │  ├─ shocks.py           # Shock model + scenario templates (13)
│  │  │  ├─ simulate.py         # vectorised Monte Carlo daily flow
│  │  │  ├─ finance.py          # units → ₹
│  │  │  ├─ prescribe.py        # OR-Tools lever selection
│  │  │  └─ stress.py           # TTS/TTR stress test, resilience score
│  │  ├─ runs/                  # run manager, cache, progress (SSE)
│  │  ├─ copilot/               # OpenRouter client, tools, prompts
│  │  └─ routers/               # network, scenarios, runs, plans, approvals, upload, copilot, executive
│  └─ tests/
├─ web/                         # Next.js 15, TS, Tailwind v4, shadcn/ui
│  ├─ app/(app)/                # executive, network, scenarios, runs/[id], compare/[id], approvals, data
│  ├─ components/               # ui/ (shadcn), kpi/, charts/, map/, copilot/, layout/
│  ├─ lib/                      # api client (generated), format (₹), hooks
│  └─ tests/e2e/                # Playwright
└─ docs/
```

### B.2 Data model (SQLAlchemy)
- `Site(id, code, name, type[plant|cnf|dc|stockist|hospital|port|cold_store|supplier_site], lat, lon, region, state, storage_classes[json], drug_licence_no, licence_expiry, approved_markets[json], throughput_capacity_units_day, recovery_days, is_critical_care bool)`
- `Lane(id, from_site, to_site, mode[road|rail|sea|air], lead_time_mean_days, lead_time_sd_days, cost_per_unit, reefer bool, is_alternate bool)`
- `Product(id, sku, name, molecule, api_id, therapeutic_class, dosage_form, schedule[none|H|H1|X], storage_class[ambient|cold|frozen], shelf_life_days, essential bool, standard_cost, selling_price, price_cap)`
- `Api(id, name)`; `Supplier(id, name, country, tier, approved_markets[json], qualification_lead_days, capacity_units_day, risk_score)`; `SupplierApi(supplier_id, api_id, share)`
- `Batch(id, product_id, site_id, batch_no, mfg_date, expiry_date, qty, status[released|quarantine|recalled])`
- `DemandProfile(product_id, site_id, base_daily, seasonality[json 12 months], cv)`
- `Scenario(id, template_id, name, params[json], created_by, created_at)`
- `Run(id, scenario_id, plan_id nullable, seed, runs, status[queued|running|done|failed], progress, started_at, finished_at, result[json], is_cached bool)`
- `Plan(id, scenario_id, kind[cost_optimal|service_optimal|balanced], levers[json], cost, recommended bool, explanation[json])`
- `Approval(id, plan_id, status[draft|pending|approved|rejected], requested_by, approver, reason, decided_at)`
- `AuditLog(id, ts, actor, action, entity, entity_id, payload[json])`: append-only.

### B.3 Synthetic network (deterministic, `seed=42`)
- **Plants:** Baddi (HP), Sikkim (Rangpo). Baddi is US-approved; Sikkim is approved for India and RoW only.
- **Ports:** JNPT (Mumbai), Chennai. **Airport cold store:** Mumbai.
- **Suppliers:** 12 API suppliers (6 China, 4 India, 2 EU) and 3 packaging suppliers (one vial supplier is single-source). 40% of APIs are single-sourced from China.
- **C&F agents:** 6 (Delhi, Lucknow, Pune, Hyderabad, Bengaluru, Patna).
- **Distribution centres:** Mumbai (Bhiwandi), Chennai, Guwahati, Kolkata; Chennai has the main 2–8 °C cold store.
- **Stockists:** 40 across regions. **Hospitals:** 25 in 3 chains; 8 flagged critical-care.
- **Products:** 300 SKUs. About 70% ambient, 25% cold-chain, 5% Schedule X. Therapeutic classes: antipyretic, antibiotic, antiviral, cardiac, diabetic, oncology, IV fluids, vaccines, respiratory, GI. 60 essential medicines with price caps.
- **Demand:** 2 years of daily history from base × monthly seasonality (monsoon months boost antipyretics, antibiotics and IV fluids; winter boosts respiratory) × noise (CV 0.2–0.5).
- **Money:** standard cost ₹5–₹4,000 per unit; selling price 1.3–2.5× cost; price caps on essential items; holding cost 18% a year; expedite multipliers road 1.5×, air 4×.
- **Recovery days** per site type: DC 21, plant 45, supplier 60, port 10.
- Calibrate so the baseline network shows about ₹2,400 cr annual revenue and resilience score of about 62/100.
- Every UI page shows a small "Synthetic demo data" badge.

### B.4 Shock model
```python
class Shock(BaseModel):
    type: Literal["node_down","lane_down","supplier_capacity","demand_multiplier",
                  "cost_multiplier","market_block","temperature_loss",
                  "lead_time_shift","batch_quarantine","price_change"]
    target: TargetSelector      # ids, or a filter: {"site_type":"dc","region":"Mumbai"}, {"supplier_country":"CN"}, {"therapeutic_class":[...]}
    start_day: int
    duration_days: Distribution # fixed | triangular(min, mode, max) | lognormal(mean, sd)
    magnitude: Distribution     # meaning depends on type: capacity fraction remaining, multiplier, extra days, loss probability
    probability: float = 1.0    # chance the shock happens in a given Monte Carlo run
```
A **ScenarioTemplate** has `id`, `name`, `description`, `params` (name, label, unit, default, min, max, step, `is_live_slider`) and `build_shocks(params, network) -> list[Shock]`. The 13 templates in `docs/scenarios.md` are the only ones implemented now. The other 32 are listed with `status="coming_in_pilot"`.

### B.5 Simulation engine (`engine/simulate.py`)
- **Horizon:** 90 days (configurable). **Runs:** 200 Monte Carlo runs (`seed` fixed, so results are reproducible).
- **State arrays** (NumPy float32): `stock[runs, nodes, skus]` and `pipeline[runs, lanes, skus, max_lead_time]`. Loop over days, vectorise over runs and SKUs. To keep memory under 1.5 GB, simulate SKU families (group the 300 SKUs into about 60 families by class and storage) and allocate results back to SKUs pro rata.
- **Each day:**
  1. Sample shocks active today (per run).
  2. Arrivals from the pipeline.
  3. Expire stock past shelf life (FEFO: oldest consumed first; track age buckets of 30 days).
  4. Apply `temperature_loss` to cold stock at affected nodes.
  5. Serve demand at hospitals and stockists. Allocation follows the plan's priority: critical-care first, then essential, then the rest.
  6. Record unmet demand by node, SKU and customer type.
  7. Replenish with an order-up-to policy (target = lead-time demand + safety stock), limited by upstream stock, node throughput, supplier capacity, and `market_block`/licence rules. Schedule X stock only moves to licensed sites; cold stock only on reefer lanes.
  8. Ship along the primary lane, or the alternate lane if the primary is down and the plan allows it.
- **Outputs per run:** fill rate; stockout days by SKU and hospital; unmet units (critical-care, essential, other); expiry write-off units; temperature loss units; expedite units by mode; time to first stockout (time-to-survive); time to recover (days until fill rate is back to 98% of baseline).
- **Aggregate:** P10/P50/P90 for each KPI plus daily time series (P50 and P90) for charts and the map replay.
- **Performance:** one scenario (200 runs, 90 days) finishes in under 30 s on a laptop; a scenario with 3 plans in under 60 s. Report progress every 10 runs.

### B.6 Finance (`engine/finance.py`)
For each run: revenue at risk = unmet units × selling price; margin impact = lost margin + extra costs (expedite, spot-buy premium, tariff, backup power, holding cost of pre-build) − mitigation savings; working capital = average stock value change × days; write-off value = expired + temperature-lost units × standard cost; penalty = tender/hospital contract penalties. Landed cost = API cost (from the ingredient list) × (1 + tariff) × FX + freight. Plan ROI = (loss avoided − plan cost) ÷ plan cost. All results in ₹, aggregated as P10/P50/P90.

### B.7 Prescription (`engine/prescribe.py`)
- **Model:** OR-Tools (`pywraplp` with the GLOP or SCIP solver). Decisions are lever quantities by SKU family × week: transfers between DCs, alternate-lane volume, alternate-supplier volume (only suppliers approved for the target market; qualification lead time applies), expedite volume by mode, pre-build weeks of cover, spot buys, backup-power days, safety-stock raise.
- **Inputs:** P50 shortfall profile from the baseline simulation.
- **Objective:** minimise lever cost + penalty × unmet critical-care units + penalty × unmet essential units + penalty × other unmet units.
- **Constraints:** capacities, lead times, budgets, licences, storage class, approved markets.
- **Three plans** from three penalty weightings: Cost-optimal, Service-optimal, **Balanced (recommended)**.
- **Verification:** re-simulate each plan through `simulate()` to get true P50/P90 KPIs. Recommend the plan with the best ROI that meets the service floor (critical-care fill rate ≥ 98%).
- **Explanation JSON:** top 3 levers by impact, binding constraints, and one sensitivity line (re-run the balanced plan at the duration's P90 and note if the recommended plan changes).

### B.8 Stress test and resilience score (`engine/stress.py`)
For each site and supplier: `node_down` for N days (default 14). Time-to-survive (TTS) = days until downstream unmet demand begins (from stock cover). Time-to-recover (TTR) = the node's recovery days. Exposure ₹ = revenue lost over max(0, TTR − TTS) at P50. Return a ranked list, plus a heatmap (rows: node types/regions; columns: product classes).

**Resilience score (0–100):** 100 × (share of revenue whose supplying nodes all have TTS ≥ TTR), adjusted −5 per single-source China API above ₹50 cr revenue (floor 0). Show the formula in the UI's Assumptions sheet.

### B.9 Runs, cache and demo safety (`runs/`)
- `make seed` creates the database and **pre-computes** all 13 scenarios at default parameters, each with 3 plans, plus the stress test. Results are stored with `is_cached=true`.
- Live re-runs execute in a background worker (`concurrent.futures.ProcessPoolExecutor`, max 2 at once). Progress streams over SSE at `/api/runs/{id}/events`.
- The same parameters + seed return the cached result instantly (cache key = hash of template, params, seed, network version).
- **Demo-safe:** if a live run errors or exceeds 120 s, the UI keeps the last good result with the banner "Live re-run didn't finish; showing result from 10:42" and a Retry button.

### B.10 API (FastAPI, OpenAPI at `/docs`)
| Method & path | Purpose |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/executive` | Resilience score, top 5 risks (₹), TTS/TTR heatmap, KPI summary |
| `GET /api/network` | Sites, lanes and their risk level (GeoJSON-friendly) |
| `GET /api/network/sites/{id}` | Site detail: stock by class, batches near expiry, licences, criticality |
| `GET /api/scenarios/templates` | 13 live templates + 32 "coming in pilot" |
| `POST /api/scenarios` | Create a scenario from a template and params |
| `POST /api/runs` | Start a run `{scenario_id, plan_id?, runs?, seed?}`; returns cached result if available |
| `GET /api/runs/{id}` · `GET /api/runs/{id}/events` | Result · SSE progress |
| `GET /api/scenarios/{id}/plans` | The 3 plans with verified KPIs |
| `POST /api/approvals` · `POST /api/approvals/{id}/decide` | Send plan for approval · approve/reject with reason |
| `GET /api/approvals` · `GET /api/audit` | Queue · audit log |
| `POST /api/upload/{entity}` · `GET /api/upload/templates/{entity}.csv` | CSV import with validation report · download template |
| `POST /api/copilot/chat` | SSE stream of copilot messages and tool events |
| `POST /api/stress-test` | Run the stress test (cached by default) |

Generate the TypeScript client from OpenAPI (`openapi-typescript` + `openapi-fetch`) with `pnpm gen:api`.

### B.11 AI copilot via OpenRouter (`copilot/`)
- **Client:** the official `openai` Python SDK with `base_url="https://openrouter.ai/api/v1"` and `api_key=OPENROUTER_API_KEY`. Send headers `HTTP-Referer: <APP_URL>` and `X-Title: PharmaTwin`.
- **Models:** `OPENROUTER_MODEL` (primary; choose a current Claude Sonnet/Opus model id from openrouter.ai/models that supports tool calling) and `OPENROUTER_FALLBACK_MODELS` (comma-separated), passed as OpenRouter's `models` array in `extra_body` for automatic fallback. Never hard-code a model id in code.
- **Tools** (OpenAI function-calling format, executed server-side):
  - `list_scenarios()`
  - `get_run_summary(run_id)`
  - `create_scenario(template_id, params)`: validated by Pydantic. The UI shows a confirmation card; nothing runs until the user clicks **Run**.
  - `run_scenario(scenario_id)`
  - `compare_plans(scenario_id)`
  - `explain_kpi(run_id, kpi)`: returns assumptions and drivers.
  - `get_site(site_id)`
- **System prompt rules:**
  - Only state numbers returned by tools, and cite the run id ("Source: run R-0042").
  - Use ₹ lakh/crore.
  - Answer in two short parts: "Money" and "Service".
  - Say "I don't have that in the model" rather than guess.
  - Never claim actions were executed in an ERP.
- **Streaming:** SSE events `message_delta`, `tool_call`, `tool_result`, `scenario_proposal`, `done`, `error`.
- **Limits:** max 6 tool calls per turn; 30 s timeout per model call; cost guard via `max_tokens`. Log token usage per conversation.
- **No key set:** the panel shows "Copilot is off. Add an OpenRouter key in `.env` to enable it." The rest of the app works.

### B.12 Front end (Next.js, shadcn/ui, tweakcn)
- **Theme:** create a tweakcn theme from the tokens in `DESIGN.md` frontmatter (light and dark), install it with `npx shadcn@latest add <tweakcn theme url>` (or paste the CSS variables into `app/globals.css`), and add custom variables `--risk-critical|high|medium|low`, `--positive`, `--recommended`. Fonts: IBM Plex Sans and IBM Plex Mono via `next/font/google`.
- **Libraries:** shadcn/ui (Button, Card, Tabs, Sheet, Dialog, Command, Table, Badge, Slider, Tooltip, Skeleton, Sonner, Chart), TanStack Query, TanStack Table, react-map-gl with maplibre-gl, Recharts via shadcn charts, Framer Motion for number transitions only, next-themes, lucide-react.
- **Formatting:** `lib/format.ts` with `formatINR(value)` → "₹186.4 cr" / "₹12.4 L" / "₹84,500" and `formatPct`, `formatDays`; tooltips show exact values. Unit-test it.
- **Screens and routes:**
  1. `/executive` (default): resilience score gauge (0–100 with label), 4 KPI cards (Revenue at risk P50, Margin at risk, Critical-care fill rate, Days to first stockout), "Top 5 risks" table (risk, ₹ exposure, likelihood, owner, "Simulate" button), TTS vs TTR heatmap, buttons "Run stress test" and "Open hero scenario".
  2. `/network`: full-height map with sites coloured by risk, lanes, a filter bar (site type, region, storage class), a site detail sheet, and a toggle to a list view.
  3. `/scenarios`: library grid (13 live cards with a one-line story and headline metric; 32 greyed "Coming in pilot"), search and filter by category.
  4. `/scenarios/[id]` (Scenario studio): left: parameters (★ live sliders first); centre: a timeline of shocks; right: a "Run" panel with runs/seed and an estimate. A "Describe it in words" box sends text to the copilot.
  5. `/runs/[id]` (Results): header (scenario name, parameters chips, cached/live badge, run id, seed); **Money | Service** panel; P50/P90 fan chart of fill rate over days; stockouts by hospital table; map replay with day scrubber; "Assumptions" sheet; "Recommended plan" bar.
  6. `/compare/[scenarioId]`: 3 plans side by side (cost, loss avoided, ROI, critical-care fill rate, stockout days, working capital); the recommended plan has the Saffron badge; "Why this plan" explanation; a sensitivity note; "Send for approval".
  7. `/approvals`: queue table, approve/reject dialog (reason required), audit log tab.
  8. `/data`: download CSV templates, upload, validation report, "Use this network" switch (synthetic vs uploaded).
  - **Global:** left nav, top bar with ⌘K command palette (jump to screens and scenarios), theme toggle, "Synthetic demo data" badge, copilot sheet toggle.
- **States:** every data view has skeleton, empty and error states as defined in `DESIGN.md`.
- **Motion:** KPI numbers animate from old to new value (400 ms) after a re-run; the map replay animates daily steps; respect `prefers-reduced-motion`.

### B.13 Testing
- **Python:** `pytest` and `hypothesis`.
  - Engine determinism (same seed → same result).
  - Monotonic sanity for every template: a longer disruption never improves fill rate; a higher tariff never improves margin.
  - Finance unit tests; prescription feasibility.
  - API tests with `httpx`.
  - Performance test asserting a scenario finishes in under 30 s.
- **Front end:** Vitest for `format.ts` and hooks; **Playwright** `demo.spec.ts` walking the presenter flow in `docs/scenarios.md` (Executive → hero scenario → change slider → re-run → compare → approve → audit entry).
- **Lint and types:** ruff, mypy (strict for `engine/`), eslint, `tsc --noEmit`.
- CI (GitHub Actions): lint, type check, tests, build on every push.

### B.14 Running and deploying
- **Local:** `make setup` (uv sync, pnpm install), `make seed`, `make dev` (API on :8000, web on :3000). `docker-compose up` runs both.
- **Deploy:** web on **Vercel** (env `NEXT_PUBLIC_API_URL`); API on **Render** as a Docker web service, running `make seed` at build time so cached results exist (deterministic, no database to manage). Set `OPENROUTER_API_KEY` in Render's environment, not in the repo. Add basic HTTP auth (`DEMO_PASSWORD`) so only invited prospects can open the link.

### B.15 Environment variables (`.env.example`)
`OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_FALLBACK_MODELS`, `APP_URL`, `DATABASE_URL=sqlite:///./pharmatwin.db`, `SIM_RUNS=200`, `SIM_HORIZON_DAYS=90`, `SIM_SEED=42`, `DEMO_PASSWORD`, `NEXT_PUBLIC_API_URL=http://localhost:8000`.

---

## Part C: Prompts to paste into Cursor Agent

Use **Agent** mode. Start each step in a **new chat** so context stays clean, and attach the listed files with `@`. Wait for each step's acceptance checks to pass before starting the next. Commit after every step.

### Prompt 0: Plan (Day 0, about 1 hour)
```
@PRODUCT.md @DESIGN.md @CURSOR_BUILD_PROMPT.md @docs/scenarios.md @docs/superpowers/specs/2026-11-15-pharmatwin-demo-design.md

You are building the PharmaTwin demo described in these files. The design is approved; do not reopen product decisions.
1. Use the superpowers writing-plans skill to write docs/plans/2026-11-demo-plan.md: a task-by-task plan for Days 1–7 matching Part C of CURSOR_BUILD_PROMPT.md, each task with files touched, tests first, and a verification command.
2. List any contradictions or gaps you find in the spec as questions at the end of the plan. Do not invent answers to product questions; make and label engineering calls yourself.
Do not write application code in this step.
```

### Prompt 1: Foundations and synthetic data (Day 1)
```
@CURSOR_BUILD_PROMPT.md @DESIGN.md @docs/plans/2026-11-demo-plan.md

Implement Day 1 using test-driven development:
- Scaffold the repo layout in B.1: api/ with uv + FastAPI + SQLAlchemy + pytest; web/ with Next.js 15 (App Router, TypeScript, Tailwind v4, pnpm) and shadcn/ui initialised. Makefile targets setup/seed/dev/test/lint. .env.example per B.15. GitHub Actions CI per B.13.
- Data model per B.2 and the deterministic synthetic network generator per B.3 (seed 42), with tests asserting counts, calibration (about ₹2,400 cr annual revenue) and determinism.
- Theme: build the tweakcn/shadcn theme from DESIGN.md tokens (light + dark), IBM Plex fonts, custom risk variables. App shell: left nav, top bar, ⌘K palette, theme toggle, "Synthetic demo data" badge, empty pages for all routes in B.12.
- lib/format.ts with formatINR and tests.
Acceptance: `make setup && make seed && make test` pass; `make dev` shows the shell in light and dark mode; GET /api/network returns the synthetic network.
```

### Prompt 2: Simulation engine and finance (Day 2)
```
@CURSOR_BUILD_PROMPT.md @docs/scenarios.md

Implement Day 2 with tests first:
- engine/network.py, engine/shocks.py (Shock model B.4, all 13 templates from docs/scenarios.md, the 32 others as coming_in_pilot metadata).
- engine/simulate.py per B.5 (vectorised NumPy, SKU families, FEFO, licences, storage class, reefer lanes, allocation priority).
- engine/finance.py per B.6.
Tests: determinism, monotonic sanity for every template, performance (< 30 s for 200 runs × 90 days), finance unit tests.
Acceptance: `uv run pytest` passes; a CLI `uv run python -m pharmatwin.engine.cli run monsoon_dengue` prints Money and Service KPIs with P10/P50/P90.
```

### Prompt 3: Prescription, stress test, runs and API (Day 3)
```
@CURSOR_BUILD_PROMPT.md

Implement Day 3 with tests first:
- engine/prescribe.py per B.7 (three plans, re-simulated, explanation JSON).
- engine/stress.py per B.8 (TTS/TTR, exposure ranking, heatmap, resilience score).
- runs/ per B.9: pre-compute in `make seed`, background worker, SSE progress, cache keys, demo-safe fallback.
- All API routes in B.10 except copilot; generate the TypeScript client (pnpm gen:api).
Acceptance: `make seed` completes in under 15 minutes and stores 13 scenarios × 3 plans + stress test; POST /api/runs with default params returns instantly from cache; changing a param streams progress and finishes in under 60 s; pytest and API tests pass.
```

### Prompt 4: Executive, Network and Scenario screens (Day 4)
```
@DESIGN.md @PRODUCT.md @CURSOR_BUILD_PROMPT.md

Before UI work, load the impeccable skill and the design-taste-frontend skill (use only its anti-generic and typography guidance; this is an Operate-mode app, not a marketing site). Follow DESIGN.md exactly: tokens, the Saffron rule, the Label-Every-Risk rule, the Neutral Money rule, the Tabular rule.
Build screens 1–4 from B.12 (/executive, /network, /scenarios, /scenarios/[id]) on the real API with TanStack Query, including skeleton, empty and error states and keyboard access.
Acceptance: all four screens render real data in light and dark; the ⌘K palette jumps to any scenario; changing a live slider and pressing Run creates a run and navigates to /runs/[id]. Run `impeccable audit` on these routes and fix every high-severity finding.
```

### Prompt 5: Results, Compare, Approvals, Data (Day 5)
```
@DESIGN.md @CURSOR_BUILD_PROMPT.md @docs/scenarios.md

Build screens 5–8 from B.12: /runs/[id] with the Money | Service panel, fan chart, stockouts table, map replay with day scrubber, Assumptions sheet, Recommended-plan bar and SSE progress for live runs; /compare/[scenarioId]; /approvals with reason-required approval and audit log; /data with CSV templates, upload and validation report.
Implement the demo-safe banner (B.9) and animated number transitions (respect reduced motion).
Acceptance: the full presenter flow in docs/scenarios.md works by hand end to end; impeccable audit has no high-severity findings on these routes.
```

### Prompt 6: Copilot via OpenRouter (Day 6, first half)
```
@CURSOR_BUILD_PROMPT.md @PRODUCT.md

Implement the copilot per B.11: backend OpenRouter client using the openai SDK (base_url https://openrouter.ai/api/v1, model ids from env only, fallback models via extra_body models), tools, system prompt rules, SSE streaming, limits and logging; frontend copilot sheet with streamed messages, tool-activity chips, "Source: run …" links and the scenario confirmation card (nothing runs until the user clicks Run). Handle the no-key state.
Tests: mock OpenRouter responses (including tool calls) — never call the real API in tests; assert the copilot cannot report a number that did not come from a tool result.
Acceptance: with a real key in .env, asking "What if Mumbai floods for 15 days during a dengue surge?" proposes the monsoon_dengue scenario with duration 15, runs on confirmation, and answers in Money and Service parts citing the run id.
```

### Prompt 7: Polish, tests, deploy (Day 6 second half and Day 7)
```
@DESIGN.md @CURSOR_BUILD_PROMPT.md @docs/scenarios.md

1. Write Playwright demo.spec.ts covering the presenter flow; make it pass in CI.
2. Run impeccable critique and polish across all routes; fix findings. Check projected-screen legibility at 1280×720 and 1920×1080, both themes.
3. Run the improve-codebase-architecture skill on api/ and web/; apply changes that deepen module boundaries without changing behaviour; keep all tests green.
4. Add Dockerfile(s), docker-compose.yml, Render and Vercel config per B.14, basic auth via DEMO_PASSWORD, and a README with run, deploy and presenter instructions.
5. Use verification-before-completion: run every check in B.13 and report the results honestly.
Acceptance: a deployed URL behind a password runs the full presenter flow; CI is green; README explains everything a salesperson needs.
```

---

## Definition of done for the demo
- All 13 scenarios open instantly from cache and re-run live in under 60 s.
- Every result shows Money | Service with P50/P90 and an Assumptions sheet.
- Three plans per scenario with a recommended plan and "why".
- Approval with reason and an audit log entry.
- Copilot works through OpenRouter, cites run ids, and never invents numbers.
- Light and dark themes pass WCAG AA; impeccable audit shows no high-severity findings.
- Playwright presenter flow passes; deployed behind a password.
