"use client";

import * as Tabs from "@radix-ui/react-tabs";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, Empty, ErrorState } from "@/components/ui";

export default function ApprovalsPage() {
  const approvals = useQuery({ queryKey: ["approvals"], queryFn: api.approvals });
  const audit = useQuery({ queryKey: ["audit"], queryFn: api.audit });
  const [reason, setReason] = useState("");
  const [active, setActive] = useState<number | null>(null);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Approvals</h1>
      <Tabs.Root defaultValue="queue">
        <Tabs.List className="flex gap-2">
          <Tabs.Trigger className="rounded-md border border-border px-3 py-1 text-sm data-[state=active]:bg-muted" value="queue">
            Queue
          </Tabs.Trigger>
          <Tabs.Trigger className="rounded-md border border-border px-3 py-1 text-sm data-[state=active]:bg-muted" value="audit">
            Audit log
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="queue" className="mt-4">
          {approvals.isError ? <ErrorState message="Approval queue unavailable." onRetry={() => approvals.refetch()} /> : null}
          {!approvals.data?.approvals.length ? <Empty title="Nothing is waiting. Send a recommended plan from Compare." /> : null}
          <div className="space-y-3">
            {approvals.data?.approvals.map((item) => (
              <Card key={item.id} className="p-4 text-sm">
                <p>
                  Plan {item.plan_id} · {item.status}
                </p>
                <p className="text-muted-foreground">Requested by {item.requested_by}</p>
                {item.status === "pending" ? (
                  <div className="mt-3 space-y-2">
                    <textarea
                      className="w-full rounded-md border border-input bg-background p-2"
                      placeholder="Reason required"
                      value={active === item.id ? reason : ""}
                      onChange={(event) => {
                        setActive(item.id);
                        setReason(event.target.value);
                      }}
                    />
                    <div className="flex gap-2">
                      <Button
                        data-testid="approve"
                        disabled={!reason.trim() || active !== item.id}
                        onClick={async () => {
                          await api.decide(item.id, "approved", reason.trim());
                          setReason("");
                          await approvals.refetch();
                          await audit.refetch();
                        }}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="secondary"
                        disabled={!reason.trim() || active !== item.id}
                        onClick={async () => {
                          await api.decide(item.id, "rejected", reason.trim());
                          setReason("");
                          await approvals.refetch();
                        }}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                ) : (
                  <p className="mt-2">Reason: {item.reason}</p>
                )}
              </Card>
            ))}
          </div>
        </Tabs.Content>
        <Tabs.Content value="audit" className="mt-4">
          <Card className="overflow-hidden">
            <table className="w-full text-sm">
              <tbody>
                {audit.data?.entries.map((entry) => (
                  <tr key={entry.id} className="border-t border-border">
                    <td className="px-3 py-2 font-mono text-xs">{entry.ts}</td>
                    <td className="px-3 py-2">{entry.actor}</td>
                    <td className="px-3 py-2">{entry.action}</td>
                    <td className="px-3 py-2">{entry.entity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}
