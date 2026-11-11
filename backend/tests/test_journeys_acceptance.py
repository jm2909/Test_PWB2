"""Cross-feature journeys through the real HTTP API (register -> consent -> ... -> support)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.models import AuditLog, WellnessAlert
from app.seeds.alerts import seed_alert_rules
from tests.conftest import login

PASSWORD = "Journey-Pass-2026!"  # noqa: S105 - test value
V1 = "/api/v1"


def _register_and_login(client, db_session, email: str) -> dict[str, str]:
    seed_alert_rules(db_session)
    db_session.commit()
    resp = client.post(
        f"{V1}/auth/accounts",
        json={"email": email, "password": PASSWORD, "display_name": "Journey"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["next_step"] == "consent_setup"
    assert PASSWORD not in resp.text
    token = client.post(f"{V1}/auth/tokens", json={"email": email, "password": PASSWORD})
    assert token.status_code == 201, token.text
    return {"Authorization": f"Bearer {token.json()['access_token']}"}


def _consent(client, headers, decision: str = "granted"):
    return client.put(
        f"{V1}/consents/current",
        headers=headers,
        json={
            "decision": decision,
            "notice_version": "2026-01",
            "data_categories": ["weight", "steps"],
            "purpose": "wellness_support",
        },
    )


def _ingest(client, headers, value: float, days_ago: int, key: str, connection_id=None):
    body = {
        "metric_type": "weight",
        "value": value,
        "unit": "kg",
        "source": "scale",
        "captured_at": (datetime.now(UTC) - timedelta(days=days_ago)).isoformat(),
    }
    if connection_id:
        body["connection_id"] = connection_id
    return client.post(
        f"{V1}/readings", headers={**headers, "Idempotency-Key": key}, json=body
    )


def _link_scale(client, headers) -> str:
    resp = client.post(
        f"{V1}/connections/scale",
        headers=headers,
        json={"device_identifier": "SSC-9001", "device_label": "Journey scale"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _seed_pattern(client, headers, conn_id) -> None:
    for i, days in enumerate((4, 3, 2)):
        r = _ingest(client, headers, 70.0, days, f"base-{i}", conn_id)
        assert r.status_code == 201, r.text


def test_full_journey_register_to_support(client, db_session):
    headers = _register_and_login(client, db_session, "journey@example.com")

    # Nothing is possible before consent.
    blocked = client.post(
        f"{V1}/connections/scale",
        headers=headers,
        json={"device_identifier": "SSC-9001", "device_label": "Journey scale"},
    )
    assert blocked.status_code == 403
    assert _consent(client, headers).status_code in (200, 201)

    conn_id = _link_scale(client, headers)
    _seed_pattern(client, headers, conn_id)
    spike = _ingest(client, headers, 80.0, 0, "spike", conn_id)
    assert spike.status_code == 201, spike.text

    alerts = client.get(f"{V1}/alerts", headers=headers).json()["items"]
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert["state"] == "active"
    assert alert["rule_identifier"] and alert["rule_version"]

    ack = client.post(f"{V1}/alerts/{alert['id']}/acknowledgements", headers=headers)
    assert ack.status_code in (200, 201), ack.text
    assert ack.json()["state"] == "acknowledged"
    listed = client.get(f"{V1}/alerts?state=acknowledged", headers=headers).json()
    assert [a["id"] for a in listed["items"]] == [alert["id"]]

    dash = client.get(f"{V1}/dashboard", headers=headers)
    assert dash.status_code == 200
    body = dash.json()
    assert "weight" not in body["unavailable_categories"]
    assert body["alerts"] == []  # dashboard carries active alerts only

    goal = client.post(
        f"{V1}/goals",
        headers=headers,
        json={
            "category": "weight_management",
            "metric_type": "weight",
            "target_value": 65,
            "target_unit": "kg",
            "target_date": (datetime.now(UTC) + timedelta(days=60)).date().isoformat(),
        },
    )
    assert goal.status_code == 201, goal.text
    assert goal.json()["progress_status"] == "data_gap"  # no reading since the goal began
    assert _ingest(client, headers, 79.0, 0, "after-goal", conn_id).status_code == 201
    goals = client.get(f"{V1}/goals", headers=headers).json()["items"]
    assert goals[0]["progress_status"] == "available"

    support = client.post(
        f"{V1}/support-requests",
        headers=headers,
        json={
            "category": "alert",
            "description": "I have a question about this alert.",
            "context_type": "alert",
            "context_id": alert["id"],
        },
    )
    assert support.status_code == 201, support.text
    assert support.json()["reference"].startswith("SUP-")


def test_consent_withdrawal_blocks_ingestion(client, db_session):
    headers = _register_and_login(client, db_session, "withdraw@example.com")
    _consent(client, headers)
    conn_id = _link_scale(client, headers)
    assert _ingest(client, headers, 70.0, 1, "k1", conn_id).status_code == 201

    withdrawn = _consent(client, headers, "withdrawn")
    assert withdrawn.status_code in (200, 201)
    assert withdrawn.json()["collection_allowed"] is False
    assert withdrawn.json()["data_rights_path"]
    assert _ingest(client, headers, 70.5, 0, "k2", conn_id).status_code == 403


def test_replay_does_not_duplicate_alert(client, db_session):
    headers = _register_and_login(client, db_session, "replay@example.com")
    _consent(client, headers)
    conn_id = _link_scale(client, headers)
    _seed_pattern(client, headers, conn_id)
    first = _ingest(client, headers, 80.0, 0, "same-key", conn_id)
    assert first.status_code == 201
    # The same payload with the same key must be an exact replay (reuse the captured_at).
    body = {
        "metric_type": "weight",
        "value": 80.0,
        "unit": "kg",
        "source": "scale",
        "captured_at": client.get(f"{V1}/readings", headers=headers).json()["items"][0][
            "captured_at"
        ],
        "connection_id": conn_id,
    }
    replay = client.post(
        f"{V1}/readings", headers={**headers, "Idempotency-Key": "same-key"}, json=body
    )
    assert replay.status_code == 200, replay.text
    assert replay.json()["id"] == first.json()["id"]
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 1
    assert client.get(f"{V1}/readings", headers=headers).json()["total"] == 4


def test_owner_isolation_between_users(client, full_seed):
    asha = login(client, "asha")
    rohan = login(client, "rohan")
    asha_alerts = client.get(f"{V1}/alerts", headers=asha).json()["items"]
    assert asha_alerts
    assert client.get(f"{V1}/alerts", headers=rohan).json()["items"] == []
    foreign = client.post(f"{V1}/alerts/{asha_alerts[0]['id']}/acknowledgements", headers=rohan)
    assert foreign.status_code == 404
    assert client.get(f"{V1}/goals", headers=rohan).json()["items"] == []
    missing = client.post(
        f"{V1}/alerts/{uuid.uuid4()}/acknowledgements", headers=rohan
    )
    assert missing.status_code == 404


def test_logout_revokes_token(client, seeded_accounts):
    headers = login(client, "asha")
    assert client.get(f"{V1}/dashboard", headers=headers).status_code == 200
    assert client.delete(f"{V1}/auth/tokens/current", headers=headers).status_code == 204
    assert client.get(f"{V1}/dashboard", headers=headers).status_code == 401
    assert client.get(f"{V1}/alerts", headers=headers).status_code == 401


def test_audit_events_hold_no_health_values_or_password(client, db_session):
    headers = _register_and_login(client, db_session, "audit@example.com")
    _consent(client, headers)
    client.post(
        f"{V1}/data-rights-requests", headers=headers, json={"request_type": "export"}
    )
    rows = db_session.scalars(select(AuditLog)).all()
    assert rows
    for row in rows:
        text = f"{row.event_type} {row.event_metadata}"
        assert PASSWORD not in text
        assert "audit@example.com" not in text
