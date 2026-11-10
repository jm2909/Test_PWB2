"""Sign in / sign out (FR-002). Failures are generic so accounts cannot be enumerated."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.security import decode_access_token, hash_password, hash_token, verify_password
from app.services.audit_service import AuditService
from app.services.session_service import SessionService

# Verified against when the account is unknown, so response time does not reveal existence.
_DUMMY_HASH = hash_password("not-a-real-password")


class InvalidCredentialsError(Exception):
    pass


@dataclass(frozen=True)
class LoginResult:
    token: str
    expires_at: datetime
    user: User


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def login(self, email: str, password: str, correlation_id: str) -> LoginResult:
        user = self.users.get_by_email(email.strip().lower())
        valid = verify_password(password, user.password_hash if user else _DUMMY_HASH)
        if user is None or not valid:
            self.audit.record(
                action="auth.login",
                outcome="failure",
                severity="warning",
                correlation_id=correlation_id,
                user_id=user.id if user else None,
            )
            self.db.commit()
            raise InvalidCredentialsError
        token = SessionService(self.db).issue(user.id)
        expires_at = decode_access_token(token, get_settings().jwt_secret_key)["exp"]
        self.audit.record(
            action="auth.login",
            outcome="success",
            correlation_id=correlation_id,
            user_id=user.id,
            entity_type="user",
            entity_id=str(user.id),
        )
        self.db.commit()
        return LoginResult(token=token, expires_at=datetime.fromtimestamp(expires_at, UTC), user=user)

    def logout(self, token: str, user_id: int, correlation_id: str) -> None:
        sessions = SessionRepository(self.db)
        row = sessions.get_by_token_hash(hash_token(token))
        if row is not None and row.user_id == user_id and row.revoked_at is None:
            sessions.revoke(row, datetime.now(UTC))
        self.audit.record(
            action="auth.logout",
            outcome="success",
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
        )
        self.db.commit()
