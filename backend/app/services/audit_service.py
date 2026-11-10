"""Audit trail. Records ids, action names and outcomes only - never emails or health values."""

import structlog
from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditRepository

log = structlog.get_logger("audit")


class AuditService:
    def __init__(self, db: Session) -> None:
        self.repo = AuditRepository(db)

    def record(
        self,
        *,
        action: str,
        outcome: str,
        correlation_id: str,
        user_id: int | None = None,
        severity: str = "info",
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> None:
        self.repo.add(
            user_id=user_id,
            action=action,
            outcome=outcome,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
        )
        log.info("audit", action=action, outcome=outcome, user_id=user_id)
