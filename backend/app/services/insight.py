"""InsightService: deterministic, wellness-only insights (FR-013, LLD 5.4)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.errors import ConflictError, NotFoundError
from app.models import Insight, InsightFeedback
from app.repositories.insight import InsightRepository
from app.schemas.common import Page
from app.schemas.insight import FeedbackResponse, InsightResponse, ObservationPeriod
from app.services.audit import AuditService
from app.services.content_policy import ensure_allowed

MIN_READINGS = 3
LABELS: dict[str, tuple[str, str]] = {
    "weight": ("weight", "kg"),
    "steps": ("daily step count", "steps"),
    "sleep_duration": ("sleep duration", "hours"),
    "active_minutes": ("active minutes", "minutes"),
    "body_fat_percentage": ("body fat percentage", "%"),
    "resting_heart_rate": ("resting heart rate", "bpm"),
}
GUIDANCE: dict[str, str] = {
    "weight": "Weigh in at a similar time of day so that readings are easier to compare.",
    "steps": "A short daily walk is one practical way to keep your step count steady.",
    "sleep_duration": "A regular bedtime routine can help keep your sleep pattern consistent.",
    "active_minutes": "Spreading activity across the week can make it easier to stay consistent.",
}
DEFAULT_GUIDANCE = "Keep logging readings regularly so that your pattern is easier to see."
NO_GUIDANCE = "Wellness guidance is not offered until enough readings are available."


def _fmt(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


class InsightService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = InsightRepository(db)
        self.audit = AuditService(db, self.clock)

    # ---- generation -----------------------------------------------------------------
    def generate(
        self,
        account_id: uuid.UUID,
        metric_type: str,
        period_days: int,
        min_readings: int = MIN_READINGS,
    ) -> Insight:
        """Build a deterministic insight from readings; persisted after the policy check."""
        now = self.clock.utc_now()
        start = now - timedelta(days=period_days)
        label, unit = LABELS.get(metric_type, (metric_type.replace("_", " "), ""))
        values = [v for _, v in self.repo.reading_values(account_id, metric_type, start, now)]
        suffix = f" {unit}" if unit and unit != "%" else unit
        if len(values) < min_readings:
            observation = (
                f"Only {len(values)} {label} reading(s) were recorded "
                f"in the last {period_days} days."
            )
            guidance = NO_GUIDANCE
            uncertainty = "There are too few readings to describe a pattern, so none is suggested."
        else:
            average = sum(values) / len(values)
            change = values[-1] - values[0]
            direction = "higher" if change > 0 else "lower" if change < 0 else "unchanged"
            observation = (
                f"Your {label} averaged {_fmt(average)}{suffix} over the last {period_days} days "
                f"across {len(values)} readings. The latest reading was "
                + (
                    f"{_fmt(abs(change))}{suffix} {direction} than the first."
                    if change
                    else "unchanged from the first."
                )
            )
            guidance = GUIDANCE.get(metric_type, DEFAULT_GUIDANCE)
            uncertainty = (
                f"Based on {len(values)} readings from your connected or manual sources; "
                "gaps in data may affect this summary."
            )
        return self._persist(
            account_id, metric_type, start, now, observation, guidance, uncertainty
        )

    def _persist(
        self,
        account_id: uuid.UUID,
        metric_type: str,
        start: datetime,
        end: datetime,
        observation: str,
        guidance: str,
        uncertainty: str,
    ) -> Insight:
        ensure_allowed(observation, guidance, uncertainty)  # before anything is stored
        insight = self.repo.add(
            Insight(
                account_id=account_id,
                metric_type=metric_type,
                observation_period_start=start,
                observation_period_end=end,
                observation=observation,
                wellness_guidance=guidance,
                uncertainty=uncertainty,
            )
        )
        self.audit.record(
            "insight.created",
            entity_type="insight",
            account_id=account_id,
            entity_id=insight.id,
            metadata={"metric_type": metric_type},
        )
        return insight

    # ---- queries / feedback ---------------------------------------------------------
    @staticmethod
    def to_response(insight: Insight) -> InsightResponse:
        return InsightResponse(
            id=insight.id,
            metric_type=insight.metric_type,
            observation_period=ObservationPeriod(
                start=insight.observation_period_start, end=insight.observation_period_end
            ),
            observation=insight.observation,
            wellness_guidance=insight.wellness_guidance,
            uncertainty=insight.uncertainty,
            created_at=insight.created_at,
        )

    def list_insights(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> Page[InsightResponse]:
        rows, total = self.repo.list_page(account_id, limit, offset)
        return Page(
            items=[self.to_response(r) for r in rows], limit=limit, offset=offset, total=total
        )

    def submit_feedback(
        self, account_id: uuid.UUID, insight_id: uuid.UUID, useful: bool
    ) -> FeedbackResponse:
        if self.repo.get_owned(account_id, insight_id) is None:
            raise NotFoundError("Insight not found")
        if self.repo.find_feedback(account_id, insight_id) is not None:
            raise ConflictError("Feedback has already been submitted for this insight")
        try:
            with self.db.begin_nested():
                entry = self.repo.add_feedback(
                    InsightFeedback(
                        insight_id=insight_id,
                        account_id=account_id,
                        useful=useful,
                        submitted_at=self.clock.utc_now(),
                    )
                )
        except IntegrityError as exc:
            raise ConflictError("Feedback has already been submitted for this insight") from exc
        self.audit.record(
            "insight.feedback_submitted",
            entity_type="insight",
            account_id=account_id,
            entity_id=insight_id,
            metadata={"useful": useful},
        )
        self.db.commit()
        return FeedbackResponse(
            id=entry.id,
            insight_id=entry.insight_id,
            useful=entry.useful,
            submitted_at=entry.submitted_at,
        )
