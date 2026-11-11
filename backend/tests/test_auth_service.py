from __future__ import annotations

from datetime import timedelta

import pytest

from app.clock import utc_now
from app.errors import AuthenticationError
from app.models import AuditLog, Session
from app.schemas.auth import LoginRequest
from app.security import hash_token
from app.seeds.constants import DEMO_ACCOUNTS
from app.services.auth import AuthService


def _login(db_session) -> tuple[AuthService, str]:
    service = AuthService(db_session)
    spec = DEMO_ACCOUNTS["asha"]
    result = service.login(LoginRequest(email=spec["email"], password=spec["password"]))
    return service, result.access_token


def test_login_stores_only_token_hash(db_session, seeded_accounts):
    _, token = _login(db_session)
    stored = db_session.query(Session).one()
    assert stored.token_hash == hash_token(token)
    assert token not in stored.token_hash


def test_login_failure_is_uniform_and_audited(db_session, seeded_accounts):
    service = AuthService(db_session)
    with pytest.raises(AuthenticationError) as unknown:
        service.login(LoginRequest(email="nobody@example.com", password="Whatever-pass-1"))
    with pytest.raises(AuthenticationError) as wrong:
        service.login(
            LoginRequest(email=DEMO_ACCOUNTS["asha"]["email"], password="Wrong-pass-12345")
        )
    assert unknown.value.detail == wrong.value.detail
    events = [a.event_type for a in db_session.query(AuditLog).all()]
    assert events.count("auth.login_failed") == 2


def test_logout_revokes_session_and_audits(db_session, seeded_accounts):
    service, _ = _login(db_session)
    session = db_session.query(Session).one()
    service.logout(session.account_id, session.id)
    db_session.refresh(session)
    assert session.revoked_at is not None
    assert db_session.query(AuditLog).filter_by(event_type="auth.logout").count() == 1


def test_logout_is_idempotent_on_revoked_at(db_session, seeded_accounts):
    service, _ = _login(db_session)
    session = db_session.query(Session).one()
    service.logout(session.account_id, session.id)
    db_session.refresh(session)
    first = session.revoked_at
    service.logout(session.account_id, session.id)
    db_session.refresh(session)
    assert session.revoked_at == first
    assert first is not None
    assert first <= utc_now() + timedelta(seconds=1)
