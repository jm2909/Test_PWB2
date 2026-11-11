"""FR-009 connection status and FR-012 trends."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.services.freshness import effective_status

NOW = datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
WINDOW = timedelta(hours=24)


def test_connection_status_policy_never_current_without_sync():
    assert effective_status("current", None, NOW, WINDOW) == "stale"
    assert effective_status("current", NOW - timedelta(hours=1), NOW, WINDOW) == "current"
    assert effective_status("current", NOW - timedelta(hours=30), NOW, WINDOW) == "stale"
    assert effective_status("pending", None, NOW, WINDOW) == "pending"
    assert effective_status("failed", NOW, NOW, WINDOW) == "failed"


def test_connection_status_requires_token(client):
    assert client.get("/api/v1/connections").status_code == 401


def test_connection_status_lists_owner_only_with_recovery(
    client, auth_headers, factories, seeded_accounts
):
    asha, rohan = seeded_accounts["asha"], seeded_accounts["rohan"]
    now = datetime.now(UTC)
    factories.connection(asha, status="current", last_successful_sync_at=now - timedelta(hours=1))
    factories.connection(asha, status="current", last_successful_sync_at=now - timedelta(days=5))
    factories.connection(asha, status="current", last_successful_sync_at=None)
    factories.connection(asha, status="pending")
    factories.connection(asha, status="failed", source="scale")
    factories.connection(asha, status="failed", source="wearable", provider="fitband")
    factories.connection(asha, status="disconnected", source="wearable", provider="x")
    factories.connection(rohan, status="current", last_successful_sync_at=now)
    r = client.get("/api/v1/connections", headers=auth_headers("asha"))
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 6 and body["limit"] == 25 and body["offset"] == 0
    statuses = [i["status"] for i in body["items"]]
    assert statuses == ["current", "stale", "stale", "pending", "failed", "failed"]
    actions = [i["recovery_action"] for i in body["items"]]
    assert actions == [None, "retry_sync", "retry_sync", None, "contact_support", "retry"]
    assert body["items"][0]["last_successful_sync_at"] is not None
    assert body["items"][2]["last_successful_sync_at"] is None


def test_connection_status_paginates(client, auth_headers, factories, seeded_accounts):
    for _ in range(3):
        factories.connection(seeded_accounts["asha"], status="pending")
    r = client.get("/api/v1/connections?limit=2&offset=2", headers=auth_headers("asha"))
    body = r.json()
    assert body["total"] == 3 and len(body["items"]) == 1


def test_connection_status_dashboard_uses_same_policy(
    client, auth_headers, factories, seeded_accounts
):
    factories.connection(seeded_accounts["asha"], status="current", last_successful_sync_at=None)
    factories.connection(seeded_accounts["asha"], status="pending")
    r = client.get("/api/v1/dashboard", headers=auth_headers("asha"))
    assert [s["status"] for s in r.json()["source_statuses"]] == ["stale", "pending"]


def test_trend_requires_token(client):
    assert client.get("/api/v1/trends/weight").status_code == 401


def test_trend_available_with_units_and_label(client, auth_headers, factories, seeded_accounts):
    now = datetime.now(UTC)
    for d in range(6):
        factories.reading(seeded_accounts["asha"], captured_at=now - timedelta(days=d))
    r = client.get("/api/v1/trends/weight?range=30d", headers=auth_headers("asha"))
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "available" and body["unit"] == "kg" and body["range"] == "30d"
    assert body["range_label"] and len(body["points"]) == 6 and body["explanation"] is None


def test_trend_insufficient_data_explains(client, auth_headers, factories, seeded_accounts):
    factories.reading(seeded_accounts["asha"])
    body = client.get("/api/v1/trends/weight?range=7d", headers=auth_headers("asha")).json()
    assert body["status"] == "insufficient_data" and body["explanation"]


def test_trend_only_owner_and_metric(client, auth_headers, factories, seeded_accounts):
    now = datetime.now(UTC)
    for d in range(5):
        factories.reading(seeded_accounts["rohan"], captured_at=now - timedelta(days=d))
    factories.reading(
        seeded_accounts["asha"], metric_type="steps", unit="count", value=5000
    )
    body = client.get("/api/v1/trends/weight?range=30d", headers=auth_headers("asha")).json()
    assert body["points"] == [] and body["status"] == "insufficient_data"


def test_trend_validation(client, auth_headers):
    h = auth_headers("asha")
    assert client.get("/api/v1/trends/weight?range=2d", headers=h).status_code == 422
    assert client.get("/api/v1/trends/bogus", headers=h).status_code == 404


def test_trend_seed_steps_365d_insufficient_weight_available(client, auth_headers, full_seed):
    h = auth_headers("asha")
    steps = client.get("/api/v1/trends/steps?range=365d", headers=h).json()
    assert steps["status"] == "insufficient_data" and len(steps["points"]) == 4
    weight = client.get("/api/v1/trends/weight?range=365d", headers=h).json()
    assert weight["status"] == "available" and len(weight["points"]) == 24
