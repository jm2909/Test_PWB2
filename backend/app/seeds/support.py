from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import Account, SupportRequest
from app.repositories.support import SupportRepository

_REFERENCE = "SUP-SEED-0001"


def seed_support(db: Session, accounts: dict[str, Account]) -> None:
    repo = SupportRepository(db)
    if repo.by_reference(_REFERENCE) is not None:
        return
    repo.add(
        SupportRequest(
            account_id=accounts["asha"].id,
            reference=_REFERENCE,
            category="connection",
            description="My bedroom scale has not synced for a week.",
            context_type="account",
            context_id=None,
            status="submitted",
            submitted_at=utc_now() - timedelta(days=1),
        )
    )
