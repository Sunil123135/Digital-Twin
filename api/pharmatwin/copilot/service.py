"""OpenRouter copilot. Model ids come from the environment. Tests inject a fake client."""

import json
from collections.abc import Iterator
from typing import Any, Protocol

from openai import OpenAI
from sqlalchemy.orm import Session

from pharmatwin.config import Settings, get_settings
from pharmatwin.copilot.guard import numbers_are_sourced
from pharmatwin.engine.network import build_network
from pharmatwin.engine.shocks import default_params, template_by_id, templates
from pharmatwin.models import RunRow, ScenarioRow
from pharmatwin.runs.keys import cache_key
from pharmatwin.seed.load import store_result

SYSTEM = """You are the PharmaTwin copilot for a CFO and a Head of Supply Chain.
Only state numbers returned by tools, and cite the run id as "Source: run R-<id>".
Use Indian rupee units when the tool result already contains them.
Answer in two short parts: Money, then Service.
If a tool did not return a fact, say "I don't have that in the model."
Never claim an action was executed in an ERP.
create_scenario only proposes a scenario. Do not say it has been run.
"""

TOOLS = [
    {"type": "function", "function": {"name": "list_scenarios", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "get_run_summary",
            "parameters": {
                "type": "object",
                "properties": {"run_id": {"type": "integer"}},
                "required": ["run_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_scenario",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "string"},
                    "params": {"type": "object"},
                },
                "required": ["template_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_scenario",
            "parameters": {
                "type": "object",
                "properties": {"scenario_id": {"type": "integer"}},
                "required": ["scenario_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_plans",
            "parameters": {
                "type": "object",
                "properties": {"scenario_id": {"type": "integer"}},
                "required": ["scenario_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_kpi",
            "parameters": {
                "type": "object",
                "properties": {"run_id": {"type": "integer"}, "kpi": {"type": "string"}},
                "required": ["run_id", "kpi"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_site",
            "parameters": {
                "type": "object",
                "properties": {"site_id": {"type": "integer"}},
                "required": ["site_id"],
            },
        },
    },
]


class ChatClient(Protocol):
    def complete(self, messages: list[dict[str, Any]]) -> dict[str, Any]: ...


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            timeout=30,
        )

    def complete(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        if self.settings.fallback_models:
            extra["models"] = self.settings.fallback_models
        response = self.client.chat.completions.create(
            model=self.settings.openrouter_model,
            messages=messages,  # type: ignore[arg-type]
            tools=TOOLS,  # type: ignore[arg-type]
            max_tokens=700,
            extra_headers={"HTTP-Referer": self.settings.app_url, "X-Title": "PharmaTwin"},
            extra_body=extra or None,
        )
        choice = response.choices[0].message
        usage = response.usage
        return {
            "content": choice.content or "",
            "tool_calls": [
                {"name": call.function.name, "arguments": call.function.arguments}
                for call in (choice.tool_calls or [])
            ],
            "usage": {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
                "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
            },
        }


def _tool(session: Session, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    if name == "list_scenarios":
        return {"scenarios": [{"id": item.id, "name": item.name, "status": item.status} for item in templates()]}
    if name == "get_run_summary":
        run = session.get(RunRow, int(arguments["run_id"]))
        if run is None or not run.result:
            return {"error": "run not found"}
        result = run.result
        baseline = result.get("baseline", result)
        return {"run_id": run.id, "status": run.status, "baseline": baseline, "source": f"R-{run.id:04d}"}
    if name == "create_scenario":
        template = template_by_id(str(arguments["template_id"]))
        params = default_params(template.id)
        params.update(arguments.get("params") or {})
        return {"proposal": {"template_id": template.id, "name": template.name, "params": params}}
    if name == "get_site":
        network = build_network(settings.sim_seed)
        site = network.sites[int(arguments["site_id"])]
        return {"site_id": site.id, "name": site.name, "type": site.type, "region": site.region}
    if name == "compare_plans":
        from pharmatwin.models import PlanRow

        plans = session.query(PlanRow).filter_by(scenario_id=int(arguments["scenario_id"])).all()
        return {
            "plans": [
                {"kind": plan.kind, "cost": plan.cost, "recommended": plan.recommended, "roi": plan.summary}
                for plan in plans
            ]
        }
    if name == "explain_kpi":
        run = session.get(RunRow, int(arguments["run_id"]))
        if run is None or not run.result:
            return {"error": "run not found"}
        return {
            "run_id": run.id,
            "kpi": arguments.get("kpi"),
            "assumptions": run.result.get("assumptions", {}),
            "source": f"R-{run.id:04d}",
        }
    if name == "run_scenario":
        return {"accepted": False, "reason": "The user must confirm the run in the product UI."}
    return {"error": f"unknown tool {name}"}


def iter_chat(
    session: Session,
    messages: list[dict[str, str]],
    client: ChatClient | None = None,
) -> Iterator[dict[str, Any]]:
    settings = get_settings()
    if client is None and (not settings.openrouter_api_key or not settings.openrouter_model):
        yield {
            "event": "error",
            "data": {"message": "Copilot is off. Add an OpenRouter key in .env to enable it."},
        }
        return
    chat = client or OpenRouterClient(settings)
    transcript: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM}, *messages]
    payloads: list[Any] = []
    proposal: dict[str, Any] | None = None
    for _ in range(6):
        result = chat.complete(transcript)
        print(json.dumps({"copilot_usage": result.get("usage", {})}))
        if not result["tool_calls"]:
            text = str(result["content"])
            if text and not numbers_are_sourced(text, payloads):
                text = "I don't have that in the model. I can only quote figures a tool returned."
            yield {"event": "message_delta", "data": {"text": text}}
            if proposal:
                yield {"event": "scenario_proposal", "data": proposal}
            yield {"event": "done", "data": {}}
            return
        for call in result["tool_calls"]:
            if len(payloads) >= 6:
                break
            args = json.loads(call["arguments"] or "{}")
            yield {"event": "tool_call", "data": {"name": call["name"], "arguments": args}}
            payload = _tool(session, call["name"], args)
            payloads.append(payload)
            yield {"event": "tool_result", "data": payload}
            if "proposal" in payload:
                proposal = payload["proposal"]
                yield {"event": "scenario_proposal", "data": proposal}
            transcript.append({"role": "assistant", "content": json.dumps(payload)})
    yield {"event": "done", "data": {}}


def confirm_proposal(session: Session, template_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """Store a scenario the user accepted. Nothing runs until this is called from the UI."""
    settings = get_settings()
    network = build_network(settings.sim_seed)
    template = template_by_id(template_id)
    merged = default_params(template.id)
    merged.update(params)
    key = cache_key(
        template.id,
        merged,
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
        params=merged,
        payload={"kind": "pending"},
        seed=settings.sim_seed,
        runs=settings.sim_runs,
        network_version=network.version,
        horizon=settings.sim_horizon_days,
    )
    session.commit()
    return {"scenario_id": scenario_id, "cached": False}
