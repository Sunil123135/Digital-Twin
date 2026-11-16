"use client";

import * as Slider from "@radix-ui/react-slider";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { TemplateParam } from "@/lib/types";
import { Button, Card, ErrorState, Skeleton } from "@/components/ui";

export default function StudioPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const query = useQuery({ queryKey: ["templates"], queryFn: api.templates });
  const template = query.data?.templates.find((item) => item.id === params.id);
  const initial = useMemo(() => {
    const values: Record<string, string | number> = {};
    template?.params.forEach((param) => {
      values[param.name] = param.default;
    });
    return values;
  }, [template]);
  const [values, setValues] = useState<Record<string, string | number>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const current = { ...initial, ...values };

  if (query.isLoading) return <Skeleton className="h-40" />;
  if (!template || template.status !== "live") return <ErrorState message="This scenario is not available in the demo." />;

  async function run() {
    setBusy(true);
    setError("");
    try {
      const created = await api.createScenario(template!.id, current);
      const started = await api.startRun(created.scenario_id);
      router.push(`/runs/${started.run_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
      setBusy(false);
    }
  }

  const live = template.params.filter((param) => param.is_live_slider);
  const rest = template.params.filter((param) => !param.is_live_slider);

  return (
    <div className="grid gap-4 lg:grid-cols-[280px_1fr_260px]">
      <Card className="p-4">
        <h1 className="text-lg font-semibold">{template.name}</h1>
        <p className="mt-2 text-sm text-muted-foreground">{template.description}</p>
        <div className="mt-4 space-y-4">
          {[...live, ...rest].map((param) => (
            <ParamControl key={param.name} param={param} value={current[param.name]} onChange={(value) => setValues((prev) => ({ ...prev, [param.name]: value }))} />
          ))}
        </div>
      </Card>
      <Card className="p-4">
        <h2 className="text-sm font-medium">Shock timeline</h2>
        <ol className="mt-4 space-y-3 text-sm">
          <li>Day 0 — baseline flow, synthetic network {`synth-42`}.</li>
          <li>Disruption begins from the parameters on the left.</li>
          <li>Horizon 90 days, 200 Monte Carlo runs, fixed seed.</li>
        </ol>
        <p className="mt-6 text-sm text-muted-foreground">{template.headline}</p>
      </Card>
      <Card className="p-4">
        <h2 className="text-sm font-medium">Run</h2>
        <p className="mt-2 text-sm text-muted-foreground">Cached defaults return immediately. A changed slider runs live.</p>
        <Button className="mt-4 w-full" data-testid="run-scenario" disabled={busy} onClick={run}>
          {busy ? "Starting…" : "Run"}
        </Button>
        {error ? <p className="mt-3 text-sm text-destructive">{error}</p> : null}
      </Card>
    </div>
  );
}

function ParamControl({
  param,
  value,
  onChange,
}: {
  param: TemplateParam;
  value: string | number | undefined;
  onChange: (value: string | number) => void;
}) {
  if (param.choices?.length) {
    return (
      <label className="block text-sm">
        {param.label}
        <select className="mt-1 w-full rounded-md border border-input bg-background px-2 py-1" value={String(value ?? "")} onChange={(event) => onChange(event.target.value)}>
          {param.choices.map((choice) => (
            <option key={choice}>{choice}</option>
          ))}
        </select>
      </label>
    );
  }
  const numeric = Number(value ?? param.default);
  return (
    <label className="block text-sm">
      <span className="flex justify-between">
        {param.label}
        {param.is_live_slider ? <span className="text-[var(--recommended)]">Live</span> : null}
      </span>
      <span className="num mt-1 block text-xs text-muted-foreground">
        {numeric} {param.unit}
      </span>
      <Slider.Root
        className="relative mt-2 flex h-5 items-center"
        min={param.minimum ?? 0}
        max={param.maximum ?? 100}
        step={param.step ?? 1}
        value={[numeric]}
        onValueChange={(next) => onChange(next[0] ?? numeric)}
      >
        <Slider.Track className="relative h-1 flex-1 rounded-full bg-muted">
          <Slider.Range className="absolute h-full rounded-full bg-primary" />
        </Slider.Track>
        <Slider.Thumb className="block size-3 rounded-full border border-border bg-card" />
      </Slider.Root>
    </label>
  );
}
