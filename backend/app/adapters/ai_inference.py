"""AI inference adapter: the only code that produces insight wording.

Without AI_PROVIDER_URL a deterministic local template is used. With it, the minimized evidence
summary is POSTed to the provider; any failure raises AIInferenceError and the insight is suppressed.
"""

from dataclasses import dataclass

import httpx
import structlog

from app.config import get_settings

log = structlog.get_logger("ai_inference")

_LABELS = {
    "weight": "Your weight",
    "body_fat": "Your body fat percentage",
    "sleep_hours": "Your nightly sleep",
    "resting_heart_rate": "Your resting heart rate",
    "steps": "Your daily steps",
}
_IMPLICATIONS = {
    ("weight", "down"): "This points to a steady downward weight pattern; keep your routine consistent.",
    ("weight", "up"): "This points to a gradual upward weight pattern; a look at your routine may help.",
    ("body_fat", "down"): "This points to a gradual decrease in body fat; keep up your current habits.",
    ("body_fat", "up"): "This points to a gradual increase in body fat; a look at your routine may help.",
    ("sleep_hours", "down"): (
        "Shorter sleep can affect energy and recovery; consider a steadier bedtime this week."
    ),
    ("sleep_hours", "up"): "Longer sleep supports recovery; keep your evening routine steady.",
    ("resting_heart_rate", "down"): "A lower resting heart rate often reflects good recovery; keep it up.",
    ("resting_heart_rate", "up"): (
        "A higher resting heart rate can follow poor sleep or stress; consider easing your routine."
    ),
    ("steps", "down"): "Your activity is lower than before; a short daily walk can help you rebuild it.",
    ("steps", "up"): "Your activity is rising; keep building at a pace that feels comfortable.",
}


class AIInferenceError(Exception):
    """The provider failed or returned an unusable answer."""


@dataclass(frozen=True)
class EvidenceSummary:
    metric: str
    unit: str
    count: int
    span_days: int
    first_value: float
    last_value: float
    percent_change: float

    @property
    def direction(self) -> str:
        return "down" if self.last_value < self.first_value else "up"


@dataclass(frozen=True)
class InferenceResult:
    observed_trend: str
    wellness_implication: str


def _fmt(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


class AIInferenceAdapter:
    def infer(self, evidence: EvidenceSummary) -> InferenceResult:
        settings = get_settings()
        if not settings.ai_provider_url:
            return self._local(evidence)
        return self._remote(evidence, settings.ai_provider_url, settings.ai_provider_key)

    @staticmethod
    def _local(evidence: EvidenceSummary) -> InferenceResult:
        label = _LABELS.get(evidence.metric, "This metric")
        verb = "decreased" if evidence.direction == "down" else "increased"
        trend = (
            f"{label} {verb} from {_fmt(evidence.first_value)} to "
            f"{_fmt(evidence.last_value)} {evidence.unit} "
            f"over {evidence.span_days} days ({abs(evidence.percent_change):.1f}% change, "
            f"{evidence.count} readings)."
        )
        implication = _IMPLICATIONS.get(
            (evidence.metric, evidence.direction), "Keep tracking to see whether this pattern continues."
        )
        return InferenceResult(trend, implication)

    @staticmethod
    def _remote(evidence: EvidenceSummary, url: str, key: str) -> InferenceResult:
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        body = {
            "metric": evidence.metric,
            "unit": evidence.unit,
            "count": evidence.count,
            "span_days": evidence.span_days,
            "first_value": evidence.first_value,
            "last_value": evidence.last_value,
            "percent_change": evidence.percent_change,
        }
        try:
            response = httpx.post(url, json=body, headers=headers, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            return InferenceResult(str(data["observed_trend"]), str(data["wellness_implication"]))
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            log.warning("ai_provider_failed", error_type=type(exc).__name__)
            raise AIInferenceError("AI provider unavailable") from exc
