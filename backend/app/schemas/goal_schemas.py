import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GoalType = Literal[
    "weight_loss", "muscle_gain", "sleep_improvement", "blood_pressure_control", "other_supported"
]


class GoalCreate(BaseModel):
    goal_type: GoalType
    target_value: Decimal
    target_unit: str = Field(max_length=24)


class GoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goal_type: str
    target_value: float
    target_unit: str
    status: str


class GoalListResponse(BaseModel):
    items: list[GoalResponse]
    total: int
