"""Deterministic synthetic network. seed=42 is the demo baseline."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from pharmatwin.engine.catalog import (
    ANCHORS,
    ANNUAL_REVENUE_INR,
    CHINA_CLASSES,
    CLASSES,
    COVER_DAYS,
    HOSPITAL_CHAINS,
    NETWORK_VERSION,
    REGION_DEPOT,
    REGION_SHARE,
    STOCKIST_CITIES,
)

RECOVERY = {
    "plant": 45,
    "supplier_site": 60,
    "port": 10,
    "cold_store": 14,
    "cnf": 14,
    "dc": 21,
    "stockist": 10,
    "hospital": 7,
}


@dataclass
class Site:
    id: int
    code: str
    name: str
    type: str
    lat: float
    lon: float
    region: str
    state: str
    storage_classes: tuple[str, ...]
    drug_licence_no: str
    licence_expiry: str
    approved_markets: tuple[str, ...]
    throughput_capacity_units_day: float
    recovery_days: int
    is_critical_care: bool
    supplier_id: int | None = None


@dataclass
class Lane:
    id: int
    from_site: int
    to_site: int
    mode: str
    lead_time_mean_days: float
    lead_time_sd_days: float
    cost_per_unit: float
    reefer: bool
    is_alternate: bool


@dataclass
class Supplier:
    id: int
    name: str
    country: str
    tier: int
    approved_markets: tuple[str, ...]
    qualification_lead_days: int
    capacity_units_day: float
    risk_score: float
    site_id: int
    single_source: bool


@dataclass
class ApiIng:
    id: int
    name: str


@dataclass
class Product:
    id: int
    sku: str
    name: str
    molecule: str
    api_id: int
    family_id: int
    therapeutic_class: str
    dosage_form: str
    schedule: str
    storage_class: str
    shelf_life_days: int
    essential: bool
    standard_cost: float
    selling_price: float
    price_cap: float | None


@dataclass
class Family:
    id: int
    therapeutic_class: str
    storage_class: str
    essential: bool
    schedule_x: bool
    china_dependent: bool
    api_id: int
    standard_cost: float
    selling_price: float
    price_cap: float | None
    shelf_life_days: int


@dataclass
class Network:
    sites: tuple[Site, ...]
    lanes: tuple[Lane, ...]
    families: tuple[Family, ...]
    products: tuple[Product, ...]
    suppliers: tuple[Supplier, ...]
    apis: tuple[ApiIng, ...]
    supplier_api: tuple[tuple[int, int, float], ...]
    depot_site_ids: NDArray[np.int64]
    customer_site_ids: NDArray[np.int64]
    customer_is_critical: NDArray[np.bool_]
    customer_is_hospital: NDArray[np.bool_]
    customer_depot: NDArray[np.int64]
    customer_region_share_index: NDArray[np.int64]
    base_daily: NDArray[np.float64]
    seasonality: NDArray[np.float64]
    stock_depot: NDArray[np.float64]
    stock_customer: NDArray[np.float64]
    supply_daily: NDArray[np.float64]
    family_cost: NDArray[np.float64]
    family_price: NDArray[np.float64]
    family_shelf: NDArray[np.int64]
    family_cold: NDArray[np.bool_]
    family_essential: NDArray[np.bool_]
    family_china: NDArray[np.bool_]
    family_weight: NDArray[np.float64]
    demand_cv: NDArray[np.float64]
    plant_share: dict[str, float]
    us_export_share: float
    version: str
    annual_revenue: float
    single_source_china_apis: int

    def site_by_code(self, code: str) -> Site:
        for site in self.sites:
            if site.code == code:
                return site
        raise KeyError(code)


def _storage_for(index: int, class_name: str) -> str:
    if class_name == "vaccine":
        return "frozen" if index % 5 == 0 else "cold"
    if class_name in {"oncology", "diabetic"} and index % 4 == 0:
        return "cold"
    return "ambient"


def build_network(seed: int = 42) -> Network:
    """Build the demo network. The same seed always returns the same object."""
    rng = np.random.default_rng(seed)
    sites: list[Site] = []
    for code, name, kind, lat, lon, region, state in ANCHORS:
        markets: tuple[str, ...] = ("IN", "US", "ROW") if code == "PLT-BAD" else ("IN", "ROW")
        if kind in {"dc", "plant", "cold_store"}:
            storage_classes = ("ambient", "cold", "frozen")
        else:
            storage_classes = ("ambient", "cold")
        if code == "DC-CHE":
            storage_classes = ("ambient", "cold", "frozen")
        sites.append(
            Site(
                id=len(sites),
                code=str(code),
                name=str(name),
                type=str(kind),
                lat=float(str(lat)),
                lon=float(str(lon)),
                region=str(region),
                state=str(state),
                storage_classes=storage_classes,
                drug_licence_no=f"DL-{1000 + len(sites)}",
                licence_expiry="2028-03-31",
                approved_markets=markets,
                throughput_capacity_units_day=2_000_000.0 if kind in {"plant", "dc"} else 400_000.0,
                recovery_days=RECOVERY[str(kind)],
                is_critical_care=False,
            )
        )

    countries = (["CN"] * 6) + (["IN"] * 4) + (["EU"] * 2) + (["IN"] * 3)
    suppliers: list[Supplier] = []
    for index, country in enumerate(countries):
        packaging = index >= 12
        code = f"{'PKG' if packaging else 'API'}-{index:02d}"
        lat = 31.2 + (index % 5) * 1.4 if country == "CN" else 19.0 + index * 0.4
        lon = 121.5 if country == "CN" else (8.5 if country == "EU" else 77.0 + index)
        site = Site(
            id=len(sites),
            code=code,
            name=f"{'Vial' if packaging else 'Ingredient'} source {index + 1} ({country})",
            type="supplier_site",
            lat=lat,
            lon=lon,
            region="Import",
            state=country,
            storage_classes=("ambient", "cold"),
            drug_licence_no=f"MFG-{2000 + index}",
            licence_expiry="2027-12-31",
            approved_markets=("IN", "US", "ROW") if country != "CN" else ("IN", "ROW"),
            throughput_capacity_units_day=500_000.0,
            recovery_days=60,
            is_critical_care=False,
            supplier_id=index,
        )
        sites.append(site)
        suppliers.append(
            Supplier(
                id=index,
                name=site.name,
                country=country,
                tier=1 if not packaging else 2,
                approved_markets=site.approved_markets,
                qualification_lead_days=120 if country == "CN" else 75,
                capacity_units_day=500_000.0,
                risk_score=0.72 if country == "CN" else 0.35,
                site_id=site.id,
                single_source=index in {0, 1} or index == 12,
            )
        )

    for index in range(40):
        region, state, lat, lon = STOCKIST_CITIES[index % len(STOCKIST_CITIES)]
        jitter = rng.normal(0, 0.15, size=2)
        sites.append(
            Site(
                id=len(sites),
                code=f"STK-{index:02d}",
                name=f"{state} stockist {index + 1}",
                type="stockist",
                lat=lat + float(jitter[0]),
                lon=lon + float(jitter[1]),
                region=region,
                state=state,
                storage_classes=("ambient", "cold"),
                drug_licence_no=f"DL-S-{3000 + index}",
                licence_expiry="2027-06-30",
                approved_markets=("IN",),
                throughput_capacity_units_day=50_000.0,
                recovery_days=10,
                is_critical_care=False,
            )
        )

    critical_ids: set[int] = set()
    for index in range(25):
        region, state, lat, lon = STOCKIST_CITIES[index % len(STOCKIST_CITIES)]
        chain = HOSPITAL_CHAINS[index % 3]
        critical = index < 8
        site = Site(
            id=len(sites),
            code=f"HOS-{index:02d}",
            name=f"{chain} {state} {index + 1}",
            type="hospital",
            lat=lat + float(rng.normal(0, 0.08)),
            lon=lon + float(rng.normal(0, 0.08)),
            region=region,
            state=state,
            storage_classes=("ambient", "cold"),
            drug_licence_no=f"HSP-{4000 + index}",
            licence_expiry="2028-01-31",
            approved_markets=("IN",),
            throughput_capacity_units_day=8_000.0,
            recovery_days=7,
            is_critical_care=critical,
        )
        if critical:
            critical_ids.add(site.id)
        sites.append(site)

    families: list[Family] = []
    for class_name in CLASSES:
        for storage in ("ambient", "cold", "frozen"):
            for essential in (True, False):
                china = class_name in CHINA_CLASSES and storage != "frozen"
                shelf = 180 if storage != "ambient" else 720
                cost = float(rng.uniform(8, 1800 if class_name != "oncology" else 4000))
                multiple = float(rng.uniform(1.3, 2.5))
                price = cost * multiple
                cap = price * 0.92 if essential else None
                if cap is not None:
                    price = min(price, cap)
                if not china:
                    api_id = CLASSES.index(class_name)
                elif class_name in {"antipyretic", "antibiotic"}:
                    api_id = 0
                elif class_name == "cardiac":
                    api_id = 1
                else:
                    api_id = 2 + (CLASSES.index(class_name) % 6)
                if class_name == "antipyretic":
                    api_id = 0
                elif class_name == "cardiac":
                    api_id = 1
                families.append(
                    Family(
                        id=len(families),
                        therapeutic_class=class_name,
                        storage_class=storage,
                        essential=essential,
                        schedule_x=False,
                        china_dependent=china,
                        api_id=int(api_id),
                        standard_cost=cost,
                        selling_price=price,
                        price_cap=cap,
                        shelf_life_days=shelf,
                    )
                )

    weight = np.ones(len(families), dtype=np.float64)
    for family in families:
        if family.storage_class == "frozen" and family.therapeutic_class != "vaccine":
            weight[family.id] = 0.05
        elif family.storage_class == "cold":
            weight[family.id] = 0.7
        elif family.china_dependent:
            weight[family.id] = 1.6
        else:
            weight[family.id] = 1.0
    weight /= weight.sum()

    products: list[Product] = []
    schedule_x_target = 15
    for index in range(300):
        family = families[index % len(families)]
        schedule = "X" if index < schedule_x_target else ("H" if family.essential else "none")
        sku_storage = family.storage_class
        if index >= schedule_x_target:
            sku_storage = _storage_for(index, family.therapeutic_class)
        cost = family.standard_cost * float(rng.uniform(0.85, 1.15))
        price = min(cost * float(rng.uniform(1.3, 2.5)), family.price_cap or 1e12)
        products.append(
            Product(
                id=index,
                sku=f"SKU-{index:04d}",
                name=f"{family.therapeutic_class} {sku_storage} {index + 1}",
                molecule=f"MOL-{family.therapeutic_class[:3].upper()}-{index:03d}",
                api_id=family.api_id,
                family_id=family.id,
                therapeutic_class=family.therapeutic_class,
                dosage_form="vial" if sku_storage != "ambient" else "tablet",
                schedule=schedule,
                storage_class=sku_storage,
                shelf_life_days=family.shelf_life_days,
                essential=family.essential,
                standard_cost=cost,
                selling_price=price,
                price_cap=family.price_cap,
            )
        )

    apis = tuple(ApiIng(id=i, name=f"API-{i:02d}") for i in range(12))
    supplier_api: list[tuple[int, int, float]] = []
    for api in apis:
        if api.id == 0:
            supplier_api.append((0, api.id, 1.0))
        elif api.id == 1:
            supplier_api.append((1, api.id, 1.0))
        else:
            china_suppliers = [s for s in suppliers if s.country == "CN" and not s.single_source and s.tier == 1]
            india = [s for s in suppliers if s.country == "IN" and s.tier == 1]
            eu = [s for s in suppliers if s.country == "EU"]
            picks = (china_suppliers + india + eu)[:3]
            share = 1 / len(picks)
            for supplier in picks:
                supplier_api.append((supplier.id, api.id, share))
    supplier_api.append((12, 11, 1.0))

    customers = [s for s in sites if s.type in {"stockist", "hospital"}]
    by_region: dict[str, list[Site]] = {region: [] for region in REGION_SHARE}
    for customer in customers:
        by_region[customer.region].append(customer)
    cust_share = np.zeros(len(customers), dtype=np.float64)
    id_to_pos = {site.id: pos for pos, site in enumerate(customers)}
    for region, share in REGION_SHARE.items():
        group = by_region[region]
        for site in group:
            cust_share[id_to_pos[site.id]] = share / len(group)

    family_price = np.array([f.selling_price for f in families], dtype=np.float64)
    family_weight = weight
    base_daily = np.zeros((len(customers), len(families)), dtype=np.float64)
    for c_index in range(len(customers)):
        revenue = ANNUAL_REVENUE_INR * cust_share[c_index] * family_weight
        base_daily[c_index, :] = revenue / family_price / 365.0

    seasonality = np.ones((12, len(families)), dtype=np.float64)
    for family in families:
        if family.therapeutic_class in {"antipyretic", "antibiotic", "iv_fluids"}:
            seasonality[5:9, family.id] = 1.35
        if family.therapeutic_class == "respiratory":
            seasonality[[10, 11, 0, 1], family.id] = 1.4
    seasonality /= seasonality.mean(axis=0, keepdims=True)

    code_to_site = {s.code: s for s in sites}
    depot_codes = ("DC-MUM", "DC-CHE", "DC-GAU", "DC-CCU", "CNF-DEL")
    depot_sites = [code_to_site[code] for code in depot_codes]
    depot_pos = {site.id: index for index, site in enumerate(depot_sites)}
    customer_depot = np.array(
        [depot_pos[code_to_site[REGION_DEPOT[c.region]].id] for c in customers],
        dtype=np.int64,
    )
    depot_demand = np.zeros((len(depot_sites), len(families)), dtype=np.float64)
    for c_index, depot in enumerate(customer_depot):
        depot_demand[int(depot)] += base_daily[c_index]

    stock_depot = np.zeros_like(depot_demand)
    for index, site in enumerate(depot_sites):
        cover = np.full(len(families), COVER_DAYS[site.code], dtype=np.float64)
        stock_depot[index] = depot_demand[index] * cover
    customer_cover = np.array(
        [COVER_DAYS["DC-MUM"] if c.region == "West" else 50.0 for c in customers],
        dtype=np.float64,
    )
    stock_customer = base_daily * customer_cover[:, None]

    supply_daily = base_daily.sum(axis=0) * 1.15
    lanes = _lanes(sites, depot_sites, customers)

    demand_cv = rng.uniform(0.2, 0.5, size=len(families))
    return Network(
        sites=tuple(sites),
        lanes=tuple(lanes),
        families=tuple(families),
        products=tuple(products),
        suppliers=tuple(suppliers),
        apis=apis,
        supplier_api=tuple(supplier_api),
        depot_site_ids=np.array([s.id for s in depot_sites], dtype=np.int64),
        customer_site_ids=np.array([s.id for s in customers], dtype=np.int64),
        customer_is_critical=np.array([s.is_critical_care for s in customers]),
        customer_is_hospital=np.array([s.type == "hospital" for s in customers]),
        customer_depot=customer_depot,
        customer_region_share_index=np.arange(len(customers)),
        base_daily=base_daily,
        seasonality=seasonality,
        stock_depot=stock_depot,
        stock_customer=stock_customer,
        supply_daily=supply_daily,
        family_cost=np.array([f.standard_cost for f in families]),
        family_price=family_price,
        family_shelf=np.array([f.shelf_life_days for f in families], dtype=np.int64),
        family_cold=np.array([f.storage_class != "ambient" for f in families]),
        family_essential=np.array([f.essential for f in families]),
        family_china=np.array([f.china_dependent for f in families]),
        family_weight=family_weight,
        demand_cv=demand_cv,
        plant_share={"PLT-BAD": 0.70, "PLT-SIK": 0.30},
        us_export_share=0.18,
        version=NETWORK_VERSION,
        annual_revenue=float((base_daily.sum(axis=0) * family_price).sum() * 365.0),
        single_source_china_apis=2,
    )


def _lanes(sites: list[Site], depots: list[Site], customers: list[Site]) -> list[Lane]:
    lanes: list[Lane] = []
    by_code = {s.code: s for s in sites}

    def add(frm: Site, to: Site, mode: str, lead: float, reefer: bool, alternate: bool, cost: float) -> None:
        lanes.append(
            Lane(
                id=len(lanes),
                from_site=frm.id,
                to_site=to.id,
                mode=mode,
                lead_time_mean_days=lead,
                lead_time_sd_days=max(lead * 0.15, 0.4),
                cost_per_unit=cost,
                reefer=reefer,
                is_alternate=alternate,
            )
        )

    for supplier in [s for s in sites if s.type == "supplier_site"]:
        port = by_code["PRT-JNP"] if "CN" in supplier.name or "EU" in supplier.name else by_code["PRT-CHE"]
        add(supplier, port, "sea", 18 if "CN" in supplier.name else 8, False, False, 4.0)
        add(supplier, by_code["AIR-BOM"], "air", 3, True, True, 16.0)
    for plant in (by_code["PLT-BAD"], by_code["PLT-SIK"]):
        add(by_code["PRT-JNP"], plant, "road", 4, False, False, 1.2)
        for depot in depots:
            add(plant, depot, "road", 6, True, False, 1.5)
            add(plant, depot, "air", 1, True, True, 8.0)
    for customer in customers:
        depot = next(d for d in depots if d.code == REGION_DEPOT[customer.region])
        add(depot, customer, "road", 3, True, False, 0.8)
        alternate = next(d for d in depots if d.code != depot.code and d.type == "dc")
        add(alternate, customer, "road", 5, True, True, 1.6)
    return lanes
