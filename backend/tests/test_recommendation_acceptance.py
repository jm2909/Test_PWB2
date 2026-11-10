from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

URL = "/api/v1/recommendations"


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401


def test_asha_recommendation(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    body = client.get(URL, headers=persona_headers("asha")).json()
    assert body["status"] == "available"
    assert body["action_text"] and body["reason_text"] and body["insight_id"]
    assert body["suggested_goal_type"] == "sleep_improvement"
    assert len(body["items"]) == 1


def test_meena_none(
    client: TestClient, seeded: Session, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    body = client.get(URL, headers=persona_headers("meena")).json()
    assert body["status"] == "none" and body["action_text"] is None
    assert client.get(URL, headers=persona_headers("rohan")).json()["status"] == "none"
