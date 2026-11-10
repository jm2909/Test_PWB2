import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import DeviationEvent


class DeviationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_unique(self, event: DeviationEvent) -> bool:
        """Insert under a savepoint; False when (reading, criterion) already has an event."""
        try:
            with self.db.begin_nested():
                self.db.add(event)
        except IntegrityError:
            return False
        return True

    def exists(self, reading_id: uuid.UUID, criterion_code: str) -> bool:
        return (
            self.db.scalar(
                select(DeviationEvent.id).where(
                    DeviationEvent.wellness_reading_id == reading_id,
                    DeviationEvent.criterion_code == criterion_code,
                )
            )
            is not None
        )

    def list_for_user(self, user_id: int, limit: int, offset: int) -> tuple[list[DeviationEvent], int]:
        total = self.db.scalar(
            select(func.count()).select_from(DeviationEvent).where(DeviationEvent.user_id == user_id)
        )
        rows = self.db.scalars(
            select(DeviationEvent)
            .where(DeviationEvent.user_id == user_id)
            .order_by(DeviationEvent.created_at.desc(), DeviationEvent.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total or 0)
