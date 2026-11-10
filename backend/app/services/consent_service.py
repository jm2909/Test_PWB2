"""Consent ledger. A missing or declined choice blocks dependent processing."""

from sqlalchemy.orm import Session

from app.models import ConsentRecord
from app.repositories.consent_repository import ConsentRepository
from app.services.audit_service import AuditService

PURPOSE_DEVICE_PROCESSING = "device_processing"
PURPOSE_PERSONALIZED_INSIGHTS = "personalized_insights"

_CONSEQUENCES = {
    PURPOSE_DEVICE_PROCESSING: "Connected-device data cannot be processed because that consent is not given.",
    PURPOSE_PERSONALIZED_INSIGHTS: (
        "Personalized insights cannot be created because consent for them is not given. "
        "You can change this choice in your consent settings."
    ),
}


class ProcessingBlockedError(Exception):
    """Dependent processing is not permitted; `explanation` is safe to show to the user."""

    def __init__(self, purpose: str, explanation: str) -> None:
        super().__init__(explanation)
        self.purpose = purpose
        self.explanation = explanation


class ConsentLedgerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.consents = ConsentRepository(db)

    def assert_permitted(self, user_id: int, purpose: str) -> None:
        latest = self.consents.latest(user_id, purpose)
        if latest is None or latest.status != "accepted":
            explanation = _CONSEQUENCES.get(purpose, "This processing cannot occur without your consent.")
            raise ProcessingBlockedError(purpose, explanation)

    def record(
        self, user_id: int, purpose: str, version: str, status: str, correlation_id: str
    ) -> ConsentRecord:
        """Append a dated choice (never updates earlier rows) and audit it."""
        row = self.consents.add(user_id, purpose, version, status)
        AuditService(self.db).record(
            action="consent.record",
            outcome=status,
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="consent_record",
            entity_id=str(row.id),
        )
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_for_user(self, user_id: int) -> tuple[list[ConsentRecord], list[ConsentRecord]]:
        """(history newest first, latest choice per purpose)."""
        history = self.consents.history(user_id)
        seen: dict[str, ConsentRecord] = {}
        for row in history:
            seen.setdefault(row.purpose, row)
        return history, list(seen.values())
