import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import WellnessReading


class ReadingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_since(self, user_id: int, since: datetime) -> list[WellnessReading]:
        return list(
            self.db.scalars(
                select(WellnessReading)
                .where(WellnessReading.user_id == user_id, WellnessReading.observed_at >= since)
                .order_by(WellnessReading.observed_at)
            )
        )

    def list_metric_since(self, user_id: int, metric_type: str, since: datetime) -> list[WellnessReading]:
        return list(
            self.db.scalars(
                select(WellnessReading)
                .where(
                    WellnessReading.user_id == user_id,
                    WellnessReading.metric_type == metric_type,
                    WellnessReading.observed_at >= since,
                )
                .order_by(WellnessReading.observed_at)
            )
        )

    def get_many(self, user_id: int, reading_ids: list[uuid.UUID]) -> list[WellnessReading]:
        if not reading_ids:
            return []
        return list(
            self.db.scalars(
                select(WellnessReading)
                .where(WellnessReading.user_id == user_id, WellnessReading.id.in_(reading_ids))
                .order_by(WellnessReading.observed_at)
            )
        )

    def list_metric_between(
        self, user_id: int, metric_type: str, since: datetime, until: datetime
    ) -> list[WellnessReading]:
        return list(
            self.db.scalars(
                select(WellnessReading)
                .where(
                    WellnessReading.user_id == user_id,
                    WellnessReading.metric_type == metric_type,
                    WellnessReading.observed_at >= since,
                    WellnessReading.observed_at <= until,
                )
                .order_by(WellnessReading.observed_at)
            )
        )

    def existing_event_ids(self, connection_id: uuid.UUID, event_ids: list[str]) -> set[str]:
        if not event_ids:
            return set()
        return set(
            self.db.scalars(
                select(WellnessReading.source_event_id).where(
                    WellnessReading.device_connection_id == connection_id,
                    WellnessReading.source_event_id.in_(event_ids),
                )
            )
        )

    def add_unique(self, reading: WellnessReading) -> bool:
        """Insert under a savepoint; False when the (connection, source_event_id) key already exists."""
        try:
            with self.db.begin_nested():
                self.db.add(reading)
        except IntegrityError:
            return False
        return True

    def metrics_created_at(self, connection_id: uuid.UUID, created_at: datetime) -> list[str]:
        return list(
            self.db.scalars(
                select(WellnessReading.metric_type).where(
                    WellnessReading.device_connection_id == connection_id,
                    WellnessReading.created_at == created_at,
                )
            )
        )
