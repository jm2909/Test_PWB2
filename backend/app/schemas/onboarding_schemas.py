from typing import Any, Literal

from pydantic import BaseModel, Field

DeviceNextStep = Literal["scale", "wearable", "later"]


class OnboardingUpdate(BaseModel):
    profile: dict[str, Any]
    goal_intent: str = Field(max_length=80)
    device_next_step: DeviceNextStep


class OnboardingResponse(BaseModel):
    profile: dict[str, Any]
    goal_intent: str
    device_next_step: str
    status: str
    remaining_steps: list[str]
