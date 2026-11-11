"""Approved wellness-only content policy (no clinical claims)."""

from __future__ import annotations

import re

from app.errors import DomainError

_BLOCKED = re.compile(
    r"\b(diagnos\w*|treat\w*|prescri\w*|medicat\w*|emergenc\w*|clinical\w*|disease\w*|disorder\w*"
    r"|syndrome\w*|therap\w*|cure\w*|patholog\w*|symptom\w*|hypertens\w*|diabet\w*|911)\b",
    re.IGNORECASE,
)

PROFESSIONAL_SUPPORT_NOTE = (
    "This is wellness guidance only. If you are concerned, consider speaking with a qualified "
    "health professional."
)


class ContentPolicyError(DomainError):
    status_code = 422
    default_detail = "Content does not meet the approved wellness-only wording policy"


def violations(*texts: str) -> list[str]:
    found: list[str] = []
    for text in texts:
        found.extend(m.group(0).lower() for m in _BLOCKED.finditer(text))
    return found


def ensure_allowed(*texts: str) -> None:
    """Raise before persistence when any text uses clinical wording."""
    if violations(*texts):
        raise ContentPolicyError()
