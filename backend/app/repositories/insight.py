from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import Insight, InsightFeedback, Reading


class InsightRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def list_recent_for_owner(self, account_id: uuid.UUID, limit: int = 5) -> list[Insight]:
        return list(
            self.db.scalars(
                select(Insight)
                .where(Insight.account_id == account_id)
                .order_by(Insight.created_at.desc(), Insight.id.desc())
                .limit(limit)
            )
        )

    def list_page(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Insight], int]:
        total = self.db.scalar(
            select(func.count()).select_from(Insight).where(Insight.account_id == account_id)
        )
        rows = self.db.scalars(
            select(Insight)
            .where(Insight.account_id == account_id)
            .order_by(Insight.created_at.desc(), Insight.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total or 0)

    def get_owned(self, account_id: uuid.UUID, insight_id: uuid.UUID) -> Insight | None:
        return self.db.scalar(
            select(Insight).where(Insight.id == insight_id, Insight.account_id == account_id)
        )

    def find_for_metric(self, account_id: uuid.UUID, metric_type: str) -> Insight | None:
        return self.db.scalar(
            select(Insight).where(
                Insight.account_id == account_id, Insight.metric_type == metric_type
            )
        )

    def add(self, entry: Insight) -> Insight:
        self.db.add(entry)
        self.db.flush()
        return entry

    def find_feedback(self, account_id: uuid.UUID, insight_id: uuid.UUID) -> InsightFeedback | None:
        return self.db.scalar(
            select(InsightFeedback).where(
                InsightFeedback.insight_id == insight_id, InsightFeedback.account_id == account_id
            )
        )

    def add_feedback(self, entry: InsightFeedback) -> InsightFeedback:
        self.db.add(entry)
        self.db.flush()
        return entry

    def reading_values(
        self, account_id: uuid.UUID, metric_type: str, start: datetime, end: datetime
    ) -> list[tuple[datetime, float]]:
        rows = self.db.execute(
            select(Reading.captured_at, Reading.value)
            .where(
                Reading.account_id == account_id,
                Reading.metric_type == metric_type,
                Reading.captured_at >= start,
                Reading.captured_at <= end,
            )
            .order_by(Reading.captured_at.asc(), Reading.id.asc())
        )
        return [(r[0], float(r[1])) for r in rows]
