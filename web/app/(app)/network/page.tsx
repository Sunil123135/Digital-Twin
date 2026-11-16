"use client";

import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { Site } from "@/lib/types";
import { Card, ErrorState, RiskChip, Skeleton } from "@/components/ui";
import { NetworkMap } from "@/components/network-map";

export default function NetworkPage() {
  const query = useQuery({ queryKey: ["network"], queryFn: api.network });
  const [type, setType] = useState("all");
  const [region, setRegion] = useState("all");
  const [list, setList] = useState(false);
  const [selected, setSelected] = useState<Site | null>(null);
  const detail = useQuery({
    queryKey: ["site", selected?.id],
    queryFn: () => api.site(selected!.id),
    enabled: selected != null,
  });
  const sites = useMemo(
    () =>
      (query.data?.sites ?? []).filter((site) => (type === "all" || site.type === type) && (region === "all" || site.region === region)),
    [query.data, region, type],
  );
  if (query.isLoading) return <Skeleton className="h-[480px]" />;
  if (query.isError) return <ErrorState message="Network map unavailable. Seed the database first." onRetry={() => query.refetch()} />;
  const regions = [...new Set((query.data?.sites ?? []).map((site) => site.region))];
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-2xl font-semibold">Network</h1>
        <select className="rounded-md border border-input bg-card px-2 py-1 text-sm" value={type} onChange={(event) => setType(event.target.value)}>
          <option value="all">All types</option>
          {["plant", "dc", "cnf", "port", "hospital", "stockist", "supplier_site", "cold_store"].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <select className="rounded-md border border-input bg-card px-2 py-1 text-sm" value={region} onChange={(event) => setRegion(event.target.value)}>
          <option value="all">All regions</option>
          {regions.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <button className="rounded-md border border-border px-3 py-1 text-sm" onClick={() => setList((value) => !value)}>
          {list ? "Map view" : "List view"}
        </button>
      </div>
      {list ? (
        <Card className="max-h-[70vh] overflow-auto">
          <table className="w-full text-sm">
            <tbody>
              {sites.map((site) => (
                <tr key={site.id} className="cursor-pointer border-t border-border hover:bg-muted" onClick={() => setSelected(site)}>
                  <td className="px-3 py-2 font-mono text-xs">{site.code}</td>
                  <td className="px-3 py-2">{site.name}</td>
                  <td className="px-3 py-2">{site.region}</td>
                  <td className="px-3 py-2"><RiskChip level={site.risk} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      ) : (
        <NetworkMap sites={sites} onSelect={setSelected} />
      )}
      {selected ? (
        <Card className="p-4 text-sm">
          <div className="flex items-center justify-between">
            <h2 className="font-medium">{selected.name}</h2>
            <button onClick={() => setSelected(null)}>Close</button>
          </div>
          <p className="mt-1 text-muted-foreground">{selected.type} · {selected.region}</p>
          <div className="mt-2"><RiskChip level={selected.risk} /></div>
          <pre className="mt-3 whitespace-pre-wrap font-mono text-xs">{JSON.stringify(detail.data ?? {}, null, 2)}</pre>
        </Card>
      ) : null}
    </div>
  );
}
