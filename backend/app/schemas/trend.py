from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class ConnectionStatusResponse(BaseModel):
    id: uuid.UUID
    source: str
    provider: str | None
    display_label: str
    status: str
    last_successful_sync_at: datetime | None
    recovery_action: str | None


class TrendPoint(BaseModel):
    captured_at: datetime
    value: Decimal


class TrendResponse(BaseModel):
    metric_type: str
    unit: str
    range: str
    range_label: str
    points: list[TrendPoint]
    status: str
    explanation: str | None
