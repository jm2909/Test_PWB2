"""Guided onboarding (FR-003): partial saves, resume, and the list of steps still required."""

from typing import Any

from sqlalchemy.orm import Session

from app.repositories.consent_repository import ConsentRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.schemas.onboarding_schemas import OnboardingResponse

STEPS = ("profile", "goal", "device", "consent")
CONSENT_PURPOSES = ("device_processing", "personalized_insights")
DEVICE_CHOICES = ("scale", "wearable", "later")
NOT_STARTED, IN_PROGRESS, COMPLETE = "not_started", "in_progress", "complete"


class OnboardingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OnboardingRepository(db)
        self.consents = ConsentRepository(db)

    def _remaining(self, user_id: int, profile: dict[str, Any], goal: str, device: str) -> list[str]:
        remaining: list[str] = []
        if not profile:
            remaining.append("profile")
        if not goal.strip():
            remaining.append("goal")
        if device not in DEVICE_CHOICES:
            remaining.append("device")
        if any(self.consents.latest(user_id, purpose) is None for purpose in CONSENT_PURPOSES):
            remaining.append("consent")
        return remaining

    def get(self, user_id: int) -> OnboardingResponse:
        row = self.repo.get(user_id)
        if row is None:
            return OnboardingResponse(
                profile={},
                goal_intent="",
                device_next_step="",
                status=NOT_STARTED,
                remaining_steps=self._remaining(user_id, {}, "", ""),
            )
        remaining = self._remaining(user_id, row.profile_json, row.goal_intent, row.device_next_step)
        return OnboardingResponse(
            profile=row.profile_json,
            goal_intent=row.goal_intent,
            device_next_step=row.device_next_step,
            status=COMPLETE if not remaining else IN_PROGRESS,
            remaining_steps=remaining,
        )

    def status(self, user_id: int) -> str:
        return self.get(user_id).status

    def save(
        self, user_id: int, profile: dict[str, Any], goal_intent: str, device_next_step: str
    ) -> OnboardingResponse:
        remaining = self._remaining(user_id, profile, goal_intent, device_next_step)
        self.repo.upsert(
            user_id, profile, goal_intent, device_next_step, COMPLETE if not remaining else IN_PROGRESS
        )
        self.db.commit()
        return self.get(user_id)
