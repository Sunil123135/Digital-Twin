"""API contract tests. They do not pre-compute the full Monte Carlo cache."""

from fastapi.testclient import TestClient
from pharmatwin.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_templates_include_pilot_cards() -> None:
    response = client.get("/api/scenarios/templates")
    body = response.json()
    live = [item for item in body["templates"] if item["status"] == "live"]
    pilot = [item for item in body["templates"] if item["status"] == "coming_in_pilot"]
    assert len(live) == 13
    assert len(pilot) == 32


def test_csv_template() -> None:
    response = client.get("/api/upload/templates/sites.csv")
    assert response.status_code == 200
    assert "code" in response.text


def test_upload_validation() -> None:
    response = client.post("/api/upload/sites", content=b"code,name\nX,Y\n", headers={"content-type": "text/csv"})
    assert response.status_code == 200
    assert response.json()["valid"] is False
