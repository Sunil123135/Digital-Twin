"""CLI: python -m pharmatwin.engine.cli run monsoon_dengue"""

import argparse
import json

from pharmatwin.config import get_settings
from pharmatwin.engine.finance import money_and_service
from pharmatwin.engine.network import build_network
from pharmatwin.engine.shocks import build_shocks, default_params
from pharmatwin.engine.simulate import simulate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one PharmaTwin scenario")
    parser.add_argument("action", choices=["run"])
    parser.add_argument("template_id")
    args = parser.parse_args()
    settings = get_settings()
    network = build_network(settings.sim_seed)
    params = default_params(args.template_id)
    shocks = build_shocks(args.template_id, params, network)
    raw = simulate(
        network,
        shocks,
        seed=settings.sim_seed,
        runs=settings.sim_runs,
        horizon=settings.sim_horizon_days,
    )
    summary = money_and_service(network, raw)
    print(
        json.dumps(
            {"template": args.template_id, "money": summary["money"], "service": summary["service"]},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
