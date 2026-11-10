"""The only writer of connection sync state (FR-010)."""

from sqlalchemy.orm import Session

from app.adapters.base import AdapterError
from app.adapters.wearable_base import AuthorizationRevokedError, PermissionsChangedError
from app.database import utcnow
from app.models import DeviceConnection
from app.repositories.device_repository import DeviceRepository

RETRY_ACTION = "Retry"
RECONNECT_ACTION = "Reconnect"
REVIEW_ACTION = "Review permissions"


def classify(exc: AdapterError) -> tuple[str, str, str]:
    """(connection status, reason, recovery action) for an adapter failure."""
    reason = exc.reason[:256]
    if isinstance(exc, AuthorizationRevokedError):
        return "revoked", reason, RECONNECT_ACTION
    if isinstance(exc, PermissionsChangedError) or not exc.retryable:
        return "action_required", reason, REVIEW_ACTION
    return "failed", reason, RETRY_ACTION


class SyncStatusRecoveryService:
    def __init__(self, db: Session) -> None:
        self.repo = DeviceRepository(db)

    def mark_success(self, row: DeviceConnection) -> None:
        self.repo.set_state(
            row,
            status="connected",
            failure_reason=None,
            recovery_action=None,
            last_successful_sync_at=utcnow(),
        )

    def mark_failure(self, row: DeviceConnection, exc: AdapterError) -> tuple[str, str]:
        status, reason, action = classify(exc)
        self.repo.set_state(row, status=status, failure_reason=reason, recovery_action=action)
        return status, reason

    @staticmethod
    def is_current(row: DeviceConnection) -> bool:
        """Failed, revoked and action-required connections are never reported current."""
        return row.status == "connected"
