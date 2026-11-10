from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ConsentRecord


class ConsentRepository:
    """Consent ledger storage. Append-only: there is no update or delete."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def latest(self, user_id: int, purpose: str) -> ConsentRecord | None:
        return self.db.scalar(
            select(ConsentRecord)
            .where(ConsentRecord.user_id == user_id, ConsentRecord.purpose == purpose)
            .order_by(ConsentRecord.recorded_at.desc(), ConsentRecord.created_at.desc())
            .limit(1)
        )

    def add(self, user_id: int, purpose: str, version: str, status: str) -> ConsentRecord:
        row = ConsentRecord(user_id=user_id, purpose=purpose, version=version, status=status)
        self.db.add(row)
        self.db.flush()
        return row

    def history(self, user_id: int) -> list[ConsentRecord]:
        """Every choice, newest first."""
        return list(
            self.db.scalars(
                select(ConsentRecord)
                .where(ConsentRecord.user_id == user_id)
                .order_by(ConsentRecord.recorded_at.desc(), ConsentRecord.created_at.desc())
            )
        )
