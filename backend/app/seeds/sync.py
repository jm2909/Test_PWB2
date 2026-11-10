"""Seed sync_attempts history for asha's connections (incl. a failed attempt for platform B)."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.database import utcnow
from app.repositories.device_repository import DeviceRepository
from app.repositories.sync_repository import SyncRepository
from app.seeds import register
from app.seeds.users import user_id


@register("sync", order=37)
def seed_sync(db: Session) -> None:
    asha = user_id(db, "asha")
    syncs = SyncRepository(db)
    now = utcnow()
    for conn in DeviceRepository(db).list_for_user(asha):
        history: list[tuple[str, str, str | None, int]] = []
        if conn.provider == "wearable_platform_b":
            history.append(("failed", conn.failure_reason or "The provider did not respond.", None, 2))
        elif conn.provider == "wearable_platform_c":
            history.append(("failed", conn.failure_reason or "Access was revoked at the provider.", None, 3))
        elif conn.status == "connected":
            history.append(("succeeded", "", None, 1))
        for status, reason, _unused, days in history:
            key = f"seed-{conn.provider}-{status}-history"[:128].ljust(16, "-")
            if syncs.find(conn.id, key) is not None:
                continue
            started = now - timedelta(days=days)
            attempt = syncs.start(conn.id, key, started)
            if attempt is not None:
                syncs.finish(attempt, status, started + timedelta(seconds=4), reason or None)
    db.flush()
