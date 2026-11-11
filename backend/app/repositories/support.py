from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.models import SupportRequest


class SupportRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def add(self, entry: SupportRequest) -> SupportRequest:
        self.db.add(entry)
        self.db.flush()
        return entry

    def by_reference(self, reference: str) -> SupportRequest | None:
        return self.db.scalar(select(SupportRequest).where(SupportRequest.reference == reference))
