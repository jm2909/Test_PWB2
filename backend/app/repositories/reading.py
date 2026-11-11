from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import Reading, ReadingProcessingOutcome


class ReadingRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def latest_for_metric(self, account_id: uuid.UUID, metric_type: str) -> Reading | None:
        """Read-only: newest reading for one owner and metric (indexed)."""
        return self.db.scalar(
            select(Reading)
            .where(Reading.account_id == account_id, Reading.metric_type == metric_type)
            .order_by(Reading.captured_at.desc(), Reading.id.desc())
            .limit(1)
        )

    def count_for_metric(self, account_id: uuid.UUID, metric_type: str) -> int:
        rows = self.db.scalars(
            select(Reading.id)
            .where(Reading.account_id == account_id, Reading.metric_type == metric_type)
            .limit(50)
        ).all()
        return len(rows)

    def series_for_metric(
        self, account_id: uuid.UUID, metric_type: str, start: datetime, limit: int = 2000
    ) -> list[Reading]:
        """Owner and metric readings since `start`, oldest first."""
        return list(
            self.db.scalars(
                select(Reading)
                .where(
                    Reading.account_id == account_id,
                    Reading.metric_type == metric_type,
                    Reading.captured_at >= start,
                )
                .order_by(Reading.captured_at, Reading.id)
                .limit(limit)
            )
        )

    def find_by_key(self, account_id: uuid.UUID, source: str, key: str) -> Reading | None:
        return self.db.scalar(
            select(Reading).where(
                Reading.account_id == account_id,
                Reading.source == source,
                Reading.idempotency_key == key,
            )
        )

    def add(self, entry: Reading) -> Reading:
        self.db.add(entry)
        self.db.flush()
        return entry

    def add_outcome(self, entry: ReadingProcessingOutcome) -> ReadingProcessingOutcome:
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_for_owner(
        self,
        account_id: uuid.UUID,
        metric_type: str | None,
        start: datetime | None,
        end: datetime | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Reading], int]:
        conditions = [Reading.account_id == account_id]
        if metric_type:
            conditions.append(Reading.metric_type == metric_type)
        if start is not None:
            conditions.append(Reading.captured_at >= start)
        if end is not None:
            conditions.append(Reading.captured_at <= end)
        total = self.db.scalar(select(func.count()).select_from(Reading).where(*conditions)) or 0
        rows = self.db.scalars(
            select(Reading)
            .where(*conditions)
            .order_by(Reading.captured_at.desc(), Reading.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total)
