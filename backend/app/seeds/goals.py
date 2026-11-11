from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import utc_now
from app.models import (
    Account,
    AlertAcknowledgement,
    AlertRule,
    Reading,
    WellnessAlert,
    WellnessGoal,
)

# (category, metric, target, unit, days until target, state, created days ago)
_GOALS = (
    ("weight_management", "weight", "65", "kg", 90, "active", 60),
    ("sleep_improvement", "sleep_duration", "8", "hours", 60, "paused", 40),
    ("fitness", "steps", "10000", "count", 45, "active", 0),  # created now: no reading since
    ("general_wellness", "active_minutes", "60", "minutes", 30, "closed", 50),
)


def seed_goals(db: Session, accounts: dict[str, Account]) -> None:
    asha = accounts["asha"]
    now = utc_now()
    for category, metric, target, unit, ahead, state, created_ago in _GOALS:
        exists = db.scalar(
            select(WellnessGoal.id).where(
                WellnessGoal.account_id == asha.id,
                WellnessGoal.category == category,
                WellnessGoal.metric_type == metric,
            )
        )
        if exists is None:
            created = now - timedelta(days=created_ago)
            db.add(
                WellnessGoal(
                    account_id=asha.id,
                    category=category,
                    metric_type=metric,
                    target_value=Decimal(target),
                    target_unit=unit,
                    target_date=(now + timedelta(days=ahead)).date(),
                    state=state,
                    created_at=created,
                    updated_at=created,
                )
            )
    db.flush()


def seed_acknowledged_alert(db: Session, accounts: dict[str, Account]) -> None:
    """Asha: a third alert (older reading) that she has already acknowledged."""
    asha = accounts["asha"]
    existing = db.scalar(
        select(WellnessAlert.id).where(
            WellnessAlert.account_id == asha.id, WellnessAlert.state == "acknowledged"
        )
    )
    if existing is not None:
        return
    rule = db.scalar(select(AlertRule).where(AlertRule.identifier == "activity-pattern"))
    reading = db.scalar(
        select(Reading)
        .where(Reading.account_id == asha.id, Reading.metric_type == "steps")
        .order_by(Reading.captured_at.asc(), Reading.id.asc())
    )
    if rule is None or reading is None:
        return
    now = utc_now()
    acked_at = now - timedelta(days=1)
    alert = WellnessAlert(
        account_id=asha.id,
        alert_rule_id=rule.id,
        source_reading_id=reading.id,
        metric_type="steps",
        event_at=reading.captured_at,
        reason="Your daily step count in this period differed from your earlier pattern.",
        state="acknowledged",
        acknowledged_at=acked_at,
        created_at=reading.captured_at,
        updated_at=acked_at,
    )
    db.add(alert)
    db.flush()
    db.add(AlertAcknowledgement(alert_id=alert.id, account_id=asha.id, acknowledged_at=acked_at))
    db.flush()
