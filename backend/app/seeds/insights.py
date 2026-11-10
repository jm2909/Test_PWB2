"""Seed insights: Asha has a published sleep insight, Meena a suppressed one (sparse data)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Insight
from app.seeds import register
from app.seeds.users import user_id


@register("insights", order=40)
def seed_insights(db: Session) -> None:
    asha = user_id(db, "asha")
    if db.scalar(select(Insight.id).where(Insight.user_id == asha)) is None:
        db.add(
            Insight(
                user_id=asha,
                status="published",
                evidence_summary="14 sleep_hours readings over 13 days (-15.1%).",
                observed_trend=(
                    "Your nightly sleep decreased from 7.2 to 6.1 h over 13 days (15.1% change, 14 readings)."
                ),
                wellness_implication=(
                    "Shorter sleep can affect energy and recovery; consider a steadier bedtime this week."
                ),
            )
        )
    meena = user_id(db, "meena")
    if db.scalar(select(Insight.id).where(Insight.user_id == meena)) is None:
        db.add(
            Insight(
                user_id=meena,
                status="suppressed",
                evidence_summary="No sufficient evidence.",
                suppression_reason="insufficient_evidence",
            )
        )
    db.flush()
