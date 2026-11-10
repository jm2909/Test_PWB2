from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import login
from tests.factories import SEED_PASSWORD

URL = "/api/v1/onboarding"
BODY = {"profile": {"display_name": "Rohan"}, "goal_intent": "build_strength", "device_next_step": "wearable"}


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401
    assert client.put(URL, json=BODY).status_code == 401


def test_seeded_complete_user(auth_client: TestClient) -> None:
    body = auth_client.get(URL).json()
    assert body["status"] == "complete" and body["remaining_steps"] == []
    assert set(body) == {"profile", "goal_intent", "device_next_step", "status", "remaining_steps"}


def test_save_and_resume_after_new_login(client: TestClient, seeded: Session) -> None:
    headers = login(client, "rohan.iyer@example.com", SEED_PASSWORD)
    before = client.get(URL, headers=headers).json()
    assert before["status"] == "in_progress" and before["remaining_steps"] == ["consent"]
    saved = client.put(URL, headers=headers, json=BODY)
    assert saved.status_code == 200 and saved.json()["remaining_steps"] == ["consent"]
    client.delete("/api/v1/auth/sessions/current", headers=headers)
    again = login(client, "rohan.iyer@example.com", SEED_PASSWORD)
    resumed = client.get(URL, headers=again).json()
    assert resumed["goal_intent"] == "build_strength" and resumed["device_next_step"] == "wearable"


def test_partial_save_identifies_remaining(client: TestClient, seeded: Session) -> None:
    headers = login(client, "rohan.iyer@example.com", SEED_PASSWORD)
    body = {"profile": {}, "goal_intent": "", "device_next_step": "later"}
    result = client.put(URL, headers=headers, json=body).json()
    assert result["status"] == "in_progress" and result["remaining_steps"] == ["profile", "goal", "consent"]


def test_invalid_payload_422(auth_client: TestClient) -> None:
    assert auth_client.put(URL, json={**BODY, "device_next_step": "fridge"}).status_code == 422
    assert auth_client.put(URL, json={**BODY, "goal_intent": "x" * 81}).status_code == 422
    assert auth_client.put(URL, json={"profile": {}}).status_code == 422
