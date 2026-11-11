from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class MeasurementResponse(BaseModel):
    metric_type: str
    value: Decimal
    unit: str
    source: str
    captured_at: datetime
    status: Literal["current", "stale"]


class SourceStatusResponse(BaseModel):
    id: uuid.UUID
    source: str
    provider: str
    display_label: str
    status: Literal["pending", "current", "stale", "failed", "disconnected"]
    last_successful_sync_at: datetime | None


class DashboardAlertResponse(BaseModel):
    id: uuid.UUID
    metric_type: str
    event_at: datetime
    reason: str
    state: str
    acknowledged_at: datetime | None = None
    wellness_boundary: str = ""


class DashboardGoalResponse(BaseModel):
    id: uuid.UUID
    category: str
    metric_type: str
    target_value: Decimal
    target_unit: str
    target_date: date
    state: str
    progress_status: str = "data_gap"
    current_value: Decimal | None = None


class DashboardInsightResponse(BaseModel):
    id: uuid.UUID | None
    metric_type: str
    status: Literal["available", "insufficient_data"]
    observation_period_start: datetime | None
    observation_period_end: datetime | None
    observation: str
    wellness_guidance: str
    uncertainty: str


class UnavailableCategoryResponse(BaseModel):
    metric_type: str
    status: Literal["unavailable"] = "unavailable"


class DashboardResponse(BaseModel):
    measurements: list[MeasurementResponse]
    source_statuses: list[SourceStatusResponse]
    alerts: list[DashboardAlertResponse]
    goals: list[DashboardGoalResponse]
    insights: list[DashboardInsightResponse]
    unavailable_categories: list[UnavailableCategoryResponse]
