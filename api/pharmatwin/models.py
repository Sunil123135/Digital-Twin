"""SQLAlchemy tables for the demo. JSON columns hold simulation payloads."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


class SiteRow(Base):
    __tablename__ = "sites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(32))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    region: Mapped[str] = mapped_column(String(32))
    state: Mapped[str] = mapped_column(String(64))
    storage_classes: Mapped[list[str]] = mapped_column(JSON)
    drug_licence_no: Mapped[str] = mapped_column(String(64))
    licence_expiry: Mapped[str] = mapped_column(String(32))
    approved_markets: Mapped[list[str]] = mapped_column(JSON)
    throughput_capacity_units_day: Mapped[float] = mapped_column(Float)
    recovery_days: Mapped[int] = mapped_column(Integer)
    is_critical_care: Mapped[bool] = mapped_column(Boolean, default=False)


class LaneRow(Base):
    __tablename__ = "lanes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_site: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    to_site: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    mode: Mapped[str] = mapped_column(String(16))
    lead_time_mean_days: Mapped[float] = mapped_column(Float)
    lead_time_sd_days: Mapped[float] = mapped_column(Float)
    cost_per_unit: Mapped[float] = mapped_column(Float)
    reefer: Mapped[bool] = mapped_column(Boolean)
    is_alternate: Mapped[bool] = mapped_column(Boolean)


class ProductRow(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    molecule: Mapped[str] = mapped_column(String(64))
    api_id: Mapped[int] = mapped_column(Integer)
    family_id: Mapped[int] = mapped_column(Integer)
    therapeutic_class: Mapped[str] = mapped_column(String(32))
    dosage_form: Mapped[str] = mapped_column(String(32))
    schedule: Mapped[str] = mapped_column(String(16))
    storage_class: Mapped[str] = mapped_column(String(16))
    shelf_life_days: Mapped[int] = mapped_column(Integer)
    essential: Mapped[bool] = mapped_column(Boolean)
    standard_cost: Mapped[float] = mapped_column(Float)
    selling_price: Mapped[float] = mapped_column(Float)
    price_cap: Mapped[float | None] = mapped_column(Float, nullable=True)


class SupplierRow(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    country: Mapped[str] = mapped_column(String(8))
    tier: Mapped[int] = mapped_column(Integer)
    approved_markets: Mapped[list[str]] = mapped_column(JSON)
    qualification_lead_days: Mapped[int] = mapped_column(Integer)
    capacity_units_day: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    site_id: Mapped[int] = mapped_column(Integer)
    single_source: Mapped[bool] = mapped_column(Boolean)


class BatchRow(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"))
    batch_no: Mapped[str] = mapped_column(String(32))
    mfg_date: Mapped[str] = mapped_column(String(32))
    expiry_date: Mapped[str] = mapped_column(String(32))
    qty: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16))


class ScenarioRow(Base):
    __tablename__ = "scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(160))
    params: Mapped[dict[str, object]] = mapped_column(JSON)
    cache_key: Mapped[str] = mapped_column(String(64), unique=True)
    created_by: Mapped[str] = mapped_column(String(64), default="demo")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class RunRow(Base):
    __tablename__ = "runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"))
    plan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seed: Mapped[int] = mapped_column(Integer)
    runs: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class PlanRow(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"))
    kind: Mapped[str] = mapped_column(String(32))
    levers: Mapped[dict[str, float]] = mapped_column(JSON)
    cost: Mapped[float] = mapped_column(Float)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    explanation: Mapped[dict[str, object]] = mapped_column(JSON)
    summary: Mapped[dict[str, object]] = mapped_column(JSON)


class ApprovalRow(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    status: Mapped[str] = mapped_column(String(16), default="pending")
    requested_by: Mapped[str] = mapped_column(String(64))
    approver: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditRow(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, default=_now)
    actor: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    entity: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, object]] = mapped_column(JSON)


class UploadRow(Base):
    __tablename__ = "uploads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity: Mapped[str] = mapped_column(String(32))
    valid: Mapped[bool] = mapped_column(Boolean)
    report: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
