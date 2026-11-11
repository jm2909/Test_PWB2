from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import Account, Connection, Reading

# (metric, unit, source, daily values newest-first)
_ASHA_SERIES: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("weight", "kg", "scale", ("68.4", "68.6", "68.9", "69.0")),
    ("steps", "count", "wearable", ("7400", "8200", "6900")),
    ("sleep_duration", "hours", "wearable", ("7.1", "6.8", "7.4")),
    ("active_minutes", "minutes", "wearable", ("42", "35", "50")),
)


def seed_readings(db: Session, accounts: dict[str, Account]) -> None:
    """Asha gets sample readings; Rohan intentionally has none (all-unavailable dashboard)."""
    asha = accounts["asha"]
    now = utc_now().replace(minute=0, second=0, microsecond=0)
    for source, provider, ext, label in (
        ("scale", "sapphire-scale", "SSC-0482", "Bathroom"),
        ("wearable", "fitband", "SEED-BAND-1", "Fitband"),
    ):
        exists = db.scalar(
            select(Connection).where(
                Connection.account_id == asha.id,
                Connection.source == source,
                Connection.provider == provider,
                Connection.external_identifier == ext,
            )
        )
        if exists is None:
            db.add(
                Connection(
                    account_id=asha.id,
                    source=source,
                    provider=provider,
                    external_identifier=ext,
                    display_label=label,
                    authorization_state="authorized",
                    status="current",
                    last_successful_sync_at=now - timedelta(hours=1),
                )
            )
    db.flush()
    for metric, unit, source, values in _ASHA_SERIES:
        conn = db.scalar(
            select(Connection).where(Connection.account_id == asha.id, Connection.source == source)
        )
        for day, value in enumerate(values):
            key = f"seed-{metric}-{day}"
            found = db.scalar(
                select(Reading.id).where(
                    Reading.account_id == asha.id,
                    Reading.source == source,
                    Reading.idempotency_key == key,
                )
            )
            if found is None:
                captured = now - timedelta(hours=1, days=day)
                db.add(
                    Reading(
                        account_id=asha.id,
                        connection_id=conn.id if conn else None,
                        metric_type=metric,
                        value=Decimal(value),
                        unit=unit,
                        source=source,
                        captured_at=captured,
                        ingested_at=captured,
                        idempotency_key=key,
                    )
                )
    db.flush()
