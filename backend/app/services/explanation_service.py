"""Plain-language, non-diagnostic metric explanations (FR-015)."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.database import utcnow
from app.repositories.reading_repository import ReadingRepository
from app.schemas.explanation_schemas import MetricExplanationResponse
from app.services.safety import contains_diagnostic_language
from app.services.trend_service import (
    METRICS,
    MIN_READINGS,
    MIN_SPAN_DAYS,
    MIN_SPAN_FRACTION,
    UnsupportedMetricError,
)

UNSUPPORTED_METRICS = {"body_fat"}
UNAVAILABLE_TEXT = "We can't explain this metric yet. We would rather not guess."
INSUFFICIENT_TEXT = "A reliable explanation is not available yet. Keep syncing to build more history."
STEADY_THRESHOLD = 0.01


class TrendExplanationService:
    """Explains the direction of a metric; never interprets it clinically."""

    def __init__(self, db: Session) -> None:
        self.readings = ReadingRepository(db)

    def explain(self, user_id: int, metric_type: str, period_days: int) -> MetricExplanationResponse:
        if metric_type not in METRICS:
            raise UnsupportedMetricError(metric_type)
        stored, label, unit, source = METRICS[metric_type]
        if metric_type in UNSUPPORTED_METRICS:
            return self._unavailable(source)
        rows = self.readings.list_metric_since(user_id, stored, utcnow() - timedelta(days=period_days))
        span = (rows[-1].observed_at - rows[0].observed_at).total_seconds() / 86400 if rows else 0.0
        if len(rows) < MIN_READINGS or span < max(MIN_SPAN_DAYS, MIN_SPAN_FRACTION * period_days):
            return MetricExplanationResponse(
                status="insufficient_history",
                direction=None,
                explanation=INSUFFICIENT_TEXT,
                reading_count=len(rows),
                source_label=source,
            )
        first, last = float(rows[0].value_numeric), float(rows[-1].value_numeric)
        change = last - first
        if first and abs(change / first) < STEADY_THRESHOLD:
            direction = "steady"
            text = (
                f"Your {label.lower()} has stayed about the same over the last {period_days} days. "
                "Day-to-day changes are normal, so look at the overall direction."
            )
        else:
            direction = "up" if change > 0 else "down"
            word = "gone up" if change > 0 else "gone down"
            text = (
                f"Your {label.lower()} has {word} gradually over the last {period_days} days, "
                f"about {abs(change):.1f} {unit}. "
                "Day-to-day changes are normal, so look at the overall direction."
            )
        if contains_diagnostic_language(text):
            return self._unavailable(source, len(rows))
        return MetricExplanationResponse(
            status="available",
            direction=direction,  # type: ignore[arg-type]
            explanation=text,
            reading_count=len(rows),
            source_label=source,
        )

    @staticmethod
    def _unavailable(source: str, count: int = 0) -> MetricExplanationResponse:
        return MetricExplanationResponse(
            status="unavailable",
            direction=None,
            explanation=UNAVAILABLE_TEXT,
            reading_count=count,
            source_label=source,
        )
