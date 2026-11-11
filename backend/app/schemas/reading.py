from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReadingRequest(BaseModel):
    """Loosely typed on purpose: domain rules are applied (and recorded) by ReadingService."""

    metric_type: str = Field(max_length=64)
    value: Decimal = Field(allow_inf_nan=False)
    unit: str = Field(max_length=32)
    source: str = Field(max_length=16)
    captured_at: datetime
    connection_id: uuid.UUID | None = None


class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    metric_type: str
    value: Decimal
    unit: str
    source: str
    captured_at: datetime
    ingested_at: datetime
    connection_id: uuid.UUID | None = None
