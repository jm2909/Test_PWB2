"""Password hashing (bcrypt cost 12), JWT creation/decoding (always with exp), token hashing."""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

BCRYPT_COST = 12
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_COST)).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def create_access_token(user_id: int, secret: str, expires_in: timedelta) -> tuple[str, datetime]:
    """Return (token, expires_at). The token always carries `exp`."""
    now = datetime.now(UTC)
    expires_at = now + expires_in
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM), expires_at


def decode_access_token(token: str, secret: str) -> dict[str, Any]:
    """Validate signature and expiry; raises jwt.PyJWTError on any failure."""
    payload: dict[str, Any] = jwt.decode(
        token, secret, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "sub"]}
    )
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
