# What the market leaders sell: scenarios and features to learn from

Compiled 2026-11-15 from public vendor pages, press releases, white papers and review sites.
Most sources are vendor marketing, so read them as **what buyers are being told to expect**, not as verified results.

## 1. What each leader offers

| Vendor | Scenarios and features they promote (public sources) | Lesson for PharmaTwin |
|---|---|---|
| **Kinaxis Maestro** | What-if planning for **tenders, supply disruptions and new product introductions**. Dr. Reddy's quote: check whether a tender can be served *before bidding*. **Expiry management and dynamic order allocation**. A dedicated **Tariff Response** product (2025). Fit for firms that must **report shortages to regulators** (FDA/EMA/BfArM). Life-sciences customers: Merck, Novartis, BMS, Sobi. | Tender feasibility and shortage-reporting triggers are concrete pharma scenarios we were missing. |
| **Blue Yonder** | Digital-twin scenario modelling; distribution plans that respect **shelf life** and **alternate sourcing compliance by market**; cold-chain monitoring; multi-tier visibility via its network; multi-echelon orchestration. | "Is the alternate supplier *registered* in this market?" is a pharma-only constraint. Model it. |
| **SAP IBP** | **Harmonised scenario management** (release 2602/2605): run a full planning cycle in an isolated copy, then compare. **Financial and unit what-ifs**; shelf-life planning; new-product planning; seasonal scenarios; control tower with alerts and simulation; Joule AI copilot. | Every scenario must show units **and** money, with a side-by-side comparison. This is baseline expectation now. |
| **o9 Solutions** | Tariffs linked automatically to **materials, suppliers and bills of material** for cost exposure. Scenarios for **tariff changes, supplier de-commitments and sourcing shifts**, with levers such as **price changes and inventory pre-builds**. A **stress-testing engine** (supplier failure, tariff escalation, logistics). A knowledge graph turns events into lead-time, cost, capacity, revenue and margin effects. Prewave partnership for multi-tier risk. | A CFO-grade translation from event to margin, and a systematic stress test rather than one scenario at a time. |
| **Coupa (formerly LLamasoft)** | **Time-to-survive vs time-to-recover** per node; risks clustered by impact × probability; network design scenarios. | A TTS/TTR heatmap across every node is a strong, simple board visual. |
| **anyLogistix** | Supply-chain digital twin, network design from scratch (greenfield analysis), risk analysis, simulation plus optimisation. | Network redesign is a sellable strategic use case. |
| **Resilinc / Everstream / Interos** | Multi-tier mapping down to **part and site level**; sub-tier discovery; live event monitoring; finding dual-source options; financial, cyber, geographic and ESG risk. Everstream cites a global pharma customer. | Supplier mapping is expected; we can buy or partner for event data rather than build it. |

## 2. New scenarios to add (not already in the 33-scenario library)

| # | Scenario | Source of the idea | CFO sees | Head of supply chain sees |
|---|---|---|---|---|
| N1 | **Tender bid feasibility**: can we serve a government or hospital-chain tender at this volume and price? | Kinaxis (Dr. Reddy's) | Margin per tender, penalty risk for short supply | Capacity, API cover, service level |
| N2 | **Supplier de-commitment**: a supplier cuts the confirmed quantity to 60% | o9 | Revenue at risk, cost of spot buying | Products and customers affected, allocation plan |
| N3 | **Inventory pre-build before a known event** (tariff date, monsoon, plant shutdown) | o9 | Working capital and holding cost vs loss avoided | Build schedule, warehouse space, expiry risk |
| N4 | **Alternate source not registered in a market**: regulatory variation lead time | Blue Yonder | Lost sales during the approval wait | Which markets can switch now and which must wait 6–18 months |
| N5 | **Shortage-reporting trigger**: forecast stockout crosses the regulator's reporting threshold | Kinaxis | Penalty and reputation exposure | Early warning date, mitigation needed to avoid the report |
| N6 | **Tariff escalation linked to bill of materials**: cost exposure by product and market | o9, Kinaxis | Margin by SKU and market, price-change lever | Sourcing or production shifts |
| N7 | **Whole-network stress test (TTS vs TTR)**: knock out every node one at a time | Coupa, o9 | Ranked ₹ exposure per node, i.e. where to spend on resilience | Single points of failure, recovery plans |
| N8 | **New product launch ramp** | Kinaxis, SAP IBP | Launch revenue at risk | Capacity, API, packaging, distribution readiness |
| N9 | **Expiry-driven reallocation**: move short-dated stock to high-use sites | Kinaxis, Blue Yonder, SAP IBP | Write-off avoided | Transfer plan and FEFO compliance |
| N10 | **Currency swing (INR/USD/CNY)** on imported ingredients and exports | SAP IBP financial what-if | Margin and cash impact | Sourcing-mix change |
| N11 | **Network redesign**: add a warehouse, a second plant or a contract manufacturer | anyLogistix, Coupa | Capex vs resilience gain, payback | Service and lead-time improvement |
| N12 | **Seasonal demand plan under risk** (monsoon, festivals, flu season) | SAP IBP | Revenue range (P50/P90) | Stock build by month and site |

## 3. Table-stakes features buyers now expect

1. Isolated scenario copies, with branching and side-by-side comparison (all four planning leaders).
2. Results in **units and money** together (SAP IBP, o9).
3. An AI copilot that explains and creates scenarios (SAP Joule, o9, Kinaxis).
4. A control tower with alerts that turn into a scenario in one click (SAP IBP, Blue Yonder).
5. Shelf-life and expiry-aware planning (Kinaxis, Blue Yonder, SAP IBP).
6. Multi-tier supplier mapping (Resilinc, Everstream, o9 + Prewave).
7. A systematic stress test, not only hand-built scenarios (o9, Coupa).

## 4. Where PharmaTwin can win

- **Speed and cost:** leaders take 6–18-month implementations at crore-scale fees. PharmaTwin pilots in 3 weeks on top of existing ERP and warehouse data.
- **India pharma depth:** Indian drug-price controls, Schedule H/X and narcotics rules, Indian drug licences, monsoon and cyclone patterns, active ingredients imported from China, USFDA exposure of Indian plants.
- **One screen for CFO and head of supply chain:** every result shows ₹ impact and service impact together.
- **Complements existing planning tools:** it can sit beside SAP IBP or Kinaxis rather than replace them (see the open question in chat).

## Sources
- Kinaxis life sciences: https://www.kinaxis.com/en/node/6086
- Sobi selects Kinaxis: https://www.businesswire.com/news/home/20251002088321/en/sobi-selects-kinaxis-to-accelerate-access-to-life-changing-treatments
- Kinaxis (Microsoft feature): https://news.microsoft.com/source/2026/09/10/what-if-everything-changes-tomorrow-a-canadian-company-is-using-ai-to-help-businesses-navigate-supply-chain-uncertainty
- Kinaxis Maestro reviews: https://www.rfp.wiki/artificial-intelligence/decision-intelligence-platforms/kinaxis-maestro
- Blue Yonder life sciences: https://blueyonder.com/industries/life-sciences
- Blue Yonder resilient pharma supply chain: https://edge.sitecorecloud.io/blueyonderie8e6-corporateefb0-prod6ccb-be06/media/project/blueyonder/corporate/files/resources/life-sciences-building-a-resilient-pharmaceutical-supply-chain.pdf
- SAP IBP harmonised scenario management (2605): https://www.sap.com/assetdetail/2026/06/c4cb2961-567f-0010-bca6-c68f7e60039b.html
- SAP unified scenario simulations: https://www.foodlogistics.com/home/news/22952070/sap-sap-rolls-out-advanced-ai-unified-scenario-simulations
- SAP IBP for life sciences: https://blogs.sap.com/2017/08/04/integrated-business-planning-for-the-life-science-industry/
- SAP IBP control tower: https://learning.sap.com/courses/discovering-sap-ibp-for-supply-chain-control-tower/enhancing-supply-chain-decision-making
- o9 supplier risk management: https://o9solutions.com/solutions/supplier-and-risk-management/supplier-risk-management
- o9 tariff and reconfiguration press release: https://www.businesswire.com/news/home/20250602913975/en/o9s-Comprehensive-Planning-and-Collaboration-Capabilities-Help-Enterprises-Rapidly-Reconfigure-Their-Global-Supply-Chains
- o9 and Prewave: https://o9solutions.com/news/o9-and-prewave-partner-to-enhance-supply-chain-risk-visibility-for-clients
- Coupa supply chain resilience (TTS/TTR): https://www.coupa.com/blog/what-is-supply-chain-resilience/
- Coupa risk and resiliency white paper: https://www.coupa.com/resources/whitepaper-risk-resiliency-and-supply-chain-modeling/
- Resilinc multi-tier mapping: https://www.resilinc.com/?p=26782
- Resilinc life sciences outlook: https://resilinc.ai/learning-center/white-papers-reports/spotlight-on-life-sciences-supply-chain-outlook
