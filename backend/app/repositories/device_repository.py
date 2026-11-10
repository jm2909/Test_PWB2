import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import utcnow
from app.models import DeviceConnection


class DeviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int, provider: str) -> DeviceConnection | None:
        return self.db.scalar(
            select(DeviceConnection).where(
                DeviceConnection.user_id == user_id, DeviceConnection.provider == provider
            )
        )

    def get_owned(self, user_id: int, connection_id: uuid.UUID) -> DeviceConnection | None:
        return self.db.scalar(
            select(DeviceConnection).where(
                DeviceConnection.id == connection_id, DeviceConnection.user_id == user_id
            )
        )

    def set_state(
        self,
        row: DeviceConnection,
        *,
        status: str,
        failure_reason: str | None,
        recovery_action: str | None,
        last_successful_sync_at: datetime | None = None,
    ) -> None:
        row.status = status
        row.failure_reason = failure_reason
        row.recovery_action = recovery_action
        if last_successful_sync_at is not None:
            row.last_successful_sync_at = last_successful_sync_at
        row.updated_at = utcnow()
        self.db.flush()

    def list_for_user(self, user_id: int) -> list[DeviceConnection]:
        return list(
            self.db.scalars(
                select(DeviceConnection)
                .where(DeviceConnection.user_id == user_id)
                .order_by(DeviceConnection.created_at, DeviceConnection.provider)
            )
        )

    def upsert(
        self,
        user_id: int,
        provider: str,
        *,
        status: str,
        permitted_categories: list[str],
        failure_reason: str | None,
        recovery_action: str | None,
        last_successful_sync_at: datetime | None = None,
    ) -> DeviceConnection:
        row = self.get(user_id, provider)
        if row is None:
            row = DeviceConnection(user_id=user_id, provider=provider)
            self.db.add(row)
        row.status = status
        row.permitted_categories = permitted_categories
        row.failure_reason = failure_reason
        row.recovery_action = recovery_action
        if last_successful_sync_at is not None:
            row.last_successful_sync_at = last_successful_sync_at
        row.updated_at = utcnow()
        self.db.flush()
        return row
