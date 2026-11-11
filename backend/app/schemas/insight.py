from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, StrictBool


class ObservationPeriod(BaseModel):
    start: datetime
    end: datetime


class InsightResponse(BaseModel):
    id: uuid.UUID
    metric_type: str
    observation_period: ObservationPeriod
    observation: str
    wellness_guidance: str
    uncertainty: str
    created_at: datetime


class FeedbackRequest(BaseModel):
    useful: StrictBool


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    insight_id: uuid.UUID
    useful: bool
    submitted_at: datetime
