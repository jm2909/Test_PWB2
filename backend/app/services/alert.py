"""AlertService: configured wellness-caution detection with deduplication (FR-015, LLD 3.4)."""

from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from app.clock import Clock, SystemClock, ensure_utc
from app.errors import NotFoundError
from app.models import AlertAcknowledgement, AlertRule, Reading, WellnessAlert
from app.repositories.alert import AlertRepository
from app.schemas.alert import AlertResponse
from app.schemas.common import Page
from app.services import reading as reading_service
from app.services.audit import AuditService
from app.services.content_policy import violations

logger = logging.getLogger("app.alerts")

METRIC_LABELS = {
    "weight": "weight",
    "steps": "daily step count",
    "sleep_duration": "sleep duration",
    "active_minutes": "active minutes",
}


class _SafeDict(dict[str, str]):
    def __missing__(self, key: str) -> str:
        raise KeyError(key)


class AlertService:
    def __init__(self, db: DbSession, clock: Clock | None = None) -> None:
        self.db = db
        self.clock = clock or SystemClock()
        self.repo = AlertRepository(db)
        self.audit = AuditService(db, self.clock)

    # ---- eligibility ----------------------------------------------------------------
    def _eligible(self, rule: AlertRule, reading: Reading) -> bool:
        """Rule definition: window_days, min_prior, threshold_pct, direction."""
        if not rule.enabled or rule.metric_type != reading.metric_type:
            return False
        d: dict[str, Any] = rule.definition or {}
        window = int(d.get("window_days", 30))
        min_prior = int(d.get("min_prior", 3))
        threshold = float(d.get("threshold_pct", 5))
        direction = str(d.get("direction", "any"))
        captured = ensure_utc(reading.captured_at)
        prior = self.repo.prior_values(
            reading.account_id, reading.metric_type, captured - timedelta(days=window), captured
        )
        if len(prior) < min_prior:
            return False
        baseline = sum(prior) / len(prior)
        if baseline == 0:
            return False
        change_pct = (float(reading.value) - baseline) / abs(baseline) * 100
        if direction == "decrease":
            return change_pct <= -threshold
        if direction == "increase":
            return change_pct >= threshold
        return abs(change_pct) >= threshold

    def _render(self, rule: AlertRule, reading: Reading) -> str | None:
        label = METRIC_LABELS.get(reading.metric_type, reading.metric_type.replace("_", " "))
        try:
            text = rule.content_template.format_map(
                _SafeDict(
                    metric=label, event_date=ensure_utc(reading.captured_at).date().isoformat()
                )
            )
        except (KeyError, IndexError, ValueError):
            return None
        if violations(text):
            return None
        return text[:1000]

    # ---- evaluation -----------------------------------------------------------------
    def evaluate(self, reading: Reading) -> list[WellnessAlert]:
        """Evaluate every enabled rule for the accepted reading. Never raises into ingestion."""
        created: list[WellnessAlert] = []
        for rule in self.repo.rules_for_metric(reading.metric_type):
            try:
                if not self._eligible(rule, reading):
                    continue
                reason = self._render(rule, reading)
                if reason is None:
                    logger.warning("alert_rule_wording_rejected rule=%s", rule.identifier)
                    continue
                alert, was_created = self.create_if_absent(rule, reading, reason)
                if was_created:
                    created.append(alert)
            except Exception:  # noqa: BLE001 - alert failure must not block ingestion
                logger.exception("alert_evaluation_failed rule=%s", rule.identifier)
        return created

    def create_if_absent(
        self, rule: AlertRule, reading: Reading, reason: str
    ) -> tuple[WellnessAlert, bool]:
        existing = self.repo.find_active(reading.account_id, rule.id, reading.id)
        if existing is not None:
            return existing, False
        try:
            with self.db.begin_nested():
                alert = self.repo.add(
                    WellnessAlert(
                        account_id=reading.account_id,
                        alert_rule_id=rule.id,
                        source_reading_id=reading.id,
                        metric_type=reading.metric_type,
                        event_at=reading.captured_at,
                        reason=reason,
                        state="active",
                    )
                )
        except IntegrityError:
            raced = self.repo.find_active(reading.account_id, rule.id, reading.id)
            if raced is None:
                raise
            return raced, False
        self.audit.record(
            "alert.created",
            entity_type="wellness_alert",
            account_id=reading.account_id,
            entity_id=alert.id,
            metadata={
                "rule_identifier": rule.identifier,
                "rule_version": rule.version,
                "metric_type": reading.metric_type,
            },
        )
        return alert, True

    def list_alerts(
        self, account_id: uuid.UUID, state: str | None, limit: int, offset: int
    ) -> Page[AlertResponse]:
        rows, total = self.repo.list_page(account_id, state, limit, offset)
        return Page(
            items=[_to_response(a, r) for a, r in rows], limit=limit, offset=offset, total=total
        )

    def acknowledge(self, account_id: uuid.UUID, alert_id: uuid.UUID) -> AlertResponse:
        found = self.repo.get_owned(account_id, alert_id)
        if found is None:
            raise NotFoundError("Alert not found")
        alert, rule = found
        if alert.state == "acknowledged":
            return _to_response(alert, rule)
        now = self.clock.utc_now()
        try:
            with self.db.begin_nested():
                alert.state = "acknowledged"
                alert.acknowledged_at = now
                alert.updated_at = now
                self.repo.add_acknowledgement(
                    AlertAcknowledgement(
                        alert_id=alert.id, account_id=account_id, acknowledged_at=now
                    )
                )
        except IntegrityError:
            self.db.refresh(alert)
            return _to_response(alert, rule)
        self.audit.record(
            "alert.acknowledged",
            entity_type="alert",
            account_id=account_id,
            entity_id=alert.id,
            metadata={"rule_identifier": rule.identifier, "metric_type": alert.metric_type},
        )
        self.db.commit()
        return _to_response(alert, rule)


WELLNESS_BOUNDARY = (
    "This is a wellness observation based on your own readings. "
    "It is not medical advice and does not diagnose or treat any condition."
)


def _to_response(alert: WellnessAlert, rule: AlertRule) -> AlertResponse:
    return AlertResponse(
        id=alert.id,
        metric_type=alert.metric_type,
        event_at=alert.event_at,
        reason=alert.reason,
        rule_identifier=rule.identifier,
        rule_version=rule.version,
        state=alert.state,
        acknowledged_at=alert.acknowledged_at,
        wellness_boundary=WELLNESS_BOUNDARY,
    )


def _observer(db: DbSession, reading: Reading) -> None:
    AlertService(db).evaluate(reading)


def register_alert_evaluation() -> None:
    """Register on the reading-accepted hook (idempotent). Replays never reach the hook."""
    if _observer not in reading_service.on_reading_accepted:
        reading_service.on_reading_accepted.append(_observer)
