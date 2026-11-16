"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MoneyService } from "@/components/figures";
import { Button, Card, ErrorState, Skeleton } from "@/components/ui";
import { api } from "@/lib/api";
import { formatPct } from "@/lib/format";

export default function RunPage() {
  const params = useParams<{ id: string }>();
  const [assumptionsOpen, setAssumptionsOpen] = useState(false);
  const [day, setDay] = useState(0);
  const query = useQuery({
    queryKey: ["run", params.id],
    queryFn: () => api.run(Number(params.id)),
    refetchInterval: (q) => (q.state.data?.status === "done" || q.state.data?.status === "failed" ? false : 1000),
  });
  if (query.isLoading) return <Skeleton className="h-48" />;
  if (query.isError || !query.data) return <ErrorState message="This run could not be loaded." onRetry={() => query.refetch()} />;
  const run = query.data;
  const result = run.result?.kind === "scenario" ? run.result : run.fallback ? null : run.result;
  const summary = run.result?.baseline;
  if (run.status !== "done" && run.status !== "failed") {
    const width = run.runs ? Math.round((run.progress / run.runs) * 100) : 8;
    return (
      <Card className="p-6">
        <p className="text-sm">Run {run.progress} of {run.runs}</p>
        <div className="mt-3 h-2 rounded-full bg-muted">
          <div className="h-2 rounded-full bg-[var(--recommended)]" style={{ width: `${width}%` }} />
        </div>
      </Card>
    );
  }
  if (!summary) {
    return <ErrorState message={run.fallback?.banner ?? run.error ?? "No result stored for this run."} onRetry={() => query.refetch()} />;
  }
  const chart = summary.daily_fill_p50.map((p50, index) => ({
    day: index + 1,
    p50: p50 * 100,
    p90: (summary.daily_fill_p90[index] ?? p50) * 100,
  }));
  const recommended = run.result?.plans?.find((plan) => plan.recommended);
  return (
    <div className="space-y-4">
      {run.fallback ? <Card className="p-3 text-sm">{run.fallback.banner}</Card> : null}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold">Run R-{String(run.run_id).padStart(4, "0")}</h1>
          <p className="font-mono text-xs text-muted-foreground">
            seed {run.seed} · {run.cached ? "cached" : "live"} · {run.status}
          </p>
        </div>
        <Button variant="secondary" onClick={() => setAssumptionsOpen(true)}>
          Assumptions
        </Button>
      </div>
      <MoneyService summary={summary} />
      <Card className="p-4">
        <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chart}>
            <CartesianGrid stroke="var(--border)" />
            <XAxis dataKey="day" stroke="var(--muted-foreground)" />
            <YAxis stroke="var(--muted-foreground)" unit="%" />
            <Tooltip />
            <Line type="monotone" dataKey="p50" stroke="var(--chart-1)" dot={false} name="Fill rate P50" />
            <Line type="monotone" dataKey="p90" stroke="var(--chart-2)" dot={false} name="Fill rate P90" />
          </LineChart>
        </ResponsiveContainer>
        </div>
      </Card>
      <Card className="overflow-hidden">
        <div className="border-b border-border px-4 py-3 text-sm font-medium">Stockouts by hospital</div>
        <table className="w-full text-sm">
          <tbody>
            {summary.stockouts_by_hospital.map((row) => (
              <tr key={row.site_id} className="border-t border-border">
                <td className="px-4 py-2">{row.name}</td>
                <td className="px-4 py-2 text-muted-foreground">{row.region}</td>
                <td className="num px-4 py-2">{row.stockout_days.p50.toFixed(1)} days</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
      <Card className="p-4">
        <label className="text-sm">
          Map replay day {day + 1}
          <input className="mt-2 w-full" type="range" min={0} max={Math.max(chart.length - 1, 0)} value={day} onChange={(event) => setDay(Number(event.target.value))} />
        </label>
        <p className="num mt-2 text-sm">Fill rate {formatPct((summary.daily_fill_p50[day] ?? 1))}</p>
      </Card>
      {recommended ? (
        <Card className="flex flex-wrap items-center justify-between gap-3 p-4">
          <div>
            <span className="rounded-md bg-[var(--recommended)] px-2 py-1 text-xs font-medium text-foreground">Recommended</span>
            <p className="mt-2 text-sm">{recommended.kind.replaceAll("_", " ")}</p>
          </div>
          <Button asChild>
            <Link href={`/compare/${run.scenario_id}`}>Compare plans</Link>
          </Button>
        </Card>
      ) : null}
      {assumptionsOpen ? (
        <Card className="p-4 text-sm">
          <pre className="whitespace-pre-wrap font-mono text-xs">{JSON.stringify(run.result?.assumptions ?? {}, null, 2)}</pre>
          <Button className="mt-3" variant="secondary" onClick={() => setAssumptionsOpen(false)}>
            Close
          </Button>
        </Card>
      ) : null}
    </div>
  );
}
