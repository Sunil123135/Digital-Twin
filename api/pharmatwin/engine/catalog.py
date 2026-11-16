"""Static synthetic catalogue. Names are fictional; nothing here is a real customer."""

from typing import Final

CLASSES: Final[tuple[str, ...]] = (
    "antipyretic",
    "antibiotic",
    "antiviral",
    "cardiac",
    "diabetic",
    "oncology",
    "iv_fluids",
    "vaccine",
    "respiratory",
    "gi",
)

CHINA_CLASSES: Final[frozenset[str]] = frozenset(
    {"antipyretic", "antibiotic", "antiviral", "cardiac", "diabetic", "gi"}
)

MONSOON_CLASSES: Final[tuple[str, ...]] = ("antipyretic", "antibiotic", "iv_fluids")
RESPIRATORY_CLASSES: Final[tuple[str, ...]] = ("respiratory", "antibiotic", "antiviral")

# (code, name, type, lat, lon, region, state, recovery override or None)
ANCHORS: Final[tuple[tuple[object, ...], ...]] = (
    ("PLT-BAD", "Baddi Plant", "plant", 30.9578, 76.7914, "North", "Himachal Pradesh"),
    ("PLT-SIK", "Sikkim Plant", "plant", 27.1756, 88.5336, "Northeast", "Sikkim"),
    ("PRT-JNP", "JNPT", "port", 18.9499, 72.9525, "West", "Maharashtra"),
    ("PRT-CHE", "Chennai Port", "port", 13.0810, 80.2920, "South", "Tamil Nadu"),
    ("AIR-BOM", "Mumbai Airport Cold Store", "cold_store", 19.0896, 72.8656, "West", "Maharashtra"),
    ("DC-MUM", "Bhiwandi DC", "dc", 19.2967, 73.0631, "West", "Maharashtra"),
    ("DC-CHE", "Chennai DC", "dc", 13.0827, 80.2707, "South", "Tamil Nadu"),
    ("DC-GAU", "Guwahati DC", "dc", 26.1445, 91.7362, "Northeast", "Assam"),
    ("DC-CCU", "Kolkata DC", "dc", 22.5726, 88.3639, "East", "West Bengal"),
    ("CNF-DEL", "Delhi C&F", "cnf", 28.6139, 77.2090, "North", "Delhi"),
    ("CNF-LKO", "Lucknow C&F", "cnf", 26.8467, 80.9462, "North", "Uttar Pradesh"),
    ("CNF-PUN", "Pune C&F", "cnf", 18.5204, 73.8567, "West", "Maharashtra"),
    ("CNF-HYD", "Hyderabad C&F", "cnf", 17.3850, 78.4867, "South", "Telangana"),
    ("CNF-BLR", "Bengaluru C&F", "cnf", 12.9716, 77.5946, "South", "Karnataka"),
    ("CNF-PAT", "Patna C&F", "cnf", 25.5941, 85.1376, "East", "Bihar"),
)

# Revenue share by the depot that serves the region. West is the fragile node.
REGION_DEPOT: Final[dict[str, str]] = {
    "West": "DC-MUM",
    "South": "DC-CHE",
    "East": "DC-CCU",
    "Northeast": "DC-GAU",
    "North": "CNF-DEL",
}

REGION_SHARE: Final[dict[str, float]] = {
    "West": 0.28,
    "North": 0.24,
    "South": 0.26,
    "East": 0.16,
    "Northeast": 0.06,
}

# Days of finished-goods cover. West is below Mumbai DC recovery (21) and plant recovery (45).
COVER_DAYS: Final[dict[str, float]] = {
    "DC-MUM": 14.0,
    "DC-CHE": 50.0,
    "DC-GAU": 50.0,
    "DC-CCU": 50.0,
    "CNF-DEL": 50.0,
}

STOCKIST_CITIES: Final[tuple[tuple[str, str, float, float], ...]] = (
    ("West", "Maharashtra", 19.07, 72.87),
    ("West", "Gujarat", 23.02, 72.57),
    ("West", "Goa", 15.49, 73.82),
    ("North", "Delhi", 28.61, 77.21),
    ("North", "Uttar Pradesh", 26.85, 80.95),
    ("North", "Rajasthan", 26.91, 75.79),
    ("North", "Punjab", 30.90, 75.86),
    ("South", "Tamil Nadu", 13.08, 80.27),
    ("South", "Karnataka", 12.97, 77.59),
    ("South", "Telangana", 17.39, 78.49),
    ("South", "Kerala", 9.93, 76.26),
    ("East", "West Bengal", 22.57, 88.36),
    ("East", "Bihar", 25.59, 85.14),
    ("East", "Odisha", 20.30, 85.82),
    ("Northeast", "Assam", 26.14, 91.74),
)

HOSPITAL_CHAINS: Final[tuple[str, ...]] = (
    "Northstar Hospitals",
    "Meridian Care",
    "Sutlej Health",
)

ANNUAL_REVENUE_INR: Final[float] = 2400.0 * 10_000_000.0
NETWORK_VERSION: Final[str] = "synth-42"
