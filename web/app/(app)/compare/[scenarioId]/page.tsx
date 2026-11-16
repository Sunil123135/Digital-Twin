"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { formatINR, formatPct } from "@/lib/format";
import { Button, Card, Empty, ErrorState, Skeleton } from "@/components/ui";

export default function ComparePage() {
  const params = useParams<{ scenarioId: string }>();
  const router = useRouter();
  const query = useQuery({ queryKey: ["plans", params.scenarioId], queryFn: () => api.plans(Number(params.scenarioId)) });
  if (query.isLoading) return <Skeleton className="h-40" />;
  if (query.isError) return <ErrorState message="Plans could not be loaded." onRetry={() => query.refetch()} />;
  if (!query.data?.plans.length) return <Empty title="No plans stored for this scenario yet. Run it from the studio first." />;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Compare plans</h1>
      <div className="grid gap-4 lg:grid-cols-3">
        {query.data.plans.map((plan) => (
          <Card key={plan.kind} className="p-4" data-testid={`plan-${plan.kind}`}>
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold capitalize">{plan.kind.replaceAll("_", " ")}</h2>
              {plan.recommended ? (
                <span className="rounded-md bg-[var(--recommended)] px-2 py-1 text-xs font-medium">Recommended</span>
              ) : null}
            </div>
            <dl className="mt-4 space-y-2 text-sm">
              <div className="flex justify-between"><dt>Plan cost</dt><dd className="num">{formatINR(plan.cost)}</dd></div>
              <div className="flex justify-between"><dt>Revenue at risk</dt><dd className="num">{formatINR(plan.summary.money.revenue_at_risk.p50)}</dd></div>
              <div className="flex justify-between"><dt>Critical-care fill</dt><dd className="num">{formatPct(plan.summary.service.critical_fill_rate.p50)}</dd></div>
              <div className="flex justify-between"><dt>Stockout days</dt><dd className="num">{plan.summary.service.stockout_days.p50.toFixed(1)}</dd></div>
              <div className="flex justify-between"><dt>Working capital</dt><dd className="num">{formatINR(plan.summary.money.working_capital.p50)}</dd></div>
            </dl>
            {plan.recommended ? (
              <div className="mt-4 text-sm">
                <p className="font-medium">Why this plan</p>
                <ul className="mt-1 list-disc pl-4 text-muted-foreground">
                  {plan.explanation.top_levers.map((lever) => (
                    <li key={lever.name}>
                      {lever.name} {Math.round(lever.intensity * 100)}%
                    </li>
                  ))}
                </ul>
                <p className="mt-2 text-muted-foreground">{plan.explanation.sensitivity}</p>
                <Button
                  className="mt-4"
                  data-testid="send-approval"
                  onClick={async () => {
                    if (!plan.id) return;
                    await api.requestApproval(plan.id);
                    router.push("/approvals");
                  }}
                >
                  Send for approval
                </Button>
              </div>
            ) : null}
          </Card>
        ))}
      </div>
    </div>
  );
}
