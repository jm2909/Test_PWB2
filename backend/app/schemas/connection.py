from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ScaleConnectRequest(BaseModel):
    device_identifier: str = Field(min_length=1, max_length=128)
    device_label: str = Field(min_length=1, max_length=100)

    @field_validator("device_identifier", "device_label")
    @classmethod
    def _nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    source: str
    external_identifier: str
    status: str
    last_successful_sync_at: datetime | None
    recovery_action: str | None
    message: str | None = None
    provider: str | None = None
    authorization_state: str | None = None


class ProviderResponse(BaseModel):
    provider: str
    display_name: str
    authorization_mode: str


class AuthorizationResponse(BaseModel):
    connection_id: uuid.UUID
    authorization_url: str
    expires_at: datetime


class CallbackRequest(BaseModel):
    connection_id: uuid.UUID
    state: str = Field(default="", max_length=256)
    code: str | None = Field(default=None, max_length=256)
    error: str | None = Field(default=None, max_length=256)
