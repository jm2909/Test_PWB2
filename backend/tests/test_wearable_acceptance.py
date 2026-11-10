from collections.abc import Callable

from fastapi.testclient import TestClient

URL = "/api/v1/device-connections"


def body(provider: str, code: str | None = None) -> dict[str, str | None]:
    return {"provider": provider, "connection_mode": "authorize", "authorization_code": code}


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401


def test_authorize_shows_connection_and_categories(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    r = client.post(URL, headers=persona_headers("asha"), json=body("wearable_platform_b", "ok"))
    assert r.status_code == 201
    b = r.json()
    assert b["status"] == "connected" and b["permitted_categories"] == [
        "sleep",
        "heart_rate",
        "activity",
        "weight",
    ]


def test_revoked_and_failed_are_actionable(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("asha")
    r = client.post(URL, headers=h, json=body("wearable_platform_a", "revoke")).json()
    assert r["status"] == "revoked" and r["recovery_action"] == "Reconnect" and r["failure_reason"]
    f = client.post(URL, headers=h, json=body("wearable_platform_b", "fail")).json()
    assert f["status"] == "failed" and f["recovery_action"] and f["failure_reason"]
    ok = client.post(URL, headers=h, json=body("wearable_platform_a", "ok")).json()
    assert ok["id"] == r["id"] and ok["status"] == "connected"


def test_list_seeded_connections(client: TestClient, persona_headers: Callable[..., dict[str, str]]) -> None:
    data = client.get(URL, headers=persona_headers("asha")).json()
    assert data["total"] == len(data["items"])
    by = {i["provider"]: i for i in data["items"]}
    assert by["sapphire_scale"]["status"] == "connected"
    assert by["wearable_platform_a"]["status"] == "connected"
    assert by["wearable_platform_b"]["failure_reason"] == "The provider did not respond."
    assert by["wearable_platform_c"]["status"] == "revoked"
    assert by["wearable_platform_c"]["failure_reason"] == "Access was revoked at the provider."
    assert any(i["status"] == "action_required" for i in data["items"])


def test_list_is_owner_scoped(client: TestClient, persona_headers: Callable[..., dict[str, str]]) -> None:
    data = client.get(URL, headers=persona_headers("meena")).json()
    providers = {i["provider"] for i in data["items"]}
    assert "wearable_platform_b" not in providers and "wearable_platform_a" in providers
