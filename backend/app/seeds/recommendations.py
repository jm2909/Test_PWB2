"""Seed recommendations: Asha's sleep recommendation; Meena's suppressed insight yields none."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Insight
from app.seeds import register
from app.seeds.users import user_id
from app.services.recommendation_service import RecommendationService


@register("recommendations", order=50)
def seed_recommendations(db: Session) -> None:
    asha = user_id(db, "asha")
    insight = db.scalar(
        select(Insight).where(Insight.user_id == asha, Insight.status == "published").limit(1)
    )
    if insight is not None:
        RecommendationService(db).create_for_insight(insight)
        db.flush()
