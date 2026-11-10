import uuid
from typing import Literal

from pydantic import BaseModel, Field


class RecommendationItem(BaseModel):
    id: uuid.UUID
    insight_id: uuid.UUID
    action_text: str
    reason_text: str
    suggested_goal_type: str | None = None


class RecommendationResponse(BaseModel):
    """status 'none' means no appropriate recommendation: the other fields are null."""

    status: Literal["available", "none"]
    action_text: str | None = None
    reason_text: str | None = None
    insight_id: uuid.UUID | None = None
    suggested_goal_type: str | None = None
    items: list[RecommendationItem] = Field(default_factory=list)
