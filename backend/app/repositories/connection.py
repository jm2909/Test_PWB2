from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import Connection


class ConnectionRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def list_for_owner(self, account_id: uuid.UUID, limit: int = 50) -> list[Connection]:
        return list(
            self.db.scalars(
                select(Connection)
                .where(Connection.account_id == account_id)
                .order_by(Connection.created_at, Connection.id)
                .limit(limit)
            )
        )

    def list_active_page(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[Connection], int]:
        """Owner-only page of connections, excluding disconnected ones."""
        conditions = (Connection.account_id == account_id, Connection.status != "disconnected")
        total = self.db.scalar(select(func.count()).select_from(Connection).where(*conditions))
        rows = self.db.scalars(
            select(Connection)
            .where(*conditions)
            .order_by(Connection.created_at, Connection.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total or 0)

    def find_one(
        self, account_id: uuid.UUID, source: str, provider: str, external_identifier: str
    ) -> Connection | None:
        return self.db.scalar(
            select(Connection).where(
                Connection.account_id == account_id,
                Connection.source == source,
                Connection.provider == provider,
                Connection.external_identifier == external_identifier,
            )
        )

    def add(self, entry: Connection) -> Connection:
        self.db.add(entry)
        self.db.flush()
        return entry

    def get_owned(self, account_id: uuid.UUID, connection_id: uuid.UUID) -> Connection | None:
        return self.db.scalar(
            select(Connection).where(
                Connection.id == connection_id, Connection.account_id == account_id
            )
        )

    def list_provider_rows(self, account_id: uuid.UUID, provider: str) -> list[Connection]:
        return list(
            self.db.scalars(
                select(Connection)
                .where(
                    Connection.account_id == account_id,
                    Connection.source == "wearable",
                    Connection.provider == provider,
                )
                .order_by(Connection.created_at, Connection.id)
            )
        )
