from __future__ import annotations

from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import Account, ConsentRecord
from app.repositories.consent import ConsentRepository

NOTICE_VERSION = "v1.0"
ASHA_CATEGORIES = ["weight", "body_composition", "steps", "sleep_duration", "active_minutes"]


def seed_consents(db: Session, accounts: dict[str, Account]) -> None:
    """asha has granted consent (notice v1.0); rohan has none. Idempotent."""
    asha = accounts["asha"]
    repo = ConsentRepository(db)
    if repo.latest_for_account(asha.id) is None:
        repo.add(
            ConsentRecord(
                account_id=asha.id,
                decision="granted",
                notice_version=NOTICE_VERSION,
                data_categories=ASHA_CATEGORIES,
                purpose="wellness_support",
                recorded_at=utc_now(),
            )
        )
