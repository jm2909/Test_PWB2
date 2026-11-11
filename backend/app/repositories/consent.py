from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.models import ConsentRecord


class ConsentRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def add(self, record: ConsentRecord) -> ConsentRecord:
        self.db.add(record)
        self.db.flush()
        return record

    def latest_for_account(self, account_id: uuid.UUID) -> ConsentRecord | None:
        return self.db.scalar(
            select(ConsentRecord)
            .where(ConsentRecord.account_id == account_id)
            .order_by(ConsentRecord.recorded_at.desc(), ConsentRecord.created_at.desc())
            .limit(1)
        )
