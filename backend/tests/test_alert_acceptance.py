from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

URL = "/api/v1/alerts"


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401


def test_asha_alerts(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.get(URL, headers=persona_headers("asha"))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    by = {i["urgency"]: i for i in body["items"]}
    assert set(by) == {"routine", "urgent_direction"}
    routine = by["routine"]
    assert routine["trend_name"] and routine["what_we_saw"] and routine["care_direction"] is None
    assert routine["recommended_next_action"] == (
        "Review your sleep and activity this week, and keep syncing your wearable."
    )
    urgent = by["urgent_direction"]
    assert "contact your doctor or a qualified health professional" in urgent["care_direction"]
    assert "local emergency number" in urgent["care_direction"]
    assert "tel:" not in r.text


def test_meena_none_and_pagination(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    assert client.get(URL, headers=persona_headers("meena")).json() == {"items": [], "total": 0}
    page = client.get(URL, headers=persona_headers("asha"), params={"limit": 1}).json()
    assert len(page["items"]) == 1 and page["total"] == 2
    assert client.get(URL, headers=persona_headers("asha"), params={"limit": 0}).status_code == 422


def test_dashboard_unread_count(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.get("/api/v1/dashboard", headers=persona_headers("asha"))
    assert r.json()["unread_alert_count"] == 2
