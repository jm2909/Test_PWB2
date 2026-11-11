"""Provider-protocol adapter interfaces. Adapters have no ORM/session dependency."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Protocol


class AdapterUnavailable(Exception):
    pass


class AdapterAuthorizationDenied(Exception):
    pass


class AdapterPayloadInvalid(Exception):
    pass


@dataclass(frozen=True)
class NormalizedReading:
    metric_type: str
    value: Decimal
    unit: str
    captured_at: datetime
    source: str
    provider_event_id: str
    connection_external_id: str | None = None


@dataclass(frozen=True)
class ConnectionResult:
    provider: str
    external_identifier: str
    display_label: str
    authorization_state: str
    status: str


@dataclass(frozen=True)
class AuthorizationStart:
    provider: str
    authorization_url: str
    state: str


class ScaleAdapter(Protocol):
    def link(self, account_id: uuid.UUID, device_identifier: str) -> ConnectionResult: ...

    def normalize(self, payload: dict[str, Any]) -> NormalizedReading: ...


class WearableAdapter(Protocol):
    def begin_authorization(self, account_id: uuid.UUID, provider: str) -> AuthorizationStart: ...

    def complete_authorization(
        self, provider: str, callback: dict[str, Any]
    ) -> ConnectionResult: ...

    def sync(self, connection: ConnectionResult) -> list[NormalizedReading]: ...
