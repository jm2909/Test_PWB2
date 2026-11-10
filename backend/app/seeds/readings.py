"""Seed device connections and readings relative to 'now' (recent, so insights see fresh data)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviceConnection, WellnessReading
from app.seeds import register
from app.seeds.users import user_id


def _connection(db: Session, uid: int, provider: str, categories: list[str]) -> DeviceConnection:
    conn = db.scalar(
        select(DeviceConnection).where(DeviceConnection.user_id == uid, DeviceConnection.provider == provider)
    )
    if conn is None:
        conn = DeviceConnection(
            user_id=uid,
            provider=provider,
            status="connected",
            permitted_categories=categories,
            last_successful_sync_at=datetime.now(UTC),
        )
        db.add(conn)
        db.flush()
    return conn


def _series(
    db: Session,
    conn: DeviceConnection,
    metric: str,
    unit: str,
    start: float,
    end: float,
    days: int,
    step: int = 1,
) -> None:
    """Linear series ending today; source_event_id is deterministic so re-runs add nothing."""
    now = datetime.now(UTC).replace(hour=7, minute=0, second=0, microsecond=0)
    offsets = list(range(days - 1, -1, -step))
    if offsets[-1] != 0:
        offsets.append(0)
    for index, offset in enumerate(offsets):
        event_id = f"seed-{metric}-{offset}"
        exists = db.scalar(
            select(WellnessReading.id).where(
                WellnessReading.device_connection_id == conn.id, WellnessReading.source_event_id == event_id
            )
        )
        if exists is not None:
            continue
        fraction = index / (len(offsets) - 1)
        value = start + (end - start) * fraction
        db.add(
            WellnessReading(
                user_id=conn.user_id,
                device_connection_id=conn.id,
                source_event_id=event_id,
                metric_type=metric,
                value_numeric=Decimal(f"{value:.4f}"),
                unit=unit,
                observed_at=now - timedelta(days=offset),
            )
        )


@register("readings", order=30)
def seed_readings(db: Session) -> None:
    asha = user_id(db, "asha")
    scale = _connection(db, asha, "sapphire_scale", ["weight", "body_fat"])
    band = _connection(db, asha, "fitband", ["sleep_hours", "resting_heart_rate", "steps"])
    _series(db, scale, "weight", "kg", 70.1, 68.4, 30)
    _series(db, scale, "body_fat", "%", 24.0, 23.2, 30, step=2)
    _series(db, band, "sleep_hours", "h", 7 + 10 / 60, 6 + 5 / 60, 14)  # 7h10 -> 6h05
    _series(db, band, "resting_heart_rate", "bpm", 62, 68, 14)
    _series(db, band, "steps", "steps", 8200, 7400, 30)

    meena = user_id(db, "meena")
    meena_band = _connection(db, meena, "fitband", ["sleep_hours"])
    _series(db, meena_band, "sleep_hours", "h", 6.8, 6.6, 3)
    db.flush()
