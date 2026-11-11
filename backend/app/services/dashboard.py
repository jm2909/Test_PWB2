"""DashboardCompositionService: bounded, owner-only, read-only composition (LLD 3.3)."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.config import Settings, get_settings
from app.repositories.connection import ConnectionRepository
from app.repositories.insight import InsightRepository
from app.repositories.reading import ReadingRepository
from app.schemas.dashboard import (
    DashboardAlertResponse,
    DashboardGoalResponse,
    DashboardInsightResponse,
    DashboardResponse,
    MeasurementResponse,
    SourceStatusResponse,
    UnavailableCategoryResponse,
)
from app.services.alert import AlertService
from app.services.freshness import effective_status
from app.services.goal import GoalService

DASHBOARD_METRICS: tuple[str, ...] = ("weight", "steps", "sleep_duration", "active_minutes")
MIN_READINGS_FOR_TREND = 3


class DashboardCompositionService:
    def __init__(
        self, db: DbSession, clock: Clock | None = None, settings: Settings | None = None
    ) -> None:
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()
        self.readings = ReadingRepository(db)
        self.connections = ConnectionRepository(db)
        self.alert_service = AlertService(db, self.clock)
        self.goal_service = GoalService(db, self.clock)
        self.insights = InsightRepository(db)

    def compose(self, account_id: uuid.UUID) -> DashboardResponse:
        now = self.clock.utc_now()
        stale_after = timedelta(hours=self.settings.freshness_stale_after_hours)

        measurements: list[MeasurementResponse] = []
        unavailable: list[UnavailableCategoryResponse] = []
        counts: dict[str, int] = {}
        for metric in DASHBOARD_METRICS:
            reading = self.readings.latest_for_metric(account_id, metric)
            if reading is None:
                unavailable.append(UnavailableCategoryResponse(metric_type=metric))
                continue
            captured = ensure_utc(reading.captured_at)
            measurements.append(
                MeasurementResponse(
                    metric_type=metric,
                    value=reading.value,
                    unit=reading.unit,
                    source=reading.source,
                    captured_at=captured,
                    status="current" if now - captured <= stale_after else "stale",
                )
            )
            counts[metric] = self.readings.count_for_metric(account_id, metric)

        source_statuses = []
        for conn in self.connections.list_for_owner(account_id):
            if conn.status == "disconnected":
                continue
            status = effective_status(conn.status, conn.last_successful_sync_at, now, stale_after)
            source_statuses.append(
                SourceStatusResponse(
                    id=conn.id,
                    source=conn.source,
                    provider=conn.provider,
                    display_label=conn.display_label,
                    status=status,
                    last_successful_sync_at=conn.last_successful_sync_at,
                )
            )

        alerts = [
            DashboardAlertResponse(
                id=a.id,
                metric_type=a.metric_type,
                event_at=a.event_at,
                reason=a.reason,
                state=a.state,
                acknowledged_at=a.acknowledged_at,
                wellness_boundary=a.wellness_boundary,
            )
            for a in self.alert_service.list_alerts(account_id, "active", 20, 0).items
        ]
        goals = [
            DashboardGoalResponse(
                id=g.id,
                category=g.category,
                metric_type=g.metric_type,
                target_value=g.target_value,
                target_unit=g.target_unit,
                target_date=g.target_date,
                state=g.state,
                progress_status=g.progress_status,
                current_value=g.current_value,
            )
            for g in self.goal_service.list_active(account_id)
        ]

        cards = [
            DashboardInsightResponse(
                id=i.id,
                metric_type=i.metric_type,
                status="available",
                observation_period_start=i.observation_period_start,
                observation_period_end=i.observation_period_end,
                observation=i.observation,
                wellness_guidance=i.wellness_guidance,
                uncertainty=i.uncertainty,
            )
            for i in self.insights.list_recent_for_owner(account_id)
        ]
        covered = {c.metric_type for c in cards}
        for metric, count in counts.items():
            if count < MIN_READINGS_FOR_TREND and metric not in covered:
                cards.append(
                    DashboardInsightResponse(
                        id=None,
                        metric_type=metric,
                        status="insufficient_data",
                        observation_period_start=None,
                        observation_period_end=None,
                        observation="Not enough readings yet to show a trend.",
                        wellness_guidance="Keep recording readings to see how this changes.",
                        uncertainty="No trend is shown until more readings are available.",
                    )
                )

        return DashboardResponse(
            measurements=measurements,
            source_statuses=source_statuses,
            alerts=alerts,
            goals=goals,
            insights=cards,
            unavailable_categories=unavailable,
        )
