"""Demo HTTP API."""

import csv
import io
import json
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from pharmatwin.config import get_settings
from pharmatwin.copilot.service import confirm_proposal, iter_chat
from pharmatwin.db import get_session
from pharmatwin.engine.network import build_network
from pharmatwin.engine.shocks import default_params, template_by_id, templates
from pharmatwin.models import (
    ApprovalRow,
    AuditRow,
    PlanRow,
    RunRow,
    ScenarioRow,
    SiteRow,
    UploadRow,
)
from pharmatwin.runs.keys import cache_key
from pharmatwin.runs.worker import enqueue, last_good
from pharmatwin.schemas import ApprovalCreate, CopilotRequest, Decision, RunCreate, ScenarioCreate
from pharmatwin.seed.load import store_result

router = APIRouter(prefix="/api")

TEMPLATES = {
    "sites": ["code", "name", "type", "lat", "lon", "region", "state"],
    "lanes": ["from_code", "to_code", "mode", "lead_time_mean_days", "reefer", "is_alternate"],
    "products": ["sku", "name", "therapeutic_class", "storage_class", "schedule", "standard_cost", "selling_price"],
    "demand": ["sku", "site_code", "base_daily"],
}


def require_demo_auth(authorization: str | None = Header(default=None)) -> None:
    password = get_settings().demo_password
    if not password:
        return
    expected = "Basic " + _basic("demo", password)
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Demo password required")


def _basic(user: str, password: str) -> str:
    import base64

    return base64.b64encode(f"{user}:{password}".encode()).decode()


def _audit(session: Session, actor: str, action: str, entity: str, entity_id: str, payload: dict[str, Any]) -> None:
    session.add(AuditRow(actor=actor, action=action, entity=entity, entity_id=entity_id, payload=payload))


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pharmatwin"}


@router.get("/executive")
def executive(session: Session = Depends(get_session), _: None = Depends(require_demo_auth)) -> dict[str, Any]:
    stress = _cached_template(session, "network_stress_test")
    china = _cached_template(session, "china_api_shock")
    hero = _cached_template(session, "monsoon_dengue")
    risks = _top_risks(session)
    stress_body = (stress.result or {}).get("stress", {}) if stress else {}
    return {
        "resilience": stress_body.get("resilience", {}),
        "heatmap": stress_body.get("heatmap", []),
        "risks": risks,
        "hero_scenario_id": hero.scenario_id if hero else None,
        "china_scenario_id": china.scenario_id if china else None,
        "kpis": (china.result or {}).get("baseline") if china else None,
        "synthetic": True,
    }


@router.get("/network")
def network(session: Session = Depends(get_session), _: None = Depends(require_demo_auth)) -> dict[str, Any]:
    sites = session.query(SiteRow).all()
    stress = _cached_template(session, "network_stress_test")
    exposure = {}
    if stress and stress.result:
        for node in stress.result.get("stress", {}).get("nodes", []):
            exposure[node["site_id"]] = node
    features = []
    for site in sites:
        node = exposure.get(site.id, {})
        level = _risk_level(node.get("tts"), node.get("ttr"))
        features.append(
            {
                "id": site.id,
                "code": site.code,
                "name": site.name,
                "type": site.type,
                "region": site.region,
                "state": site.state,
                "lat": site.lat,
                "lon": site.lon,
                "storage_classes": site.storage_classes,
                "recovery_days": site.recovery_days,
                "is_critical_care": site.is_critical_care,
                "risk": level,
                "tts": node.get("tts"),
                "ttr": node.get("ttr"),
                "exposure": node.get("exposure"),
            }
        )
    return {"sites": features, "synthetic": True, "version": build_network(42).version}


@router.get("/network/sites/{site_id}")
def site_detail(
    site_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    site = session.get(SiteRow, site_id)
    if site is None:
        raise HTTPException(404, "Site not found")
    from pharmatwin.models import BatchRow

    batches = session.query(BatchRow).filter_by(site_id=site_id).limit(8).all()
    return {
        "site": {"id": site.id, "code": site.code, "name": site.name, "type": site.type, "region": site.region},
        "licence": {"number": site.drug_licence_no, "expiry": site.licence_expiry, "markets": site.approved_markets},
        "storage_classes": site.storage_classes,
        "batches": [
            {"batch_no": batch.batch_no, "expiry_date": batch.expiry_date, "qty": batch.qty, "status": batch.status}
            for batch in batches
        ],
        "critical": site.is_critical_care,
    }


@router.get("/scenarios/templates")
def list_templates(_: None = Depends(require_demo_auth)) -> dict[str, Any]:
    return {"templates": [item.model_dump() for item in templates()]}


@router.post("/scenarios")
def create_scenario(
    body: ScenarioCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    settings = get_settings()
    template = template_by_id(body.template_id)
    params = default_params(template.id)
    params.update(body.params)
    network = build_network(settings.sim_seed)
    key = cache_key(
        template.id,
        params,
        seed=settings.sim_seed,
        runs=settings.sim_runs,
        horizon=settings.sim_horizon_days,
        network_version=network.version,
    )
    found = session.query(ScenarioRow).filter_by(cache_key=key).one_or_none()
    if found:
        return {"scenario_id": found.id, "cached": True}
    scenario_id = store_result(
        session,
        template_id=template.id,
        name=template.name,
        params=params,
        payload={"kind": "pending"},
        seed=settings.sim_seed,
        runs=settings.sim_runs,
        network_version=network.version,
        horizon=settings.sim_horizon_days,
    )
    session.commit()
    return {"scenario_id": scenario_id, "cached": False}


@router.post("/runs")
def start_run(
    body: RunCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    settings = get_settings()
    scenario = session.get(ScenarioRow, body.scenario_id)
    if scenario is None:
        raise HTTPException(404, "Scenario not found")
    cached = (
        session.query(RunRow)
        .filter_by(scenario_id=scenario.id, status="done", is_cached=True)
        .order_by(RunRow.id.asc())
        .first()
    )
    if cached and cached.result and cached.result.get("kind") != "pending":
        return {"run_id": cached.id, "status": "done", "cached": True, "result": cached.result}
    run = RunRow(
        scenario_id=scenario.id,
        seed=body.seed or settings.sim_seed,
        runs=body.runs or settings.sim_runs,
        status="queued",
        progress=0,
        is_cached=False,
    )
    session.add(run)
    session.commit()
    enqueue(run.id)
    return {"run_id": run.id, "status": "queued", "cached": False}


@router.get("/runs/{run_id}")
def get_run(
    run_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    run = session.get(RunRow, run_id)
    if run is None:
        raise HTTPException(404, "Run not found")
    fallback = None
    if run.status == "failed":
        previous = last_good(session, run.scenario_id)
        if previous and previous.id != run.id:
            fallback = {
                "banner": f"Live re-run didn't finish; showing result from {previous.finished_at}",
                "result": previous.result,
                "run_id": previous.id,
            }
    return {
        "run_id": run.id,
        "scenario_id": run.scenario_id,
        "status": run.status,
        "progress": run.progress,
        "runs": run.runs,
        "seed": run.seed,
        "cached": run.is_cached,
        "error": run.error,
        "result": run.result,
        "fallback": fallback,
    }


@router.get("/runs/{run_id}/events")
def run_events(run_id: int, _: None = Depends(require_demo_auth)) -> StreamingResponse:
    def stream() -> Any:
        import time

        from pharmatwin.db import SessionLocal

        while True:
            with SessionLocal() as session:
                run = session.get(RunRow, run_id)
                if run is None:
                    yield 'event: error\ndata: {"message": "missing"}\n\n'
                    return
                payload = {"status": run.status, "progress": run.progress, "runs": run.runs}
                yield f"event: progress\ndata: {json.dumps(payload)}\n\n"
                if run.status in {"done", "failed"}:
                    return
            time.sleep(0.4)

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/scenarios/{scenario_id}/plans")
def plans(
    scenario_id: int,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    rows = session.query(PlanRow).filter_by(scenario_id=scenario_id).all()
    return {
        "plans": [
            {
                "id": row.id,
                "kind": row.kind,
                "levers": row.levers,
                "cost": row.cost,
                "recommended": row.recommended,
                "explanation": row.explanation,
                "summary": row.summary,
            }
            for row in rows
        ]
    }


@router.post("/approvals")
def request_approval(
    body: ApprovalCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, int]:
    plan = session.get(PlanRow, body.plan_id)
    if plan is None:
        raise HTTPException(404, "Plan not found")
    approval = ApprovalRow(plan_id=plan.id, status="pending", requested_by=body.requested_by)
    session.add(approval)
    session.flush()
    _audit(session, body.requested_by, "request_approval", "plan", str(plan.id), {"approval_id": approval.id})
    session.commit()
    return {"approval_id": approval.id}


@router.post("/approvals/{approval_id}/decide")
def decide(
    approval_id: int,
    body: Decision,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, str]:
    if body.status not in {"approved", "rejected"}:
        raise HTTPException(400, "Decision must be approved or rejected")
    if not body.reason.strip():
        raise HTTPException(400, "A reason is required")
    approval = session.get(ApprovalRow, approval_id)
    if approval is None:
        raise HTTPException(404, "Approval not found")
    approval.status = body.status
    approval.approver = body.approver
    approval.reason = body.reason.strip()
    approval.decided_at = datetime.now(UTC)
    _audit(
        session,
        body.approver,
        body.status,
        "approval",
        str(approval.id),
        {"plan_id": approval.plan_id, "reason": approval.reason},
    )
    session.commit()
    return {"status": approval.status}


@router.get("/approvals")
def list_approvals(session: Session = Depends(get_session), _: None = Depends(require_demo_auth)) -> dict[str, Any]:
    rows = session.query(ApprovalRow).order_by(ApprovalRow.id.desc()).all()
    return {
        "approvals": [
            {
                "id": row.id,
                "plan_id": row.plan_id,
                "status": row.status,
                "requested_by": row.requested_by,
                "approver": row.approver,
                "reason": row.reason,
                "decided_at": row.decided_at.isoformat() if row.decided_at else None,
            }
            for row in rows
        ]
    }


@router.get("/audit")
def audit(session: Session = Depends(get_session), _: None = Depends(require_demo_auth)) -> dict[str, Any]:
    rows = session.query(AuditRow).order_by(AuditRow.id.desc()).limit(100).all()
    return {
        "entries": [
            {
                "id": row.id,
                "ts": row.ts.isoformat() if row.ts else None,
                "actor": row.actor,
                "action": row.action,
                "entity": row.entity,
                "entity_id": row.entity_id,
                "payload": row.payload,
            }
            for row in rows
        ]
    }


@router.get("/upload/templates/{entity}.csv")
def csv_template(entity: str, _: None = Depends(require_demo_auth)) -> StreamingResponse:
    if entity not in TEMPLATES:
        raise HTTPException(404, "Unknown template")
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(TEMPLATES[entity])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={entity}.csv"},
    )


@router.post("/upload/{entity}")
async def upload(
    entity: str,
    request: Request,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    if entity not in TEMPLATES:
        raise HTTPException(404, "Unknown entity")
    raw = (await request.body()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    missing = [column for column in TEMPLATES[entity] if column not in (reader.fieldnames or [])]
    rows = list(reader)
    errors = [f"Missing column {column}" for column in missing]
    if not rows:
        errors.append("The file has no data rows")
    report = {"entity": entity, "rows": len(rows), "errors": errors, "valid": not errors}
    session.add(UploadRow(entity=entity, valid=not errors, report=report))
    session.commit()
    return report


@router.post("/stress-test")
def run_stress(session: Session = Depends(get_session), _: None = Depends(require_demo_auth)) -> dict[str, Any]:
    cached = _cached_template(session, "network_stress_test")
    if cached is None or cached.result is None:
        raise HTTPException(404, "Stress test has not been seeded")
    return {"run_id": cached.id, "cached": True, "result": cached.result}


@router.post("/copilot/chat")
def copilot(
    body: CopilotRequest,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> StreamingResponse:
    messages = [{"role": item.role, "content": item.content} for item in body.messages]

    def stream() -> Any:
        for event in iter_chat(session, messages):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/copilot/confirm")
def copilot_confirm(
    body: ScenarioCreate,
    session: Session = Depends(get_session),
    _: None = Depends(require_demo_auth),
) -> dict[str, Any]:
    return confirm_proposal(session, body.template_id, body.params)


def _cached_template(session: Session, template_id: str) -> RunRow | None:
    scenario = (
        session.query(ScenarioRow)
        .filter_by(template_id=template_id)
        .order_by(ScenarioRow.id.asc())
        .first()
    )
    if scenario is None:
        return None
    return (
        session.query(RunRow)
        .filter_by(scenario_id=scenario.id, status="done")
        .order_by(RunRow.id.asc())
        .first()
    )


def _top_risks(session: Session) -> list[dict[str, Any]]:
    risks = []
    for template_id, owner in (
        ("china_api_shock", "Procurement"),
        ("monsoon_dengue", "Distribution"),
        ("usfda_warning", "Quality"),
        ("cold_chain_failure", "Cold chain"),
        ("tariff_bom", "Finance"),
    ):
        run = _cached_template(session, template_id)
        if run is None or not run.result:
            continue
        scenario = session.get(ScenarioRow, run.scenario_id)
        baseline = run.result.get("baseline") or {}
        money = baseline.get("money", {}).get("revenue_at_risk", {})
        risks.append(
            {
                "template_id": template_id,
                "scenario_id": run.scenario_id,
                "name": scenario.name if scenario else template_id,
                "exposure": money.get("p50", 0),
                "likelihood": "Scenario default",
                "owner": owner,
            }
        )
    risks.sort(key=lambda item: item["exposure"], reverse=True)
    return risks


def _risk_level(tts: float | None, ttr: float | None) -> str:
    if tts is None or ttr is None:
        return "low"
    gap = ttr - tts
    if gap > 20:
        return "critical"
    if gap > 8:
        return "high"
    if gap > 0:
        return "medium"
    return "low"
