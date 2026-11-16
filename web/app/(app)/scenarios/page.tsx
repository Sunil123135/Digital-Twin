"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useMemo, useState } from "react";
import { api } from "@/lib/api";
import { Card, ErrorState, Skeleton } from "@/components/ui";

export default function ScenariosPage() {
  const query = useQuery({ queryKey: ["templates"], queryFn: api.templates });
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("All");
  const categories = useMemo(() => {
    const set = new Set((query.data?.templates ?? []).map((item) => item.category));
    return ["All", ...set];
  }, [query.data]);
  if (query.isLoading) return <Skeleton className="h-40" />;
  if (query.isError) return <ErrorState message="Scenario library unavailable." onRetry={() => query.refetch()} />;
  const items = (query.data?.templates ?? []).filter((item) => {
    const matches = item.name.toLowerCase().includes(q.toLowerCase());
    return matches && (category === "All" || item.category === category);
  });
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Scenarios</h1>
      <div className="flex flex-wrap gap-2">
        <input className="rounded-md border border-input bg-card px-3 py-2 text-sm" placeholder="Search" value={q} onChange={(event) => setQ(event.target.value)} />
        <select className="rounded-md border border-input bg-card px-3 py-2 text-sm" value={category} onChange={(event) => setCategory(event.target.value)}>
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        {items.map((item) =>
          item.status === "live" ? (
            <Link key={item.id} href={`/scenarios/${item.id}`}>
              <Card className="h-full p-4 hover:bg-muted">
                <p className="text-xs text-muted-foreground">{item.category}</p>
                <h2 className="mt-1 text-base font-semibold">{item.name}</h2>
                <p className="mt-2 text-sm text-muted-foreground">{item.description}</p>
              </Card>
            </Link>
          ) : (
            <Card key={item.id} className="h-full p-4 opacity-60">
              <p className="text-xs text-muted-foreground">{item.category}</p>
              <h2 className="mt-1 text-base font-semibold">{item.name}</h2>
              <p className="mt-2 text-sm">Coming in pilot</p>
            </Card>
          ),
        )}
      </div>
    </div>
  );
}
