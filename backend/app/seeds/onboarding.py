"""Seed onboarding: asha and meena complete; rohan has profile, goal and device saved (consent remains)."""

from sqlalchemy.orm import Session

from app.repositories.onboarding_repository import OnboardingRepository
from app.seeds import register
from app.seeds.users import user_id
from app.services.onboarding_service import COMPLETE, IN_PROGRESS


@register("onboarding", order=30)
def seed_onboarding(db: Session) -> None:
    repo = OnboardingRepository(db)
    entries = {
        "asha": ({"display_name": "Asha", "age_range": "30-39"}, "lose_weight", "scale", COMPLETE),
        "meena": ({"display_name": "Meena", "age_range": "40-49"}, "improve_sleep", "wearable", COMPLETE),
    }
    for persona, (profile, goal, device, status) in entries.items():
        uid = user_id(db, persona)
        if repo.get(uid) is None:
            repo.upsert(uid, profile, goal, device, status)
    rohan = user_id(db, "rohan")
    if repo.get(rohan) is None:
        repo.upsert(
            rohan, {"display_name": "Rohan", "age_range": "20-29"}, "build_muscle", "wearable", IN_PROGRESS
        )
