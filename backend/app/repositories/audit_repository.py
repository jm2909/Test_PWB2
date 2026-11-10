from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditRepository:
    """Append-only: there is no update or delete."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self,
        *,
        user_id: int | None,
        action: str,
        outcome: str,
        severity: str,
        entity_type: str | None,
        entity_id: str | None,
        correlation_id: str,
    ) -> AuditLog:
        row = AuditLog(
            user_id=user_id,
            action=action,
            outcome=outcome,
            severity=severity,
            entity_type=entity_type,
            entity_id=entity_id,
            correlation_id=correlation_id,
        )
        self.db.add(row)
        self.db.flush()
        return row
