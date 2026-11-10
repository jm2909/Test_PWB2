import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AuditLog
from app.security import create_access_token, decode_access_token, hash_password, hash_token, verify_password
from app.services.account_service import AccountService, DuplicateEmailError


def test_hash_uses_bcrypt_cost_12_and_verifies() -> None:
    hashed = hash_password("a-long-password-1")
    assert hashed.startswith("$2b$12$")
    assert verify_password("a-long-password-1", hashed)
    assert not verify_password("wrong-password-1", hashed)


def test_token_has_exp_and_hash_is_sha256() -> None:
    from datetime import timedelta

    secret = get_settings().jwt_secret_key
    token, _ = create_access_token(5, secret, timedelta(minutes=5))
    assert "exp" in decode_access_token(token, secret)
    assert len(hash_token(token)) == 64
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token, "x" * 32)


def test_register_creates_user_and_audit(db_session: Session) -> None:
    user = AccountService(db_session).register("New.User@Example.com", "long-enough-pass", "corr-1")
    assert user.id is not None
    assert user.email == "new.user@example.com"
    assert user.password_hash != "long-enough-pass"
    actions = [a.action for a in db_session.scalars(select(AuditLog))]
    assert "account.created" in actions


def test_register_duplicate_raises(db_session: Session) -> None:
    service = AccountService(db_session)
    service.register("dup@example.com", "long-enough-pass", "c")
    with pytest.raises(DuplicateEmailError):
        service.register("DUP@example.com", "another-long-pass", "c")
