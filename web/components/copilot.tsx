"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";
import { Button, Card } from "./ui";

type Line = { role: "user" | "assistant" | "tool"; text: string };

export function Copilot() {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("What if Mumbai floods for 15 days during a dengue surge?");
  const [lines, setLines] = useState<Line[]>([]);
  const [proposal, setProposal] = useState<{ template_id: string; name: string; params: Record<string, number | string> } | null>(null);
  const [busy, setBusy] = useState(false);

  async function send() {
    setBusy(true);
    setLines((current) => [...current, { role: "user", text }]);
    const response = await fetch(`${API_URL}/api/copilot/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [{ role: "user", content: text }] }),
    });
    if (!response.body) {
      setBusy(false);
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let assistant = "";
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      buffer += decoder.decode(chunk.value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";
      for (const part of parts) {
        const event = /event: (\w+)/.exec(part)?.[1];
        const data = /data: (.+)/.exec(part)?.[1];
        if (!event || !data) continue;
        const payload = JSON.parse(data) as { text?: string; message?: string; name?: string; template_id?: string; params?: Record<string, number | string>; proposal?: { template_id: string; name: string; params: Record<string, number | string> } };
        if (event === "error") setLines((current) => [...current, { role: "assistant", text: payload.message ?? "Copilot is off." }]);
        if (event === "tool_call") setLines((current) => [...current, { role: "tool", text: payload.name ?? "tool" }]);
        if (event === "message_delta" && payload.text) assistant += payload.text;
        if (event === "scenario_proposal" && payload.template_id) {
          setProposal({ template_id: payload.template_id, name: payload.name ?? payload.template_id, params: payload.params ?? {} });
        }
        if (payload.proposal) setProposal(payload.proposal);
      }
    }
    if (assistant) setLines((current) => [...current, { role: "assistant", text: assistant }]);
    setBusy(false);
  }

  async function confirm() {
    if (!proposal) return;
    const created = await fetch(`${API_URL}/api/copilot/confirm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id: proposal.template_id, params: proposal.params }),
    }).then((response) => response.json());
    const run = await fetch(`${API_URL}/api/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_id: created.scenario_id }),
    }).then((response) => response.json());
    window.location.href = `/runs/${run.run_id}`;
  }

  return (
    <>
      <button className="fixed bottom-4 right-4 rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground" onClick={() => setOpen(true)}>
        Copilot
      </button>
      {open ? (
        <aside className="fixed bottom-0 right-0 top-0 z-20 flex w-[min(400px,100vw)] flex-col border-l border-border bg-card p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Copilot</h2>
            <button className="text-sm text-muted-foreground" onClick={() => setOpen(false)}>
              Close
            </button>
          </div>
          <div className="mt-4 flex-1 space-y-2 overflow-auto text-sm">
            {lines.map((line, index) => (
              <Card key={index} className="p-3">
                <p className="text-xs text-muted-foreground">{line.role}</p>
                <p className="mt-1 whitespace-pre-wrap">{line.text}</p>
              </Card>
            ))}
            {proposal ? (
              <Card className="p-3" data-testid="scenario-proposal">
                <p className="text-sm font-medium">{proposal.name}</p>
                <p className="mt-1 font-mono text-xs text-muted-foreground">{JSON.stringify(proposal.params)}</p>
                <Button className="mt-3" onClick={confirm}>
                  Run
                </Button>
              </Card>
            ) : null}
          </div>
          <textarea className="mt-3 min-h-20 rounded-md border border-input bg-background p-2 text-sm" value={text} onChange={(event) => setText(event.target.value)} />
          <Button className="mt-2" disabled={busy} onClick={send}>
            {busy ? "Asking…" : "Ask"}
          </Button>
        </aside>
      ) : null}
    </>
  );
}
