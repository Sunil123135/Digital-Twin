"""Copilot tests mock OpenRouter. They never call the network."""

from pharmatwin.copilot.guard import numbers_are_sourced
from pharmatwin.copilot.service import iter_chat


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, messages: list[dict[str, object]]) -> dict[str, object]:
        self.calls += 1
        if self.calls == 1:
            return {
                "content": "",
                "tool_calls": [{"name": "get_run_summary", "arguments": "{\"run_id\": 42}"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5},
            }
        return {
            "content": "Money: revenue at risk is 100. Service: fill rate is 0.91. Source: run R-0042.",
            "tool_calls": [],
            "usage": {"prompt_tokens": 12, "completion_tokens": 8},
        }


def test_copilot_off_without_key(monkeypatch: object) -> None:
    from pharmatwin.config import Settings

    def fake_settings() -> Settings:
        return Settings(openrouter_api_key="", openrouter_model="")

    monkeypatch.setattr("pharmatwin.copilot.service.get_settings", fake_settings)  # type: ignore[attr-defined]
    events = list(iter_chat(session=None, messages=[{"role": "user", "content": "hello"}]))  # type: ignore[arg-type]
    assert events[0]["event"] == "error"
    assert "Copilot is off" in events[0]["data"]["message"]


def test_numbers_must_come_from_tools() -> None:
    assert numbers_are_sourced("Revenue is 186.4", [{"revenue": 186.4}])
    assert not numbers_are_sourced("Revenue is 999", [{"revenue": 186.4}])


def test_mocked_tool_call_is_cited(monkeypatch: object) -> None:
    class Session:
        def get(self, model: object, ident: int) -> object:
            del model, ident

            class Run:
                id = 42
                status = "done"
                result = {
                    "baseline": {
                        "money": {"revenue_at_risk": {"p50": 100}},
                        "service": {"fill_rate": {"p50": 0.91}},
                    }
                }

            return Run()

    events = list(
        iter_chat(
            Session(),  # type: ignore[arg-type]
            [{"role": "user", "content": "What is at risk?"}],
            client=FakeClient(),  # type: ignore[arg-type]
        )
    )
    text = "".join(event["data"].get("text", "") for event in events if event["event"] == "message_delta")
    assert "Source: run R-0042" in text
    assert "999" not in text
