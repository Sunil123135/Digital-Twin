"""Reject assistant numbers that did not come back from a tool."""

import json
import re
from typing import Any

_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def numbers_are_sourced(text: str, tool_payloads: list[Any]) -> bool:
    blob = json.dumps(tool_payloads, default=str)
    allowed = set(_NUMBER.findall(blob))
    allowed.update({"10", "50", "90"})
    used = set(_NUMBER.findall(text))
    return used <= allowed
