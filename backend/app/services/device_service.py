"""Device connections: consent gate first, then the provider adapter."""

from sqlalchemy.orm import Session

from app.adapters.base import AdapterError, DeviceAdapter
from app.adapters.registry import build_registry
from app.adapters.wearable_base import AuthorizationRevokedError
from app.models import DeviceConnection
from app.repositories.device_repository import DeviceRepository
from app.schemas.device_schemas import DeviceConnectionCreate, DeviceConnectionResponse, SyncSummary
from app.services.audit_service import AuditService
from app.services.consent_service import PURPOSE_DEVICE_PROCESSING, ConsentLedgerService


class UnsupportedConnectionError(Exception):
    """Provider or mode is not supported by this service."""


def default_adapters() -> dict[str, DeviceAdapter]:
    return build_registry()


def to_response(row: DeviceConnection, summary: SyncSummary | None = None) -> DeviceConnectionResponse:
    data = DeviceConnectionResponse.model_validate(row)
    data.last_sync_summary = summary
    return data


class DeviceService:
    def __init__(self, db: Session, adapters: dict[str, DeviceAdapter] | None = None) -> None:
        self.db = db
        self.repo = DeviceRepository(db)
        self.consents = ConsentLedgerService(db)
        self.audit = AuditService(db)
        self.adapters = adapters if adapters is not None else default_adapters()

    def connect(self, user_id: int, payload: DeviceConnectionCreate, correlation_id: str) -> DeviceConnection:
        adapter = self.adapters.get(payload.provider)
        if adapter is None or payload.connection_mode not in adapter.supported_modes:
            raise UnsupportedConnectionError("This provider or connection mode is not supported.")
        try:
            # Consent gate first: a refusal never reaches the adapter.
            self.consents.assert_permitted(user_id, PURPOSE_DEVICE_PROCESSING)
        except Exception:
            self.audit.record(
                action="device.connect",
                outcome="blocked_no_consent",
                correlation_id=correlation_id,
                user_id=user_id,
                severity="warning",
                entity_type="device_connection",
            )
            self.db.commit()
            raise
        try:
            result = adapter.connect(payload.authorization_code)
        except AdapterError as exc:
            row = self.repo.upsert(
                user_id,
                payload.provider,
                status=(
                    "revoked"
                    if isinstance(exc, AuthorizationRevokedError)
                    else "failed"
                    if exc.retryable
                    else "action_required"
                ),
                permitted_categories=[],
                failure_reason=exc.reason[:256],
                recovery_action=exc.recovery_action,
            )
            outcome = "failed"
        else:
            row = self.repo.upsert(
                user_id,
                payload.provider,
                status="connected",
                permitted_categories=result.permitted_categories,
                failure_reason=None,
                recovery_action=None,
            )
            outcome = "connected"
        self.audit.record(
            action="device.connect",
            outcome=outcome,
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="device_connection",
            entity_id=str(row.id),
        )
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_for_user(self, user_id: int) -> list[DeviceConnection]:
        return self.repo.list_for_user(user_id)
