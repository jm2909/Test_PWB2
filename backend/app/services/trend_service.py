"""Chronological metric trends (FR-014) built only from stored readings."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.database import utcnow
from app.repositories.reading_repository import ReadingRepository
from app.schemas.trend_schemas import TrendPoint, TrendResponse

METRICS: dict[str, tuple[str, str, str, str]] = {
    # api metric -> (stored metric, label, unit, source label)
    "weight": ("weight", "Weight", "kg", "Smart scale"),
    "body_fat": ("body_fat", "Body fat", "%", "Smart scale"),
    "sleep_duration": ("sleep_hours", "Sleep duration", "h", "Wearable"),
    "resting_heart_rate": ("resting_heart_rate", "Resting heart rate", "bpm", "Wearable"),
    "steps": ("steps", "Steps", "steps", "Wearable"),
}
MIN_READINGS = 3
MIN_SPAN_DAYS = 3
MIN_SPAN_FRACTION = 0.25
UNAVAILABLE = "A reliable trend is not available yet."


class UnsupportedMetricError(ValueError):
    pass


class TrendExplanationService:
    def __init__(self, db: Session) -> None:
        self.readings = ReadingRepository(db)

    def trend(self, user_id: int, metric_type: str, period_days: int) -> TrendResponse:
        if metric_type not in METRICS:
            raise UnsupportedMetricError(metric_type)
        stored, label, unit, source = METRICS[metric_type]
        since = utcnow() - timedelta(days=period_days)
        rows = self.readings.list_metric_since(user_id, stored, since)
        points = [TrendPoint(observed_at=r.observed_at, value=float(r.value_numeric)) for r in rows]
        span = (rows[-1].observed_at - rows[0].observed_at).total_seconds() / 86400 if rows else 0.0
        enough = len(rows) >= MIN_READINGS and span >= max(MIN_SPAN_DAYS, MIN_SPAN_FRACTION * period_days)
        if not enough:
            return TrendResponse(
                metric_type=metric_type,
                period_days=period_days,
                status="insufficient_history",
                points=points,
                explanation=f"{UNAVAILABLE} Keep syncing {label.lower()} readings to build more history.",
                reading_count=len(rows),
                source_label=source,
            )
        first, last = points[0].value, points[-1].value
        change = last - first
        if first and abs(change / first) < 0.01:
            direction = "stayed about the same"
        else:
            direction = f"{'risen' if change > 0 else 'fallen'} by {abs(change):.1f} {unit}"
        return TrendResponse(
            metric_type=metric_type,
            period_days=period_days,
            status="available",
            points=points,
            explanation=(
                f"Over the last {period_days} days your {label.lower()} has {direction}, "
                f"from {first:.1f} to {last:.1f} {unit}. This is wellness information, not medical advice."
            ),
            reading_count=len(rows),
            source_label=source,
        )
