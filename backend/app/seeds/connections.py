from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import Account, Connection
from app.repositories.connection import ConnectionRepository


def seed_scale_connections(db: Session, accounts: dict[str, Account]) -> None:
    """asha: Bathroom (SSC-0482, current, seeded with readings) and Bedroom (SSC-0517, stale)."""
    asha = accounts["asha"]
    repo = ConnectionRepository(db)
    now = utc_now()
    if repo.find_one(asha.id, "scale", "sapphire-scale", "SSC-0517") is None:
        repo.add(
            Connection(
                account_id=asha.id,
                source="scale",
                provider="sapphire-scale",
                external_identifier="SSC-0517",
                display_label="Bedroom",
                authorization_state="authorized",
                status="stale",
                last_successful_sync_at=now - timedelta(days=8),
            )
        )
