from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

DataCategory = Literal["weight", "body_composition", "steps", "sleep_duration", "active_minutes"]


class ConsentRequest(BaseModel):
    decision: Literal["granted", "withdrawn"]
    notice_version: str = Field(min_length=1, max_length=64)
    data_categories: list[DataCategory] = Field(min_length=1)
    purpose: Literal["wellness_support"]


class ConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision: str
    notice_version: str
    recorded_at: datetime
    collection_allowed: bool
    data_rights_path: str | None = None
