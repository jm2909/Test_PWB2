from __future__ import annotations

from sqlalchemy.orm import Session as DbSession

from app.models import AuditLog


class AuditRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def add(self, entry: AuditLog) -> AuditLog:
        self.db.add(entry)
        self.db.flush()
        return entry
