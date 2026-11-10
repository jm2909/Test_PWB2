import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Provider = Literal["sapphire_scale", "wearable_platform_a", "wearable_platform_b", "wearable_platform_c"]
ConnectionMode = Literal["pair", "authorize"]


class DeviceConnectionCreate(BaseModel):
    provider: Provider
    connection_mode: ConnectionMode
    authorization_code: str | None = Field(default=None, max_length=256)


class SyncSummary(BaseModel):
    new_readings: int = 0
    by_metric: dict[str, int] = Field(default_factory=dict)
    duplicates: int = 0


class DeviceConnectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    status: str
    permitted_categories: list[str]
    last_successful_sync_at: datetime | None = None
    failure_reason: str | None = None
    recovery_action: str | None = None
    last_sync_summary: SyncSummary | None = None


class DeviceConnectionListResponse(BaseModel):
    items: list[DeviceConnectionResponse]
    total: int
