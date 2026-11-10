from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Insight, Recommendation
from app.seeds.users import user_id
from app.services.recommendation_service import RecommendationService


def test_asha_available(seeded: Session) -> None:
    res = RecommendationService(seeded).select(user_id(seeded, "asha"))
    assert res.status == "available"
    assert res.action_text == "Set a regular bedtime for the next 7 days"
    assert res.reason_text == "Your sleep duration has fallen over the last 2 weeks."
    assert res.suggested_goal_type == "sleep_improvement"
    assert res.insight_id is not None


def test_meena_none(seeded: Session) -> None:
    res = RecommendationService(seeded).select(user_id(seeded, "meena"))
    assert res.status == "none" and res.action_text is None and res.items == []


def test_irrelevant_insight_forces_nothing(seeded: Session) -> None:
    ins = Insight(
        user_id=user_id(seeded, "rohan"),
        status="published",
        evidence_summary="9 weight readings over 20 days (+3.0%).",
        observed_trend="x",
        wellness_implication="y",
    )
    seeded.add(ins)
    seeded.commit()
    assert RecommendationService(seeded).select(user_id(seeded, "rohan")).status == "none"
    assert seeded.scalar(select(Recommendation).where(Recommendation.insight_id == ins.id)) is None


def test_create_is_idempotent(seeded: Session) -> None:
    ins = seeded.scalar(select(Insight).where(Insight.user_id == user_id(seeded, "asha")))
    assert ins is not None
    svc = RecommendationService(seeded)
    a, b = svc.create_for_insight(ins), svc.create_for_insight(ins)
    assert a is not None and b is not None and a.id == b.id
