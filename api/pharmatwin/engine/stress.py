"""Time-to-survive, time-to-recover, exposure and the resilience score."""

from typing import Any

import numpy as np

from pharmatwin.engine.network import Network
from pharmatwin.engine.shocks import Shock, fixed
from pharmatwin.engine.simulate import simulate


def _knock_shocks(network: Network, site_id: int, days: int) -> list[Shock]:
    site = network.sites[site_id]
    if site.type in {"dc", "cnf"}:
        return [
            Shock(
                type="node_down",
                target={"site_code": site.code},
                start_day=0,
                duration_days=fixed(float(days)),
                magnitude=fixed(0),
            )
        ]
    if site.type == "supplier_site" and site.supplier_id is not None:
        return [
            Shock(
                type="supplier_capacity",
                target=(
                    {"supplier_country": "CN"}
                    if site.state == "CN" and site.supplier_id in {0, 1}
                    else {"supplier_id": site.supplier_id}
                ),
                start_day=0,
                duration_days=fixed(float(days)),
                magnitude=fixed(0),
            )
        ]
    if site.type == "port":
        return [
            Shock(
                type="lead_time_shift",
                target={"mode": "sea"},
                start_day=0,
                duration_days=fixed(float(days)),
                magnitude=fixed(21),
            )
        ]
    if site.code == "PLT-BAD":
        return [
            Shock(
                type="market_block",
                target={"site_code": "PLT-BAD", "market": "US"},
                start_day=0,
                duration_days=fixed(float(days)),
                magnitude=fixed(0),
            )
        ]
    return []


def resilience(network: Network, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """100 × revenue share whose nodes all have TTS ≥ TTR, minus 5 per single-source China API over ₹50 cr."""
    from pharmatwin.engine.catalog import REGION_DEPOT

    stocking = set(REGION_DEPOT.values())
    failing_regions: set[str] = set()
    for row in rows:
        if row["code"] in stocking and row["tts"] < row["ttr"]:
            failing_regions.add(str(row["region"]))
    from pharmatwin.engine.catalog import REGION_SHARE

    failed_share = sum(REGION_SHARE[region] for region in failing_regions)
    score = max(0.0, 100 * (1 - failed_share) - 5 * network.single_source_china_apis)
    return {
        "score": round(score, 1),
        "failed_revenue_share": failed_share,
        "single_source_china_apis": network.single_source_china_apis,
        "formula": (
            "100 × share of revenue whose depots have TTS ≥ TTR, "
            "minus 5 per single-source China API above ₹50 cr."
        ),
    }


def stress_test(network: Network, *, outage_days: int = 14, seed: int = 42) -> dict[str, Any]:
    """One deterministic run per stocking node and the plants, ports and single-source suppliers."""
    interesting = [
        site
        for site in network.sites
        if site.type in {"dc", "cnf", "plant", "port", "cold_store"} or (site.supplier_id in {0, 1, 12})
    ]
    rows: list[dict[str, Any]] = []
    horizon = max(outage_days + 20, 40)
    for site in interesting:
        shocks = _knock_shocks(network, site.id, outage_days)
        if not shocks:
            tts = float(horizon)
            exposure = 0.0
        else:
            raw = simulate(network, shocks, seed=seed, runs=1, horizon=horizon)
            unmet = raw["daily_unmet"][:, 0]
            hit = np.where(unmet > 1)[0]
            tts = float(hit[0]) if len(hit) else float(horizon)
            daily_rev = network.annual_revenue / 365.0
            gap = max(0.0, site.recovery_days - tts)
            exposure = daily_rev * gap * _exposure_share(network, site)
        rows.append(
            {
                "site_id": site.id,
                "code": site.code,
                "name": site.name,
                "type": site.type,
                "region": site.region,
                "tts": tts,
                "ttr": float(site.recovery_days),
                "exposure": exposure,
            }
        )
    rows.sort(key=lambda row: row["exposure"], reverse=True)
    score = resilience(network, rows)
    heatmap = _heatmap(rows)
    return {"nodes": rows, "resilience": score, "heatmap": heatmap, "outage_days": outage_days}


def _exposure_share(network: Network, site: Any) -> float:
    from pharmatwin.engine.catalog import REGION_SHARE

    if site.type in {"dc", "cnf"} and site.region in REGION_SHARE:
        return REGION_SHARE[site.region]
    if site.code == "PLT-BAD":
        return network.us_export_share
    if site.supplier_id in {0, 1}:
        return float(network.family_weight[network.family_china].sum()) * 0.5
    if site.type == "port":
        return 0.2
    return 0.05


def _heatmap(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[float]] = {}
    for row in rows:
        key = (str(row["type"]), str(row["region"]))
        gap = max(0.0, float(row["ttr"]) - float(row["tts"]))
        buckets.setdefault(key, []).append(gap)
    return [
        {"type": kind, "region": region, "gap_days": float(np.mean(values))}
        for (kind, region), values in sorted(buckets.items())
    ]
