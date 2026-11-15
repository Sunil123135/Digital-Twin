# Build Prompt — "PharmaTwin": Digital Twin for Pharma Supply Chain Risk Simulation

> **Note (2026-11-15):** this is the long-term product vision. For the demo, the approved choices override it: build in **Cursor**, AI models through **OpenRouter** (not the Claude Agent SDK directly), SQLite instead of Supabase. See `CURSOR_BUILD_PROMPT.md`.

> Paste everything below the line into Claude Code (or another coding agent) at the root of an empty repository.
> Working name: **PharmaTwin** (rename freely).

---

## 0. Role, mission and working rules

You are a senior product engineer, supply-chain operations-research specialist and product designer. Build **PharmaTwin**: a cloud-based digital twin of a pharmaceutical distribution network that lets planners simulate disruptions (floods, port shutdowns, ingredient shocks, recalls, cold-chain failures, regulatory actions) and get **prescriptive, explainable, approvable** responses.

**Target customer:** pharma manufacturers and distributors (factory → C&F agent → stockist → hospital/retail pharmacy), including pharma businesses inside large Indian corporate groups. India first, with regulated export markets later.

**Buyers (they sign together):** the **CFO** and the **Head of Supply Chain**. Every result must speak both languages on one screen: **money** (margin, working capital, revenue at risk) and **service** (stockouts, fill rate, days to recover).

**Positioning: sit alongside, don't replace.** Many target customers already run SAP IBP, Kinaxis Maestro, o9 or Blue Yonder for planning. PharmaTwin is the **risk-simulation and resilience layer** that reads from those planning tools, the ERP and the data warehouse, stress-tests the plan, and sends approved responses back. **Non-goals:** no demand-planning engine, no S&OP workflow, no MRP, and no replacement of the customer's planning system.

**Deliverable for this engagement:** a **pilot-ready MVP**. It must be good enough to run a 3-week paid pilot with one pharma distributor, with real data from their ERP or data warehouse.

**Working rules:**
1. **Brainstorm and plan before coding.** Install and use the Superpowers skills (section 2). Run `brainstorming`, then `writing-plans`, then `executing-plans` / `subagent-driven-development`. Use `test-driven-development` and `verification-before-completion` on every feature.
2. **Clean-room only.** Study competitors from public material (section 3). Never copy proprietary code, UI assets, text, data or models. Never bypass logins, paywalls, licence checks or bot protection. Never scrape behind authentication. Features and ideas are fair game; expression is not.
3. **Evidence over assertion.** Every simulation result, recommendation and AI answer shows its inputs, assumptions and confidence.
4. **Human in the loop.** AI agents draft actions; a named planner approves before anything is written back to an ERP.
5. **Ship vertical slices.** Each milestone ends with a working, demo-able flow, not layers of half-built plumbing.

---

## 1. Tech stack (fixed)

| Layer | Choice |
|---|---|
| Front end | **Next.js 15 (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui**, themed with **tweakcn** |
| Maps & network views | MapLibre GL + deck.gl (geographic network, flood/heat overlays); React Flow (logical network graph) |
| Charts | shadcn/ui charts (Recharts); TanStack Table for dense grids |
| State/data fetching | TanStack Query; Zod schemas shared via OpenAPI-generated TS client |
| Back end | **Python 3.12 + FastAPI**, Pydantic v2, SQLAlchemy 2, Alembic |
| Simulation | **SimPy** (discrete-event), NumPy/SciPy Monte Carlo, NetworkX (network graph, criticality) |
| Optimisation | **Google OR-Tools** (MIP/CP-SAT, routing); HiGHS as a fallback LP/MIP solver |
| Forecasting | Nixtla `statsforecast` (baseline demand), with seasonality for monsoon/epidemic patterns |
| Jobs | Celery or Arq on Redis for long simulation runs; Server-Sent Events for live progress |
| Database | **Postgres (Supabase)** with PostGIS; Row-Level Security for multi-tenant isolation |
| Auth | Supabase Auth (email + SSO via Azure AD/Entra ID for enterprise) |
| AI agents | **Claude Agent SDK** with `claude-opus-5-5` for planning/reasoning agents and `claude-haiku-5-5` for high-volume classification (e.g. news triage) |
| Integrations | See section 6 (Fabric, Snowflake, Databricks, SAP, Dynamics 365, Oracle) |
| Infra | Docker Compose locally; deploy to Azure (Container Apps) or Vercel + Fly/Render. Data residency: India region by default |
| Quality | pytest + hypothesis, Vitest, Playwright E2E, ruff, mypy, eslint, Storybook for components |

---

## 2. Skills and tools to install first

Run these before writing product code. Verify each repository is the official source before installing.

```bash
# Superpowers brainstorming (plus writing-plans / executing-plans from the same repo)
npx skills add https://github.com/obra/superpowers --skill brainstorming
npx skills add https://github.com/obra/superpowers --skill writing-plans
npx skills add https://github.com/obra/superpowers --skill executing-plans
npx skills add https://github.com/obra/superpowers --skill test-driven-development

# Architecture review of the codebase after each milestone
npx skills add https://github.com/mattpocock/skills --skill improve-codebase-architecture

# Impeccable: design-quality skill (audit, critique, polish)
npx skills add https://github.com/pbakaus/impeccable --skill impeccable

# Taste skill: anti-generic front-end design guidance
npx skills add https://github.com/leonxlnx/taste-skill --skill design-taste-frontend

# shadcn/ui
npx shadcn@latest init
# tweakcn: design the theme visually at tweakcn.com, then install it
npx shadcn@latest add https://tweakcn.com/r/themes/<your-theme-id>.json

# REA: reverse-engineering MCP (used only as described in section 3)
npx rea-agents setup
```

**How to use the skills:**
- **improve-codebase-architecture:** run at the end of every milestone from M2 onward. Act on findings that deepen module boundaries (simulation engine, prescription engine, connectors, agents) before starting the next milestone.
- **Taste skill (design-taste-frontend):** apply before building any screen. It is tuned for marketing sites, so use it fully for the public website and demo landing page, and use only its anti-generic and typography guidance inside the app. Set design-variance, motion and density levels suited to an *enterprise operations tool*: low-to-medium variance, purposeful motion, high information density.
- **Impeccable:** run its audit, critique and polish commands at the end of every UI milestone. Fix every typography, spacing, contrast, empty-state and loading-state finding before calling the milestone done.
- **shadcn/ui + tweakcn:** all components come from shadcn/ui; all colour, radius, font and shadow tokens come from one tweakcn theme. No raw hex values in components.

---

## 3. Competitive research with REA (legal, clean-room)

### 3.1 Products to study
| Category | Products | What to learn |
|---|---|---|
| Concurrent planning / digital twin | Kinaxis Maestro, o9 Digital Brain, Blue Yonder Luminate, SAP IBP, Oracle SCM | What-if scenario branching, concurrent planning, supply/demand balancing |
| Network design & simulation | anyLogistix (AnyLogic), Coupa Supply Chain Design (LLamasoft), Optilogic Cosmic Frog | Simulation + optimisation workflows, scenario comparison |
| Risk intelligence | Resilinc, Everstream, Interos, Prewave, Exiger, riskmethods (Sphera) | Multi-tier supplier mapping, event feeds, risk scoring |
| Visibility / control tower | project44, FourKites, Everstream, o9 control tower | Live shipment tracking, ETA prediction, exception management |
| Pharma-specific | TraceLink, SAP ATTP, rfxcel (Antares Vision), Tive / Controlant (cold chain) | Serialisation, track-and-trace, temperature monitoring, recall |

### 3.2 Allowed sources
Public product pages, documentation, help centres, release notes, public demo videos and webinars, analyst reports (Gartner/IDC summaries), G2/Capterra/PeerSpot reviews, patents, conference talks and published case studies.

### 3.3 How to use REA (and only this way)
- **Public marketing pages:** `rea analyze-web-bundle` and `rea capture-browser-scenario` on public, logged-out pages only, to understand front-end patterns such as interactive demos, map libraries and chart libraries. Respect robots.txt and terms of service; low request rates; no automation behind logins.
- **Open-source supply-chain software:** use REA's JavaScript, Electron and route-inventory tools freely on OpenBoxes, Odoo Inventory, ERPNext, Apache OFBiz and open-source SimPy/AnyLogic-style models, to learn data models and workflows.
- **Your own product:** run `rea capture-browser-scenario` on PharmaTwin to record real user flows. Use `rea environment-build` on the resulting HAR to create **agent test environments**, then evaluate the PharmaTwin AI agents against them (regression tests for the copilot).
- **Do not** use REA on competitors' logged-in apps, desktop clients, trial instances whose terms forbid reverse engineering, or to extract code, models or data.

### 3.4 Starting research already done
`docs/research/competitor-scenarios.md` (copy it into the repo) summarises what Kinaxis, Blue Yonder, SAP IBP, o9, Coupa, anyLogistix, Resilinc and Everstream publicly promote. The **table-stakes features** buyers now expect:
1. Isolated scenario copies with branching and side-by-side comparison.
2. Results in units **and** money.
3. An AI copilot that explains and creates scenarios.
4. Control-tower alerts that become a scenario in one click.
5. Shelf-life and expiry-aware planning.
6. Multi-tier supplier mapping.
7. A systematic whole-network stress test, not only hand-built scenarios.

### 3.5 Output
Write `docs/research/feature-matrix.md`: features (rows) × competitors (columns) × PharmaTwin decision (Build MVP / Build later / Skip). Each cell cites its public source URL. Then write `docs/research/differentiation.md` covering what PharmaTwin does better: India pharma context, affordability, a pilot that runs in weeks, AI copilot, regulatory awareness.

---

## 4. Solution approaches considered (Superpowers brainstorm)

Before building, evaluate these four ways of making a digital twin, and record the decision in `docs/adr/0001-twin-architecture.md`:

1. **Simulation-first** (anyLogistix style): discrete-event simulation of every node and lane. Most realistic; slower; needs good parameters.
2. **Optimisation-first** (Coupa/LLamasoft style): network flow / MIP model solved per scenario. Fast prescriptions; less time-dynamic.
3. **Graph-risk-first** (Resilinc/Interos style): multi-tier knowledge graph plus risk scoring and propagation. Great for exposure; weak for operational response.
4. **Event-driven control tower** (project44/o9 style): live events trigger alerts and playbooks. Great for operations; little "what-if".

**Required decision: a hybrid.** Use a graph model as the twin backbone (3). Monte Carlo + SimPy evaluates disruption impact over time (1). OR-Tools prescribes the best mitigation (2). A control-tower layer turns live signals into scenarios automatically (4). Each engine sits behind its own interface so it can be swapped or improved independently.

---

## 5. Domain model (Postgres)

Multi-tenant: every table has `tenant_id`, protected by RLS.

- **Network:** `site` (type: plant, C&F agent, distributor warehouse, stockist, hospital, retail pharmacy, port, airport, cold store; geo point; drug-licence number and expiry; GDP certification; storage classes: ambient, 2–8 °C, frozen, narcotic vault), `lane` (from, to, mode: road/rail/air/sea; lead-time distribution; cost; reefer capability; alternate routes), `carrier`.
- **Products:** `product` (SKU, molecule/API, strength, dosage form, therapeutic class, Schedule H/H1/X, NDPS flag, NLEM/essential flag, DPCO price cap, storage class, shelf life), `bom_api` (product → active ingredient → supplier → country of origin), `substitute` (therapeutic alternatives with clinical-equivalence notes).
- **Inventory:** `batch` (batch/lot, manufacture date, expiry, QA status: released/quarantine/rejected/recalled, serial/QR code reference), `stock_position` (site × batch × qty × status), `safety_stock_policy`.
- **Demand & orders:** `demand_history`, `forecast`, `sales_order`, `purchase_order`, `transfer_order`, `shipment` (with temperature log reference).
- **Suppliers:** `supplier` (tiers 1–3, approved-vendor status per product, regulatory inspection history, WHO-GMP/USFDA/EU-GMP status, financial risk score, country), `supplier_site`.
- **Risk & scenarios:** `risk_event` (source, type, geo polygon, severity, start/end, confidence), `scenario` (template, parameters, version, parent scenario for branching), `simulation_run` (seed, iterations, status, KPIs), `mitigation_plan`, `action` (draft → approved → executed → verified; approver; ERP write-back reference), `audit_log` (immutable, append-only; 21 CFR Part 11-style e-signature fields).

Seed a realistic **synthetic Indian pharma network**: 2 plants (Baddi, Sikkim), 1 API import via JNPT/Mundra, 6 C&F agents, 4 distributor warehouses (Mumbai, Chennai, Guwahati, Kolkata), 40 stockists, 25 hospitals in 3 chains, 300 SKUs across ambient, cold-chain and narcotic classes, and 2 years of daily demand with monsoon, dengue and festival seasonality.

---

## 6. Data integration (three paths, all in the MVP)

Build a connector framework: `connectors/<name>/` with a common interface `discover() → schema`, `extract(entity, since) → records`, `map(records) → canonical model`, `health()`, and for ERPs only `write_back(action)`, which is gated by approval. A **mapping studio** UI lets users map source columns to PharmaTwin fields, save mappings as versions, preview row counts and validation errors, and schedule incremental syncs.

### 6.1 Data warehouses / lakehouses
| Source | Method |
|---|---|
| **Microsoft Fabric** | OneLake (ADLS Gen2 API, Delta tables) and the Lakehouse/Warehouse SQL analytics endpoint via ODBC with Entra ID service principal |
| **Snowflake** | `snowflake-connector-python` / Snowpark with key-pair auth; support Secure Data Sharing for read-only shares |
| **Databricks** | `databricks-sql-connector` against a SQL warehouse; Unity Catalog permissions; Delta Sharing as an option |

### 6.2 Live ERP connectors (read + approved write-back)
| ERP | Read | Write-back (after approval) |
|---|---|---|
| **SAP S/4HANA** | OData APIs: material stock, batch, purchase orders, sales orders, stock transport orders, business partners | Create purchase requisition / stock transport order |
| **SAP ECC** | RFC/BAPI via `pyrfc`, IDocs (MATMAS, ORDERS, DESADV) | BAPI_PR_CREATE, STO creation |
| **Microsoft Dynamics 365 SCM / F&O** | OData data entities (released products, on-hand inventory, batches, purchase/sales/transfer orders) | Create planned/transfer orders |
| **Oracle NetSuite** | SuiteTalk REST + SuiteQL | Create transfer order / purchase order |
| **Oracle Fusion SCM** | Fusion REST APIs (inventory, lots, purchase orders) | Create transfer/purchase orders |

### 6.3 Planning systems (sit-alongside connectors)
| Planning tool | Read | Send back (after approval) |
|---|---|---|
| **SAP IBP** | OData APIs for key figures and master data (consensus demand, supply plan, projected stock, safety stock, shelf-life attributes) | Approved plan written to a *separate IBP scenario or version* for the planner to accept in IBP; never overwrite the baseline |
| **Kinaxis Maestro** | Data integration exports / REST APIs (customer-enabled) | Approved actions as files or an API payload into a Maestro scenario |
| **o9 / Blue Yonder** | Customer-provided extracts or APIs | Approved actions as files or an API payload |

Rules: the planning system stays the **system of record for the plan**; PharmaTwin is the **system of record for risk, scenarios and decisions**. Show the plan's source and timestamp on every screen.

### 6.4 Fallback
Excel/CSV templates for every canonical entity, with validation reports, so a pilot can start before IT approves connectors.

### 6.5 Building connectors without paid licences
Simulation and optimisation run in PharmaTwin's own Python back end; **no scenario needs Databricks, Snowflake or Fabric to run.** Those are only places a *customer's* data may live. Build and test each connector against free sandboxes, and keep a contract-test suite with recorded fixtures so CI never needs live accounts:
- **Databricks:** Free Edition is for development only. Its terms forbid commercial use: one 2X-Small SQL warehouse, no SSO, no SLA. Production connections always use the **customer's** workspace and licence.
- **Snowflake:** 30-day free trial for development; customer account in production.
- **Microsoft Fabric:** free Fabric trial capacity plus the Azure free account; customer tenant in production.
- **SAP:** SAP Business Accelerator Hub sandbox APIs for S/4HANA and IBP payload shapes; customer system in production.
- **Dynamics 365:** 30-day trial environment.
- **Oracle NetSuite / Fusion:** no free developer account; use recorded fixtures until a partner sandbox or the pilot customer's sandbox is available.

### 6.6 Rules
Credentials go in a secrets vault (Azure Key Vault / Supabase Vault), never in the database or logs. Every sync writes data-quality metrics (completeness, freshness, mismatches) to a **Data Health** page. Every write-back is idempotent, logged, and reversible where the ERP allows it.

---

## 7. External risk signals (control-tower feed)

Ingest with clear licensing: IMD weather and rainfall warnings, GDACS and ReliefWeb disaster alerts, NASA FIRMS (fire), GDELT news events, port notices (JNPT, Mundra, Chennai), Central Water Commission flood forecasts, public CDSCO alerts (not-of-standard-quality drug lists, licence suspensions), WHO medical product alerts, and USFDA import alerts / warning letters for supplier sites. Haiku-tier agents classify and geo-tag events. Events that intersect the network's sites, lanes or suppliers create **suggested scenarios**.

---

## 8. Scenario library (build all as configurable templates)

Each template has parameters (location, start, duration, severity, probability distribution), affected entities (auto-selected by geography or rule), and default mitigation levers.

**A. Climate & geography**
1. Monsoon flood closes highways / submerges a warehouse (Mumbai, Chennai, Guwahati, Kerala)
2. Cyclone landfall (Odisha, Andhra, Gujarat coast) with port and power outage
3. Heatwave plus grid power cuts threatening 2–8 °C storage
4. Landslide / snow closure of hill routes (Sikkim, Himachal plants, North-East supply)
5. Earthquake at a manufacturing cluster

**B. Logistics & infrastructure**
6. Port shutdown or congestion (JNPT, Mundra, Chennai): strike, customs IT outage
7. Red Sea / Suez rerouting adding 2–3 weeks to imports and exports
8. Air-cargo capacity crunch for cold-chain biologics
9. Truckers' strike / highway blockade / state border closure
10. Reefer truck breakdown or cold-room failure mid-route
11. Fuel price spike raising lane costs

**C. Supply & ingredients**
12. China export restriction or tariff on key APIs/KSMs (paracetamol, antibiotics, vitamins)
13. Single-source API supplier fire or shutdown
14. Supplier receives a USFDA warning letter / import alert / WHO-GMP downgrade
15. Packaging material shortage (glass vials, blister foil)
16. Supplier financial distress or insolvency

**D. Regulatory & quality**
17. Product recall: contaminated or not-of-standard-quality batch; trace and isolate all affected units by batch and serial
18. Drug-licence suspension of a distributor or warehouse
19. DPCO/NPPA price revision squeezing margin on essential drugs
20. Ban on a fixed-dose combination (FDC) by CDSCO
21. New serialisation/QR mandate deadline, and its readiness impact
22. GDP audit observation halting dispatches from a site
23. NDPS/narcotic quota or permit delay

**E. Demand**
24. Epidemic surge (dengue, malaria, COVID-like wave), with demand spikes by therapeutic class
25. Government tender win or loss changing volumes
26. Hospital chain adds new hospitals (network expansion)
27. Competitor stockout shifting demand to you

**F. Operations & cyber**
28. Ransomware / ERP outage at a warehouse
29. Warehouse labour shortage during a festival season
30. Near-expiry stock accumulation (write-off risk)

**G. Compound scenarios**
31. Flood + epidemic surge (monsoon dengue): the default "hero" demo
32. API shock + recall of an alternate product
33. User-built composite: chain any templates on a timeline

**H. Market-leader scenarios** (ideas drawn from public material by Kinaxis, Blue Yonder, SAP IBP, o9 and Coupa; built clean-room)
34. **Tender bid feasibility:** can we serve this government or hospital-chain tender at this volume and price?
35. **Supplier de-commitment:** a supplier cuts the confirmed quantity (e.g. to 60%); who gets supplied first
36. **Inventory pre-build before a known event** (tariff date, monsoon, plant shutdown): working capital vs loss avoided
37. **Alternate source not registered in a market:** regulatory approval lead time (6–18 months) per market
38. **Shortage-reporting trigger:** forecast stockout crosses a regulator's reporting threshold; warn before it happens
39. **Tariff escalation traced through each product's ingredient list:** margin by SKU and market; price, sourcing and production-shift levers
40. **Whole-network stress test:** knock out every node in turn; compare time-to-survive with time-to-recover; rank ₹ exposure
41. **New product launch ramp-up:** readiness of capacity, API, packaging and distribution
42. **Expiry-driven reallocation:** move short-dated stock to high-use sites before write-off
43. **Currency swing** (INR vs USD and CNY) on imported ingredients and exports
44. **Network redesign:** add a warehouse, a second plant or a contract manufacturer; capital cost vs resilience gain and payback
45. **Seasonal plan under risk** (monsoon, festivals, flu season): P50/P90 revenue and stock build by month

**Top 10 for corporate buyers** (polish these first; each result shows the CFO and Head of Supply Chain columns):
1. China ingredient shock (12) · 2. Tariff escalation by ingredient list (39) · 3. USFDA warning letter at a plant (14) · 4. Product recall (17) · 5. Monsoon flood at a hub (1/31) · 6. Global shipping disruption (7) · 7. Epidemic demand surge (24) · 8. Supplier or contract-manufacturer failure (13/35) · 9. Cold-chain failure (3) · 10. Cyberattack / ERP outage (28).
Plus three that sell to both buyers at once: **tender feasibility (34)**, **pre-build (36)** and the **whole-network stress test (40)**.

**Default pilot configuration** (setting `PILOT_PROFILE`, changeable without code):
- `hospital_distributor` *(default)*: regional distributor supplying hospital chains; hero scenarios 1, 31, 17.
- `manufacturer_network`: scenarios 6, 12, 13.
- `cold_chain_biologics`: scenarios 3, 8, 10.
- `government_medical_supply`: scenarios 24, 25.
- `exporter_regulated_markets`: scenarios 7, 14, 22.

---

## 9. Simulation and prescription engine

1. **Twin build:** compile the network into a graph. Compute node and lane criticality (betweenness, time-to-survive, time-to-recover per node, as in Simchi-Levi's TTS/TTR approach) and single-points-of-failure per SKU.
2. **Impact simulation:** Monte Carlo (default 500 iterations, seeded, reproducible) over disruption duration and lead-time distributions. SimPy steps through daily inventory flows, honouring **FEFO**, shelf life, storage-class constraints, licence constraints (only licensed sites may hold Schedule X/NDPS) and cold-chain excursion probability.
3. **Financial translation layer:** standard cost per SKU, landed cost built from the ingredient list (tariff, FX, freight), selling price and price caps, holding cost, penalty clauses (tenders, hospital contracts). Every service result is converted into ₹ margin, working capital and revenue at risk.
4. **KPIs per run, in two columns:** *CFO:* revenue at risk, margin impact, working capital, expediting and write-off cost, cost of the mitigation vs loss avoided (ROI). *Head of Supply Chain:* fill rate, stockout days and patients/orders affected (weighted by NLEM/essential and critical-care flags), temperature-excursion loss, time-to-survive and time-to-recover. Both columns show P50/P90 bands.
5. **Prescription (OR-Tools):** pick the cheapest mix of levers that meets service targets:
   - alternate lanes/modes; inter-warehouse transfers; pre-positioning before forecast events
   - safety-stock and reorder-point changes; expedited or emergency purchases
   - alternate approved suppliers; therapeutic substitutes (flagged for clinical review)
   - allocation rules (protect ICU/critical-care hospitals first; fair-share otherwise)
   - cold-chain contingencies (backup generators, dry-ice, alternate cold stores)
6. **Compare:** side-by-side baseline vs mitigated vs alternative plans; branching scenario tree (Kinaxis-style "what-if" versions).
7. **Explainability:** each recommendation shows its drivers, binding constraints, sensitivity ("if the flood lasts 3 more days, plan B becomes cheaper") and confidence.
8. **Performance targets:** a 300-SKU, 80-node network, 30-day horizon and 500 iterations completes in under 90 seconds; progress streams live.

---

## 10. AI agents (copilot with human approval)

Built on the Claude Agent SDK. Every tool call is logged; agents never write to an ERP directly.

| Agent | Job |
|---|---|
| **Sentinel** | Watches the external signals (section 7) and internal data; flags events that touch the network; drafts a scenario |
| **Scenario Architect** | Turns plain language ("What if Chennai port is shut for 10 days during a dengue spike?") into a parameterised scenario; asks clarifying questions |
| **Analyst** | Runs simulations, interprets results, explains trade-offs in plain English (and Hindi), cites the numbers |
| **Planner** | Drafts mitigation plans and ERP actions (transfer orders, purchase requisitions) for approval |
| **Compliance Checker** | Checks every draft against licences, storage class, NDPS rules, GDP, DPCO price caps and recall status; blocks non-compliant actions with reasons |
| **Recall Tracer** | Traces affected batches/serials forward to every site and customer in minutes and drafts recall notices |
| **Briefing Writer** | Produces daily risk briefings and board-ready PDFs/slides |

**Approval workflow:** Draft → Compliance check → Planner approves (e-signature with reason) → Write-back → Verify (read back from ERP) → Close. Approval limits are configurable by role and amount (e.g. above ₹5 lakh needs the supply-chain head).

**Agent evaluation:** a golden set of 50 scenario questions with expected answers, plus REA-built agent environments from recorded app sessions (section 3.3). These run in CI.

---

## 11. Screens and UX

Design principles: calm, dense, trustworthy; decisions in three clicks or fewer; every number clickable down to its source data; keyboard-first (⌘K command palette); light and dark themes; WCAG 2.2 AA; works on a laptop and a tablet in a war room; English first, with Hindi copy for briefings.

0. **Executive mode (landing page for the CFO and Head of Supply Chain):** resilience score by business unit, plant and product family; top 5 risks in ₹ crore; time-to-survive vs time-to-recover heatmap; buttons for "Run stress test" and "Start tabletop exercise" (a guided crisis simulation run live with the leadership team). Every simulation result uses the **two-column layout: Money | Service**, with one shared recommendation underneath.
1. **Onboarding & Data Connect:** pick a source (Fabric / Snowflake / Databricks / SAP / Dynamics / Oracle / Excel); connection test; mapping studio; data-health score.
2. **Network Twin map:** geographic map (MapLibre + deck.gl) with sites, lanes, live risk overlays (flood polygons, heat, port status) and a toggle to a logical graph view (React Flow). Click any node for stock, batches, expiry, licences and criticality.
3. **Risk Radar / Control Tower:** live event feed, exposure heatmap by site × therapeutic class, suggested scenarios with one-click "simulate".
4. **Scenario Studio:** template gallery (section 8); parameter form *or* natural-language prompt; timeline composer for compound scenarios; branch and version.
5. **Simulation Results:** KPI cards with P50/P90 bands; stockout timeline by SKU/hospital; animated playback of the disruption on the map; fan charts.
6. **Mitigation Compare:** 2–4 plans side by side (cost, service, risk, compliance); "why this plan" explanation; sensitivity sliders.
7. **Action Center:** approval queue, e-signature, write-back status, verification, audit trail.
8. **Recall Command:** batch/serial search; forward/backward trace graph; affected customers; recall notice drafts; status tracker.
9. **Supplier & API Risk:** multi-tier map; country-concentration charts (e.g. % of APIs from China); single-source alerts; alternate-vendor qualification tracker.
10. **Pilot ROI dashboard:** baseline vs pilot period: response time, stockout incidents, expiry write-offs, expediting cost. Exportable for the case study.
11. **Copilot panel:** persistent side panel; chat with the agents; every answer links to the scenario, run and data it used.
12. **Admin:** tenants, roles (Viewer, Planner, Approver, Admin, Auditor), approval limits, connectors, audit-log export.

Every screen has designed empty, loading, error and partial-data states. Use Impeccable and the Taste skill to review each one.

---

## 12. Security, compliance and trust

- Tenant isolation with Postgres RLS, tested by automated cross-tenant access tests.
- SSO (Entra ID / Okta), MFA, role-based access, approval limits.
- Immutable audit log with 21 CFR Part 11 / EU Annex 11-style e-signature fields (who, what, when, why).
- India **DPDP Act 2023** compliance; data residency in India by default; encryption in transit and at rest; customer-managed keys as an enterprise option.
- Regulatory knowledge built in: Drugs & Cosmetics Act and Rules, CDSCO GDP guidelines, revised Schedule M, NDPS Act, DPCO 2013/NPPA, QR-code mandates for APIs and top brands, DGFT export track-and-trace; for exports, US DSCSA and EU FMD.
- Plan for SOC 2 Type II and ISO 27001 (log the controls from day one).

---

## 13. Monetisation features to build into the product

- **Plans:** Pilot (fixed fee, 3 weeks); Professional (₹1–2.5 lakh/month, warehouse/CSV connectors, 10 users); Enterprise (₹2.5–5 lakh/month, live ERP connectors, control tower, SSO, unlimited scenarios); per-scenario fee (₹10,000–50,000) for non-subscribers; real-time control-tower integration as a premium add-on.
- Usage metering: simulation runs, connector syncs, agent tokens. Billing via Razorpay (India) and Stripe (international).
- Shareable, branded scenario reports (PDF/PPTX) that customers forward internally, which also helps growth.

---

## 14. Pilot validation (built into the product)

- **Profile:** `hospital_distributor` by default (section 8).
- **Baseline:** import 12 months of history; compute baseline response time (from event detection to an approved plan) and stockout incidents.
- **Pilot:** 3 weeks live; Sentinel watches IMD/CWC alerts; run the monsoon flood + dengue compound scenario and a recall drill.
- **Targets:** response time at least **30% faster**; stockout incidents at least **35% fewer**; recall trace in under 2 hours; zero non-compliant actions approved.
- **Output:** the Pilot ROI dashboard plus an auto-generated case-study draft (with customer approval) for sales and LinkedIn content.

---

## 15. Milestones (vertical slices)

| # | Weeks | Outcome |
|---|---|---|
| M0 | 1 | Research (section 3), ADRs (section 4), design system (tweakcn theme, Taste settings), repo + CI, synthetic data generator |
| M1 | 2–3 | Canonical model, CSV import, Network Twin map, node detail |
| M2 | 4–5 | Scenario Studio + Monte Carlo/SimPy engine + Results for templates 1, 6, 12, 17, 24, 31 |
| M3 | 6–7 | OR-Tools prescription, Mitigation Compare, Action Center with approvals and audit log |
| M4 | 8–9 | Connectors: Fabric, Snowflake, Databricks, SAP S/4HANA (read), Dynamics 365 (read), NetSuite/Oracle Fusion (read), SAP IBP (read); mapping studio; Data Health; Executive mode with Money \| Service results; scenarios 34, 36, 39, 40 |
| M5 | 10–11 | AI agents (Sentinel, Architect, Analyst, Planner, Compliance, Recall Tracer), external signals, Risk Radar, Recall Command |
| M6 | 12 | ERP write-back (approved actions), remaining scenario templates, Pilot ROI dashboard, Impeccable polish pass, security hardening, pilot runbook |

---

## 16. Definition of done (every milestone)

- Unit, integration and Playwright E2E tests pass; simulation results are reproducible with a fixed seed.
- Impeccable audit has no open high-severity findings; WCAG AA contrast passes; all four UI states are designed.
- Docs updated: `README.md`, `docs/adr/`, `docs/runbooks/`, OpenAPI spec, connector setup guides.
- A 2-minute demo script for the milestone's flow is recorded in `docs/demos/`.
- No secrets in code; dependency audit clean; tenant-isolation tests pass.

---

## 17. Beyond the MVP (what else makes this genuinely useful)

1. **Pre-emptive mode:** 7–14-day monsoon/cyclone forecasts automatically trigger pre-positioning plans before the event.
2. **Hospital-side twin:** ward-level consumption for critical drugs (oncology, ICU, anaesthesia), with distributor and hospital sharing one view.
3. **Collaborative network:** suppliers confirm capacity and alternates inside the platform (a supplier portal); WhatsApp alerts and approvals for field teams.
4. **Expiry and returns optimiser:** redistribute near-expiry stock to high-consumption sites before write-off.
5. **Cold-chain IoT:** ingest data loggers (Tive, Sensitech, local IoT) for live excursion risk.
6. **Benchmarking:** anonymised cross-customer resilience scores ("your Chennai network recovers 2× slower than peers").
7. **Insurance and finance:** resilience scores for parametric flood insurance and supply-chain finance.
8. **ESG:** emissions per lane and per mitigation choice (Scope 3), so planners can see the cost/service/carbon trade-off.
9. **Tender and contract intelligence:** simulate government tender commitments before bidding.
10. **Public-health mode:** a state medical-supply version for epidemic preparedness (a possible CSR or grant channel).
11. **Marketplace of scenario templates** contributed by consultants and partners.
12. **MCP server for PharmaTwin**, so customers' own AI agents can query the twin and run scenarios.
13. **Board risk pack:** a quarterly PDF/PPTX of the resilience score, top risks, decisions taken and their outcomes, for the board and audit committee, plus supply-chain risk data for SEBI's sustainability report (BRSR).
14. **Tender desk:** sales enters a tender; PharmaTwin returns go/no-go, margin and penalty risk within minutes.
15. **Working-capital optimiser:** a CFO view of where safety stock is worth its cost and where cash can be released.
16. **Supply-chain due diligence for M&A:** score an acquisition target's network resilience from its data room.
17. **Microsoft Teams / WhatsApp approvals:** alerts and one-tap approval for executives away from their desks.
18. **Risk-register sync:** push top risks and mitigations into the customer's governance tools (ServiceNow GRC, Archer).
19. **Excel add-in:** finance teams pull scenario results into their own models.

---

## 18. Start now

1. Install the skills in section 2.
2. Run Superpowers `brainstorming` to confirm this spec with me. Ask me any open questions, one at a time.
3. Produce `docs/research/feature-matrix.md` (section 3) and `docs/adr/0001-twin-architecture.md` (section 4).
4. Run `writing-plans` for milestone M0–M1, then execute with TDD.
5. After every milestone, run the Impeccable polish pass and show me a demo before moving on.
