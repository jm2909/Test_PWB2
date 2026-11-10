"""Trend-based deviation detection (FR-019): configured criteria over freshly ingested readings."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

import structlog
from sqlalchemy.orm import Session

from app.models import DeviationEvent, WellnessReading
from app.repositories.deviation_repository import DeviationRepository
from app.repositories.reading_repository import ReadingRepository

log = structlog.get_logger("deviation")

WINDOW_DAYS = 14
MIN_WINDOW_READINGS = 3
MIN_WINDOW_SPAN_DAYS = 7.0
SUSTAINED_SPAN_DAYS = 10.0


@dataclass(frozen=True)
class Criterion:
    code: str
    metric: str
    trend_name: str
    check: Callable[[list[float], float], bool]  # (window values oldest->newest, span_days)


RHR_RISE_BPM = 5.0
RHR_USUAL_UPPER_BPM = 65.0  # configured upper bound of the usual resting range
SLEEP_DECLINE_HOURS = 45 / 60
WEIGHT_CHANGE_KG = 2.0


def _rhr_rise(values: list[float], span: float) -> bool:
    return values[-1] - values[0] >= RHR_RISE_BPM


def _rhr_sustained(values: list[float], span: float) -> bool:
    # Every reading in the final week sits above the usual range, over a window of at least 10 days.
    return span >= SUSTAINED_SPAN_DAYS and all(v > RHR_USUAL_UPPER_BPM for v in values[-MIN_WINDOW_READINGS:])


def _sleep_decline(values: list[float], span: float) -> bool:
    return values[0] - values[-1] >= SLEEP_DECLINE_HOURS


def _weight_change(values: list[float], span: float) -> bool:
    return abs(values[-1] - values[0]) >= WEIGHT_CHANGE_KG


CRITERIA: list[Criterion] = [
    Criterion("rhr_rise_14d", "resting_heart_rate", "Resting heart rate rising over 14 days", _rhr_rise),
    Criterion(
        "rhr_sustained_14d",
        "resting_heart_rate",
        "Resting heart rate sustained above your usual range",
        _rhr_sustained,
    ),
    Criterion("sleep_decline_14d", "sleep_hours", "Sleep duration declining over 14 days", _sleep_decline),
    Criterion("weight_change_14d", "weight", "Weight change over 14 days", _weight_change),
]


class DeviationDetectionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.readings = ReadingRepository(db)
        self.events = DeviationRepository(db)

    def evaluate(self, user_id: int, reading_ids: list[uuid.UUID]) -> list[DeviationEvent]:
        """Check each metric's newest new reading against the criteria; one event per (reading, criterion)."""
        newest: dict[str, WellnessReading] = {}
        for reading in self.readings.get_many(user_id, reading_ids):  # ordered by observed_at
            newest[reading.metric_type] = reading
        created: list[DeviationEvent] = []
        for criterion in CRITERIA:
            latest = newest.get(criterion.metric)
            if latest is None:
                continue
            reading = latest
            window = self.readings.list_metric_between(
                user_id,
                criterion.metric,
                reading.observed_at - timedelta(days=WINDOW_DAYS),
                reading.observed_at,
            )
            if len(window) < MIN_WINDOW_READINGS:
                continue
            span = (window[-1].observed_at - window[0].observed_at).total_seconds() / 86400
            if span < MIN_WINDOW_SPAN_DAYS:
                continue
            if not criterion.check([float(r.value_numeric) for r in window], span):
                continue
            event = DeviationEvent(
                user_id=user_id,
                wellness_reading_id=reading.id,
                criterion_code=criterion.code,
                trend_name=criterion.trend_name,
            )
            if self.events.add_unique(event):
                created.append(event)
        return created


def post_ingest_hook(db: Session, user_id: int, reading_ids: list[uuid.UUID]) -> None:
    """Registered with the sync ingestion hook; failures are logged and suppressed."""
    try:
        DeviationDetectionService(db).evaluate(user_id, reading_ids)
        db.commit()
    except Exception:
        db.rollback()
        log.warning("deviation_evaluation_failed")
