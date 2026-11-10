from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Insight


class InsightRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self,
        *,
        user_id: int,
        status: str,
        evidence_summary: str,
        observed_trend: str | None,
        wellness_implication: str | None,
        suppression_reason: str | None,
    ) -> Insight:
        row = Insight(
            user_id=user_id,
            status=status,
            evidence_summary=evidence_summary,
            observed_trend=observed_trend,
            wellness_implication=wellness_implication,
            suppression_reason=suppression_reason,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_for_user(self, user_id: int, limit: int, offset: int) -> tuple[list[Insight], int]:
        total = self.db.scalar(select(func.count()).select_from(Insight).where(Insight.user_id == user_id))
        rows = self.db.scalars(
            select(Insight)
            .where(Insight.user_id == user_id)
            .order_by(Insight.created_at.desc(), Insight.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total or 0)
