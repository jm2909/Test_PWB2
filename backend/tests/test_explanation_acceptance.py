from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

URL = "/api/v1/metric-explanations"


def test_requires_auth(client: TestClient) -> None:
    assert client.post(URL, json={"metric_type": "weight", "period_days": 30}).status_code == 401


def test_weight_explanation(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("asha"), json={"metric_type": "weight", "period_days": 30})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "available" and body["direction"] == "down"
    assert "1.7 kg" in body["explanation"] and body["reading_count"] > 3 and body["source_label"]


def test_body_fat_unavailable_without_guidance(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("asha"), json={"metric_type": "body_fat", "period_days": 30})
    assert r.status_code == 200
    assert r.json()["status"] == "unavailable"
    assert "rather not guess" in r.json()["explanation"]


def test_validation(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    h = persona_headers("asha")
    assert client.post(URL, headers=h, json={"metric_type": "weight", "period_days": 3}).status_code == 422
    assert client.post(URL, headers=h, json={"metric_type": "weight", "period_days": 400}).status_code == 422
    assert client.post(URL, headers=h, json={"metric_type": "mood", "period_days": 30}).status_code == 422


def test_meena_insufficient(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("meena"), json={"metric_type": "weight", "period_days": 30})
    assert r.json()["status"] == "insufficient_history"
