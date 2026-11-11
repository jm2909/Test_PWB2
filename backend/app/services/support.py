"""SupportService: record a support request with a non-sensitive reference (FR-023)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.errors import NotFoundError
from app.models import SupportRequest
from app.repositories.alert import AlertRepository
from app.repositories.connection import ConnectionRepository
from app.repositories.support import SupportRepository
from app.schemas.support import SupportRequestCreate, SupportRequestResponse
from app.services.audit import AuditService


class SupportService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = SupportRepository(db)
        self.audit = AuditService(db, self.clock)

    def _check_context(self, account_id: uuid.UUID, command: SupportRequestCreate) -> None:
        if command.context_id is None:
            return
        found = False
        if command.context_type == "device":
            found = (
                ConnectionRepository(self.db).get_owned(account_id, command.context_id) is not None
            )
        elif command.context_type == "alert":
            found = AlertRepository(self.db).get_owned(account_id, command.context_id) is not None
        if not found:
            raise NotFoundError("Support context not found")

    def submit(
        self, account_id: uuid.UUID, command: SupportRequestCreate
    ) -> SupportRequestResponse:
        self._check_context(account_id, command)
        now = self.clock.utc_now()
        record = self.repo.add(
            SupportRequest(
                account_id=account_id,
                reference=f"SUP-{uuid.uuid4().hex[:16].upper()}",
                category=command.category,
                description=command.description,
                context_type=command.context_type,
                context_id=command.context_id,
                status="submitted",
                submitted_at=now,
            )
        )
        # Audit carries identifiers only: never the description or any health value.
        self.audit.record(
            "support.submitted",
            entity_type="support_request",
            account_id=account_id,
            entity_id=record.id,
            metadata={
                "category": record.category,
                "context_type": record.context_type,
                "reference": record.reference,
            },
        )
        self.db.commit()
        return SupportRequestResponse(
            id=record.id,
            reference=record.reference,
            status=record.status,
            submitted_at=record.submitted_at,
        )
