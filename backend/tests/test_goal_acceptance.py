from collections.abc import Callable

from fastapi.testclient import TestClient

URL = "/api/v1/goals"


def test_requires_auth(client: TestClient) -> None:
    assert client.get(URL).status_code == 401
    assert (
        client.post(
            URL, json={"goal_type": "weight_loss", "target_value": 65, "target_unit": "kg"}
        ).status_code
        == 401
    )


def test_goal_saved_and_listed(client: TestClient, persona_headers: Callable[..., dict[str, str]]) -> None:
    h = persona_headers("rohan")
    r = client.post(
        URL, headers=h, json={"goal_type": "muscle_gain", "target_value": 75, "target_unit": "kg"}
    )
    assert r.status_code == 201
    b = r.json()
    assert b["status"] == "active" and b["goal_type"] == "muscle_gain" and b["target_value"] == 75 and b["id"]
    data = client.get(URL, headers=h).json()
    assert data["total"] == 1 and data["items"][0]["id"] == b["id"]


def test_invalid_target_422_with_guidance_and_no_goal(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("rohan")
    r = client.post(URL, headers=h, json={"goal_type": "weight_loss", "target_value": 0, "target_unit": "kg"})
    assert r.status_code == 422
    assert r.json()["detail"] == "Enter a target above 0 kg that is realistic for you, for example 65."
    assert client.get(URL, headers=h).json() == {"items": [], "total": 0}


def test_unknown_type_and_long_unit_422(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("rohan")
    assert (
        client.post(
            URL, headers=h, json={"goal_type": "x", "target_value": 5, "target_unit": "kg"}
        ).status_code
        == 422
    )
    long_unit = "k" * 25
    assert (
        client.post(
            URL, headers=h, json={"goal_type": "other_supported", "target_value": 5, "target_unit": long_unit}
        ).status_code
        == 422
    )


def test_seeded_goal_and_replacement(
    client: TestClient, persona_headers: Callable[..., dict[str, str]]
) -> None:
    h = persona_headers("asha")
    items = client.get(URL, headers=h).json()["items"]
    assert [(i["goal_type"], i["target_value"], i["target_unit"]) for i in items] == [
        ("weight_loss", 65, "kg")
    ]
    client.post(URL, headers=h, json={"goal_type": "weight_loss", "target_value": 63, "target_unit": "kg"})
    items = client.get(URL, headers=h).json()["items"]
    assert len(items) == 1 and items[0]["target_value"] == 63
    assert client.get(URL, headers=persona_headers("meena")).json()["total"] == 0
