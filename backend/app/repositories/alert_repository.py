import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Alert, DeviationEvent


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_unread(self, user_id: int) -> int:
        """Alerts have no read marker yet, so every stored alert counts as unread."""
        return int(
            self.db.scalar(select(func.count()).select_from(Alert).where(Alert.user_id == user_id)) or 0
        )

    def unalerted_events(self, user_id: int) -> list[DeviationEvent]:
        return list(
            self.db.scalars(
                select(DeviationEvent)
                .outerjoin(Alert, Alert.deviation_event_id == DeviationEvent.id)
                .where(DeviationEvent.user_id == user_id, Alert.id.is_(None))
                .order_by(DeviationEvent.created_at, DeviationEvent.id)
            )
        )

    def add_unique(self, alert: Alert) -> bool:
        """Insert under a savepoint; False when the deviation event already has an alert."""
        try:
            with self.db.begin_nested():
                self.db.add(alert)
        except IntegrityError:
            return False
        return True

    def list_with_events(
        self, user_id: int, limit: int, offset: int
    ) -> tuple[list[tuple[Alert, DeviationEvent]], int]:
        stmt = (
            select(Alert, DeviationEvent)
            .join(DeviationEvent, DeviationEvent.id == Alert.deviation_event_id)
            .where(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc(), Alert.id)
            .limit(limit)
            .offset(offset)
        )
        rows = [(a, e) for a, e in self.db.execute(stmt).all()]
        return rows, self.count_unread(user_id)

    def get_for_event(self, event_id: uuid.UUID) -> Alert | None:
        return self.db.scalar(select(Alert).where(Alert.deviation_event_id == event_id))
