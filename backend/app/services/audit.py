"""AuditService: safe audit events (no health values, passwords or tokens)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.context import get_correlation_id
from app.models import AuditLog
from app.repositories.audit import AuditRepository

_FORBIDDEN_KEYS = {
    "password",
    "token",
    "access_token",
    "authorization",
    "secret",
    "value",
    "reading",
    "readings",
    "credential",
    "credentials",
}


def sanitize_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for key, val in (metadata or {}).items():
        if key.lower() in _FORBIDDEN_KEYS:
            continue
        clean[key] = val if isinstance(val, str | int | bool | float | type(None)) else str(val)
    return clean


class AuditService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.repo = AuditRepository(db)
        self.clock = clock or SystemClock()

    def record(
        self,
        event_type: str,
        *,
        entity_type: str,
        account_id: uuid.UUID | None = None,
        entity_id: uuid.UUID | None = None,
        severity: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.repo.add(
            AuditLog(
                account_id=account_id,
                correlation_id=get_correlation_id(),
                event_type=event_type,
                severity=severity,
                entity_type=entity_type,
                entity_id=entity_id,
                event_metadata=sanitize_metadata(metadata),
                occurred_at=self.clock.utc_now(),
            )
        )
