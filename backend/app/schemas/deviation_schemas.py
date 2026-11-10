import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeviationEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    criterion_code: str
    trend_name: str
    created_at: datetime
    wellness_reading_id: uuid.UUID


class DeviationEventListResponse(BaseModel):
    items: list[DeviationEventResponse] = Field(default_factory=list)
    total: int
