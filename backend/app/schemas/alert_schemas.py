import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    id: uuid.UUID
    trend_name: str
    urgency: Literal["routine", "urgent_direction"]
    what_we_saw: str
    recommended_next_action: str
    care_direction: str | None = None
    created_at: datetime


class AlertListResponse(BaseModel):
    items: list[AlertResponse] = Field(default_factory=list)
    total: int
