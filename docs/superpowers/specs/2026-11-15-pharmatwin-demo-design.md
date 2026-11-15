# PharmaTwin Demo: Design

Date: 2026-11-15 · Status: **approved 2026-11-15** · Build tool: Cursor · AI provider: OpenRouter · Deadline: working demo within 7 days

## 1. Intent and the why
Win the first meetings with **pharma CFOs and Heads of Supply Chain**, who sign together. In a live meeting, the CFO changes a number (flood length, tariff %, supplier cut) and watches the ₹ impact, the service impact and the recommended plan update on one screen. The demo is built on the real engine, so it becomes the foundation of the pilot MVP.

Positioning: a **risk-simulation layer that sits alongside** SAP IBP, Kinaxis, o9 or Blue Yonder. It does not replace them.

## 2. Goals
1. Thirteen polished scenarios on a realistic synthetic Indian pharma network: China API shock, tariff escalation by ingredient list, USFDA warning letter, product recall, monsoon flood plus dengue surge, global shipping disruption, epidemic demand surge, supplier/contract-manufacturer failure, cold-chain failure, cyber/ERP outage, tender feasibility, inventory pre-build, whole-network stress test.
2. Every result uses one two-column layout, **Money | Service**, with one shared recommendation underneath.
3. Pre-computed results open instantly; changing a parameter re-runs live in under 60 seconds with progress shown.
4. An executive landing page: resilience score, top 5 risks in ₹ crore, time-to-survive vs time-to-recover heatmap, "Run stress test".
5. A network map, a scenario studio, a mitigation comparison and an approval queue (approval is simulated; no ERP write-back).
6. An AI copilot that explains results and builds a scenario from plain English, through **OpenRouter** (needs an OpenRouter key; the app works without it).
7. CSV upload of a prospect's sample network for a second meeting.
8. Runs with one command; optional public deployment.

## 3. Non-goals (this week)
Live ERP, warehouse or planning-system connectors; multi-tenant login and SSO; ERP write-back; tabletop exercise mode; the other 32 scenario templates (kept as greyed "coming in pilot" cards); Hindi; billing; external risk feeds (the Risk Radar uses scripted sample events).

## 4. Anti-goals (failure even if it "works")
- A number on screen that can't be traced to inputs and assumptions.
- A demo that stalls or errors in front of a client (hence pre-computed results plus an offline-safe fallback).
- Generic "AI dashboard" look. It must feel like a calm, credible enterprise tool.
- Any competitor code, assets or text copied.

## 5. Approaches considered
| Option | Trade-off | Decision |
|---|---|---|
| 1. Clickable prototype with canned numbers | Fastest and pretty, but can't answer "what if…", so thrown away later | Rejected |
| **2. Real engine, made safe for demos** | Real maths, live re-runs, carries into the MVP; tightest timeline | **Chosen by the user** |
| 3. Notebook / Streamlit | Real maths, but looks like a data-science tool to a CFO | Rejected |

## 6. Decided by the user
- Next.js + shadcn/ui + tweakcn front end; Python FastAPI back end; OR-Tools optimiser.
- Pharma focus; CFO + Head of Supply Chain buyers; sits alongside existing planning tools.
- Scenarios above; demo first, connectors in the pilot phase.
- Build in **Cursor**; AI models through **OpenRouter**. Claude produces the design and build prompt only; Cursor does the build.

## 7. Builder's calls (proposals the user can correct)
- **Storage:** SQLite through SQLAlchemy for the demo (zero setup, no failures in a meeting). Moving to Postgres/Supabase in the pilot is a configuration change.
- **Simulation:** a vectorised daily flow simulation in NumPy with Monte Carlo (200 runs by default) instead of SimPy, to meet the under-60-second target. Event-level SimPy detail is added in the pilot if needed.
- **One shock model for all scenarios:** each scenario is a list of shocks (`node_down`, `lane_down`, `supplier_capacity`, `demand_multiplier`, `cost_multiplier`, `market_block`, `temperature_loss`, `lead_time_shift`) with timing and probability. New scenarios are configuration, not code.
- **Prescription:** OR-Tools linear model choosing levers (transfers, alternate lane, alternate approved supplier, expedite, pre-build, allocation priority) to minimise cost plus a penalty for unmet critical demand.
- **Map:** MapLibre with free OpenStreetMap-based tiles; no paid map key.
- **Copilot:** OpenRouter (OpenAI-compatible API) with the model chosen by environment variable, fallback models, and tools `create_scenario`, `run_scenario`, `explain_kpi`, `compare_plans`; answers always cite the run they used.
- **Synthetic network:** 2 plants (Baddi, Sikkim), API imports via JNPT, 6 C&F agents, 4 warehouses (Mumbai, Chennai, Guwahati, Kolkata), 40 stockists, 25 hospitals, 300 SKUs (ambient, cold-chain, Schedule H/X), 2 years of seasonal demand, costs and prices in ₹. The demo labels everything as synthetic.
- **Design:** one tweakcn theme (light + dark), dense enterprise layout, Impeccable audit before handover.

## 8. Components
| Unit | Purpose | Interface |
|---|---|---|
| `engine/network` | Load and validate the network (synthetic or CSV) | `Network` object |
| `engine/shocks` | Scenario → list of shocks | `Scenario.to_shocks()` |
| `engine/simulate` | Monte Carlo daily flow → per-run KPIs | `simulate(network, shocks, plan, runs, seed)` |
| `engine/finance` | Units → ₹ margin, working capital, revenue at risk | `to_money(kpis, network)` |
| `engine/prescribe` | OR-Tools lever selection | `prescribe(network, shocks) → Plan` |
| `engine/stress` | Knock out each node; time-to-survive vs time-to-recover | `stress_test(network)` |
| `api` | FastAPI: scenarios, runs (with live progress), plans, approvals, upload, copilot | OpenAPI |
| `web` | Next.js screens | Generated TypeScript client |

## 9. Screens
Executive · Network map · Scenario studio · Results (Money \| Service) · Mitigation compare · Approval queue · Data upload · Copilot side panel.

## 10. Testing and verification
- Engine unit tests with fixed seeds; a sanity check that every scenario moves the KPIs in the expected direction (e.g. a flood never improves fill rate).
- API tests; one Playwright test that walks the full demo script.
- Performance check: a live re-run finishes in under 60 seconds.
- Impeccable audit with no high-severity findings.

## 11. Left to the builder
File layout, component breakdown, exact colours inside the chosen theme, and chart choices within shadcn charts.

## 12. Needs from the user
1. Repository: https://github.com/Sunil123135/Digital-Twin (provided).
2. An OpenRouter key in `.env` / Render environment (optional; copilot only).
3. Vercel and Render accounts for a password-protected public link.

## 13. Build instructions
See `CURSOR_BUILD_PROMPT.md` (Part B spec, Part C step-by-step Cursor prompts), `DESIGN.md`, `PRODUCT.md` and `docs/scenarios.md`.
