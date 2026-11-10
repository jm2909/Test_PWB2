import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID | None
    status: Literal["published", "suppressed"]
    observed_trend: str | None
    wellness_implication: str | None
    suppression_reason: str | None


class InsightListResponse(BaseModel):
    items: list[InsightResponse] = Field(default_factory=list)
    total: int
