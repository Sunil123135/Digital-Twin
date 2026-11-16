"""Background runs. A process pool keeps the API responsive during a live re-run."""

from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
from typing import Any

from pharmatwin.config import get_settings
from pharmatwin.db import SessionLocal
from pharmatwin.engine.network import build_network
from pharmatwin.models import PlanRow, RunRow, ScenarioRow
from pharmatwin.seed.load import evaluate

_pool: ProcessPoolExecutor | None = None


def pool() -> ProcessPoolExecutor:
    global _pool
    if _pool is None:
        _pool = ProcessPoolExecutor(max_workers=2)
    return _pool


def execute_run(run_id: int) -> None:
    settings = get_settings()
    network = build_network(settings.sim_seed)
    with SessionLocal() as session:
        run = session.get(RunRow, run_id)
        if run is None:
            return
        scenario = session.get(ScenarioRow, run.scenario_id)
        if scenario is None:
            return
        run.status = "running"
        run.started_at = datetime.now(UTC)
        session.commit()
        template_id = scenario.template_id
        params = dict(scenario.params)
        seed = run.seed
        runs = run.runs
        horizon = settings.sim_horizon_days
    try:
        payload = evaluate(template_id, params, network, seed=seed, runs=runs, horizon=horizon)
        status = "done"
        error = None
    except Exception as exc:  # demo-safe: keep the last result and surface the failure
        payload = None
        status = "failed"
        error = str(exc)
    with SessionLocal() as session:
        run = session.get(RunRow, run_id)
        if run is None:
            return
        run.status = status
        run.progress = runs
        run.finished_at = datetime.now(UTC)
        run.error = error
        if payload is not None:
            run.result = payload
            run.is_cached = False
            _store_plans(session, run.scenario_id, payload)
        session.commit()


def _store_plans(session: Any, scenario_id: int, payload: dict[str, Any]) -> None:
    if payload.get("kind") != "scenario":
        return
    session.query(PlanRow).filter_by(scenario_id=scenario_id).delete()
    for plan in payload.get("plans", []):
        session.add(
            PlanRow(
                scenario_id=scenario_id,
                kind=plan["kind"],
                levers=plan["levers"],
                cost=plan["cost"],
                recommended=plan["recommended"],
                explanation=plan["explanation"],
                summary=plan["summary"],
            )
        )


def enqueue(run_id: int) -> None:
    pool().submit(execute_run, run_id)


def last_good(session: Any, scenario_id: int) -> RunRow | None:
    return (
        session.query(RunRow)
        .filter(RunRow.scenario_id == scenario_id, RunRow.status == "done", RunRow.result.is_not(None))
        .order_by(RunRow.id.desc())
        .first()
    )
