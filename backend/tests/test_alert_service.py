from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, AuditLog, DeviationEvent
from app.seeds.users import user_id
from app.services import alert_service
from app.services.alert_service import SafeAlertPresentationService
from app.services.safety import is_safe_alert


def test_seeded_alerts_for_asha(seeded: Session) -> None:
    rows = list(seeded.scalars(select(Alert).where(Alert.user_id == user_id(seeded, "asha"))))
    assert sorted(r.urgency for r in rows) == ["routine", "urgent_direction"]


def test_materialize_is_idempotent(seeded: Session) -> None:
    svc = SafeAlertPresentationService(seeded)
    assert svc.materialize(user_id(seeded, "asha"), "t") == 0
    assert len(list(seeded.scalars(select(Alert)))) == 2


def test_urgent_copy_is_safe_and_non_diagnostic(seeded: Session) -> None:
    urgent = seeded.scalar(select(Alert).where(Alert.urgency == "urgent_direction"))
    assert urgent is not None and urgent.care_direction
    assert "doctor or a qualified health professional" in urgent.care_direction
    assert "local emergency number" in urgent.care_direction
    assert "tel:" not in urgent.care_direction
    assert is_safe_alert("urgent_direction", urgent.recommended_next_action, urgent.care_direction)


def test_validator_rejects_unsafe() -> None:
    assert not is_safe_alert("routine", "You have a heart condition, see treatment", None)
    assert not is_safe_alert("urgent_direction", "Check in", None)
    assert not is_safe_alert("urgent_direction", "Check in", "Call tel:112 doctor")


def test_unsafe_text_suppresses_alert_and_records_failure(seeded: Session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    for a in seeded.scalars(select(Alert)):
        seeded.delete(a)
    seeded.commit()
    monkeypatch.setattr(alert_service, "ROUTINE_ACTION", "You have a disease")
    monkeypatch.setattr(alert_service, "URGENT_ACTION", "You have a disease")
    asha = user_id(seeded, "asha")
    assert SafeAlertPresentationService(seeded).materialize(asha, "t") == 0
    assert seeded.scalar(select(Alert)) is None
    assert seeded.scalar(select(AuditLog).where(AuditLog.action == "alert.safety_validation")) is not None
    assert seeded.scalar(select(DeviationEvent)) is not None
