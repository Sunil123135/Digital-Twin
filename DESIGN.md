---
name: PharmaTwin
description: Calm, precise risk-simulation workspace for pharma CFOs and Heads of Supply Chain
colors:
  light:
    background: "oklch(0.985 0.004 95)"
    foreground: "oklch(0.22 0.02 250)"
    card: "oklch(1 0 0)"
    card-foreground: "oklch(0.22 0.02 250)"
    popover: "oklch(1 0 0)"
    popover-foreground: "oklch(0.22 0.02 250)"
    primary: "oklch(0.42 0.08 200)"
    primary-foreground: "oklch(0.985 0.004 95)"
    secondary: "oklch(0.955 0.006 95)"
    secondary-foreground: "oklch(0.28 0.02 250)"
    muted: "oklch(0.955 0.006 95)"
    muted-foreground: "oklch(0.50 0.02 250)"
    accent: "oklch(0.94 0.03 200)"
    accent-foreground: "oklch(0.30 0.06 200)"
    destructive: "oklch(0.55 0.19 27)"
    border: "oklch(0.90 0.008 95)"
    input: "oklch(0.90 0.008 95)"
    ring: "oklch(0.42 0.08 200)"
    risk-critical: "oklch(0.55 0.19 27)"
    risk-high: "oklch(0.66 0.16 50)"
    risk-medium: "oklch(0.78 0.14 85)"
    risk-low: "oklch(0.62 0.11 160)"
    positive: "oklch(0.52 0.12 155)"
    recommended: "oklch(0.72 0.13 75)"
    chart-1: "oklch(0.42 0.08 200)"
    chart-2: "oklch(0.55 0.09 255)"
    chart-3: "oklch(0.72 0.13 75)"
    chart-4: "oklch(0.50 0.10 330)"
    chart-5: "oklch(0.65 0.06 150)"
  dark:
    background: "oklch(0.17 0.015 250)"
    foreground: "oklch(0.95 0.005 95)"
    card: "oklch(0.21 0.015 250)"
    card-foreground: "oklch(0.95 0.005 95)"
    popover: "oklch(0.21 0.015 250)"
    popover-foreground: "oklch(0.95 0.005 95)"
    primary: "oklch(0.74 0.10 195)"
    primary-foreground: "oklch(0.17 0.015 250)"
    secondary: "oklch(0.26 0.015 250)"
    secondary-foreground: "oklch(0.92 0.005 95)"
    muted: "oklch(0.26 0.015 250)"
    muted-foreground: "oklch(0.70 0.015 250)"
    accent: "oklch(0.30 0.04 200)"
    accent-foreground: "oklch(0.92 0.03 195)"
    destructive: "oklch(0.65 0.19 27)"
    border: "oklch(0.30 0.015 250)"
    input: "oklch(0.30 0.015 250)"
    ring: "oklch(0.74 0.10 195)"
    risk-critical: "oklch(0.66 0.19 27)"
    risk-high: "oklch(0.74 0.15 55)"
    risk-medium: "oklch(0.84 0.13 88)"
    risk-low: "oklch(0.72 0.11 160)"
    positive: "oklch(0.72 0.12 155)"
    recommended: "oklch(0.80 0.13 78)"
    chart-1: "oklch(0.74 0.10 195)"
    chart-2: "oklch(0.70 0.09 255)"
    chart-3: "oklch(0.80 0.13 78)"
    chart-4: "oklch(0.70 0.10 330)"
    chart-5: "oklch(0.75 0.07 150)"
typography:
  sans: "IBM Plex Sans"
  mono: "IBM Plex Mono"
  numerals: "tabular-nums lining-nums"
radius: "0.5rem"
spacing-base: "4px"
---

# Design System: PharmaTwin

## Overview

**Creative North Star: "The Quiet War Room"**

PharmaTwin is used when something is going wrong, or might. The interface stays calm so the numbers can be loud. Think of a well-run operations room: warm paper-white surfaces, deep teal ink, dense but orderly information, and colour reserved for risk and for the one recommended action. Nothing decorative competes with a ₹ figure.

The density is high (an Operate-mode tool for executives who read dashboards daily), but hierarchy is unmistakable: one headline number per card, supporting detail one step quieter, assumptions one click away. Motion explains change (a number counting to its new value after a re-run, a disruption spreading across the map) and never decorates.

Rejected looks: purple-gradient "AI" dashboards, glassmorphism, neon dark themes, stock photos of warehouses, emoji, and generic KPI-card grids with sparklines that carry no meaning.

**Key characteristics:**
- Warm neutral canvas, deep teal primary, a single saffron "recommended" highlight.
- Risk colours (critical/high/medium/low) always paired with a text label.
- IBM Plex Sans with tabular numerals; ₹ in Indian lakh/crore format.
- Flat surfaces separated by 1 px borders; shadows only for overlays.
- Two-column **Money | Service** layout on every result.

## Colors

A restrained, warm-neutral palette where colour carries meaning, not mood.

### Primary
- **Pharmacopoeia Teal** (`oklch(0.42 0.08 200)`; dark `oklch(0.74 0.10 195)`): primary buttons, active navigation, focus rings, the baseline series in charts, selected map nodes.

### Secondary
- **Saffron Recommendation** (`oklch(0.72 0.13 75)`): only for the recommended plan badge, the recommended row in comparisons and the live re-run progress bar. Never decorative.

### Risk scale
- **Critical** `oklch(0.55 0.19 27)` · **High** `oklch(0.66 0.16 50)` · **Medium** `oklch(0.78 0.14 85)` · **Low** `oklch(0.62 0.11 160)`. Always shown with a label ("Critical") or icon; used on map nodes, risk table rows and heatmap cells.

### Neutral
- **Paper** `oklch(0.985 0.004 95)`: page background.
- **White card** `oklch(1 0 0)`: cards and tables.
- **Ink** `oklch(0.22 0.02 250)`: primary text and headline numbers.
- **Slate** `oklch(0.50 0.02 250)`: secondary text, axis labels, assumptions.
- **Hairline** `oklch(0.90 0.008 95)`: borders and dividers.

### Named Rules
**The Saffron Rule.** Saffron appears at most once per screen region and always means "this is what we recommend".
**The Label-Every-Risk Rule.** No risk colour without a word next to it.
**The Neutral Money Rule.** ₹ figures are Ink, never red or green by default. Direction is shown with an arrow and a signed value ("▼ ₹42.6 cr"); red is reserved for breaches of a threshold.

## Typography

**Display/Body font:** IBM Plex Sans (fallback: system-ui, "Segoe UI", sans-serif)
**Mono font:** IBM Plex Mono, for SKU codes, batch numbers, run IDs and seeds.

**Character:** engineered, trustworthy, slightly technical; it reads like an instrument, not a marketing site.

### Hierarchy
- **Display** (600, 40px, 1.1): the single headline number on Executive cards (e.g. "₹186.4 cr at risk").
- **Headline** (600, 24px, 1.25): page titles.
- **Title** (600, 16px, 1.4): card titles, section headers.
- **Body** (400, 14px, 1.5): default UI text; long explanations max 72ch.
- **Small** (400, 13px, 1.45): table cells, assumptions.
- **Label** (500, 12px, letter-spacing 0.02em, sentence case): field labels, column headers, chip text.

### Named Rules
**The Tabular Rule.** Every number uses `font-variant-numeric: tabular-nums` and is right-aligned in tables.
**The Indian Money Rule.** Money uses `Intl.NumberFormat('en-IN')`: below ₹1 lakh show the full number; ₹1 lakh–₹1 crore show "₹12.4 L"; above show "₹186.4 cr". Tooltips show the exact value.

## Layout

- App shell: fixed left navigation (240px, collapsible to 64px), top bar (56px) with scenario context, global search (⌘K) and theme toggle; optional right copilot panel (400px, resizable).
- Content uses a 12-column grid, 24px gutters, max width 1600px; cards snap to 3, 4, 6 or 12 columns.
- Spacing scale on a 4px base: 4, 8, 12, 16, 24, 32, 48.
- Minimum supported width 1280px for the demo; at 1024px the copilot overlays instead of docking. Phone layouts are out of scope for the demo.

## Elevation & Depth

Flat by default. Surfaces are separated by 1px Hairline borders and a slight tonal step (Paper vs White card). Shadows are used only for floating layers.

### Shadow Vocabulary
- **Overlay** (`0 8px 24px oklch(0.22 0.02 250 / 0.12)`): popovers, command palette, dialogs, the copilot panel when floating.

### Named Rules
**The Flat-By-Default Rule.** Nothing at rest has a shadow.

## Shapes

Radius 8px for cards, inputs and buttons; 6px for chips and badges; full round only for avatars and status dots. Map nodes are circles (sites) and rounded squares (ports/airports); lanes are 1.5px lines, dashed when disrupted.

## Components

### Buttons
- **Primary:** Teal background, Paper text, 8px radius, 36px height, 14px/500 label. Hover darkens 6%; focus shows a 2px Teal ring with 2px offset.
- **Secondary:** White card background, Ink text, Hairline border.
- **Ghost:** text only, for tertiary actions in tables.
- **Approve (Action queue):** Primary with a check icon; requires a reason before it is enabled.

### KPI card
Title (Label), headline number (Display or Headline), change vs baseline (signed value with arrow), P50–P90 range as small Slate text, "Assumptions" link opening a side sheet. No sparkline unless it shows the same metric over the simulated horizon.

### Money | Service result panel
Two equal columns with headers "Money (CFO)" and "Service (Supply chain)". Each column has 4 KPI rows. Below, one full-width "Recommended plan" bar with the Saffron badge, the plan's cost, the loss avoided, ROI, and "Compare plans" / "Send for approval" buttons.

### Risk chip
6px radius, tinted background (risk colour at 15% opacity), risk colour text plus a dot and the word ("High").

### Tables
TanStack Table, 40px rows, sticky header, right-aligned numbers, Mono for codes, row hover in Muted, sortable columns, a CSV export button.

### Map
MapLibre with a muted, low-contrast basemap. Sites coloured by risk; disrupted lanes dashed Critical; flood or heat zones as translucent polygons. A timeline scrubber under the map replays the simulated days.

### Copilot panel
Right-side sheet. Messages in plain cards; every numeric answer shows a "Source: run R-0042" link. When the copilot proposes a scenario, it shows a confirmation card with parameters before running.

### Empty, loading, error states
- **Loading:** skeletons shaped like the final content; live re-runs show a Saffron progress bar with "Run 120 of 200".
- **Empty:** one sentence explaining what will appear, plus the action that fills it.
- **Error:** what happened, what was kept (e.g. "Showing cached result from 10:42"), and a retry button.
