from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import OnboardingProgress


class OnboardingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> OnboardingProgress | None:
        return self.db.scalar(select(OnboardingProgress).where(OnboardingProgress.user_id == user_id))

    def upsert(
        self, user_id: int, profile: dict[str, Any], goal_intent: str, device_next_step: str, status: str
    ) -> OnboardingProgress:
        row = self.get(user_id)
        if row is None:
            row = OnboardingProgress(
                user_id=user_id,
                profile_json=profile,
                goal_intent=goal_intent,
                device_next_step=device_next_step,
                status=status,
            )
            self.db.add(row)
        else:
            row.profile_json = profile
            row.goal_intent = goal_intent
            row.device_next_step = device_next_step
            row.status = status
        self.db.flush()
        return row
