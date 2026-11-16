"""Shock model and the 13 live scenario templates. The other 32 are pilot metadata."""

from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from pharmatwin.engine.network import Network

ShockType = Literal[
    "node_down",
    "lane_down",
    "supplier_capacity",
    "demand_multiplier",
    "cost_multiplier",
    "market_block",
    "temperature_loss",
    "lead_time_shift",
    "batch_quarantine",
    "price_change",
]


class Distribution(BaseModel):
    kind: Literal["fixed", "triangular", "lognormal"] = "fixed"
    value: float = 0
    minimum: float = 0
    mode: float = 0
    maximum: float = 0
    mean: float = 0
    sd: float = 0


class Shock(BaseModel):
    type: ShockType
    target: dict[str, Any] = Field(default_factory=dict)
    start_day: int = 0
    duration_days: Distribution = Field(default_factory=Distribution)
    magnitude: Distribution = Field(default_factory=lambda: Distribution(value=1))
    probability: float = 1.0


class ParamSpec(BaseModel):
    name: str
    label: str
    unit: str
    default: float | str
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    is_live_slider: bool = False
    choices: list[str] | None = None


class ScenarioTemplate(BaseModel):
    id: str
    name: str
    description: str
    category: str
    status: Literal["live", "coming_in_pilot"] = "live"
    params: list[ParamSpec] = Field(default_factory=list)
    headline: str = ""


def fixed(value: float) -> Distribution:
    return Distribution(kind="fixed", value=value)


def _num(params: dict[str, Any], name: str, default: float) -> float:
    raw = params.get(name, default)
    return float(raw)


Builder = Callable[[dict[str, Any], Network], list[Shock]]


def _china(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    cut = _num(params, "supply_cut_pct", 70) / 100
    return [
        Shock(
            type="supplier_capacity",
            target={"supplier_country": "CN"},
            start_day=int(_num(params, "start_day", 5)),
            duration_days=fixed(_num(params, "duration_days", 45)),
            magnitude=fixed(max(0.0, 1 - cut)),
        ),
        Shock(
            type="cost_multiplier",
            target={"china_dependent": True},
            start_day=int(_num(params, "start_day", 5)),
            duration_days=fixed(_num(params, "duration_days", 45)),
            magnitude=fixed(1.35),
        ),
    ]


def _tariff(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    api_tariff = _num(params, "api_tariff_pct", 25) / 100
    us_tariff = _num(params, "us_tariff_pct", 15) / 100
    day = int(_num(params, "effective_day", 30))
    return [
        Shock(
            type="cost_multiplier",
            target={"china_dependent": True},
            start_day=day,
            duration_days=fixed(90),
            magnitude=fixed(1 + api_tariff),
        ),
        Shock(
            type="price_change",
            target={"us_export": True},
            start_day=day,
            duration_days=fixed(90),
            magnitude=fixed(max(0.05, 1 - us_tariff)),
        ),
    ]


def _usfda(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    months = _num(params, "halt_months", 12)
    return [
        Shock(
            type="market_block",
            target={"site_code": "PLT-BAD", "market": "US"},
            start_day=2,
            duration_days=fixed(months * 30),
            magnitude=fixed(0),
        )
    ]


def _recall(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    batches = _num(params, "batches_affected", 3)
    return [
        Shock(
            type="batch_quarantine",
            target={"therapeutic_class": ["cardiac"]},
            start_day=1,
            duration_days=fixed(60),
            magnitude=fixed(min(0.8, batches / 10)),
        )
    ]


def _monsoon(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    duration = _num(params, "flood_days", 10)
    uplift = 1 + _num(params, "dengue_uplift_pct", 80) / 100
    return [
        Shock(
            type="node_down",
            target={"site_code": "DC-MUM"},
            start_day=3,
            duration_days=fixed(duration),
            magnitude=fixed(0),
        ),
        Shock(
            type="lane_down",
            target={"region": "West"},
            start_day=3,
            duration_days=fixed(duration),
            magnitude=fixed(0),
        ),
        Shock(
            type="demand_multiplier",
            target={"region": "West", "therapeutic_class": ["antipyretic", "iv_fluids", "antibiotic"]},
            start_day=3,
            duration_days=fixed(duration + 14),
            magnitude=fixed(uplift),
        ),
    ]


def _shipping(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    extra = _num(params, "extra_days", 18)
    return [
        Shock(
            type="lead_time_shift",
            target={"mode": "sea"},
            start_day=2,
            duration_days=fixed(70),
            magnitude=fixed(extra),
        ),
        Shock(
            type="cost_multiplier",
            target={"mode": "sea"},
            start_day=2,
            duration_days=fixed(70),
            magnitude=fixed(1.6),
        ),
    ]


def _epidemic(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    uplift = 1 + _num(params, "uplift_pct", 150) / 100
    weeks = _num(params, "duration_weeks", 6)
    return [
        Shock(
            type="demand_multiplier",
            target={"therapeutic_class": ["respiratory", "antibiotic", "antiviral"]},
            start_day=4,
            duration_days=fixed(weeks * 7),
            magnitude=fixed(uplift),
        )
    ]


def _supplier_failure(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    remaining = 1 - _num(params, "capacity_lost_pct", 100) / 100
    return [
        Shock(
            type="supplier_capacity",
            target={"supplier_id": 12},
            start_day=2,
            duration_days=fixed(_num(params, "duration_days", 60)),
            magnitude=fixed(max(0.0, remaining)),
        )
    ]


def _cold(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    hours = _num(params, "power_cut_hours", 6)
    probability = min(0.85, hours / 18)
    return [
        Shock(
            type="temperature_loss",
            target={"site_code": "DC-CHE"},
            start_day=2,
            duration_days=fixed(_num(params, "heatwave_days", 7)),
            magnitude=fixed(probability),
        )
    ]


def _cyber(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    manual = _num(params, "manual_capacity_pct", 30) / 100
    return [
        Shock(
            type="node_down",
            target={"site_code": "DC-CCU"},
            start_day=1,
            duration_days=fixed(_num(params, "outage_days", 5)),
            magnitude=fixed(manual),
        )
    ]


def _tender(params: dict[str, Any], network: Network) -> list[Shock]:
    del network
    volume = _num(params, "tender_volume_index", 1.4)
    discount = _num(params, "price_discount_pct", 18) / 100
    return [
        Shock(
            type="demand_multiplier",
            target={"region": "East", "essential": True},
            start_day=5,
            duration_days=fixed(60),
            magnitude=fixed(volume),
        ),
        Shock(
            type="price_change",
            target={"region": "East", "essential": True},
            start_day=5,
            duration_days=fixed(60),
            magnitude=fixed(max(0.05, 1 - discount)),
        ),
    ]


def _prebuild(params: dict[str, Any], network: Network) -> list[Shock]:
    """The event is the monsoon flood. Pre-build weeks are a plan lever, not a shock."""
    del params
    return _monsoon({"flood_days": 10, "dengue_uplift_pct": 80}, network)


def _stress_template(params: dict[str, Any], network: Network) -> list[Shock]:
    del params, network
    return []


BUILDERS: dict[str, Builder] = {
    "china_api_shock": _china,
    "tariff_bom": _tariff,
    "usfda_warning": _usfda,
    "product_recall": _recall,
    "monsoon_dengue": _monsoon,
    "shipping_disruption": _shipping,
    "epidemic_surge": _epidemic,
    "supplier_failure": _supplier_failure,
    "cold_chain_failure": _cold,
    "cyber_outage": _cyber,
    "tender_feasibility": _tender,
    "prebuild_decision": _prebuild,
    "network_stress_test": _stress_template,
}


def _slider(
    name: str,
    label: str,
    unit: str,
    default: float,
    minimum: float,
    maximum: float,
    step: float,
    *,
    live: bool = True,
) -> ParamSpec:
    return ParamSpec(
        name=name,
        label=label,
        unit=unit,
        default=default,
        minimum=minimum,
        maximum=maximum,
        step=step,
        is_live_slider=live,
    )


LIVE: tuple[ScenarioTemplate, ...] = (
    ScenarioTemplate(
        id="china_api_shock",
        name="China ingredient shock",
        description="China restricts exports of key active ingredients; 42 SKUs depend on 3 Chinese suppliers.",
        category="Supply & ingredients",
        headline="Revenue at risk, SKUs stocking out, days until first stockout",
        params=[
            _slider("supply_cut_pct", "Supply cut", "%", 70, 20, 100, 5),
            _slider("duration_days", "Duration", "days", 45, 14, 120, 1),
            _slider("start_day", "Start day", "day", 5, 0, 30, 1, live=False),
        ],
    ),
    ScenarioTemplate(
        id="tariff_bom",
        name="Tariff escalation by ingredient list",
        description="Import tariff on Chinese APIs and a US tariff on finished exports.",
        category="Market",
        headline="Margin by SKU and market, working capital for pre-build",
        params=[
            _slider("api_tariff_pct", "API import tariff", "%", 25, 0, 100, 1),
            _slider("us_tariff_pct", "US export tariff", "%", 15, 0, 50, 1),
            _slider("effective_day", "Effective day", "day", 30, 0, 60, 1, live=False),
        ],
    ),
    ScenarioTemplate(
        id="usfda_warning",
        name="USFDA warning letter at a plant",
        description="Baddi plant gets a warning letter; US exports from it halt.",
        category="Regulatory & quality",
        headline="US revenue at risk, months to recover, capacity gap",
        params=[
            _slider("halt_months", "Halt duration", "months", 12, 3, 36, 1),
            ParamSpec(name="plant", label="Plant", unit="choice", default="Baddi", choices=["Baddi"]),
        ],
    ),
    ScenarioTemplate(
        id="product_recall",
        name="Product recall",
        description="A contaminated batch of a cardiac drug; trace and isolate.",
        category="Regulatory & quality",
        headline="Units traced, cost of recall, stockout days",
        params=[
            _slider("batches_affected", "Batches affected", "batches", 3, 1, 10, 1),
            ParamSpec(
                name="recall_class",
                label="Recall class",
                unit="choice",
                default="Class II",
                choices=["Class I", "Class II", "Class III"],
            ),
        ],
    ),
    ScenarioTemplate(
        id="monsoon_dengue",
        name="Monsoon flood + dengue surge",
        description=(
            "Mumbai floods close highways and the Bhiwandi warehouse; "
            "dengue lifts demand for antipyretics and fluids."
        ),
        category="Climate",
        headline="Hospital stockout days, critical-care orders missed, cost of pre-positioning",
        params=[
            _slider("flood_days", "Flood duration", "days", 10, 3, 30, 1),
            _slider("dengue_uplift_pct", "Dengue demand uplift", "%", 80, 0, 200, 5),
            ParamSpec(name="region", label="Region", unit="choice", default="Mumbai", choices=["Mumbai"]),
        ],
    ),
    ScenarioTemplate(
        id="shipping_disruption",
        name="Global shipping disruption",
        description="Red Sea rerouting plus JNPT congestion.",
        category="Logistics",
        headline="Delays, freight cost increase, expiry write-off in transit",
        params=[_slider("extra_days", "Extra transit", "days", 18, 5, 30, 1)],
    ),
    ScenarioTemplate(
        id="epidemic_surge",
        name="Epidemic demand surge",
        description="A respiratory wave lifts demand for antibiotics and antivirals nationally.",
        category="Demand",
        headline="Fill rate, lost sales, allocation fairness",
        params=[
            _slider("uplift_pct", "Demand uplift", "%", 150, 50, 400, 10),
            _slider("duration_weeks", "Duration", "weeks", 6, 2, 16, 1),
        ],
    ),
    ScenarioTemplate(
        id="supplier_failure",
        name="Supplier or contract-manufacturer failure",
        description="A packaging (vial) supplier fire; two product lines lose their pack source.",
        category="Supply & ingredients",
        headline="Products stopping, days to qualify backup, revenue at risk",
        params=[
            _slider("capacity_lost_pct", "Capacity lost", "%", 100, 30, 100, 5),
            _slider("duration_days", "Duration", "days", 60, 14, 180, 1),
        ],
    ),
    ScenarioTemplate(
        id="cold_chain_failure",
        name="Cold-chain failure",
        description="Heatwave and power cuts at the Chennai cold store.",
        category="Climate",
        headline="Value of cold-chain stock exposed and lost",
        params=[
            _slider("power_cut_hours", "Power-cut hours/day", "hours", 6, 0, 16, 1),
            _slider("heatwave_days", "Heatwave", "days", 7, 3, 21, 1),
        ],
    ),
    ScenarioTemplate(
        id="cyber_outage",
        name="Cyberattack / ERP outage",
        description="Ransomware stops order processing at the Kolkata warehouse.",
        category="Operations",
        headline="Orders delayed, revenue at risk, recovery order",
        params=[
            _slider("outage_days", "Outage", "days", 5, 1, 21, 1),
            _slider("manual_capacity_pct", "Manual capacity", "%", 30, 0, 60, 5),
        ],
    ),
    ScenarioTemplate(
        id="tender_feasibility",
        name="Tender bid feasibility",
        description="A state medical-supply tender for essential SKUs at fixed prices with penalties.",
        category="Market",
        headline="Go/no-go, tender margin, penalty risk",
        params=[
            _slider("tender_volume_index", "Tender volume", "index", 1.4, 1.0, 3.0, 0.1),
            _slider("price_discount_pct", "Price discount", "%", 18, 0, 40, 1),
            _slider("penalty_pct", "Penalty", "%", 10, 0, 30, 1, live=False),
        ],
    ),
    ScenarioTemplate(
        id="prebuild_decision",
        name="Inventory pre-build before a known event",
        description="Build stock before the monsoon. The decision is how many weeks of cover to add.",
        category="Operations",
        headline="Working capital and holding cost versus loss avoided",
        params=[
            _slider("prebuild_weeks", "Pre-build cover", "weeks", 4, 0, 12, 1),
            ParamSpec(
                name="event",
                label="Event",
                unit="choice",
                default="monsoon",
                choices=["monsoon", "tariff"],
            ),
        ],
    ),
    ScenarioTemplate(
        id="network_stress_test",
        name="Whole-network stress test",
        description="Knock out every node in turn and compare time-to-survive with time-to-recover.",
        category="Network",
        headline="Ranked exposure, TTS versus TTR, resilience score",
        params=[_slider("outage_days", "Outage length", "days", 14, 7, 60, 1)],
    ),
)

PILOT: tuple[ScenarioTemplate, ...] = tuple(
    ScenarioTemplate(
        id=item[0],
        name=item[1],
        description="Coming in the pilot. Not simulated in this demo.",
        category=item[2],
        status="coming_in_pilot",
    )
    for item in (
        ("cyclone_landfall", "Cyclone landfall", "Climate"),
        ("landslide_hill_routes", "Landslide on hill routes", "Climate"),
        ("earthquake_cluster", "Earthquake at a manufacturing cluster", "Climate"),
        ("port_shutdown", "Port shutdown or congestion", "Logistics"),
        ("air_cargo_crunch", "Air-cargo capacity crunch", "Logistics"),
        ("truckers_strike", "Truckers' strike", "Logistics"),
        ("reefer_breakdown", "Reefer breakdown mid-route", "Logistics"),
        ("fuel_spike", "Fuel price spike", "Logistics"),
        ("packaging_shortage", "Packaging material shortage", "Supply & ingredients"),
        ("supplier_insolvency", "Supplier financial distress", "Supply & ingredients"),
        ("licence_suspension", "Drug-licence suspension", "Regulatory & quality"),
        ("dpco_price_cut", "DPCO price revision", "Regulatory & quality"),
        ("fdc_ban", "Fixed-dose combination ban", "Regulatory & quality"),
        ("serialisation_mandate", "Serialisation mandate deadline", "Regulatory & quality"),
        ("gdp_halt", "GDP audit halt", "Regulatory & quality"),
        ("ndps_delay", "Narcotic quota delay", "Regulatory & quality"),
        ("tender_win_loss", "Government tender win or loss", "Demand"),
        ("hospital_expansion", "Hospital chain expansion", "Demand"),
        ("competitor_stockout", "Competitor stockout", "Demand"),
        ("festival_labour", "Festival labour shortage", "Operations"),
        ("near_expiry", "Near-expiry accumulation", "Operations"),
        ("api_plus_recall", "API shock plus alternate recall", "Compound"),
        ("user_composite", "User-built composite timeline", "Compound"),
        ("kerala_warehouse_flood", "Kerala warehouse flood", "Climate"),
        ("unregistered_source", "Alternate source not registered", "Regulatory & quality"),
        ("shortage_reporting", "Shortage-reporting trigger", "Regulatory & quality"),
        ("launch_ramp", "New product launch ramp-up", "Operations"),
        ("expiry_reallocation", "Expiry-driven reallocation", "Operations"),
        ("currency_swing", "Currency swing on imports", "Market"),
        ("network_redesign", "Network redesign", "Network"),
        ("seasonal_plan", "Seasonal plan under risk", "Demand"),
        ("customs_it_outage", "Customs IT outage at JNPT", "Logistics"),
    )
)


def templates() -> list[ScenarioTemplate]:
    return [*LIVE, *PILOT]


def template_by_id(template_id: str) -> ScenarioTemplate:
    for template in LIVE:
        if template.id == template_id:
            return template
    raise KeyError(template_id)


def default_params(template_id: str) -> dict[str, Any]:
    template = template_by_id(template_id)
    return {param.name: param.default for param in template.params}


def build_shocks(template_id: str, params: dict[str, Any], network: Network) -> list[Shock]:
    merged = default_params(template_id)
    merged.update(params)
    return BUILDERS[template_id](merged, network)
