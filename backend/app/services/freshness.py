"""Single freshness policy shared by the dashboard and the connection status list (FR-009)."""

from __future__ import annotations

from datetime import datetime, timedelta

from app.clock import ensure_utc


def effective_status(
    stored_status: str,
    last_successful_sync_at: datetime | None,
    now: datetime,
    stale_after: timedelta,
) -> str:
    """pending and failed stay as stored; current needs a sync inside the window."""
    if stored_status in ("pending", "failed"):
        return stored_status
    if stored_status not in ("current", "stale"):
        return stored_status
    if last_successful_sync_at is None:
        return "stale"
    if now - ensure_utc(last_successful_sync_at) > stale_after:
        return "stale"
    return "current" if stored_status == "current" else "stale"


def recovery_action_for(status: str, source: str) -> str | None:
    """Safe, user-facing recovery code for stale or failed sources only."""
    if status == "stale":
        return "retry_sync"
    if status == "failed":
        return "contact_support" if source == "scale" else "retry"
    return None
