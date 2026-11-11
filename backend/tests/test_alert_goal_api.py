import uuid
from datetime import date, timedelta

from sqlalchemy import func, select

from app.models import AlertAcknowledgement, AuditLog, Reading, WellnessAlert


def _asha_alerts(db_session, seeded_accounts):
    return db_session.scalars(
        select(WellnessAlert).where(WellnessAlert.account_id == seeded_accounts["asha"].id)
    ).all()


def test_alert_list_filters_by_state_and_owner(client, full_seed, auth_headers):
    h = auth_headers("asha")
    body = client.get("/api/v1/alerts", headers=h).json()
    assert body["total"] == 3
    item = body["items"][0]
    for key in ("rule_identifier", "rule_version", "acknowledged_at", "wellness_boundary"):
        assert key in item
    active = client.get("/api/v1/alerts?state=active", headers=h).json()
    acked = client.get("/api/v1/alerts?state=acknowledged", headers=h).json()
    assert active["total"] == 2 and acked["total"] == 1
    assert acked["items"][0]["acknowledged_at"] is not None
    assert client.get("/api/v1/alerts?state=bogus", headers=h).status_code == 422
    assert client.get("/api/v1/alerts", headers=auth_headers("rohan")).json()["total"] == 0
    assert client.get("/api/v1/alerts").status_code == 401


def test_alert_acknowledge_is_idempotent_and_keeps_history(
    client, full_seed, auth_headers, db_session
):
    h = auth_headers("asha")
    alert = client.get("/api/v1/alerts?state=active", headers=h).json()["items"][0]
    url = f"/api/v1/alerts/{alert['id']}/acknowledgements"
    audit_before = db_session.scalar(select(func.count()).select_from(AuditLog))
    first = client.post(url, headers=h)
    assert first.status_code == 200
    assert first.json()["state"] == "acknowledged" and first.json()["acknowledged_at"]
    second = client.post(url, headers=h)
    assert second.status_code == 200
    assert second.json()["acknowledged_at"] == first.json()["acknowledged_at"]
    db_session.expire_all()
    rows = db_session.scalars(
        select(AlertAcknowledgement).where(AlertAcknowledgement.alert_id == uuid.UUID(alert["id"]))
    ).all()
    assert len(rows) == 1
    assert db_session.scalar(select(func.count()).select_from(AuditLog)) == audit_before + 1
    assert client.get("/api/v1/alerts", headers=h).json()["total"] == 3
    dash = client.get("/api/v1/dashboard", headers=h).json()
    assert alert["id"] not in [a["id"] for a in dash["alerts"]]


def test_alert_acknowledge_unknown_or_foreign_is_404(client, full_seed, auth_headers):
    alert = client.get("/api/v1/alerts", headers=auth_headers("asha")).json()["items"][0]
    rohan = auth_headers("rohan")
    assert (
        client.post(f"/api/v1/alerts/{alert['id']}/acknowledgements", headers=rohan).status_code
        == 404
    )
    missing = "00000000-0000-0000-0000-000000000009"
    assert (
        client.post(f"/api/v1/alerts/{missing}/acknowledgements", headers=rohan).status_code == 404
    )


def _goal(**kw):
    body = {
        "category": "weight_management",
        "metric_type": "weight",
        "target_value": "65",
        "target_unit": "kg",
        "target_date": (date.today() + timedelta(days=30)).isoformat(),
    }
    return {**body, **kw}


def test_goal_create_validates_input(client, full_seed, auth_headers):
    h = auth_headers("rohan")
    bad = [
        _goal(target_value="0"),
        _goal(target_value="-3"),
        _goal(category="nope"),
        _goal(metric_type="steps"),
        _goal(target_unit="lb"),
        _goal(target_date=date.today().isoformat()),
        _goal(target_date=(date.today() - timedelta(days=1)).isoformat()),
    ]
    for payload in bad:
        assert client.post("/api/v1/goals", headers=h, json=payload).status_code == 422, payload
    missing = _goal()
    del missing["target_value"]
    assert client.post("/api/v1/goals", headers=h, json=missing).status_code == 422


def test_goal_create_progress_data_gap_and_available(client, full_seed, auth_headers):
    h = auth_headers("rohan")
    r = client.post("/api/v1/goals", headers=h, json=_goal())
    assert r.status_code == 201
    assert r.json()["state"] == "active"
    assert r.json()["progress_status"] == "data_gap" and r.json()["current_value"] is None
    asha = client.get("/api/v1/goals", headers=auth_headers("asha")).json()
    by_metric = {g["metric_type"]: g for g in asha["items"]}
    assert asha["total"] == 4
    assert by_metric["weight"]["progress_status"] == "available"
    assert by_metric["weight"]["current_value"] is not None
    assert by_metric["steps"]["progress_status"] == "data_gap"
    assert by_metric["sleep_duration"]["state"] == "paused"
    assert by_metric["active_minutes"]["state"] == "closed"
    assert client.get("/api/v1/goals", headers=h).json()["total"] == 1


def test_goal_state_transitions_keep_readings(client, full_seed, auth_headers, db_session):
    h = auth_headers("asha")
    readings = db_session.scalar(select(func.count()).select_from(Reading))
    goals = {g["metric_type"]: g for g in client.get("/api/v1/goals", headers=h).json()["items"]}
    gid = goals["weight"]["id"]
    assert (
        client.patch(f"/api/v1/goals/{gid}", headers=h, json={"state": "paused"}).json()["state"]
        == "paused"
    )
    assert (
        client.patch(f"/api/v1/goals/{gid}", headers=h, json={"state": "active"}).json()["state"]
        == "active"
    )
    assert (
        client.patch(f"/api/v1/goals/{gid}", headers=h, json={"state": "closed"}).json()["state"]
        == "closed"
    )
    assert (
        client.patch(f"/api/v1/goals/{gid}", headers=h, json={"state": "active"}).status_code == 409
    )
    assert (
        client.patch(f"/api/v1/goals/{gid}", headers=h, json={"state": "bogus"}).status_code == 422
    )
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Reading)) == readings
    dash = client.get("/api/v1/dashboard", headers=h).json()
    assert gid not in [g["id"] for g in dash["goals"]]
    assert all("progress_status" in g for g in dash["goals"])


def test_goal_patch_foreign_is_404(client, full_seed, auth_headers):
    gid = client.get("/api/v1/goals", headers=auth_headers("asha")).json()["items"][0]["id"]
    r = client.patch(
        f"/api/v1/goals/{gid}", headers=auth_headers("rohan"), json={"state": "paused"}
    )
    assert r.status_code == 404
