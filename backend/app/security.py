"""Password hashing (bcrypt, direct), JWT issue/verify (PyJWT) and token hashing."""

from __future__ import annotations

import base64
import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

import bcrypt
import jwt

from app.clock import ensure_utc
from app.config import Settings, get_settings
from app.errors import AuthenticationError


def _prehash(password: str) -> bytes:
    # bcrypt truncates at 72 bytes; pre-hash so every character counts.
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def hash_password(password: str, rounds: int | None = None) -> str:
    cost = rounds if rounds is not None else get_settings().bcrypt_rounds
    if cost < 12:
        raise ValueError("bcrypt cost must be >= 12")
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt(rounds=cost)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_prehash(password), password_hash.encode("ascii"))
    except ValueError:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SessionClaims:
    session_id: uuid.UUID
    account_id: uuid.UUID
    issued_at: datetime
    expires_at: datetime


class TokenIssuer(Protocol):
    def issue(self, claims: SessionClaims) -> str: ...

    def verify(self, token: str) -> SessionClaims: ...


class JwtTokenIssuer:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def issue(self, claims: SessionClaims) -> str:
        payload = {
            "sub": str(claims.account_id),
            "sid": str(claims.session_id),
            "iat": int(ensure_utc(claims.issued_at).timestamp()),
            "exp": int(ensure_utc(claims.expires_at).timestamp()),
        }
        return jwt.encode(
            payload, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm
        )

    def verify(self, token: str) -> SessionClaims:
        try:
            data = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
                options={"require": ["exp", "iat", "sub", "sid"]},
            )
            return SessionClaims(
                session_id=uuid.UUID(data["sid"]),
                account_id=uuid.UUID(data["sub"]),
                issued_at=ensure_utc(datetime.fromtimestamp(data["iat"], tz=UTC)),
                expires_at=ensure_utc(datetime.fromtimestamp(data["exp"], tz=UTC)),
            )
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise AuthenticationError("Invalid or expired token") from exc
