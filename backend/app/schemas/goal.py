from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

GoalCategory = Literal["weight_management", "fitness", "sleep_improvement", "general_wellness"]


class GoalCreateRequest(BaseModel):
    category: GoalCategory
    metric_type: str = Field(min_length=1, max_length=64)
    target_value: Decimal = Field(gt=0, max_digits=14, decimal_places=4)
    target_unit: str = Field(min_length=1, max_length=32)
    target_date: date


class GoalStateRequest(BaseModel):
    state: Literal["active", "paused", "closed"]


class GoalResponse(BaseModel):
    id: uuid.UUID
    state: str
    category: str
    metric_type: str
    target_value: Decimal
    target_unit: str
    target_date: date
    progress_status: Literal["available", "data_gap"]
    current_value: Decimal | None
