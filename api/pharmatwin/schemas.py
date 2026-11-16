"""API models. Field names here are the contract for the TypeScript client."""

from typing import Any

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    service: str = "pharmatwin"


class ScenarioCreate(BaseModel):
    template_id: str
    params: dict[str, Any] = Field(default_factory=dict)


class RunCreate(BaseModel):
    scenario_id: int
    runs: int | None = None
    seed: int | None = None


class ApprovalCreate(BaseModel):
    plan_id: int
    requested_by: str = "demo"


class Decision(BaseModel):
    status: str
    approver: str = "demo"
    reason: str


class CopilotMessage(BaseModel):
    role: str
    content: str


class CopilotRequest(BaseModel):
    messages: list[CopilotMessage]
    confirm_scenario_id: int | None = None
