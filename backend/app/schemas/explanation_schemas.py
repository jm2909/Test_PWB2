from typing import Literal

from pydantic import BaseModel, Field


class MetricExplanationRequest(BaseModel):
    metric_type: str = Field(min_length=1, max_length=64)
    period_days: int = Field(ge=7, le=365)


class MetricExplanationResponse(BaseModel):
    status: Literal["available", "unavailable", "insufficient_history"]
    direction: Literal["up", "down", "steady"] | None
    explanation: str
    reading_count: int
    source_label: str
