from __future__ import annotations

from datetime import timedelta

from app.clock import utc_now
from app.models import AuditLog, Session
from tests.conftest import login


def test_inactive_session_requires_reauthentication(client, db_session, seeded_accounts):
    headers = login(client, "asha")
    session = db_session.query(Session).one()
    session.last_activity_at = utc_now() - timedelta(days=1)
    db_session.commit()
    response = client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 401


def test_activity_updates_last_activity(client, db_session, seeded_accounts):
    headers = login(client, "asha")
    session = db_session.query(Session).one()
    old = utc_now() - timedelta(minutes=1)
    session.last_activity_at = old
    db_session.commit()
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 200
    db_session.refresh(session)
    assert session.last_activity_at > old


def test_expired_session_rejected(client, db_session, seeded_accounts):
    headers = login(client, "asha")
    session = db_session.query(Session).one()
    session.expires_at = utc_now() - timedelta(seconds=1)
    db_session.commit()
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 401


def test_revoked_session_rejected(client, db_session, seeded_accounts):
    headers = login(client, "asha")
    session = db_session.query(Session).one()
    session.revoked_at = utc_now()
    db_session.commit()
    assert client.get("/api/v1/dashboard", headers=headers).status_code == 401


def test_token_hashed_and_not_in_audit(client, db_session, seeded_accounts):
    headers = login(client, "asha")
    token = headers["Authorization"].split(" ", 1)[1]
    client.delete("/api/v1/auth/tokens/current", headers=headers)
    assert db_session.query(Session).one().token_hash != token
    for event in db_session.query(AuditLog).all():
        dumped = f"{event.event_type} {event.event_metadata}"
        assert token not in dumped
        assert "Wellness-Demo-2026!" not in dumped
    types = {e.event_type for e in db_session.query(AuditLog).all()}
    assert {"auth.login_succeeded", "auth.logout"} <= types
