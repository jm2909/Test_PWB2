"""In-process metrics counters and fail-open OpenTelemetry registration."""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)
_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0)


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self.requests: dict[tuple[str, str, int], int] = defaultdict(int)
            self.errors = 0
            self.latency: dict[float, int] = defaultdict(int)
            self.latency_sum = 0.0
            self.latency_count = 0

    def observe(self, method: str, route: str, status: int, seconds: float) -> None:
        with self._lock:
            self.requests[(method, route, status)] += 1
            if status >= 500:
                self.errors += 1
            self.latency_sum += seconds
            self.latency_count += 1
            for bound in _BUCKETS:
                if seconds <= bound:
                    self.latency[bound] += 1

    def render(self) -> str:
        with self._lock:
            lines = ["# TYPE http_requests_total counter"]
            for (method, route, status), n in sorted(self.requests.items()):
                labels = f'method="{method}",route="{route}",status="{status}"'
                lines.append(f"http_requests_total{{{labels}}} {n}")
            lines += ["# TYPE http_errors_total counter", f"http_errors_total {self.errors}"]
            lines.append("# TYPE http_request_duration_seconds histogram")
            for bound in _BUCKETS:
                lines.append(
                    f'http_request_duration_seconds_bucket{{le="{bound}"}} {self.latency[bound]}'
                )
            lines.append(f'http_request_duration_seconds_bucket{{le="+Inf"}} {self.latency_count}')
            lines.append(f"http_request_duration_seconds_sum {self.latency_sum:.6f}")
            lines.append(f"http_request_duration_seconds_count {self.latency_count}")
            return "\n".join(lines) + "\n"


metrics = Metrics()


def setup_tracing(app: Any, engine: Any) -> None:
    """Register OpenTelemetry instrumentation; never blocks startup."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        SQLAlchemyInstrumentor().instrument(engine=engine)
    except Exception as exc:  # noqa: BLE001 - fail open by design
        logger.info("OpenTelemetry not enabled: %s", type(exc).__name__)
