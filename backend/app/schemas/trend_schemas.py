from datetime import datetime
from typing import Literal

from pydantic import BaseModel

TrendMetric = Literal["weight", "body_fat", "sleep_duration", "resting_heart_rate", "steps"]


class TrendPoint(BaseModel):
    observed_at: datetime
    value: float


class TrendResponse(BaseModel):
    metric_type: str
    period_days: int
    status: Literal["available", "insufficient_history"]
    points: list[TrendPoint]
    explanation: str
    reading_count: int
    source_label: str
