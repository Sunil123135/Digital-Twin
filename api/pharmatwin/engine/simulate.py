"""Vectorised Monte Carlo daily flow. Loops over days only."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from pharmatwin.engine.network import Network
from pharmatwin.engine.shocks import Shock

Progress = Callable[[int, int], None]


@dataclass
class Levers:
    expedite: float = 0.0
    alternate_supplier: float = 0.0
    transfer: float = 0.0
    prebuild_weeks: float = 0.0
    backup_power: float = 0.0
    spot_buy: float = 0.0
    safety_stock_raise: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "expedite": self.expedite,
            "alternate_supplier": self.alternate_supplier,
            "transfer": self.transfer,
            "prebuild_weeks": self.prebuild_weeks,
            "backup_power": self.backup_power,
            "spot_buy": self.spot_buy,
            "safety_stock_raise": self.safety_stock_raise,
        }


def _sample(dist_value: float, runs: int) -> NDArray[np.float64]:
    return np.full(runs, dist_value, dtype=np.float64)


def _class_mask(network: Network, names: list[str] | None) -> NDArray[np.bool_]:
    if not names:
        return np.ones(len(network.families), dtype=bool)
    wanted = set(names)
    return np.array([family.therapeutic_class in wanted for family in network.families])


def _customer_mask(network: Network, target: dict[str, object]) -> NDArray[np.bool_]:
    mask = np.ones(len(network.customer_site_ids), dtype=bool)
    region = target.get("region")
    if region == "West" or region == "Mumbai":
        mask &= np.array([network.sites[int(i)].region == "West" for i in network.customer_site_ids])
    elif isinstance(region, str):
        mask &= np.array([network.sites[int(i)].region == region for i in network.customer_site_ids])
    return mask


def simulate(
    network: Network,
    shocks: list[Shock],
    *,
    seed: int,
    runs: int,
    horizon: int,
    levers: Levers | None = None,
    progress: Progress | None = None,
) -> dict[str, NDArray[np.float64] | NDArray[np.int64]]:
    """Run `runs` trajectories for `horizon` days. `seed` fixes every draw."""
    plan = levers or Levers()
    rng = np.random.default_rng(seed)
    n_fam = len(network.families)
    n_cust = int(network.base_daily.shape[0])
    n_dep = int(network.stock_depot.shape[0])
    max_lead = 40

    noise = np.clip(1 + network.demand_cv * rng.normal(0, 1, size=(runs, n_fam)), 0.25, 2.5)
    depot_stock = np.broadcast_to(network.stock_depot, (runs, n_dep, n_fam)).copy()
    cust_stock = np.broadcast_to(network.stock_customer, (runs, n_cust, n_fam)).copy()
    prebuild = network.base_daily * (plan.prebuild_weeks * 7)
    for depot in range(n_dep):
        members = np.where(network.customer_depot == depot)[0]
        if len(members):
            depot_stock[:, depot, :] += prebuild[members].sum(axis=0)
    cust_stock += prebuild * (1 + plan.safety_stock_raise)
    depot_stock *= 1 + plan.safety_stock_raise * 0.5

    sea_lead = int(np.clip(14 - plan.expedite * 10, 2, max_lead - 1))
    supply_pipe = np.zeros((runs, n_fam, max_lead), dtype=np.float64)
    supply_pipe[:, :, :sea_lead] = network.supply_daily[None, :, None]

    served = np.zeros(runs)
    demanded = np.zeros(runs)
    revenue_at_risk = np.zeros(runs)
    served_margin = np.zeros(runs)
    quarantine_done = np.zeros((runs, n_fam), dtype=bool)
    served_crit = np.zeros(runs)
    demand_crit = np.zeros(runs)
    unmet_fam = np.zeros((runs, n_fam))
    unmet_critical = np.zeros(runs)
    unmet_essential = np.zeros(runs)
    unmet_other = np.zeros(runs)
    writeoff = np.zeros((runs, n_fam))
    temp_loss = np.zeros((runs, n_fam))
    expedite_units = np.zeros(runs)
    extra_cost = np.zeros(runs)
    stock_value_acc = np.zeros(runs)
    daily_fill = np.ones((horizon, runs))
    daily_unmet = np.zeros((horizon, runs))
    stockout_days = np.zeros((runs, n_cust))
    us_unmet_value_units = np.zeros((runs, n_fam))

    cold = network.family_cold.astype(np.float64)
    essential = network.family_essential
    critical_c = network.customer_is_critical
    china = network.family_china

    prepared: list[dict[str, Any]] = []
    for shock in shocks:
        prepared.append(
            {
                "shock": shock,
                "duration": _sample(shock.duration_days.value, runs),
                "magnitude": _sample(shock.magnitude.value, runs),
                "happens": rng.random(runs) < shock.probability,
            }
        )

    depot_codes = [network.sites[int(i)].code for i in network.depot_site_ids]
    for day in range(horizon):
        month = (5 + day // 30) % 12
        seasonal = network.seasonality[month]
        demand = network.base_daily[None, :, :] * seasonal[None, None, :] * noise[:, None, :]
        supply_mult = np.ones((runs, n_fam))
        price_mult = np.ones((runs, n_fam))
        cost_mult = np.ones((runs, n_fam))
        depot_open = np.ones((runs, n_dep))
        lane_region_open = np.ones((runs, n_cust))
        temp_p = np.zeros((runs, n_dep))
        lead_add = np.zeros(runs)
        quarantine = np.zeros((runs, n_fam))
        us_blocked = np.zeros(runs)

        for item in prepared:
            event: Shock = item["shock"]
            active = item["happens"] & (day >= event.start_day) & (day < event.start_day + item["duration"])
            if not np.any(active):
                continue
            mag = item["magnitude"]
            target = event.target
            if event.type == "supplier_capacity":
                china_cut = target.get("supplier_country") == "CN" or target.get("china_dependent")
                fam = china if china_cut else np.ones(n_fam, dtype=bool)
                if "supplier_id" in target and int(target["supplier_id"]) == 12:
                    fam = cold.astype(bool)
                restored = mag + (1 - mag) * plan.alternate_supplier
                supply_mult = np.where(active[:, None] & fam[None, :], supply_mult * restored[:, None], supply_mult)
            elif event.type == "node_down":
                code = str(target.get("site_code", ""))
                if code in depot_codes:
                    idx = depot_codes.index(code)
                    depot_open[:, idx] = np.where(active, mag, depot_open[:, idx])
            elif event.type == "lane_down":
                cmask = _customer_mask(network, target)
                lane_region_open = np.where(active[:, None] & cmask[None, :], mag[:, None], lane_region_open)
            elif event.type == "demand_multiplier":
                cmask = _customer_mask(network, target)
                fmask = _class_mask(network, target.get("therapeutic_class"))
                if target.get("essential") is True:
                    fmask = fmask & essential
                demand = np.where(
                    active[:, None, None] & cmask[None, :, None] & fmask[None, None, :],
                    demand * mag[:, None, None],
                    demand,
                )
            elif event.type == "cost_multiplier":
                fam = china if target.get("china_dependent") else np.ones(n_fam, dtype=bool)
                cost_mult = np.where(active[:, None] & fam[None, :], cost_mult * mag[:, None], cost_mult)
            elif event.type == "price_change":
                if target.get("us_export"):
                    price_mult = np.where(active[:, None], price_mult * mag[:, None], price_mult)
                else:
                    cmask = _customer_mask(network, target)
                    fmask = essential if target.get("essential") else np.ones(n_fam, dtype=bool)
                    demand_scale = 1.0
                    del demand_scale
                    price_mult = np.where(
                        active[:, None] & fmask[None, :],
                        price_mult * mag[:, None],
                        price_mult,
                    )
                    del cmask
            elif event.type == "market_block":
                us_blocked = np.where(active, 1.0, us_blocked)
            elif event.type == "temperature_loss":
                code = str(target.get("site_code", "DC-CHE"))
                if code in depot_codes:
                    idx = depot_codes.index(code)
                    temp_p[:, idx] = np.where(active, mag * (1 - plan.backup_power), temp_p[:, idx])
            elif event.type == "lead_time_shift":
                lead_add = np.where(active, mag, lead_add)
            elif event.type == "batch_quarantine":
                fmask = _class_mask(network, target.get("therapeutic_class"))
                quarantine = np.where(
                    active[:, None] & fmask[None, :],
                    np.maximum(quarantine, mag[:, None]),
                    quarantine,
                )

        if np.any(quarantine > 0):
            fresh = (quarantine > 0) & ~quarantine_done
            removed = cust_stock * quarantine[:, None, :] * fresh[:, None, :]
            cust_stock -= removed
            writeoff += removed.sum(axis=1)
            quarantine_done |= fresh

        arrivals = supply_pipe[:, :, 0]
        supply_pipe = np.concatenate([supply_pipe[:, :, 1:], np.zeros((runs, n_fam, 1))], axis=2)
        inject_at = np.clip((sea_lead - 1 + lead_add).astype(np.int64), 0, max_lead - 1)
        injection = network.supply_daily[None, :] * supply_mult * (1 + 0.35 * plan.spot_buy)
        for lead in np.unique(inject_at):
            rows = inject_at == lead
            supply_pipe[rows, :, int(lead)] += injection[rows]

        plant_pool = arrivals
        us_cut = network.us_export_share * us_blocked[:, None]
        plant_pool = plant_pool * (1 - us_cut)
        us_unmet_value_units += network.supply_daily[None, :] * us_cut

        loss = depot_stock * temp_p[:, :, None] * cold[None, None, :]
        depot_stock -= loss
        temp_loss += loss.sum(axis=1)
        writeoff += loss.sum(axis=1) * 0

        if day % 30 == 29:
            expiring = depot_stock * cold[None, None, :] / 6.0
            depot_stock -= expiring
            writeoff += expiring.sum(axis=1)

        priorities = (
            critical_c[:, None] & np.ones((1, n_fam), dtype=bool),
            (~critical_c[:, None]) & essential[None, :],
            (~critical_c[:, None]) & (~essential[None, :]),
        )
        day_served = np.zeros_like(demand)
        remaining = demand.copy()
        for mask in priorities:
            need = remaining * mask[None, :, :]
            take = np.minimum(cust_stock, need)
            cust_stock -= take
            day_served += take
            remaining -= take
        unmet = demand - day_served
        unit_price = network.family_price[None, None, :] * price_mult[:, None, :]
        unit_cost = network.family_cost[None, None, :] * cost_mult[:, None, :]
        revenue_at_risk += (unmet * unit_price).sum(axis=(1, 2))
        served_margin += (day_served * (unit_price - unit_cost)).sum(axis=(1, 2))
        served += day_served.sum(axis=(1, 2))
        demanded += demand.sum(axis=(1, 2))
        crit_need = demand[:, critical_c, :].sum(axis=(1, 2))
        crit_got = day_served[:, critical_c, :].sum(axis=(1, 2))
        served_crit += crit_got
        demand_crit += crit_need
        unmet_fam += unmet.sum(axis=1)
        unmet_critical += unmet[:, critical_c, :].sum(axis=(1, 2))
        ess_slice = unmet[:, ~critical_c][:, :, essential]
        unmet_essential += ess_slice.sum(axis=(1, 2)) if ess_slice.size else 0
        other_mask_c = ~critical_c
        unmet_other += (unmet[:, other_mask_c][:, :, ~essential]).sum(axis=(1, 2))
        stockout_days += (unmet.sum(axis=2) > 1).astype(np.float64)
        daily_unmet[day] = unmet.sum(axis=(1, 2))
        daily_fill[day] = np.divide(day_served.sum(axis=(1, 2)), np.maximum(demand.sum(axis=(1, 2)), 1))

        cust_target = demand * (4 + 3 * plan.safety_stock_raise)
        cust_order = np.maximum(0, cust_target - cust_stock)
        cust_order *= lane_region_open[:, :, None]
        for depot in range(n_dep):
            members = np.where(network.customer_depot == depot)[0]
            if not len(members):
                continue
            wanted = cust_order[:, members, :].sum(axis=1)
            open_factor = depot_open[:, depot][:, None]
            can = depot_stock[:, depot, :] * open_factor
            if plan.transfer > 0 and depot_open[:, depot].min() < 1:
                others = [i for i in range(n_dep) if i != depot]
                borrowed = depot_stock[:, others, :].sum(axis=1) * plan.transfer * 0.25
                can = can + borrowed
                for other in others:
                    give = np.minimum(depot_stock[:, other, :], borrowed / max(len(others), 1))
                    depot_stock[:, other, :] -= give
            ship = np.minimum(can, wanted)
            depot_stock[:, depot, :] = np.maximum(0, depot_stock[:, depot, :] - ship)
            if ship.sum() <= 0:
                continue
            share = np.divide(cust_order[:, members, :], np.maximum(wanted[:, None, :], 1e-6))
            cust_stock[:, members, :] += ship[:, None, :] * share
            fast = ship.sum(axis=1) * plan.expedite
            expedite_units += fast

        depot_need = np.maximum(0, (network.stock_depot[None, :, :] * 0.5) - depot_stock)
        ship_up = np.minimum(depot_need.sum(axis=1), plant_pool)
        if ship_up.sum() > 0:
            weights = np.maximum(depot_need.sum(axis=2), 1e-6)
            weights = weights / weights.sum(axis=1, keepdims=True)
            added = ship_up[:, None, :] * weights[:, :, None]
            added = np.minimum(added, depot_need)
            depot_stock += added
        premium = (cost_mult - 1) + plan.expedite * 3 + plan.spot_buy * 0.8
        extra_cost += (plant_pool * np.maximum(premium, 0) * network.family_cost[None, :]).sum(axis=1)
        extra_cost += plan.backup_power * 250_000
        stock_value_acc += (depot_stock.sum(axis=1) * network.family_cost[None, :]).sum(axis=1)
        stock_value_acc += (cust_stock.sum(axis=1) * network.family_cost[None, :]).sum(axis=1)

        if progress and (day + 1) % max(horizon // 10, 1) == 0:
            progress(min(runs, int((day + 1) / horizon * runs)), runs)

    if progress:
        progress(runs, runs)

    with np.errstate(divide="ignore", invalid="ignore"):
        fill = np.divide(served, np.maximum(demanded, 1))
        critical_fill = np.divide(served_crit, np.maximum(demand_crit, 1))
    hit = daily_unmet > 1
    days_to_stockout = np.where(hit.any(axis=0), np.argmax(hit, axis=0).astype(np.float64), float(horizon))
    below = daily_fill < 0.98
    last_gap = horizon - 1 - np.argmax(below[::-1], axis=0)
    days_to_recover = np.where(below.any(axis=0), last_gap.astype(np.float64), 0.0)
    return {
        "fill_rate": fill,
        "critical_fill": critical_fill,
        "unmet_fam": unmet_fam,
        "unmet_critical_units": unmet_critical,
        "unmet_essential_units": unmet_essential,
        "unmet_other_units": unmet_other,
        "writeoff_fam": writeoff,
        "temp_loss_fam": temp_loss,
        "expedite_units": expedite_units,
        "extra_cost": extra_cost,
        "avg_stock_value": stock_value_acc / max(horizon, 1),
        "daily_fill": daily_fill,
        "daily_unmet": daily_unmet,
        "stockout_days": stockout_days,
        "days_to_stockout": days_to_stockout,
        "days_to_recover": days_to_recover,
        "us_unmet_units": us_unmet_value_units,
        "revenue_at_risk": revenue_at_risk + (us_unmet_value_units * network.family_price[None, :]).sum(axis=1),
        "served_margin": served_margin,
    }
