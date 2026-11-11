"""AuthService: credential check, session creation (hashed token)."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.config import Settings, get_settings
from app.errors import AuthenticationError, DomainError
from app.models import Account, Session
from app.repositories.account import AccountRepository
from app.repositories.session import SessionRepository
from app.schemas.auth import AccountResponse, LoginRequest, RegisterRequest, TokenResponse
from app.security import (
    JwtTokenIssuer,
    SessionClaims,
    TokenIssuer,
    hash_password,
    hash_token,
    verify_password,
)
from app.services.audit import AuditService

_DUMMY_HASH: str | None = None


def _dummy_hash() -> str:
    global _DUMMY_HASH  # noqa: PLW0603
    if _DUMMY_HASH is None:
        _DUMMY_HASH = hash_password("timing-equalisation-placeholder")
    return _DUMMY_HASH


class AuthService:
    def __init__(
        self,
        db: DbSession,
        clock: Clock | None = None,
        issuer: TokenIssuer | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()
        self.issuer = issuer or JwtTokenIssuer(self.settings)
        self.accounts = AccountRepository(db)
        self.sessions = SessionRepository(db)
        self.audit = AuditService(db, self.clock)

    def register(self, command: RegisterRequest) -> AccountResponse:
        """Create the account after validation; the password is only ever hashed."""
        duplicate = DomainError("Email address is already registered")
        if self.accounts.get_by_email(command.email) is not None:
            raise duplicate
        try:
            account = self.accounts.add(
                Account(
                    email=command.email,
                    password_hash=hash_password(command.password),
                    display_name=command.display_name,
                )
            )
            self.audit.record(
                "auth.account_registered",
                entity_type="account",
                account_id=account.id,
                entity_id=account.id,
            )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise duplicate from exc
        return AccountResponse.model_validate(account)

    def logout(self, account_id: uuid.UUID, session_id: uuid.UUID) -> None:
        """Revoke the authenticated session; its token no longer authorizes anything."""
        self.sessions.revoke(session_id, self.clock.utc_now())
        self.audit.record(
            "auth.logout",
            entity_type="session",
            account_id=account_id,
            entity_id=session_id,
        )
        self.db.commit()

    def login(self, command: LoginRequest) -> TokenResponse:
        account = self.accounts.get_by_email(command.email)
        # Always run one bcrypt verification so unknown accounts are not distinguishable by timing.
        hashed = account.password_hash if account else _dummy_hash()
        valid = verify_password(command.password, hashed)
        if account is None or not valid:
            self.audit.record(
                "auth.login_failed",
                entity_type="session",
                account_id=account.id if account else None,
                severity="warning",
                metadata={"reason": "invalid_credentials"},
            )
            self.db.commit()
            raise AuthenticationError("Invalid credentials")

        now = self.clock.utc_now()
        expires_at = now + timedelta(minutes=self.settings.session_ttl_minutes)
        session_id = uuid.uuid4()
        token = self.issuer.issue(
            SessionClaims(
                session_id=session_id,
                account_id=account.id,
                issued_at=now,
                expires_at=expires_at,
            )
        )
        self.sessions.create(
            Session(
                id=session_id,
                account_id=account.id,
                token_hash=hash_token(token),
                issued_at=now,
                expires_at=expires_at,
                last_activity_at=now,
            )
        )
        self.audit.record(
            "auth.login_succeeded",
            entity_type="session",
            account_id=account.id,
            entity_id=session_id,
        )
        self.db.commit()
        return TokenResponse(
            access_token=token,
            expires_at=expires_at,
            account=AccountResponse.model_validate(account),
        )
