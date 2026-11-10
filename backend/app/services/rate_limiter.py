"""Per-key fixed-window rate limiter (in process). Limits come from settings, e.g. '10/minute'."""

import threading
import time

_UNITS = {"second": 1, "minute": 60, "hour": 3600}


def parse_limit(spec: str) -> tuple[int, int]:
    """'10/minute' -> (10, 60)."""
    count, _, unit = spec.partition("/")
    return int(count), _UNITS[unit.strip().lower().rstrip("s")]


class FixedWindowLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, tuple[float, int]] = {}

    def hit(self, key: str, spec: str, now: float | None = None) -> bool:
        """Count one attempt; return False when the key is over the limit for this window."""
        limit, seconds = parse_limit(spec)
        current = time.monotonic() if now is None else now
        with self._lock:
            start, count = self._windows.get(key, (current, 0))
            if current - start >= seconds:
                start, count = current, 0
            count += 1
            self._windows[key] = (start, count)
            return count <= limit

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()


login_limiter = FixedWindowLimiter()
