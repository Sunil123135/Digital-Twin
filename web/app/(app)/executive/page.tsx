"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { api } from "@/lib/api";
import { formatINR } from "@/lib/format";
import { Button, Card, Empty, ErrorState, Skeleton } from "@/components/ui";
import { MoneyFigure, Range } from "@/components/figures";

export default function ExecutivePage() {
  const query = useQuery({ queryKey: ["executive"], queryFn: api.executive });
  if (query.isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Skeleton key={index} className="h-28" />
        ))}
      </div>
    );
  }
  if (query.isError) {
    return <ErrorState message="The executive view could not be loaded. Seed the database, then retry." onRetry={() => query.refetch()} />;
  }
  const data = query.data;
  if (!data?.kpis) {
    return <Empty title="No cached scenarios yet. Run make seed, then refresh." />;
  }
  const score = data.resilience.score ?? 0;
  const label = score >= 70 ? "Resilient" : score >= 50 ? "Exposed" : "Fragile";
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Executive</h1>
          <p className="text-sm text-muted-foreground">Money and service from the cached China-ingredient scenario.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" asChild>
            <Link href="/scenarios/network_stress_test">Run stress test</Link>
          </Button>
          <Button asChild>
            <Link href="/scenarios/monsoon_dengue" data-testid="open-hero">
              Open hero scenario
            </Link>
          </Button>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Resilience score</p>
          <p className="num mt-2 text-4xl font-semibold">{score.toFixed(0)}</p>
          <p className="text-sm text-muted-foreground">{label} / 100</p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Revenue at risk P50</p>
          <MoneyFigure value={data.kpis.money.revenue_at_risk.p50} />
          <Range pct={data.kpis.money.revenue_at_risk} kind="inr" />
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Margin at risk P50</p>
          <MoneyFigure value={data.kpis.money.margin_impact.p50} />
        </Card>
        <Card className="p-4">
          <p className="text-xs text-muted-foreground">Critical-care fill rate</p>
          <p className="num mt-2 text-3xl font-semibold">{(data.kpis.service.critical_fill_rate.p50 * 100).toFixed(1)}%</p>
          <p className="text-sm text-muted-foreground">
            First stockout {data.kpis.service.days_to_first_stockout.p50.toFixed(0)} days
          </p>
        </Card>
      </div>
      <Card className="overflow-hidden">
        <div className="border-b border-border px-4 py-3 text-sm font-medium">Top risks</div>
        {data.risks.length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground">Risks appear after the scenarios are cached.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground">
              <tr>
                <th className="px-4 py-2 text-left font-medium">Risk</th>
                <th className="px-4 py-2 text-right font-medium">Exposure</th>
                <th className="px-4 py-2 text-left font-medium">Likelihood</th>
                <th className="px-4 py-2 text-left font-medium">Owner</th>
                <th className="px-4 py-2" />
              </tr>
            </thead>
            <tbody>
              {data.risks.map((risk) => (
                <tr key={risk.template_id} className="border-t border-border">
                  <td className="px-4 py-3">{risk.name}</td>
                  <td className="num px-4 py-3">{formatINR(risk.exposure)}</td>
                  <td className="px-4 py-3 text-muted-foreground">{risk.likelihood}</td>
                  <td className="px-4 py-3">{risk.owner}</td>
                  <td className="px-4 py-3 text-right">
                    <Link className="text-sm text-primary" href={`/scenarios/${risk.template_id}`}>
                      Simulate
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
      <Card className="p-4">
        <h2 className="text-sm font-medium">TTS versus TTR gap</h2>
        <div className="mt-3 grid gap-2 md:grid-cols-3">
          {data.heatmap.map((cell) => (
            <div key={`${cell.type}-${cell.region}`} className="rounded-md border border-border px-3 py-2 text-sm">
              <p>
                {cell.type} · {cell.region}
              </p>
              <p className="num text-muted-foreground">{cell.gap_days.toFixed(0)} day gap</p>
            </div>
          ))}
        </div>
        <p className="mt-3 max-w-3xl text-xs text-muted-foreground">{data.resilience.formula}</p>
      </Card>
    </div>
  );
}
