"use client";

import { useEffect, useState } from "react";
import { formatINR, formatINRExact, formatPct } from "@/lib/format";
import type { Pct, Summary } from "@/lib/types";
import { Card } from "./ui";

export function Range({ pct, kind }: { pct: Pct; kind: "inr" | "pct" | "days" }) {
  const text = (value: number) => {
    if (kind === "inr") return formatINR(value);
    if (kind === "pct") return formatPct(value);
    return `${value.toFixed(0)}d`;
  };
  return (
    <span className="num text-xs text-muted-foreground" title={`${formatINRExact(pct.p50)} exact P50`}>
      P10 {text(pct.p10)} · P90 {text(pct.p90)}
    </span>
  );
}

export function MoneyFigure({ value }: { value: number }) {
  const [shown, setShown] = useState(value);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(value);
      return;
    }
    const start = shown;
    const began = performance.now();
    let frame = 0;
    const tick = (now: number) => {
      const t = Math.min(1, (now - began) / 400);
      setShown(start + (value - start) * t);
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
    // shown is the animation origin; including it would restart the tween.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);
  const sign = value < 0 ? "▼ " : value > 0 ? "▲ " : "";
  return (
    <p className="num text-3xl font-semibold tracking-tight text-foreground" title={formatINRExact(value)}>
      {sign}
      {formatINR(shown)}
    </p>
  );
}

export function MoneyService({ summary }: { summary: Summary }) {
  const money: [string, Pct][] = [
    ["Revenue at risk", summary.money.revenue_at_risk],
    ["Margin impact", summary.money.margin_impact],
    ["Working capital", summary.money.working_capital],
    ["Write-off", summary.money.write_off],
  ];
  const service: [string, string][] = [
    ["Fill rate", formatPct(summary.service.fill_rate.p50)],
    ["Critical-care fill rate", formatPct(summary.service.critical_fill_rate.p50)],
    ["Days to first stockout", `${summary.service.days_to_first_stockout.p50.toFixed(0)} days`],
    ["Mean stockout days", `${summary.service.stockout_days.p50.toFixed(1)} days`],
  ];
  return (
    <div className="grid gap-4 md:grid-cols-2" data-testid="money-service">
      <Card className="p-4">
        <h2 className="text-xs font-medium tracking-wide text-muted-foreground">Money (CFO)</h2>
        <ul className="mt-3 space-y-3">
          {money.map(([label, pct]) => (
            <li key={label} className="flex items-baseline justify-between gap-4">
              <span className="text-sm">{label}</span>
              <span className="text-right">
                <span className="num block text-sm font-medium">{formatINR(pct.p50)}</span>
                <Range pct={pct} kind="inr" />
              </span>
            </li>
          ))}
        </ul>
      </Card>
      <Card className="p-4">
        <h2 className="text-xs font-medium tracking-wide text-muted-foreground">Service (Supply chain)</h2>
        <ul className="mt-3 space-y-3">
          {service.map(([label, value]) => (
            <li key={label} className="flex items-baseline justify-between gap-4">
              <span className="text-sm">{label}</span>
              <span className="num text-sm font-medium">{value}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
