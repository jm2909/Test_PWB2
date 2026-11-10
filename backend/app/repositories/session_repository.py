from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, user_id: int, token_hash: str, issued_at: datetime, expires_at: datetime) -> AuthSession:
        row = AuthSession(
            user_id=user_id,
            token_hash=token_hash,
            issued_at=issued_at,
            expires_at=expires_at,
            last_activity_at=issued_at,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_by_token_hash(self, token_hash: str) -> AuthSession | None:
        return self.db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))

    def touch(self, row: AuthSession, now: datetime) -> None:
        row.last_activity_at = now
        self.db.flush()

    def revoke(self, row: AuthSession, now: datetime) -> None:
        row.revoked_at = now
        self.db.flush()
