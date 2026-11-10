"""Account registration (FR-001)."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository
from app.security import hash_password
from app.services.audit_service import AuditService

ONBOARDING_NOT_STARTED = "not_started"


class DuplicateEmailError(Exception):
    pass


class AccountService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def register(self, email: str, password: str, correlation_id: str) -> User:
        normalized = email.strip().lower()
        if self.users.get_by_email(normalized) is not None:
            self._audit_failure(correlation_id)
            raise DuplicateEmailError
        try:
            user = self.users.add(normalized, hash_password(password))
            self.audit.record(
                action="account.created",
                outcome="success",
                correlation_id=correlation_id,
                user_id=user.id,
                entity_type="user",
                entity_id=str(user.id),
            )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            self._audit_failure(correlation_id)
            raise DuplicateEmailError from exc
        return user

    def _audit_failure(self, correlation_id: str) -> None:
        self.audit.record(
            action="account.create",
            outcome="duplicate_email",
            severity="warning",
            correlation_id=correlation_id,
        )
        self.db.commit()
