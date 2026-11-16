"""Cache identity for a scenario. Same inputs always hit the same stored run."""

import hashlib
import json
from typing import Any


def cache_key(
    template_id: str,
    params: dict[str, Any],
    *,
    seed: int,
    runs: int,
    horizon: int,
    network_version: str,
) -> str:
    payload = {
        "template": template_id,
        "params": params,
        "seed": seed,
        "runs": runs,
        "horizon": horizon,
        "network": network_version,
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()
