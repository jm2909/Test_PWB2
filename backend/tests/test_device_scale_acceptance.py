from collections.abc import Callable

from fastapi.testclient import TestClient

URL = "/api/v1/device-connections"
PAIR = {"provider": "sapphire_scale", "connection_mode": "pair", "authorization_code": "ok"}


def test_requires_auth(client: TestClient) -> None:
    assert client.post(URL, json=PAIR).status_code == 401


def test_pairing_associates_device(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("asha"), json=PAIR)
    assert r.status_code == 201
    b = r.json()
    assert b["status"] == "connected" and b["permitted_categories"] == ["weight", "body_fat"]
    assert b["failure_reason"] is None and b["id"]
    assert "last_sync_summary" in b


def test_pairing_failure_shows_state_and_recovery(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("asha"), json={**PAIR, "authorization_code": "fail"})
    assert r.status_code == 201
    b = r.json()
    assert b["status"] == "failed" and b["recovery_action"] == "Try again" and b["failure_reason"]
    again = client.post(URL, headers=persona_headers("asha"), json=PAIR).json()
    assert again["id"] == b["id"] and again["status"] == "connected"


def test_declined_or_missing_consent_403(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    for persona in ("meena", "rohan"):
        r = client.post(URL, headers=persona_headers(persona), json=PAIR)
        assert r.status_code == 403 and r.json()["detail"]


def test_unsupported_provider_or_mode_422(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("asha")
    assert client.post(URL, headers=h, json={**PAIR, "provider": "fitbit"}).status_code == 422
    assert client.post(URL, headers=h, json={**PAIR, "connection_mode": "authorize"}).status_code == 422
    assert client.post(URL, headers=h, json={**PAIR, "provider": "wearable_platform_a"}).status_code == 422
