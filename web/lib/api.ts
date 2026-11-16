import { API_URL } from "./utils";
import type { Plan, Site, Summary, Template } from "./types";

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new ApiError(await response.text(), response.status);
  }
  const type = response.headers.get("content-type") ?? "";
  if (type.includes("application/json")) return (await response.json()) as T;
  return (await response.text()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/api/health"),
  executive: () =>
    request<{
      resilience: { score?: number; formula?: string };
      heatmap: { type: string; region: string; gap_days: number }[];
      risks: { template_id: string; scenario_id: number; name: string; exposure: number; likelihood: string; owner: string }[];
      hero_scenario_id: number | null;
      kpis: { money: Summary["money"]; service: Summary["service"] } | null;
    }>("/api/executive"),
  network: () => request<{ sites: Site[]; version: string }>("/api/network"),
  site: (id: number) => request<Record<string, unknown>>(`/api/network/sites/${id}`),
  templates: () => request<{ templates: Template[] }>("/api/scenarios/templates"),
  createScenario: (template_id: string, params: Record<string, string | number>) =>
    request<{ scenario_id: number; cached: boolean }>("/api/scenarios", {
      method: "POST",
      body: JSON.stringify({ template_id, params }),
    }),
  startRun: (scenario_id: number) =>
    request<{ run_id: number; status: string; cached: boolean; result?: unknown }>("/api/runs", {
      method: "POST",
      body: JSON.stringify({ scenario_id }),
    }),
  run: (id: number) =>
    request<{
      run_id: number;
      scenario_id: number;
      status: string;
      progress: number;
      runs: number;
      seed: number;
      cached: boolean;
      error: string | null;
      result: {
        kind?: string;
        baseline?: Summary;
        plans?: Plan[];
        assumptions?: Record<string, unknown>;
        stress?: Record<string, unknown>;
      } | null;
      fallback: { banner: string; result: unknown; run_id: number } | null;
    }>(`/api/runs/${id}`),
  plans: (scenarioId: number) => request<{ plans: Plan[] }>(`/api/scenarios/${scenarioId}/plans`),
  approvals: () =>
    request<{
      approvals: {
        id: number;
        plan_id: number;
        status: string;
        requested_by: string;
        approver: string | null;
        reason: string | null;
        decided_at: string | null;
      }[];
    }>("/api/approvals"),
  audit: () =>
    request<{ entries: { id: number; ts: string; actor: string; action: string; entity: string; entity_id: string; payload: unknown }[] }>(
      "/api/audit",
    ),
  requestApproval: (plan_id: number) =>
    request<{ approval_id: number }>("/api/approvals", { method: "POST", body: JSON.stringify({ plan_id, requested_by: "demo" }) }),
  decide: (id: number, status: "approved" | "rejected", reason: string) =>
    request<{ status: string }>(`/api/approvals/${id}/decide`, {
      method: "POST",
      body: JSON.stringify({ status, approver: "demo", reason }),
    }),
  upload: async (entity: string, file: File) => {
    const text = await file.text();
    return request<{ valid: boolean; rows: number; errors: string[] }>(`/api/upload/${entity}`, {
      method: "POST",
      body: text,
      headers: { "Content-Type": "text/csv" },
    });
  },
};

export function templateUrl(entity: string) {
  return `${API_URL}/api/upload/templates/${entity}.csv`;
}

export { API_URL };
