from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.clock import utc_now
from app.config import get_settings
from app.models import Account, DataRightsRequest
from app.repositories.data_rights import DataRightsRepository

_SEEDS = (("DR-SEED-EXPORT", "export", "submitted"), ("DR-SEED-DELETION", "deletion", "in_review"))


def seed_data_rights(db: Session, accounts: dict[str, Account]) -> None:
    asha = accounts["asha"]
    repo = DataRightsRepository(db)
    now = utc_now()
    days = get_settings().data_rights_fulfillment_days
    for reference, kind, status in _SEEDS:
        if repo.by_reference(reference) is None:
            repo.add(
                DataRightsRequest(
                    account_id=asha.id,
                    reference=reference,
                    request_type=kind,
                    status=status,
                    requested_at=now - timedelta(days=2),
                    fulfillment_due_at=now - timedelta(days=2) + timedelta(days=days),
                )
            )
