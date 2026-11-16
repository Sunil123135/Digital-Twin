"use client";

import Map, { Marker } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Site } from "@/lib/types";

const style = {
  version: 8 as const,
  sources: {
    osm: {
      type: "raster" as const,
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "© OpenStreetMap",
    },
  },
  layers: [{ id: "osm", type: "raster" as const, source: "osm" }],
};

const color: Record<string, string> = {
  critical: "var(--risk-critical)",
  high: "var(--risk-high)",
  medium: "var(--risk-medium)",
  low: "var(--risk-low)",
};

export function NetworkMap({ sites, onSelect }: { sites: Site[]; onSelect: (site: Site) => void }) {
  const visible = sites.filter((site) => Number.isFinite(site.lat) && Number.isFinite(site.lon)).slice(0, 120);
  return (
    <div className="h-[70vh] overflow-hidden rounded-lg border border-border">
      <Map initialViewState={{ longitude: 78.5, latitude: 22.5, zoom: 4 }} mapStyle={style}>
        {visible.map((site) => (
          <Marker key={site.id} longitude={site.lon} latitude={site.lat} anchor="center" onClick={() => onSelect(site)}>
            <button
              title={`${site.name} (${site.risk})`}
              className="size-3 rounded-full border border-white"
              style={{ background: color[site.risk] ?? color.low }}
            />
          </Marker>
        ))}
      </Map>
    </div>
  );
}
