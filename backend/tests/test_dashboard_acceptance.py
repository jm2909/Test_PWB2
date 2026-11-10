from fastapi.testclient import TestClient


def test_dashboard_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard").status_code == 401


def test_ac1_available_data_presented_together(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert {"display_name", "last_synced_at", "signal_groups", "source_gaps", "active_goals"} <= body.keys()
    assert body["unread_alert_count"] == 2
    assert {g["key"] for g in body["signal_groups"]} >= {
        "body_composition",
        "sleep",
        "heart_rate",
        "activity",
    }
    assert len(body["active_goals"]) >= 1


def test_ac2_gap_explained_other_signals_usable(client: TestClient, persona_headers) -> None:  # type: ignore[no-untyped-def]
    response = client.get("/api/v1/dashboard", headers=persona_headers("rohan"))
    assert response.status_code == 200
    body = response.json()
    gap = next(g for g in body["source_gaps"] if g["group"] == "sleep")
    assert gap["recovery_action"] == "Check wearable connection"
    assert gap["link"]
    assert any(g["reason"] == "No goal set" for g in body["source_gaps"]) or body["active_goals"]
