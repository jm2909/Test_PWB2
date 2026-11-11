from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import DataRightsRequest


class DataRightsRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def add(self, entry: DataRightsRequest) -> DataRightsRequest:
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_for_owner(
        self, account_id: uuid.UUID, limit: int, offset: int
    ) -> tuple[list[DataRightsRequest], int]:
        base = select(DataRightsRequest).where(DataRightsRequest.account_id == account_id)
        total = self.db.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = self.db.scalars(
            base.order_by(DataRightsRequest.requested_at.desc(), DataRightsRequest.id)
            .limit(limit)
            .offset(offset)
        )
        return list(rows), int(total)

    def by_reference(self, reference: str) -> DataRightsRequest | None:
        return self.db.scalar(
            select(DataRightsRequest).where(DataRightsRequest.reference == reference)
        )
