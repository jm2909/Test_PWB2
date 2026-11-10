"""Synchronize readings: consent gate, idempotency, adapter fetch, normalize, persist, status, hooks."""

import uuid
from collections import Counter
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal

import structlog
from sqlalchemy.orm import Session

from app.adapters.base import AdapterError, DeviceAdapter, RawReading
from app.adapters.registry import build_registry
from app.database import utcnow
from app.models import DeviceConnection, SyncAttempt, WellnessReading
from app.repositories.device_repository import DeviceRepository
from app.repositories.reading_repository import ReadingRepository
from app.repositories.sync_repository import SyncRepository
from app.schemas.device_schemas import SyncSummary
from app.services.audit_service import AuditService
from app.services.consent_service import PURPOSE_DEVICE_PROCESSING, ConsentLedgerService
from app.services.sync_status_service import SyncStatusRecoveryService

log = structlog.get_logger("sync")

PostIngestHook = Callable[[Session, int, list[uuid.UUID]], None]
_HOOKS: list[PostIngestHook] = []

# Idempotency-Key prefixes that route a sync into the provider-fault handling paths (fail/revoke/permission).
_SIM_PREFIXES = {"sim-fail": "fail", "sim-revoke": "revoke", "sim-permission": "permission"}


def register_post_ingest_hook(hook: PostIngestHook) -> None:
    """Called as hook(db, user_id, new_reading_ids) after a sync stored new readings."""
    if hook not in _HOOKS:
        _HOOKS.append(hook)


def clear_post_ingest_hooks() -> None:
    _HOOKS.clear()


class ConnectionNotFoundError(Exception):
    pass


class SyncUnsupportedError(Exception):
    pass


# provider metric -> (canonical metric, canonical unit, converter)
_NORMALIZERS: dict[str, tuple[str, str, Callable[[float], float]]] = {
    "sleep_minutes": ("sleep_hours", "h", lambda v: v / 60.0),
    "hr_resting": ("resting_heart_rate", "bpm", lambda v: v),
    "step_count": ("steps", "steps", lambda v: v),
    "weight": ("weight", "kg", lambda v: v * 0.45359237),
    "body_fat": ("body_fat", "%", lambda v: v),
}


def normalize(
    raw: RawReading, now: datetime, user_id: int, connection_id: uuid.UUID
) -> WellnessReading | None:
    spec = _NORMALIZERS.get(raw.metric)
    if spec is None:
        return None
    metric, unit, convert = spec
    observed = raw.observed_at if raw.observed_at.tzinfo else raw.observed_at.replace(tzinfo=UTC)
    return WellnessReading(
        user_id=user_id,
        device_connection_id=connection_id,
        source_event_id=raw.source_event_id[:128],
        metric_type=metric,
        value_numeric=Decimal(str(round(convert(raw.value), 4))),
        unit=unit,
        observed_at=observed.astimezone(UTC),
        normalized_at=now,
        created_at=now,
    )


class SyncIngestionService:
    def __init__(self, db: Session, adapters: dict[str, DeviceAdapter] | None = None) -> None:
        self.db = db
        self.adapters = adapters if adapters is not None else build_registry()
        self.devices = DeviceRepository(db)
        self.syncs = SyncRepository(db)
        self.readings = ReadingRepository(db)
        self.status = SyncStatusRecoveryService(db)
        self.audit = AuditService(db)

    def sync(
        self, user_id: int, connection_id: uuid.UUID, idempotency_key: str, correlation_id: str
    ) -> tuple[DeviceConnection, SyncSummary]:
        conn = self.devices.get_owned(user_id, connection_id)
        if conn is None:
            raise ConnectionNotFoundError
        adapter = self.adapters.get(conn.provider)
        if adapter is None:
            raise SyncUnsupportedError("Synchronization is not supported for this device.")
        self._assert_consent(user_id, conn, correlation_id)

        existing = self.syncs.find(conn.id, idempotency_key)
        if existing is not None:
            return conn, self._replay(conn, existing)
        now = utcnow()
        attempt = self.syncs.start(conn.id, idempotency_key, now)
        if attempt is None:  # lost a race with the same key: return the original
            original = self.syncs.find(conn.id, idempotency_key)
            assert original is not None
            return conn, self._replay(conn, original)
        self.db.commit()

        try:
            categories = list(conn.permitted_categories) or adapter.connect(None).permitted_categories
            raw = adapter.fetch_readings(categories, now, simulate=self._simulate(conn, idempotency_key))
        except AdapterError as exc:
            status, reason = self.status.mark_failure(conn, exc)
            self.syncs.finish(attempt, "failed", utcnow(), reason)
            self._audit(user_id, conn, "failed", correlation_id, "warning")
            self.db.commit()
            log.info("sync_failed", connection_status=status)
            return conn, SyncSummary()

        new_ids, summary = self._persist(user_id, conn, raw, now)
        if not conn.permitted_categories:  # restored after a failed authorization
            conn.permitted_categories = categories
        self.status.mark_success(conn)
        self.syncs.finish(attempt, "succeeded", utcnow(), None)
        self._audit(user_id, conn, "succeeded", correlation_id, "info")
        self.db.commit()
        self._run_hooks(user_id, new_ids)
        return conn, summary

    # -- internals -------------------------------------------------------
    def _assert_consent(self, user_id: int, conn: DeviceConnection, correlation_id: str) -> None:
        try:
            ConsentLedgerService(self.db).assert_permitted(user_id, PURPOSE_DEVICE_PROCESSING)
        except Exception:
            self._audit(user_id, conn, "blocked_no_consent", correlation_id, "warning")
            self.db.commit()
            raise

    @staticmethod
    def _simulate(conn: DeviceConnection, key: str) -> str | None:
        if conn.status == "revoked":
            return "revoke"
        if conn.status == "action_required":
            return "permission"
        for prefix, fault in _SIM_PREFIXES.items():
            if key.startswith(prefix):
                return fault
        return None

    def _persist(
        self, user_id: int, conn: DeviceConnection, raw: list[RawReading], now: datetime
    ) -> tuple[list[uuid.UUID], SyncSummary]:
        known = self.readings.existing_event_ids(conn.id, [r.source_event_id[:128] for r in raw])
        by_metric: Counter[str] = Counter()
        new_ids: list[uuid.UUID] = []
        duplicates = 0
        seen: set[str] = set()
        for item in raw:
            reading = normalize(item, now, user_id, conn.id)
            if reading is None:
                continue
            if reading.source_event_id in known or reading.source_event_id in seen:
                duplicates += 1
                continue
            seen.add(reading.source_event_id)
            if self.readings.add_unique(reading):
                new_ids.append(reading.id)
                by_metric[reading.metric_type] += 1
            else:
                duplicates += 1
        self.db.flush()
        return new_ids, SyncSummary(
            new_readings=len(new_ids), by_metric=dict(by_metric), duplicates=duplicates
        )

    def _replay(self, conn: DeviceConnection, attempt: SyncAttempt) -> SyncSummary:
        """Original result for a repeated key. Never adds readings."""
        if attempt.status != "succeeded":
            return SyncSummary()
        metrics = self.readings.metrics_created_at(conn.id, attempt.started_at)
        return SyncSummary(new_readings=len(metrics), by_metric=dict(Counter(metrics)), duplicates=0)

    def _run_hooks(self, user_id: int, new_ids: list[uuid.UUID]) -> None:
        if not new_ids:
            return
        for hook in list(_HOOKS):
            try:
                hook(self.db, user_id, new_ids)
            except Exception:  # a failing hook must never undo a stored sync
                self.db.rollback()
                log.warning("post_ingest_hook_failed", hook=getattr(hook, "__name__", "hook"))

    def _audit(self, user_id: int, conn: DeviceConnection, outcome: str, cid: str, severity: str) -> None:
        self.audit.record(
            action="sync.run",
            outcome=outcome,
            correlation_id=cid,
            user_id=user_id,
            severity=severity,
            entity_type="device_connection",
            entity_id=str(conn.id),
        )
