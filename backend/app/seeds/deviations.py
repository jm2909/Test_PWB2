"""Seed deviation events: Asha has a heart-rate rise and a sustained heart-rate event; Meena none."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviationEvent, WellnessReading
from app.repositories.deviation_repository import DeviationRepository
from app.seeds import register
from app.seeds.users import user_id

SEED_EVENTS = [
    ("rhr_rise_14d", "Resting heart rate rising over 14 days"),
    ("rhr_sustained_14d", "Resting heart rate sustained above your usual range"),
]


@register("deviations", order=35)
def seed_deviations(db: Session) -> None:
    asha = user_id(db, "asha")
    reading = db.scalar(
        select(WellnessReading)
        .where(WellnessReading.user_id == asha, WellnessReading.metric_type == "resting_heart_rate")
        .order_by(WellnessReading.observed_at.desc())
    )
    if reading is None:
        return
    repo = DeviationRepository(db)
    for code, name in SEED_EVENTS:
        if not repo.exists(reading.id, code):
            db.add(
                DeviationEvent(
                    user_id=asha, wellness_reading_id=reading.id, criterion_code=code, trend_name=name
                )
            )
