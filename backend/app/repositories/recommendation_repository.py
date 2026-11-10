import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Insight, Recommendation


class RecommendationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def latest_insight(self, user_id: int) -> Insight | None:
        return self.db.scalar(
            select(Insight)
            .where(Insight.user_id == user_id)
            .order_by(Insight.created_at.desc(), Insight.id)
            .limit(1)
        )

    def for_insight(self, insight_id: uuid.UUID) -> Recommendation | None:
        return self.db.scalar(select(Recommendation).where(Recommendation.insight_id == insight_id).limit(1))

    def add(
        self, *, user_id: int, insight_id: uuid.UUID, action_text: str, reason_text: str
    ) -> Recommendation:
        row = Recommendation(
            user_id=user_id, insight_id=insight_id, action_text=action_text, reason_text=reason_text
        )
        self.db.add(row)
        self.db.flush()
        return row
