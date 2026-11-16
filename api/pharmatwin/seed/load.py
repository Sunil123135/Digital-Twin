"""Create the SQLite demo database and pre-compute the 13 scenarios."""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from pharmatwin.config import get_settings
from pharmatwin.db import SessionLocal, engine
from pharmatwin.engine.network import Network, build_network
from pharmatwin.engine.prescribe import prescribe
from pharmatwin.engine.shocks import LIVE, build_shocks, default_params
from pharmatwin.engine.stress import stress_test
from pharmatwin.models import (
    AuditRow,
    Base,
    BatchRow,
    LaneRow,
    PlanRow,
    ProductRow,
    RunRow,
    ScenarioRow,
    SiteRow,
    SupplierRow,
)
from pharmatwin.runs.keys import cache_key


def reset_schema() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def persist_master(session: Session, network: Network) -> None:
    for site in network.sites:
        session.add(
            SiteRow(
                id=site.id,
                code=site.code,
                name=site.name,
                type=site.type,
                lat=site.lat,
                lon=site.lon,
                region=site.region,
                state=site.state,
                storage_classes=list(site.storage_classes),
                drug_licence_no=site.drug_licence_no,
                licence_expiry=site.licence_expiry,
                approved_markets=list(site.approved_markets),
                throughput_capacity_units_day=site.throughput_capacity_units_day,
                recovery_days=site.recovery_days,
                is_critical_care=site.is_critical_care,
            )
        )
    for lane in network.lanes:
        session.add(
            LaneRow(
                id=lane.id,
                from_site=lane.from_site,
                to_site=lane.to_site,
                mode=lane.mode,
                lead_time_mean_days=lane.lead_time_mean_days,
                lead_time_sd_days=lane.lead_time_sd_days,
                cost_per_unit=lane.cost_per_unit,
                reefer=lane.reefer,
                is_alternate=lane.is_alternate,
            )
        )
    for product in network.products:
        session.add(
            ProductRow(
                id=product.id,
                sku=product.sku,
                name=product.name,
                molecule=product.molecule,
                api_id=product.api_id,
                family_id=product.family_id,
                therapeutic_class=product.therapeutic_class,
                dosage_form=product.dosage_form,
                schedule=product.schedule,
                storage_class=product.storage_class,
                shelf_life_days=product.shelf_life_days,
                essential=product.essential,
                standard_cost=product.standard_cost,
                selling_price=product.selling_price,
                price_cap=product.price_cap,
            )
        )
    for supplier in network.suppliers:
        session.add(
            SupplierRow(
                id=supplier.id,
                name=supplier.name,
                country=supplier.country,
                tier=supplier.tier,
                approved_markets=list(supplier.approved_markets),
                qualification_lead_days=supplier.qualification_lead_days,
                capacity_units_day=supplier.capacity_units_day,
                risk_score=supplier.risk_score,
                site_id=supplier.site_id,
                single_source=supplier.single_source,
            )
        )
    plant = next(site for site in network.sites if site.code == "PLT-BAD")
    today = datetime.now(UTC).date()
    for product in network.products[:40]:
        session.add(
            BatchRow(
                product_id=product.id,
                site_id=plant.id,
                batch_no=f"B-{product.sku}",
                mfg_date=str(today - timedelta(days=40)),
                expiry_date=str(today + timedelta(days=30 if product.id % 7 == 0 else 400)),
                qty=10_000,
                status="released",
            )
        )
    session.flush()


def evaluate(
    template_id: str,
    params: dict[str, Any],
    network: Network,
    *,
    seed: int,
    runs: int,
    horizon: int,
) -> dict[str, Any]:
    if template_id == "network_stress_test":
        outage = int(params.get("outage_days", 14))
        report = stress_test(network, outage_days=outage, seed=seed)
        return {"kind": "stress", "stress": report, "assumptions": _assumptions(network, seed, runs, horizon, params)}
    shocks = build_shocks(template_id, params, network)
    prebuild = float(params["prebuild_weeks"]) if template_id == "prebuild_decision" else None
    prescribed = prescribe(
        network,
        shocks,
        seed=seed,
        runs=runs,
        horizon=horizon,
        prebuild_weeks=prebuild,
    )
    return {
        "kind": "scenario",
        "baseline": prescribed["baseline"],
        "plans": prescribed["plans"],
        "assumptions": _assumptions(network, seed, runs, horizon, params),
    }


def _assumptions(network: Network, seed: int, runs: int, horizon: int, params: dict[str, Any]) -> dict[str, Any]:
    return {
        "network_version": network.version,
        "annual_revenue_inr": network.annual_revenue,
        "seed": seed,
        "runs": runs,
        "horizon_days": horizon,
        "params": params,
        "holding_cost": "18% a year",
        "expedite": "Road 1.5×, air 4×, blended by the expedite lever",
        "allocation": "Critical-care hospitals, then essential medicines, then the rest",
        "data": "Synthetic demo data. Not a real manufacturer's network.",
        "resilience_formula": (
            "100 × share of revenue whose depots have TTS ≥ TTR, "
            "minus 5 per single-source China API above ₹50 cr."
        ),
    }


def store_result(
    session: Session,
    *,
    template_id: str,
    name: str,
    params: dict[str, Any],
    payload: dict[str, Any],
    seed: int,
    runs: int,
    network_version: str,
    horizon: int,
) -> int:
    key = cache_key(template_id, params, seed=seed, runs=runs, horizon=horizon, network_version=network_version)
    existing = session.query(ScenarioRow).filter_by(cache_key=key).one_or_none()
    if existing:
        return existing.id
    scenario = ScenarioRow(template_id=template_id, name=name, params=params, cache_key=key)
    session.add(scenario)
    session.flush()
    now = datetime.now(UTC)
    run = RunRow(
        scenario_id=scenario.id,
        seed=seed,
        runs=runs,
        status="done",
        progress=runs,
        started_at=now,
        finished_at=now,
        result=payload,
        is_cached=True,
    )
    session.add(run)
    session.flush()
    if payload.get("kind") == "scenario":
        for plan in payload["plans"]:
            session.add(
                PlanRow(
                    scenario_id=scenario.id,
                    kind=plan["kind"],
                    levers=plan["levers"],
                    cost=plan["cost"],
                    recommended=plan["recommended"],
                    explanation=plan["explanation"],
                    summary=plan["summary"],
                )
            )
    session.flush()
    return scenario.id


def precompute(session: Session, network: Network, *, seed: int, runs: int, horizon: int) -> None:
    for template in LIVE:
        params = default_params(template.id)
        print(f"seeding {template.id} ({runs} runs, {horizon} days)")
        payload = evaluate(template.id, params, network, seed=seed, runs=runs, horizon=horizon)
        store_result(
            session,
            template_id=template.id,
            name=template.name,
            params=params,
            payload=payload,
            seed=seed,
            runs=runs,
            network_version=network.version,
            horizon=horizon,
        )
        session.commit()


def main() -> None:
    settings = get_settings()
    reset_schema()
    network = build_network(settings.sim_seed)
    with SessionLocal() as session:
        persist_master(session, network)
        session.add(
            AuditRow(
                actor="system",
                action="seed",
                entity="network",
                entity_id=network.version,
                payload={"annual_revenue": network.annual_revenue},
            )
        )
        session.commit()
        precompute(
            session,
            network,
            seed=settings.sim_seed,
            runs=settings.sim_runs,
            horizon=settings.sim_horizon_days,
        )
    print("seed complete")


if __name__ == "__main__":
    main()
