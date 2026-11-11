from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session as DbSession

from app.models import Session


class SessionRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def create(self, session: Session) -> Session:
        self.db.add(session)
        self.db.flush()
        return session

    def get_by_token_hash(self, token_hash: str) -> Session | None:
        return self.db.scalar(select(Session).where(Session.token_hash == token_hash))

    def touch(self, session_id: uuid.UUID, when: datetime) -> None:
        self.db.execute(
            update(Session).where(Session.id == session_id).values(last_activity_at=when)
        )

    def revoke(self, session_id: uuid.UUID, when: datetime) -> None:
        self.db.execute(
            update(Session)
            .where(Session.id == session_id, Session.revoked_at.is_(None))
            .values(revoked_at=when)
        )
