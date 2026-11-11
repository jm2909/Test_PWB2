"""Structured logging with correlation id and PII masking."""

from __future__ import annotations

import logging
import re

from app.context import get_correlation_id

_EMAIL = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+)")


def mask_email(value: str) -> str:
    return _EMAIL.sub(r"\1***@\2", value)


class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        record.msg = mask_email(str(record.msg))
        return True


def configure_logging(debug: bool = False) -> None:
    root = logging.getLogger()
    if any(getattr(h, "_fitconnect", False) for h in root.handlers):
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(correlation_id)s] %(name)s: %(message)s")
    )
    handler.addFilter(CorrelationFilter())
    handler._fitconnect = True  # type: ignore[attr-defined]
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if debug else logging.INFO)
