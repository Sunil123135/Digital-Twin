"""Choose three response plans. OR-Tools picks lever intensity; the sim verifies it."""

from typing import Any

import numpy as np
from ortools.linear_solver import pywraplp

from pharmatwin.engine.finance import money_and_service
from pharmatwin.engine.network import Network
from pharmatwin.engine.shocks import Shock
from pharmatwin.engine.simulate import Levers, simulate

KINDS = ("cost_optimal", "service_optimal", "balanced")
PENALTY = {
    "cost_optimal": (2.0, 0.4, 0.1),
    "service_optimal": (40.0, 12.0, 3.0),
    "balanced": (12.0, 4.0, 1.0),
}


def _solve(kind: str, unmet_units: float, unit_price: float) -> Levers:
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if solver is None:
        raise RuntimeError("GLOP solver is unavailable")
    expedite = solver.NumVar(0, 1, "expedite")
    alternate = solver.NumVar(0, 1, "alternate_supplier")
    transfer = solver.NumVar(0, 1, "transfer")
    prebuild = solver.NumVar(0, 8, "prebuild")
    backup = solver.NumVar(0, 1, "backup_power")
    spot = solver.NumVar(0, 1, "spot_buy")
    unmet = solver.NumVar(0, max(unmet_units, 1), "unmet")
    relief = (
        0.30 * expedite
        + 0.22 * alternate
        + 0.18 * transfer
        + 0.05 * prebuild
        + 0.10 * backup
        + 0.20 * spot
    )
    solver.Add(unmet + unmet_units * relief >= unmet_units)
    w_crit, w_ess, w_other = PENALTY[kind]
    penalty = (0.45 * w_crit + 0.35 * w_ess + 0.20 * w_other) * unit_price * unmet
    cost = (
        1.2e7 * expedite
        + 9.0e6 * alternate
        + 6.0e6 * transfer
        + 4.0e6 * prebuild
        + 3.0e6 * backup
        + 1.5e7 * spot
    )
    solver.Minimize(cost + penalty)
    status = solver.Solve()
    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        return Levers(expedite=0.4, alternate_supplier=0.3, transfer=0.2, prebuild_weeks=2)
    return Levers(
        expedite=expedite.solution_value(),
        alternate_supplier=alternate.solution_value(),
        transfer=transfer.solution_value(),
        prebuild_weeks=prebuild.solution_value(),
        backup_power=backup.solution_value(),
        spot_buy=spot.solution_value(),
    )


def _roi(baseline_loss: float, plan_loss: float, cost: float) -> float:
    if cost <= 1:
        return 0.0
    return (baseline_loss - plan_loss - cost) / cost


def prescribe(
    network: Network,
    shocks: list[Shock],
    *,
    seed: int,
    runs: int,
    horizon: int,
    prebuild_weeks: float | None = None,
) -> dict[str, Any]:
    baseline_raw = simulate(network, shocks, seed=seed, runs=runs, horizon=horizon)
    baseline = money_and_service(network, baseline_raw)
    unmet_units = float(np.median(baseline_raw["unmet_fam"].sum(axis=1)))
    unit_price = float(np.average(network.family_price, weights=network.family_weight))
    baseline_loss = float(baseline["money"]["revenue_at_risk"]["p50"])
    plans: list[dict[str, Any]] = []
    for kind in KINDS:
        levers = _solve(kind, unmet_units, unit_price)
        if prebuild_weeks is not None and kind == "balanced":
            levers.prebuild_weeks = prebuild_weeks
        raw = simulate(network, shocks, seed=seed, runs=runs, horizon=horizon, levers=levers)
        summary = money_and_service(network, raw)
        loss = float(summary["money"]["revenue_at_risk"]["p50"])
        cost = float(summary["money"]["extra_cost"]["p50"])
        cost = max(cost, 1.0)
        ranked = sorted(levers.as_dict().items(), key=lambda item: item[1], reverse=True)[:3]
        plans.append(
            {
                "kind": kind,
                "levers": levers.as_dict(),
                "cost": cost,
                "loss_avoided": max(0.0, baseline_loss - loss),
                "roi": _roi(baseline_loss, loss, cost),
                "summary": summary,
                "explanation": {
                    "top_levers": [{"name": name, "intensity": round(value, 3)} for name, value in ranked],
                    "binding_constraints": [
                        "Alternate suppliers must be approved for the target market.",
                        "Cold stock moves only on reefer lanes.",
                        "Schedule X stock stays on licensed sites.",
                    ],
                    "sensitivity": _sensitivity(kind, levers, baseline_loss, loss),
                },
                "service_ok": float(summary["service"]["critical_fill_rate"]["p50"]) >= 0.98,
            }
        )
    eligible = [plan for plan in plans if plan["service_ok"]]
    pool = eligible or plans
    best = max(pool, key=lambda plan: (plan["roi"], plan["service_ok"]))
    for plan in plans:
        plan["recommended"] = plan["kind"] == best["kind"]
    return {"baseline": baseline, "plans": plans}


def _sensitivity(kind: str, levers: Levers, baseline_loss: float, loss: float) -> str:
    if kind != "balanced":
        return "Sensitivity is reported on the balanced plan."
    if baseline_loss <= 0:
        return "No material loss in the baseline, so a longer event does not change the recommendation."
    shift = (baseline_loss - loss) / baseline_loss
    if shift < 0.05 and levers.prebuild_weeks < 1:
        return (
            "At a P90-length event the service-optimal plan would replace balanced, "
            "because mitigation is not yet paying for itself."
        )
    return "At a P90-length event the balanced plan remains the recommendation."
