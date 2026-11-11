"""DataRightsService: record export/deletion requests with a reference and deadline."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.config import Settings, get_settings
from app.models import DataRightsRequest
from app.repositories.data_rights import DataRightsRepository
from app.schemas.common import Page
from app.schemas.data_rights import DataRightsRequestCreate, DataRightsRequestResponse
from app.services.audit import AuditService


class DataRightsService:
    def __init__(
        self, db: DbSession, clock: Clock | None = None, settings: Settings | None = None
    ) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.settings = settings or get_settings()
        self.repo = DataRightsRepository(db)
        self.audit = AuditService(db, self.clock)

    def submit(
        self, account_id: uuid.UUID, command: DataRightsRequestCreate
    ) -> DataRightsRequestResponse:
        now = self.clock.utc_now()
        record = self.repo.add(
            DataRightsRequest(
                account_id=account_id,
                reference=f"DR-{uuid.uuid4().hex[:16].upper()}",
                request_type=command.request_type,
                status="submitted",
                requested_at=now,
                fulfillment_due_at=now + timedelta(days=self.settings.data_rights_fulfillment_days),
            )
        )
        # Audit carries identifiers only: never the free-text description or health values.
        self.audit.record(
            "data_rights.requested",
            entity_type="data_rights_request",
            account_id=account_id,
            entity_id=record.id,
            metadata={"request_type": record.request_type, "reference": record.reference},
        )
        self.db.commit()
        return DataRightsRequestResponse.model_validate(record)

    def list_for_owner(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> Page[DataRightsRequestResponse]:
        rows, total = self.repo.list_for_owner(account_id, limit, offset)
        return Page[DataRightsRequestResponse](
            items=[DataRightsRequestResponse.model_validate(r) for r in rows],
            limit=limit,
            offset=offset,
            total=total,
        )
