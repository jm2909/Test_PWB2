"""Safe wellness alerts (FR-020): deviation events become non-diagnostic alerts, idempotently."""

import structlog
from sqlalchemy.orm import Session

from app.models import Alert, DeviationEvent
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert_schemas import AlertResponse
from app.services.audit_service import AuditService
from app.services.safety import is_safe_alert

log = structlog.get_logger("alerts")

ROUTINE_ACTION = "Review your sleep and activity this week, and keep syncing your wearable."
URGENT_ACTION = "Check in with how you feel today and consider speaking with a health professional."
CARE_DIRECTION = (
    "If you feel unwell, contact your doctor or a qualified health professional. "
    "If you think it is an emergency, call your local emergency number now."
)
URGENT_CRITERIA = {"rhr_sustained_14d"}

_WHAT_WE_SAW = {
    "rhr_rise_14d": "Your resting heart rate has been rising over the last 14 days.",
    "rhr_sustained_14d": "Your resting heart rate has stayed above your usual range for about 14 days.",
    "sleep_decline_14d": "Your sleep duration has fallen over the last 14 days.",
    "weight_change_14d": "Your weight has changed noticeably over the last 14 days.",
}


def what_we_saw(event: DeviationEvent) -> str:
    return _WHAT_WE_SAW.get(event.criterion_code, f"We noticed a change: {event.trend_name}.")


def to_response(alert: Alert, event: DeviationEvent) -> AlertResponse:
    return AlertResponse.model_validate(
        {
            "id": alert.id,
            "trend_name": event.trend_name,
            "urgency": alert.urgency,
            "what_we_saw": what_we_saw(event),
            "recommended_next_action": alert.recommended_next_action,
            "care_direction": alert.care_direction,
            "created_at": alert.created_at,
        }
    )


class SafeAlertPresentationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AlertRepository(db)
        self.audit = AuditService(db)

    @staticmethod
    def compose(event: DeviationEvent) -> tuple[str, str, str | None]:
        if event.criterion_code in URGENT_CRITERIA:
            return "urgent_direction", URGENT_ACTION, CARE_DIRECTION
        return "routine", ROUTINE_ACTION, None

    def materialize(self, user_id: int, correlation_id: str) -> int:
        """Create alerts for the user's unalerted events; unsafe copy suppresses the alert."""
        created = 0
        for event in self.repo.unalerted_events(user_id):
            urgency, action, care = self.compose(event)
            if not is_safe_alert(urgency, action, care):
                log.error("alert_suppressed_unsafe_text", criterion=event.criterion_code)
                self.audit.record(
                    action="alert.safety_validation",
                    outcome="failure",
                    severity="error",
                    correlation_id=correlation_id,
                    user_id=user_id,
                    entity_type="deviation_event",
                    entity_id=str(event.id),
                )
                continue
            alert = Alert(
                user_id=user_id,
                deviation_event_id=event.id,
                urgency=urgency,
                recommended_next_action=action,
                care_direction=care,
            )
            if self.repo.add_unique(alert):
                created += 1
                self.audit.record(
                    action="alert.created",
                    outcome=urgency,
                    correlation_id=correlation_id,
                    user_id=user_id,
                    entity_type="alert",
                    entity_id=str(alert.id),
                )
        self.db.commit()
        return created

    def list_for_user(
        self, user_id: int, limit: int, offset: int, correlation_id: str
    ) -> tuple[list[AlertResponse], int]:
        self.materialize(user_id, correlation_id)
        rows, total = self.repo.list_with_events(user_id, limit, offset)
        return [to_response(a, e) for a, e in rows], total
