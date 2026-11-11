"""TrendService: owner-only metric series with explicit insufficient-data state (FR-012)."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.errors import NotFoundError
from app.repositories.reading import ReadingRepository
from app.schemas.trend import TrendPoint, TrendResponse
from app.services.reading import METRICS

# range code -> (days, label, minimum points for a trend)
RANGES: dict[str, tuple[int, str, int]] = {
    "7d": (7, "Last 7 days", 3),
    "30d": (30, "Last 30 days", 5),
    "90d": (90, "Last 90 days", 7),
    "365d": (365, "Last 365 days", 10),
}


class TrendService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.clock = clock or SystemClock()
        self.readings = ReadingRepository(db)

    def trend(self, account_id: uuid.UUID, metric_type: str, range_code: str) -> TrendResponse:
        spec = METRICS.get(metric_type)
        if spec is None:
            raise NotFoundError("Metric is not supported")
        unit = spec[0]
        days, label, minimum = RANGES[range_code]
        start = self.clock.utc_now() - timedelta(days=days)
        rows = self.readings.series_for_metric(account_id, metric_type, start)
        points = [TrendPoint(captured_at=ensure_utc(r.captured_at), value=r.value) for r in rows]
        if len(points) < minimum:
            return TrendResponse(
                metric_type=metric_type,
                unit=unit,
                range=range_code,
                range_label=label,
                points=points,
                status="insufficient_data",
                explanation=(
                    f"A trend is not available: {len(points)} reading(s) in the {label.lower()}, "
                    f"at least {minimum} are needed."
                ),
            )
        return TrendResponse(
            metric_type=metric_type,
            unit=unit,
            range=range_code,
            range_label=label,
            points=points,
            status="available",
            explanation=None,
        )
