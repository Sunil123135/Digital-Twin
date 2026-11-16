"""Turn simulated units into rupees. Every figure is P10, P50 and P90."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from pharmatwin.engine.network import Network


def percentiles(values: NDArray[np.float64]) -> dict[str, float]:
    p10, p50, p90 = np.percentile(values, [10, 50, 90])
    return {"p10": float(p10), "p50": float(p50), "p90": float(p90)}


def money_and_service(network: Network, raw: dict[str, Any]) -> dict[str, Any]:
    revenue = raw["revenue_at_risk"]
    writeoff_value = (raw["writeoff_fam"] * network.family_cost[None, :]).sum(axis=1)
    temp_value = (raw["temp_loss_fam"] * network.family_cost[None, :]).sum(axis=1)
    penalty = raw["unmet_critical_units"] * 80.0 + raw["unmet_essential_units"] * 25.0
    lost_margin = revenue - (raw["unmet_fam"] * network.family_cost[None, :]).sum(axis=1)
    margin_impact = lost_margin + raw["extra_cost"] + writeoff_value + penalty - np.minimum(raw["served_margin"], 0)
    working_capital = raw["avg_stock_value"]
    daily = raw["daily_fill"]
    p50_curve = np.percentile(daily, 50, axis=1)
    p90_curve = np.percentile(daily, 90, axis=1)
    hospitals = np.where(network.customer_is_hospital)[0]
    stockout_rows: list[dict[str, Any]] = []
    for index in hospitals:
        site = network.sites[int(network.customer_site_ids[index])]
        days = raw["stockout_days"][:, index]
        stockout_rows.append(
            {
                "site_id": site.id,
                "name": site.name,
                "region": site.region,
                "critical": bool(site.is_critical_care),
                "stockout_days": percentiles(days),
            }
        )
    stockout_rows.sort(key=lambda row: row["stockout_days"]["p50"], reverse=True)
    return {
        "money": {
            "revenue_at_risk": percentiles(revenue),
            "margin_impact": percentiles(margin_impact),
            "working_capital": percentiles(working_capital),
            "write_off": percentiles(writeoff_value + temp_value),
            "penalty": percentiles(penalty),
            "extra_cost": percentiles(raw["extra_cost"]),
        },
        "service": {
            "fill_rate": percentiles(raw["fill_rate"]),
            "critical_fill_rate": percentiles(raw["critical_fill"]),
            "stockout_days": percentiles(raw["stockout_days"].mean(axis=1)),
            "days_to_first_stockout": percentiles(raw["days_to_stockout"]),
            "days_to_recover": percentiles(raw["days_to_recover"]),
            "unmet_critical_units": percentiles(raw["unmet_critical_units"]),
            "unmet_essential_units": percentiles(raw["unmet_essential_units"]),
            "unmet_other_units": percentiles(raw["unmet_other_units"]),
            "expedite_units": percentiles(raw["expedite_units"]),
        },
        "daily_fill_p50": [float(v) for v in p50_curve],
        "daily_fill_p90": [float(v) for v in p90_curve],
        "stockouts_by_hospital": stockout_rows[:12],
    }
