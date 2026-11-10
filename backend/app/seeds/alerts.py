"""Seed alerts: Asha gets a routine and an urgent_direction alert for her two deviation events."""

from sqlalchemy.orm import Session

from app.seeds import register
from app.seeds.users import user_id
from app.services.alert_service import SafeAlertPresentationService


@register("alerts", order=45)
def seed_alerts(db: Session) -> None:
    SafeAlertPresentationService(db).materialize(user_id(db, "asha"), "seed")
