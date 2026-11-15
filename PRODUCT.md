# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Next.js 15 (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui, themed with tweakcn (`web/`). Python 3.12 + FastAPI + NumPy + Google OR-Tools (`api/`). SQLite through SQLAlchemy for the demo; Postgres/Supabase in the pilot. AI copilot through **OpenRouter** (OpenAI-compatible API). Built in **Cursor**.

## Users

- **CFO** of an Indian pharma manufacturer or distributor, often inside a larger corporate group. Sees the product in a sales meeting or board-prep session. Job: know how much money is at risk from supply disruptions and what it costs to protect it.
- **Head of Supply Chain** at the same company, in the same meeting. Job: know which products, sites and customers are exposed, how long the network survives a disruption, and which response plan to approve.
- They **sign together**. Every decision screen must answer both of them at once.
- Later users (pilot phase): supply planners, procurement and quality heads.

## Product Purpose

PharmaTwin is a digital twin of a pharmaceutical supply network. It simulates disruptions such as floods, port shutdowns, China ingredient shocks, USFDA actions, recalls, cold-chain failures and tariff changes, shows the impact in **money and service** together, and recommends response plans for approval.

Success for the demo: in a live meeting, the CFO changes a number (flood length, tariff %, supplier cut) and within a minute sees the ₹ impact, the service impact and the recommended plan update on one screen, and asks for a pilot.

## Positioning

A **risk-simulation layer that sits alongside** existing planning systems (SAP IBP, Kinaxis, o9, Blue Yonder). It is not a planning-system replacement. Distinctive: India pharma depth (Indian drug price controls, Schedule H/X, drug licences, monsoon and cyclone patterns, China API dependence, USFDA exposure of Indian plants), one shared screen for CFO and Head of Supply Chain, and a pilot measured in weeks rather than an 18-month implementation.

## Operating Context

- Sales demo on a laptop, often mirrored to a meeting-room screen or video call. Must read well at 1280–1920 px wide and when projected.
- Later: crisis "war room" use, so dark mode matters.
- Money is shown in Indian format: ₹ lakh and ₹ crore, `en-IN` grouping.

## Capabilities and Constraints

- Demo scope: 13 polished scenarios on a synthetic Indian pharma network; the other 32 scenario templates appear as "Coming in pilot".
- No live ERP or warehouse connectors, multi-tenant login, ERP write-back or external risk feeds in the demo.
- Every number must be traceable to inputs and assumptions.
- The copilot only states numbers returned by the simulation tools.
- All demo data is synthetic and labelled as such.

## Brand Commitments

Working name **PharmaTwin** (may be renamed). No logo yet. Voice: calm, precise, plain English; numbers first; no hype words ("revolutionary", "AI-powered magic").

## Evidence on Hand

- `docs/research/competitor-scenarios.md`: public research on Kinaxis, Blue Yonder, SAP IBP, o9, Coupa, anyLogistix, Resilinc, Everstream.
- No customer logos, testimonials, case studies or benchmarks yet. **Do not fabricate any.**

## Product Principles

1. Money and service, always together.
2. Every number can be clicked down to its assumptions.
3. Humans approve; the software recommends.
4. Sit alongside the customer's systems; never ask them to replace one.
5. The demo never fails in front of a client: cached results first, live re-runs second.

## Accessibility & Inclusion

WCAG 2.2 AA. Colour is never the only signal for risk level (always paired with a label or icon). Full keyboard navigation and a ⌘K command palette.
