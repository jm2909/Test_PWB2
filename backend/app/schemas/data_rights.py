from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_NUMERIC_MEASUREMENT = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:kg|lbs?|bpm|mmhg|mg/dl|steps|hours?|h|cm|%)\b", re.I
)


class DataRightsRequestCreate(BaseModel):
    request_type: Literal["export", "deletion"]
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("description")
    @classmethod
    def _no_health_values(cls, value: str | None) -> str | None:
        if value is not None and _NUMERIC_MEASUREMENT.search(value):
            raise ValueError("Description must not include health values")
        return value


class DataRightsRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reference: str
    request_type: str
    status: str
    requested_at: datetime
    fulfillment_due_at: datetime
