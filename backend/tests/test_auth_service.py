from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.repositories.session_repository import SessionRepository
from app.security import hash_token
from app.services.auth_service import AuthService, InvalidCredentialsError
from app.services.rate_limiter import FixedWindowLimiter, parse_limit
from tests.factories import SEED_EMAIL, SEED_PASSWORD


def test_login_success_stores_hashed_session_and_audits(seeded: Session) -> None:
    result = AuthService(seeded).login(SEED_EMAIL.upper(), SEED_PASSWORD, "cid")
    row = SessionRepository(seeded).get_by_token_hash(hash_token(result.token))
    assert row is not None and row.user_id == result.user.id and row.revoked_at is None
    audit = seeded.scalars(select(AuditLog).where(AuditLog.action == "auth.login")).all()
    assert [a.outcome for a in audit] == ["success"]


@pytest.mark.parametrize("email,password", [(SEED_EMAIL, "wrong-password"), ("nobody@example.com", "x")])
def test_login_failure_is_generic_and_audited(seeded: Session, email: str, password: str) -> None:
    with pytest.raises(InvalidCredentialsError):
        AuthService(seeded).login(email, password, "cid")
    audit = seeded.scalars(select(AuditLog).where(AuditLog.action == "auth.login")).all()
    assert [a.outcome for a in audit] == ["failure"]


def test_logout_revokes_session(seeded: Session) -> None:
    service = AuthService(seeded)
    result = service.login(SEED_EMAIL, SEED_PASSWORD, "cid")
    service.logout(result.token, result.user.id, "cid")
    row = SessionRepository(seeded).get_by_token_hash(hash_token(result.token))
    assert row is not None and row.revoked_at is not None
    assert row.revoked_at <= datetime.now(UTC) + timedelta(seconds=1)


def test_fixed_window_limiter() -> None:
    assert parse_limit("10/minute") == (10, 60)
    limiter = FixedWindowLimiter()
    assert [limiter.hit("ip", "2/minute", now=0.0) for _ in range(3)] == [True, True, False]
    assert limiter.hit("other", "2/minute", now=1.0)
    assert limiter.hit("ip", "2/minute", now=61.0)
