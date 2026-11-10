from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

URL = "/api/v1/deviation-events"


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401


def test_asha_has_two_events(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    r = client.get(URL, headers=persona_headers("asha"))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2 and len(body["items"]) == 2
    item = body["items"][0]
    assert {"id", "criterion_code", "trend_name", "created_at", "wellness_reading_id"} <= set(item)
    assert {i["criterion_code"] for i in body["items"]} == {"rhr_rise_14d", "rhr_sustained_14d"}


def test_meena_none_and_pagination(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    assert client.get(URL, headers=persona_headers("meena")).json() == {"items": [], "total": 0}
    page = client.get(URL, headers=persona_headers("asha"), params={"limit": 1, "offset": 1}).json()
    assert page["total"] == 2 and len(page["items"]) == 1
    assert client.get(URL, headers=persona_headers("asha"), params={"limit": 0}).status_code == 422
