"""Clock abstraction and UTC helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol


def ensure_utc(value: datetime) -> datetime:
    """Return a timezone-aware UTC datetime (naive values are assumed to be UTC)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def utc_now() -> datetime:
    return datetime.now(UTC)


class Clock(Protocol):
    def utc_now(self) -> datetime: ...


class SystemClock:
    def utc_now(self) -> datetime:
        return utc_now()
