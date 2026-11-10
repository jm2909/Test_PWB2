from collections.abc import Callable

from fastapi.testclient import TestClient

URL = "/api/v1/consents"


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401
    assert client.post(URL, json={}).status_code == 401


def test_accept_and_decline_dated_choice(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("asha")
    r = client.post(
        URL, headers=h, json={"purpose": "device_processing", "version": "2024-05", "status": "declined"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "declined" and body["recorded_at"] and body["purpose"] == "device_processing"
    listing = client.get(URL, headers=h).json()
    assert listing["total"] == len(listing["items"]) >= 3
    latest = {i["purpose"]: i["status"] for i in listing["latest"]}
    assert latest["device_processing"] == "declined" and latest["personalized_insights"] == "accepted"


def test_invalid_enum_422(client: TestClient, persona_headers: Callable[..., dict[str, str]]) -> None:
    h = persona_headers("asha")
    for bad in (
        {"purpose": "ads", "version": "1", "status": "accepted"},
        {"purpose": "device_processing", "version": "1", "status": "maybe"},
        {"purpose": "device_processing", "version": "x" * 33, "status": "accepted"},
    ):
        assert client.post(URL, headers=h, json=bad).status_code == 422


def test_declined_purpose_blocks_dependent_processing(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("asha")
    client.post(
        URL, headers=h, json={"purpose": "personalized_insights", "version": "1", "status": "declined"}
    )
    r = client.post("/api/v1/insights", headers=h)
    assert r.status_code == 403 and r.json()["detail"]


def test_owner_scoped(client: TestClient, persona_headers: Callable[..., dict[str, str]]) -> None:
    client.post(
        URL,
        headers=persona_headers("asha"),
        json={"purpose": "device_processing", "version": "9", "status": "accepted"},
    )
    other = client.get(URL, headers=persona_headers("rohan")).json()
    assert all(i["version"] != "9" for i in other["items"])
