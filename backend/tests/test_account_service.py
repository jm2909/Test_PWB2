import pytest
from pydantic import ValidationError

from app.errors import DomainError
from app.models import Account, AuditLog
from app.schemas.auth import RegisterRequest
from app.security import verify_password
from app.services.auth import AuthService


def _cmd(**kw):
    data = {
        "email": "New.User@Example.com",
        "password": "A-long-password-1",
        "display_name": " Neo ",
    }
    return RegisterRequest(**{**data, **kw})


def test_register_creates_account_hashed_and_normalised(db_session):
    result = AuthService(db_session).register(_cmd())
    account = db_session.get(Account, result.id)
    assert account is not None
    assert account.email == "new.user@example.com"
    assert account.display_name == "Neo"
    assert account.password_hash != "A-long-password-1"
    assert verify_password("A-long-password-1", account.password_hash)
    assert result.next_step == "consent_setup"


def test_register_duplicate_email_rejected(db_session):
    service = AuthService(db_session)
    service.register(_cmd())
    with pytest.raises(DomainError) as exc:
        service.register(_cmd(email="new.user@example.com"))
    assert exc.value.status_code == 400
    assert db_session.query(Account).count() == 1


def test_register_audit_has_no_password(db_session):
    AuthService(db_session).register(_cmd())
    rows = db_session.query(AuditLog).filter_by(event_type="auth.account_registered").all()
    assert len(rows) == 1
    assert "A-long-password-1" not in str(rows[0].event_metadata)


@pytest.mark.parametrize(
    "bad",
    [
        {"email": "nope"},
        {"password": "short"},
        {"password": "x" * 129},
        {"display_name": "   "},
        {"display_name": "x" * 101},
    ],
)
def test_register_request_validation(bad):
    with pytest.raises(ValidationError):
        _cmd(**bad)
