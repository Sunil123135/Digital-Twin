"""Engine tests: determinism, calibration, and monotonic shocks."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st
from pharmatwin.engine.finance import money_and_service
from pharmatwin.engine.network import build_network
from pharmatwin.engine.prescribe import prescribe
from pharmatwin.engine.shocks import LIVE, PILOT, build_shocks, default_params
from pharmatwin.engine.simulate import simulate
from pharmatwin.engine.stress import stress_test


def test_network_counts_and_revenue() -> None:
    network = build_network(42)
    assert len(network.products) == 300
    assert len(network.families) == 60
    assert sum(1 for site in network.sites if site.type == "stockist") == 40
    assert sum(1 for site in network.sites if site.type == "hospital") == 25
    assert sum(1 for site in network.sites if site.is_critical_care) == 8
    assert network.single_source_china_apis == 2
    assert abs(network.annual_revenue - 2400 * 10_000_000) / (2400 * 10_000_000) < 0.02
    again = build_network(42)
    assert np.allclose(network.base_daily, again.base_daily)


def test_same_seed_same_fill() -> None:
    network = build_network(42)
    shocks = build_shocks("monsoon_dengue", default_params("monsoon_dengue"), network)
    first = simulate(network, shocks, seed=42, runs=12, horizon=20)
    second = simulate(network, shocks, seed=42, runs=12, horizon=20)
    assert np.allclose(first["fill_rate"], second["fill_rate"])


def test_longer_flood_does_not_improve_fill() -> None:
    network = build_network(42)
    short = build_shocks("monsoon_dengue", {"flood_days": 5, "dengue_uplift_pct": 80}, network)
    long = build_shocks("monsoon_dengue", {"flood_days": 25, "dengue_uplift_pct": 80}, network)
    short_fill = float(np.median(simulate(network, short, seed=7, runs=10, horizon=30)["fill_rate"]))
    long_fill = float(np.median(simulate(network, long, seed=7, runs=10, horizon=30)["fill_rate"]))
    assert long_fill <= short_fill + 1e-6


def test_higher_tariff_does_not_improve_margin() -> None:
    network = build_network(42)
    low = build_shocks("tariff_bom", {"api_tariff_pct": 5, "us_tariff_pct": 0, "effective_day": 1}, network)
    high = build_shocks("tariff_bom", {"api_tariff_pct": 80, "us_tariff_pct": 40, "effective_day": 1}, network)
    low_raw = simulate(network, low, seed=3, runs=8, horizon=20)
    high_raw = simulate(network, high, seed=3, runs=8, horizon=20)
    low_margin = money_and_service(network, low_raw)["money"]["margin_impact"]["p50"]  # type: ignore[index]
    high_margin = money_and_service(network, high_raw)["money"]["margin_impact"]["p50"]  # type: ignore[index]
    assert high_margin >= low_margin - 1.0


def test_every_live_template_builds() -> None:
    network = build_network(42)
    assert len(LIVE) == 13
    assert len(PILOT) == 32
    for template in LIVE:
        shocks = build_shocks(template.id, default_params(template.id), network)
        assert isinstance(shocks, list)


def test_prescription_is_feasible() -> None:
    network = build_network(42)
    shocks = build_shocks("cyber_outage", default_params("cyber_outage"), network)
    result = prescribe(network, shocks, seed=1, runs=6, horizon=15)
    assert len(result["plans"]) == 3
    assert sum(1 for plan in result["plans"] if plan["recommended"]) == 1
    for plan in result["plans"]:
        assert plan["cost"] >= 0
        for value in plan["levers"].values():
            assert 0 <= value <= 8


def test_finance_percentiles_ordered() -> None:
    network = build_network(42)
    shocks = build_shocks("epidemic_surge", default_params("epidemic_surge"), network)
    summary = money_and_service(network, simulate(network, shocks, seed=2, runs=10, horizon=20))
    money = summary["money"]["revenue_at_risk"]  # type: ignore[index]
    assert money["p10"] <= money["p50"] <= money["p90"]


def test_stress_score_band() -> None:
    network = build_network(42)
    report = stress_test(network, outage_days=14, seed=42)
    score = report["resilience"]["score"]
    assert 40 <= score <= 85
    assert report["nodes"]


@settings(max_examples=3, deadline=None)
@given(st.integers(min_value=4, max_value=20))
def test_duration_monotonic_property(days: int) -> None:
    network = build_network(42)
    shorter = build_shocks("shipping_disruption", {"extra_days": days}, network)
    longer = build_shocks("shipping_disruption", {"extra_days": days + 8}, network)
    short_fill = float(np.median(simulate(network, shorter, seed=11, runs=6, horizon=24)["fill_rate"]))
    long_fill = float(np.median(simulate(network, longer, seed=11, runs=6, horizon=24)["fill_rate"]))
    assert long_fill <= short_fill + 1e-6
