from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class SupportRequestCreate(BaseModel):
    category: Literal["connection", "data_quality", "account", "alert"]
    description: str = Field(min_length=1, max_length=2000)
    context_type: Literal["device", "account", "alert"]
    context_id: uuid.UUID | None = None

    @field_validator("description")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Description must not be blank")
        return value

    @model_validator(mode="after")
    def _account_has_no_context_id(self) -> SupportRequestCreate:
        if self.context_type == "account" and self.context_id is not None:
            raise ValueError("Account context does not take a context_id")
        return self


class SupportRequestResponse(BaseModel):
    id: uuid.UUID
    reference: str
    status: str
    submitted_at: datetime
