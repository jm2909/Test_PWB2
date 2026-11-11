"""ReadingService: consent-gated, idempotent reading ingestion (FR-008, LLD 3.2 / 8.1)."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.errors import ConflictError, DomainError
from app.models import Reading, ReadingProcessingOutcome
from app.repositories.connection import ConnectionRepository
from app.repositories.reading import ReadingRepository
from app.schemas.common import Page
from app.schemas.reading import ReadingRequest, ReadingResponse
from app.services.audit import AuditService
from app.services.consent import ConsentService

logger = logging.getLogger("app.readings")

# metric -> (canonical unit, minimum, maximum)
METRICS: dict[str, tuple[str, Decimal, Decimal]] = {
    "weight": ("kg", Decimal("20"), Decimal("500")),
    "body_fat_percentage": ("percent", Decimal("1"), Decimal("75")),
    "steps": ("count", Decimal("0"), Decimal("100000")),
    "sleep_duration": ("hours", Decimal("0"), Decimal("24")),
    "active_minutes": ("minutes", Decimal("0"), Decimal("1440")),
    "resting_heart_rate": ("bpm", Decimal("20"), Decimal("250")),
}
SOURCES = ("manual", "scale", "wearable")
FUTURE_TOLERANCE = timedelta(minutes=5)
MISMATCH_DETAIL = "Idempotency key payload mismatch"
_QUANT = Decimal("0.0001")

ReadingObserver = Callable[[DbSession, Reading], None]
# Observers run after a reading is persisted and before commit (alert evaluation hooks in here).
on_reading_accepted: list[ReadingObserver] = []


class ReadingRejectedError(DomainError):
    status_code = 400
    default_detail = "Reading rejected"


@dataclass(frozen=True)
class IngestResult:
    reading: ReadingResponse
    created: bool


def _same(existing: Reading, command: ReadingRequest, captured: datetime) -> bool:
    return (
        existing.metric_type == command.metric_type
        and Decimal(existing.value).quantize(_QUANT) == command.value.quantize(_QUANT)
        and existing.unit == command.unit
        and ensure_utc(existing.captured_at) == captured
        and existing.connection_id == command.connection_id
    )


class ReadingService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = ReadingRepository(db)
        self.connections = ConnectionRepository(db)
        self.consent = ConsentService(db, self.clock)
        self.audit = AuditService(db, self.clock)

    def _validate(self, account_id: uuid.UUID, command: ReadingRequest) -> str | None:
        """Return a safe reason code, or None when the reading is acceptable."""
        spec = METRICS.get(command.metric_type)
        if spec is None:
            return "unsupported_metric"
        if command.source not in SOURCES:
            return "unsupported_source"
        unit, low, high = spec
        if command.unit != unit:
            return "unit_not_allowed"
        if not command.value.is_finite() or not (low <= command.value <= high):
            return "value_out_of_range"
        captured = command.captured_at
        if captured.tzinfo is None or captured.utcoffset() is None:
            return "timestamp_not_utc"
        if ensure_utc(captured) > self.clock.utc_now() + FUTURE_TOLERANCE:
            return "timestamp_in_future"
        if command.source == "manual":
            if command.connection_id is not None:
                return "connection_not_allowed"
            return None
        if command.connection_id is None:
            return "connection_required"
        conn = self.connections.get_owned(account_id, command.connection_id)
        if conn is None or conn.source != command.source:
            return "connection_not_owned"
        if conn.authorization_state != "authorized" or conn.status == "disconnected":
            return "connection_not_authorized"
        return None

    def _record_outcome(
        self,
        account_id: uuid.UUID,
        key: str | None,
        outcome: str,
        reason: str,
        connection_id: uuid.UUID | None = None,
    ) -> None:
        owned = None
        if connection_id is not None:
            owned = self.connections.get_owned(account_id, connection_id)
        self.repo.add_outcome(
            ReadingProcessingOutcome(
                account_id=account_id,
                connection_id=owned.id if owned else None,
                idempotency_key=key,
                outcome=outcome,
                reason_code=reason,
                occurred_at=self.clock.utc_now(),
            )
        )

    def ingest(
        self, account_id: uuid.UUID, command: ReadingRequest, idempotency_key: str | None
    ) -> IngestResult:
        # 1. consent (before any normalization or persistence)
        self.consent.require_active(account_id)
        key = (idempotency_key or "").strip()
        if not key or len(key) > 128:
            self._record_outcome(account_id, None, "rejected", "idempotency_key_invalid")
            self.db.commit()
            raise ReadingRejectedError("Idempotency-Key header is required")
        # 2. validate
        reason = self._validate(account_id, command)
        if reason is not None:
            self._record_outcome(account_id, key, "rejected", reason, command.connection_id)
            self.audit.record(
                "reading.rejected",
                entity_type="reading",
                account_id=account_id,
                severity="warning",
                metadata={"reason_code": reason, "source": command.source[:16]},
            )
            self.db.commit()
            raise ReadingRejectedError(f"Reading rejected: {reason}")
        captured = ensure_utc(command.captured_at)
        # 3. dedupe
        existing = self.repo.find_by_key(account_id, command.source, key)
        if existing is not None:
            return self._replay(account_id, existing, command, key, captured)
        # 4. persist
        now = self.clock.utc_now()
        reading = Reading(
            account_id=account_id,
            connection_id=command.connection_id,
            metric_type=command.metric_type,
            value=command.value.quantize(_QUANT),
            unit=command.unit,
            source=command.source,
            captured_at=captured,
            ingested_at=now,
            idempotency_key=key,
        )
        try:
            with self.db.begin_nested():
                self.repo.add(reading)
        except IntegrityError:
            raced = self.repo.find_by_key(account_id, command.source, key)
            if raced is None:
                raise
            return self._replay(account_id, raced, command, key, captured)
        self._record_outcome(account_id, key, "accepted", "ok", command.connection_id)
        # 5. evaluate rules (observers), 6. update source sync state
        for observer in list(on_reading_accepted):
            observer(self.db, reading)
        if command.connection_id is not None:
            conn = self.connections.get_owned(account_id, command.connection_id)
            if conn is not None:
                conn.last_successful_sync_at = now
                conn.last_failure_code = None
                if conn.status in ("pending", "stale", "failed"):
                    conn.status = "current"
        self.audit.record(
            "reading.accepted",
            entity_type="reading",
            account_id=account_id,
            entity_id=reading.id,
            metadata={"metric_type": reading.metric_type, "source": reading.source},
        )
        self.db.commit()
        return IngestResult(ReadingResponse.model_validate(reading), True)

    def _replay(
        self,
        account_id: uuid.UUID,
        existing: Reading,
        command: ReadingRequest,
        key: str,
        captured: datetime,
    ) -> IngestResult:
        if not _same(existing, command, captured):
            self._record_outcome(
                account_id, key, "rejected", "idempotency_mismatch", command.connection_id
            )
            self.db.commit()
            raise ConflictError(MISMATCH_DETAIL)
        self._record_outcome(
            account_id, key, "duplicate", "idempotent_replay", existing.connection_id
        )
        self.db.commit()
        return IngestResult(ReadingResponse.model_validate(existing), False)

    def list_readings(
        self,
        account_id: uuid.UUID,
        metric_type: str | None,
        start: datetime | None,
        end: datetime | None,
        limit: int,
        offset: int,
    ) -> Page[ReadingResponse]:
        rows, total = self.repo.list_for_owner(
            account_id,
            metric_type,
            ensure_utc(start) if start else None,
            ensure_utc(end) if end else None,
            limit,
            offset,
        )
        return Page[ReadingResponse](
            items=[ReadingResponse.model_validate(r) for r in rows],
            limit=limit,
            offset=offset,
            total=total,
        )
