"""FastAPI dependencies: db, clock, token issuer, rate limit, and the single get_current_user."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.config import Settings, get_settings
from app.database import get_db
from app.errors import AuthenticationError, RateLimitedError
from app.ratelimit import login_limiter
from app.repositories.account import AccountRepository
from app.repositories.session import SessionRepository
from app.security import JwtTokenIssuer, TokenIssuer, hash_token
from app.services.auth import AuthService
from app.services.consent import ConsentService

_bearer = HTTPBearer(auto_error=False)
_WWW = {"WWW-Authenticate": "Bearer"}

__all__ = [
    "CurrentUser",
    "get_auth_service",
    "get_clock",
    "get_consent_service",
    "require_active_consent",
    "get_current_user",
    "get_db",
    "get_token_issuer",
    "login_rate_limit",
]


@dataclass(frozen=True)
class CurrentUser:
    account_id: uuid.UUID
    session_id: uuid.UUID
    email: str
    display_name: str


def get_clock() -> Clock:
    return SystemClock()


def get_token_issuer(settings: Settings = Depends(get_settings)) -> TokenIssuer:
    return JwtTokenIssuer(settings)


def get_auth_service(
    db: DbSession = Depends(get_db),
    clock: Clock = Depends(get_clock),
    issuer: TokenIssuer = Depends(get_token_issuer),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(db, clock, issuer, settings)


def client_ip(request: Request, settings: Settings) -> str:
    if settings.trust_forwarded_for:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def login_rate_limit(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if not settings.rate_limit_enabled:
        return
    if not login_limiter.allow(client_ip(request, settings), settings.login_rate_limit):
        raise RateLimitedError(headers={"Retry-After": "60"})


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: DbSession = Depends(get_db),
    clock: Clock = Depends(get_clock),
    issuer: TokenIssuer = Depends(get_token_issuer),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    """Single owner resolution: signature, token hash, revocation, expiry, inactivity."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Authentication required", headers=_WWW)
    token = credentials.credentials
    try:
        claims = issuer.verify(token)
    except AuthenticationError as exc:
        raise AuthenticationError("Invalid or expired token", headers=_WWW) from exc

    sessions = SessionRepository(db)
    session = sessions.get_by_token_hash(hash_token(token))
    now = clock.utc_now()
    if (
        session is None
        or session.id != claims.session_id
        or session.account_id != claims.account_id
    ):
        raise AuthenticationError("Session is not active", headers=_WWW)
    if session.revoked_at is not None or ensure_utc(session.expires_at) <= now:
        raise AuthenticationError("Session is not active", headers=_WWW)
    idle = timedelta(minutes=settings.session_inactivity_minutes)
    if now - ensure_utc(session.last_activity_at) > idle:
        raise AuthenticationError("Session expired due to inactivity", headers=_WWW)
    account = AccountRepository(db).get(session.account_id)
    if account is None:
        raise AuthenticationError("Session is not active", headers=_WWW)

    sessions.touch(session.id, now)
    db.commit()
    return CurrentUser(
        account_id=account.id,
        session_id=session.id,
        email=account.email,
        display_name=account.display_name,
    )


def get_consent_service(
    db: DbSession = Depends(get_db), clock: Clock = Depends(get_clock)
) -> ConsentService:
    return ConsentService(db, clock)


def require_active_consent(
    user: CurrentUser = Depends(get_current_user),
    service: ConsentService = Depends(get_consent_service),
) -> CurrentUser:
    """Reusable gate for sync / manual entry / source connection (403 without consent)."""
    service.require_active(user.account_id)
    return user
