"""Insight generation (FR-017): consent gate, evidence sufficiency, AI adapter, safety validator."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.adapters.ai_inference import AIInferenceAdapter, AIInferenceError, EvidenceSummary
from app.models import Insight, WellnessReading
from app.repositories.insight_repository import InsightRepository
from app.repositories.reading_repository import ReadingRepository
from app.services.audit_service import AuditService
from app.services.consent_service import PURPOSE_PERSONALIZED_INSIGHTS, ConsentLedgerService
from app.services.recommendation_service import RecommendationService
from app.services.safety import is_safe_insight

WINDOW_DAYS = 30
MIN_READINGS = 5
MIN_SPAN_DAYS = 7
MAX_STALENESS_DAYS = 3
MIN_CHANGE_PERCENT = 1.0

# metric -> (plausible minimum, plausible maximum) used as the validity check
VALID_RANGES: dict[str, tuple[float, float]] = {
    "weight": (20.0, 400.0),
    "body_fat": (2.0, 70.0),
    "sleep_hours": (0.0, 24.0),
    "resting_heart_rate": (25.0, 220.0),
    "steps": (0.0, 100000.0),
}

REASON_INSUFFICIENT = "insufficient_evidence"
REASON_STALE = "stale_data"
REASON_NO_TREND = "no_clear_trend"
REASON_AI_FAILED = "ai_unavailable"
REASON_SAFETY = "safety_blocked"


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


class InsightService:
    def __init__(self, db: Session, adapter: AIInferenceAdapter | None = None) -> None:
        self.db = db
        self.adapter = adapter or AIInferenceAdapter()
        self.readings = ReadingRepository(db)
        self.insights = InsightRepository(db)
        self.consent = ConsentLedgerService(db)
        self.audit = AuditService(db)

    def generate(self, user_id: int, correlation_id: str) -> Insight:
        self.consent.assert_permitted(user_id, PURPOSE_PERSONALIZED_INSIGHTS)
        now = datetime.now(UTC)
        readings = self.readings.list_since(user_id, now - timedelta(days=WINDOW_DAYS))
        evidence, reason = self.evaluate_evidence(readings, now)

        if evidence is None:
            return self._finish(user_id, correlation_id, None, None, reason, "No sufficient evidence.")

        summary_text = (
            f"{evidence.count} {evidence.metric} readings over {evidence.span_days} days "
            f"({evidence.percent_change:+.1f}%)."
        )
        try:
            result = self.adapter.infer(evidence)
        except AIInferenceError:
            return self._finish(user_id, correlation_id, None, None, REASON_AI_FAILED, summary_text)
        if not is_safe_insight(result.observed_trend, result.wellness_implication):
            return self._finish(user_id, correlation_id, None, None, REASON_SAFETY, summary_text)
        return self._finish(
            user_id,
            correlation_id,
            result.observed_trend,
            result.wellness_implication,
            None,
            summary_text,
        )

    @staticmethod
    def evaluate_evidence(
        readings: list[WellnessReading], now: datetime
    ) -> tuple[EvidenceSummary | None, str | None]:
        """Pick the metric with the largest change among those with sufficient, valid, recent data."""
        by_metric: dict[str, list[WellnessReading]] = {}
        for reading in readings:
            bounds = VALID_RANGES.get(reading.metric_type)
            if bounds is None or not bounds[0] <= float(reading.value_numeric) <= bounds[1]:
                continue
            by_metric.setdefault(reading.metric_type, []).append(reading)

        best: EvidenceSummary | None = None
        saw_stale = False
        saw_trend_candidate = False
        for metric, rows in by_metric.items():
            rows.sort(key=lambda r: _aware(r.observed_at))
            first, last = rows[0], rows[-1]
            span = (_aware(last.observed_at) - _aware(first.observed_at)).days
            if len(rows) < MIN_READINGS or span < MIN_SPAN_DAYS:
                continue
            if now - _aware(last.observed_at) > timedelta(days=MAX_STALENESS_DAYS):
                saw_stale = True
                continue
            saw_trend_candidate = True
            first_value, last_value = float(first.value_numeric), float(last.value_numeric)
            change = (last_value - first_value) / first_value * 100 if first_value else 0.0
            if abs(change) < MIN_CHANGE_PERCENT:
                continue
            if best is None or abs(change) > abs(best.percent_change):
                best = EvidenceSummary(metric, last.unit, len(rows), span, first_value, last_value, change)
        if best is not None:
            return best, None
        if saw_trend_candidate:
            return None, REASON_NO_TREND
        return None, REASON_STALE if saw_stale else REASON_INSUFFICIENT

    def _finish(
        self,
        user_id: int,
        correlation_id: str,
        trend: str | None,
        implication: str | None,
        reason: str | None,
        summary: str,
    ) -> Insight:
        status = "published" if reason is None else "suppressed"
        row = self.insights.add(
            user_id=user_id,
            status=status,
            evidence_summary=summary,
            observed_trend=trend,
            wellness_implication=implication,
            suppression_reason=reason,
        )
        if status == "published":
            RecommendationService(self.db).create_for_insight(row)
        self.audit.record(
            action="insight.generated",
            outcome=status,
            correlation_id=correlation_id,
            user_id=user_id,
            entity_type="insight",
            entity_id=str(row.id),
        )
        self.db.commit()
        return row

    def list_for_user(self, user_id: int, limit: int, offset: int) -> tuple[list[Insight], int]:
        return self.insights.list_for_user(user_id, limit, offset)
