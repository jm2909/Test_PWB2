"""Wearable connections (pending / failed / disconnected) and ~30 days of readings."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import Account, Connection, Reading, ReadingProcessingOutcome
from app.repositories.connection import ConnectionRepository

# provider, identifier, label, authorization_state, status, failure code
_CONNECTIONS = (
    ("pulsewear", "pulsewear-seed-a", "Provider A", "pending", "pending", None),
    ("fitband", "fitband-seed-b", "Provider B", "failed", "failed", "authorization_failed"),
    ("stridelink", "stridelink-seed-c", "Provider C", "revoked", "disconnected", None),
)
# metric, unit, source, base, step, first day, last day (exclusive) of the extra history.
# Weight totals 24 distinct days and steps only 4, so 365d steps is "insufficient_data".
_DAILY = (
    ("weight", "kg", "scale", Decimal("69.8"), Decimal("-0.04"), 4, 24),
    ("steps", "count", "wearable", Decimal("7600"), Decimal("15"), 3, 4),
    ("sleep_duration", "hours", "wearable", Decimal("7.0"), Decimal("0.01"), 2, 32),
    ("active_minutes", "minutes", "wearable", Decimal("38"), Decimal("0.2"), 2, 32),
)
_REJECTED = ("value_out_of_range", "unit_not_allowed", "timestamp_in_future")


def seed_wearables(db: Session, accounts: dict[str, Account]) -> None:
    asha = accounts["asha"]
    repo = ConnectionRepository(db)
    now = utc_now().replace(minute=0, second=0, microsecond=0)
    for provider, ext, label, auth, status, failure in _CONNECTIONS:
        if repo.find_one(asha.id, "wearable", provider, ext) is None:
            repo.add(
                Connection(
                    account_id=asha.id,
                    source="wearable",
                    provider=provider,
                    external_identifier=ext,
                    display_label=label,
                    authorization_state=auth,
                    status=status,
                    last_failure_code=failure,
                )
            )
    for metric, unit, source, base, step, first_day, last_day in _DAILY:
        conn = db.scalar(
            select(Connection).where(
                Connection.account_id == asha.id,
                Connection.source == source,
                Connection.status == "current",
            )
        )
        for day in range(first_day, last_day):
            key = f"seed30-{metric}-{day}"
            if db.scalar(
                select(Reading.id).where(
                    Reading.account_id == asha.id,
                    Reading.source == source,
                    Reading.idempotency_key == key,
                )
            ):
                continue
            captured = now - timedelta(days=day, hours=1)
            db.add(
                Reading(
                    account_id=asha.id,
                    connection_id=conn.id if conn else None,
                    metric_type=metric,
                    value=(base + step * (day % 7)).quantize(Decimal("0.0001")),
                    unit=unit,
                    source=source,
                    captured_at=captured,
                    ingested_at=captured,
                    idempotency_key=key,
                )
            )
    for i, reason in enumerate(_REJECTED):
        key = f"seed-rejected-{i}"
        if not db.scalar(
            select(ReadingProcessingOutcome.id).where(
                ReadingProcessingOutcome.account_id == asha.id,
                ReadingProcessingOutcome.idempotency_key == key,
            )
        ):
            db.add(
                ReadingProcessingOutcome(
                    account_id=asha.id,
                    idempotency_key=key,
                    outcome="rejected",
                    reason_code=reason,
                    occurred_at=now - timedelta(days=i + 1),
                )
            )
    db.flush()
