"""Next-action recommendations (FR-023): derived from the latest published insight, else none."""

import re

from sqlalchemy.orm import Session

from app.models import Insight, Recommendation
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation_schemas import RecommendationItem, RecommendationResponse
from app.services.safety import is_safe_recommendation

_EVIDENCE = re.compile(r"^\d+ (\w+) readings over \d+ days \(([+-]?[\d.]+)%\)")

# (metric, direction) -> (action, reason, suggested goal type). Anything else yields no recommendation.
_RULES: dict[tuple[str, str], tuple[str, str, str | None]] = {
    (
        "sleep_hours",
        "down",
    ): (
        "Set a regular bedtime for the next 7 days",
        "Your sleep duration has fallen over the last 2 weeks.",
        "sleep_improvement",
    ),
    (
        "steps",
        "down",
    ): (
        "Add a short walk to your day for the next 7 days",
        "Your daily steps have fallen over the last 2 weeks.",
        None,
    ),
}

_GOAL_BY_TEXT = {rule[0]: rule[2] for rule in _RULES.values()}


def derive(insight: Insight) -> tuple[str, str, str | None] | None:
    if insight.status != "published":
        return None
    match = _EVIDENCE.match(insight.evidence_summary or "")
    if match is None:
        return None
    direction = "down" if float(match.group(2)) < 0 else "up"
    rule = _RULES.get((match.group(1), direction))
    if rule is None or not is_safe_recommendation(rule[0], rule[1]):
        return None
    return rule


class RecommendationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RecommendationRepository(db)

    def create_for_insight(self, insight: Insight) -> Recommendation | None:
        """Persist the recommendation for a published insight (idempotent); None when not appropriate."""
        existing = self.repo.for_insight(insight.id)
        if existing is not None:
            return existing
        rule = derive(insight)
        if rule is None:
            return None
        return self.repo.add(
            user_id=insight.user_id, insight_id=insight.id, action_text=rule[0], reason_text=rule[1]
        )

    def select(self, user_id: int) -> RecommendationResponse:
        insight = self.repo.latest_insight(user_id)
        if insight is None or insight.status != "published":
            return RecommendationResponse(status="none")
        row = self.repo.for_insight(insight.id)
        if row is None:
            row = self.create_for_insight(insight)
            if row is None:
                return RecommendationResponse(status="none")
            self.db.commit()
        goal = _GOAL_BY_TEXT.get(row.action_text)
        item = RecommendationItem(
            id=row.id,
            insight_id=row.insight_id,
            action_text=row.action_text,
            reason_text=row.reason_text,
            suggested_goal_type=goal,
        )
        return RecommendationResponse(
            status="available",
            action_text=row.action_text,
            reason_text=row.reason_text,
            insight_id=row.insight_id,
            suggested_goal_type=goal,
            items=[item],
        )
