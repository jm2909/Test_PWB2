"""Seed wearable connections for the personas (order after readings, which makes asha's fitband/scale)."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeviceConnection
from app.seeds import register
from app.seeds.users import user_id


def _ensure(
    db: Session,
    uid: int,
    provider: str,
    status: str,
    categories: list[str],
    *,
    synced: bool = False,
    reason: str | None = None,
    action: str | None = None,
) -> None:
    exists = db.scalar(
        select(DeviceConnection.id).where(
            DeviceConnection.user_id == uid, DeviceConnection.provider == provider
        )
    )
    if exists is not None:
        return
    db.add(
        DeviceConnection(
            user_id=uid,
            provider=provider,
            status=status,
            permitted_categories=categories,
            last_successful_sync_at=datetime.now(UTC) if synced else None,
            failure_reason=reason,
            recovery_action=action,
        )
    )


@register("devices", order=35)
def seed_devices(db: Session) -> None:
    asha = user_id(db, "asha")
    # The scale (connected) is created by the readings seed; the platform rows are added here.
    _ensure(db, asha, "wearable_platform_a", "connected", ["sleep", "heart_rate", "activity"], synced=True)
    _ensure(
        db,
        asha,
        "wearable_platform_b",
        "failed",
        [],
        reason="The provider did not respond.",
        action="Try again",
    )
    _ensure(
        db,
        asha,
        "wearable_platform_c",
        "revoked",
        [],
        reason="Access was revoked at the provider.",
        action="Reconnect",
    )
    # Permissions attention state: the fitband needs its permissions re-granted.
    band = db.scalar(
        select(DeviceConnection).where(
            DeviceConnection.user_id == asha, DeviceConnection.provider == "fitband"
        )
    )
    if band is not None and band.status == "connected":
        band.status = "action_required"
        band.failure_reason = "Permissions need to be updated."
        band.recovery_action = "Review permissions"

    meena = user_id(db, "meena")
    _ensure(db, meena, "wearable_platform_a", "connected", ["heart_rate", "activity"], synced=True)
    db.flush()
