"""Safety validator: insight text must cite a trend, state an implication and stay non-diagnostic."""

import re

_PROHIBITED = re.compile(
    r"\b(diagnos\w*|disease\w*|disorder\w*|syndrome|cancer|diabet\w*|hypertension|"
    r"cardiac|heart attack|stroke|treat(?:s|ed|ing|ment)?|cure\w*|prescri\w*|medicat\w*|"
    r"you have|you are suffering|clinical\w*|illness\w*)\b",
    re.IGNORECASE,
)


def contains_diagnostic_language(text: str) -> bool:
    return _PROHIBITED.search(text) is not None


def is_safe_insight(observed_trend: str | None, wellness_implication: str | None) -> bool:
    if not observed_trend or not observed_trend.strip():
        return False
    if not wellness_implication or not wellness_implication.strip():
        return False
    return not (
        contains_diagnostic_language(observed_trend) or contains_diagnostic_language(wellness_implication)
    )


_FORBIDDEN_LINK = re.compile(r"tel:|https?://|\bdial\b|\bcall (?:now|911|112|999)\b", re.IGNORECASE)
_CARE_MARKERS = re.compile(r"doctor|health professional|emergency number", re.IGNORECASE)


def is_safe_alert(urgency: str, next_action: str, care_direction: str | None) -> bool:
    """Alert copy must be non-diagnostic, carry no dial links, and urgent ones must direct to care."""
    texts = [next_action] + ([care_direction] if care_direction else [])
    if not next_action.strip():
        return False
    if any(contains_diagnostic_language(t) or _FORBIDDEN_LINK.search(t) for t in texts):
        return False
    if urgency == "urgent_direction":
        return bool(care_direction and _CARE_MARKERS.search(care_direction))
    return urgency == "routine"


def is_safe_recommendation(action_text: str, reason_text: str) -> bool:
    return bool(action_text.strip() and reason_text.strip()) and not (
        contains_diagnostic_language(action_text) or contains_diagnostic_language(reason_text)
    )
