"""Structured logging with PII masking (emails, bearer tokens, password-like fields)."""

import logging
import re
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
BEARER_RE = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+")
SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "token_hash",
    "authorization",
    "email",
    "jwt_secret_key",
}


def mask_text(value: str) -> str:
    value = EMAIL_RE.sub("[email]", value)
    return BEARER_RE.sub("Bearer [redacted]", value)


def _mask(value: Any) -> Any:
    if isinstance(value, str):
        return mask_text(value)
    if isinstance(value, dict):
        return {k: "[redacted]" if str(k).lower() in SENSITIVE_KEYS else _mask(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_mask(v) for v in value]
    return value


def pii_mask_processor(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    masked: MutableMapping[str, Any] = _mask(dict(event_dict))
    return masked


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            pii_mask_processor,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=False,
    )
