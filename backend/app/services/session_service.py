"""Server-side sessions: a JWT whose SHA-256 hash is stored so it can be revoked and expired."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.session_repository import SessionRepository
from app.security import create_access_token, hash_token


class SessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sessions = SessionRepository(db)

    def issue(self, user_id: int) -> str:
        """Create a session row and return the bearer token (only its hash is stored)."""
        settings = get_settings()
        token, expires_at = create_access_token(
            user_id, settings.jwt_secret_key, timedelta(minutes=settings.jwt_expire_minutes)
        )
        self.sessions.add(user_id, hash_token(token), datetime.now(UTC), expires_at)
        self.db.commit()
        return token
