"""ConsentService: append-only consent evidence; the latest record decides."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock
from app.errors import NotFoundError, PermissionDeniedError
from app.models import ConsentRecord
from app.repositories.consent import ConsentRepository
from app.schemas.consent import ConsentRequest, ConsentResponse
from app.services.audit import AuditService

DATA_RIGHTS_PATH = "/data-rights"
CONSENT_REQUIRED_DETAIL = "Active consent is required before connecting a source"


def _to_response(record: ConsentRecord) -> ConsentResponse:
    granted = record.decision == "granted"
    return ConsentResponse(
        id=record.id,
        decision=record.decision,
        notice_version=record.notice_version,
        recorded_at=record.recorded_at,
        collection_allowed=granted,
        data_rights_path=None if granted else DATA_RIGHTS_PATH,
    )


class ConsentService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = ConsentRepository(db)
        self.audit = AuditService(db, self.clock)

    def current(self, account_id: uuid.UUID) -> ConsentResponse:
        record = self.repo.latest_for_account(account_id)
        if record is None:
            raise NotFoundError("Consent record not found")
        return _to_response(record)

    def record(self, account_id: uuid.UUID, command: ConsentRequest) -> ConsentResponse:
        now = self.clock.utc_now()
        record = self.repo.add(
            ConsentRecord(
                account_id=account_id,
                decision=command.decision,
                notice_version=command.notice_version,
                data_categories=list(command.data_categories),
                purpose=command.purpose,
                recorded_at=now,
            )
        )
        self.audit.record(
            "consent.recorded",
            entity_type="consent",
            account_id=account_id,
            entity_id=record.id,
            metadata={"decision": record.decision, "notice_version": record.notice_version},
        )
        self.db.commit()
        return _to_response(record)

    def is_active(self, account_id: uuid.UUID) -> bool:
        record = self.repo.latest_for_account(account_id)
        return record is not None and record.decision == "granted"

    def require_active(self, account_id: uuid.UUID) -> None:
        if not self.is_active(account_id):
            raise PermissionDeniedError(CONSENT_REQUIRED_DETAIL)
