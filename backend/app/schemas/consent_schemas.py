import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ConsentPurpose = Literal["device_processing", "personalized_insights"]
ConsentStatus = Literal["accepted", "declined"]


class ConsentCreate(BaseModel):
    purpose: ConsentPurpose
    version: str = Field(min_length=1, max_length=32)
    status: ConsentStatus


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    purpose: ConsentPurpose
    version: str
    status: ConsentStatus
    recorded_at: datetime


class ConsentListResponse(BaseModel):
    items: list[ConsentResponse]  # full history, newest first
    total: int
    latest: list[ConsentResponse]  # current choice per purpose
