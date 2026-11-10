from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.orm import Session

from app.adapters.ai_inference import AIInferenceAdapter, AIInferenceError, EvidenceSummary, InferenceResult
from app.services.consent_service import ConsentLedgerService, ProcessingBlockedError
from app.services.insight_service import InsightService
from app.services.safety import contains_diagnostic_language, is_safe_insight
from tests.factories import make_connection, make_consent, make_reading, make_user


def _series(db: Session, user_id_user, conn, metric: str, values: list[float], end_offset: int = 0) -> None:
    now = datetime.now(UTC)
    for i, v in enumerate(values):
        make_reading(
            db,
            user_id_user,
            conn,
            metric_type=metric,
            value_numeric=v,
            unit="h",
            observed_at=now - timedelta(days=len(values) - 1 - i + end_offset),
        )


def _ready(db: Session):
    user = make_user(db)
    make_consent(db, user, purpose="personalized_insights", status="accepted")
    return user, make_connection(db, user)


class _Boom(AIInferenceAdapter):
    def infer(self, evidence: EvidenceSummary) -> InferenceResult:
        raise AIInferenceError("down")


class _Diagnostic(AIInferenceAdapter):
    def infer(self, evidence: EvidenceSummary) -> InferenceResult:
        return InferenceResult("Sleep fell.", "This indicates a sleep disorder.")


def test_assert_permitted_blocks_missing_and_declined(db_session: Session) -> None:
    user = make_user(db_session)
    ledger = ConsentLedgerService(db_session)
    with pytest.raises(ProcessingBlockedError):
        ledger.assert_permitted(user.id, "personalized_insights")
    make_consent(db_session, user, purpose="personalized_insights", status="declined")
    with pytest.raises(ProcessingBlockedError) as err:
        ledger.assert_permitted(user.id, "personalized_insights")
    assert err.value.explanation
    make_consent(
        db_session,
        user,
        purpose="personalized_insights",
        status="accepted",
        recorded_at=datetime.now(UTC) + timedelta(seconds=5),
    )
    ledger.assert_permitted(user.id, "personalized_insights")


def test_sufficient_evidence_publishes_trend_and_implication(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [7.2, 7.1, 7.0, 6.9, 6.7, 6.5, 6.4, 6.2, 6.1])
    row = InsightService(db_session).generate(user.id, "c")
    assert row.status == "published"
    assert row.observed_trend and row.wellness_implication and row.suppression_reason is None


def test_sparse_data_is_suppressed(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [7.0, 6.8, 6.6])
    row = InsightService(db_session).generate(user.id, "c")
    assert row.status == "suppressed"
    assert row.observed_trend is None and row.suppression_reason == "insufficient_evidence"


def test_stale_data_is_suppressed(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [7.2, 7.0, 6.8, 6.6, 6.4, 6.2, 6.0, 5.9], end_offset=10)
    assert InsightService(db_session).generate(user.id, "c").suppression_reason == "stale_data"


def test_invalid_values_are_ignored(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0, 97.0])
    assert InsightService(db_session).generate(user.id, "c").status == "suppressed"


def test_adapter_failure_suppresses(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [7.2, 7.1, 7.0, 6.9, 6.7, 6.5, 6.4, 6.2, 6.1])
    row = InsightService(db_session, _Boom()).generate(user.id, "c")
    assert row.status == "suppressed" and row.suppression_reason == "ai_unavailable"


def test_diagnostic_output_is_blocked(db_session: Session) -> None:
    user, conn = _ready(db_session)
    _series(db_session, user, conn, "sleep_hours", [7.2, 7.1, 7.0, 6.9, 6.7, 6.5, 6.4, 6.2, 6.1])
    row = InsightService(db_session, _Diagnostic()).generate(user.id, "c")
    assert row.status == "suppressed" and row.suppression_reason == "safety_blocked"
    assert row.wellness_implication is None


def test_safety_validator() -> None:
    assert contains_diagnostic_language("This may be a diagnosis of insomnia")
    assert not contains_diagnostic_language("Your sleep decreased.")
    assert not is_safe_insight("trend", "")
    assert not is_safe_insight(None, "fine")
    assert is_safe_insight("Sleep fell 10%.", "Consider a steadier bedtime.")
