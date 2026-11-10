"""Device adapter contract and error classification.

Retryable errors are transient (try again later); non-retryable errors need the user to act
(reconnect, re-authorize). Adapter messages are already sanitized and safe to show.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from typing import Protocol


class AdapterError(Exception):
    retryable = True
    recovery_action = "Try again"

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class RetryableAdapterError(AdapterError):
    retryable = True


class NonRetryableAdapterError(AdapterError):
    retryable = False
    recovery_action = "Reconnect your device"


@dataclass(frozen=True)
class ConnectResult:
    permitted_categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawReading:
    """A reading as the provider reports it: provider metric/unit and a timestamp with any offset."""

    source_event_id: str
    metric: str
    value: float
    unit: str
    observed_at: datetime


# category -> (provider metric, provider unit, base value, daily step)
_SIMULATED: dict[str, tuple[str, str, float, float]] = {
    "sleep": ("sleep_minutes", "min", 420.0, 5.0),
    "heart_rate": ("hr_resting", "bpm", 62.0, 1.0),
    "activity": ("step_count", "count", 7800.0, 150.0),
    "weight": ("weight", "lb", 152.0, 0.2),
    "body_fat": ("body_fat", "percent", 23.5, 0.1),
}
_SIMULATED_DAYS = 3


def simulated_readings(provider: str, categories: Sequence[str], now: datetime) -> list[RawReading]:
    """Deterministic readings for the last few days with stable source_event_ids (same day => same ids)."""
    tz = timezone_offset()
    out: list[RawReading] = []
    for category in categories:
        spec = _SIMULATED.get(category)
        if spec is None:
            continue
        metric, unit, base, step = spec
        for offset in range(_SIMULATED_DAYS):
            day = (now - timedelta(days=offset)).astimezone(UTC).date()
            observed = datetime(day.year, day.month, day.day, 6, 30, tzinfo=tz)
            value = base + ((day.toordinal() * 7) % 10) * step
            out.append(
                RawReading(
                    f"{provider}:{category}:{day.isoformat()}", metric, round(value, 2), unit, observed
                )
            )
    return out


def timezone_offset() -> timezone:
    return timezone(timedelta(hours=5, minutes=30))


class DeviceAdapter(Protocol):
    provider: str
    supported_modes: tuple[str, ...]

    def connect(self, authorization_code: str | None) -> ConnectResult:
        """Pair/authorize; raise AdapterError on failure."""
        ...

    def fetch_readings(
        self, categories: Sequence[str], now: datetime, simulate: str | None = None
    ) -> list[RawReading]:
        """Return provider readings; raise AdapterError on failure. `simulate` forces a fault (tests/demo)."""
        ...
