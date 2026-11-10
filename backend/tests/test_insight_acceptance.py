"""FR-017 acceptance criteria."""

from collections.abc import Callable

from fastapi.testclient import TestClient

from app.services.safety import contains_diagnostic_language

URL = "/api/v1/insights"


def test_sufficient_data_cites_trend_and_implication(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    body = client.post(URL, headers=persona_headers("asha")).json()
    assert body["status"] == "published"
    assert body["observed_trend"] and body["wellness_implication"]
    assert not contains_diagnostic_language(body["observed_trend"] + body["wellness_implication"])
    listed = client.get(URL, headers=persona_headers("asha")).json()
    assert listed["total"] >= 2  # seeded published insight + the new one
    assert any(i["status"] == "published" for i in listed["items"])


def test_insufficient_data_shows_no_conclusion(
    client: TestClient, persona_headers: Callable[[str], dict[str, str]]
) -> None:
    body = client.post(URL, headers=persona_headers("meena")).json()
    assert body["status"] == "suppressed"
    assert body["observed_trend"] is None
    assert body["wellness_implication"] is None
    assert body["suppression_reason"]
