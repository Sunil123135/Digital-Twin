"use client";

import { useState } from "react";
import { templateUrl } from "@/lib/api";
import { api } from "@/lib/api";
import { Button, Card } from "@/components/ui";

const ENTITIES = ["sites", "lanes", "products", "demand"];

export default function DataPage() {
  const [report, setReport] = useState<string>("Upload a template to see the validation report.");
  const [network, setNetwork] = useState("synthetic");
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Data</h1>
      <p className="max-w-2xl text-sm text-muted-foreground">
        The simulation uses the synthetic network until a complete, valid upload is accepted. Partial files are stored with their validation errors and do not change any rupee figure.
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {ENTITIES.map((entity) => (
          <Card key={entity} className="p-4">
            <h2 className="text-sm font-medium capitalize">{entity}</h2>
            <a className="mt-2 block text-sm text-primary" href={templateUrl(entity)}>
              Download template
            </a>
            <input
              className="mt-3 block text-sm"
              type="file"
              accept=".csv,text/csv"
              onChange={async (event) => {
                const file = event.target.files?.[0];
                if (!file) return;
                const result = await api.upload(entity, file);
                setReport(`${entity}: ${result.rows} rows. ${result.valid ? "Valid." : result.errors.join(" ")}`);
                if (!result.valid) setNetwork("synthetic");
              }}
            />
          </Card>
        ))}
      </div>
      <Card className="p-4 text-sm">
        <p>{report}</p>
        <label className="mt-3 flex items-center gap-2">
          <input type="checkbox" checked={network === "uploaded"} onChange={(event) => setNetwork(event.target.checked ? "uploaded" : "synthetic")} />
          Use an uploaded network
        </label>
        <p className="mt-2 text-muted-foreground">
          Active network: {network === "synthetic" ? "synthetic demo (synth-42)" : "uploaded files are not a complete twin, so results stay on synth-42"}.
        </p>
        <Button className="mt-3" variant="secondary" onClick={() => setNetwork("synthetic")}>
          Use synthetic network
        </Button>
      </Card>
    </div>
  );
}
