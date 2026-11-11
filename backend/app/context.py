"""Request-scoped context (correlation id)."""

from __future__ import annotations

import re
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{8,128}$")


def is_valid_correlation_id(value: str | None) -> bool:
    return bool(value and _VALID_ID.match(value))


def get_correlation_id() -> str:
    return correlation_id_var.get()
