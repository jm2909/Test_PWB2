"""Auth dependency. `get_current_user` is the only place a bearer token is parsed."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.security import decode_access_token, hash_token

_bearer = HTTPBearer(auto_error=False)


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=401, detail="Not authenticated.", headers={"WWW-Authenticate": "Bearer"})


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise _unauthorized()
    settings = get_settings()
    try:
        payload = decode_access_token(credentials.credentials, settings.jwt_secret_key)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise _unauthorized() from exc

    sessions = SessionRepository(db)
    row = sessions.get_by_token_hash(hash_token(credentials.credentials))
    now = datetime.now(UTC)
    if (
        row is None
        or row.user_id != user_id
        or row.revoked_at is not None
        or row.expires_at <= now
        or row.last_activity_at + timedelta(minutes=settings.session_inactivity_minutes) <= now
    ):
        raise _unauthorized()
    user = UserRepository(db).get(user_id)
    if user is None:
        raise _unauthorized()
    sessions.touch(row, now)
    db.commit()
    return user
