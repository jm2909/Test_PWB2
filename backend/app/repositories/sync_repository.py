import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import SyncAttempt


class SyncRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find(self, connection_id: uuid.UUID, key: str) -> SyncAttempt | None:
        return self.db.scalar(
            select(SyncAttempt).where(
                SyncAttempt.device_connection_id == connection_id, SyncAttempt.idempotency_key == key
            )
        )

    def start(self, connection_id: uuid.UUID, key: str, started_at: datetime) -> SyncAttempt | None:
        """Create a started attempt, or None when the (connection, key) pair already exists."""
        attempt = SyncAttempt(
            device_connection_id=connection_id, idempotency_key=key, status="started", started_at=started_at
        )
        try:
            with self.db.begin_nested():
                self.db.add(attempt)
        except IntegrityError:
            return None
        return attempt

    def finish(self, attempt: SyncAttempt, status: str, completed_at: datetime, reason: str | None) -> None:
        attempt.status = status
        attempt.completed_at = completed_at
        attempt.failure_reason = reason[:256] if reason else None
        self.db.flush()
