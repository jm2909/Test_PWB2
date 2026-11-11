"""In-memory sliding-window rate limiter (per key)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

_PERIODS = {"second": 1, "minute": 60, "hour": 3600}


def parse_limit(spec: str) -> tuple[int, int]:
    count, _, period = spec.partition("/")
    return int(count), _PERIODS[period.strip().lower()]


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, spec: str) -> bool:
        limit, window = parse_limit(spec)
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= window:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


login_limiter = RateLimiter()
