from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

AlertState = Literal["active", "acknowledged"]


class AlertResponse(BaseModel):
    id: uuid.UUID
    metric_type: str
    event_at: datetime
    reason: str
    rule_identifier: str
    rule_version: str
    state: str
    acknowledged_at: datetime | None
    wellness_boundary: str
