"""Seed alert rules, asha's insights and two alerts (one active, one ready for acknowledgement)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Account, AlertRule, Reading
from app.repositories.alert import AlertRepository
from app.repositories.insight import InsightRepository
from app.services.alert import AlertService
from app.services.content_policy import PROFESSIONAL_SUPPORT_NOTE
from app.services.insight import InsightService

_TEMPLATE = (
    "Your {metric} reading on {event_date} differs from your recent pattern. "
    + PROFESSIONAL_SUPPORT_NOTE
)

RULES = (
    (
        "weight-change-pattern",
        "weight",
        {"window_days": 30, "min_prior": 3, "threshold_pct": 3, "direction": "any"},
    ),
    (
        "activity-pattern",
        "steps",
        {"window_days": 14, "min_prior": 3, "threshold_pct": 25, "direction": "any"},
    ),
)


def seed_alert_rules(db: Session) -> dict[str, AlertRule]:
    repo = AlertRepository(db)
    rules: dict[str, AlertRule] = {}
    for identifier, metric, definition in RULES:
        rule = repo.get_rule(identifier)
        if rule is None:
            rule = repo.add_rule(
                AlertRule(
                    identifier=identifier,
                    version="1.0",
                    metric_type=metric,
                    definition=definition,
                    content_template=_TEMPLATE,
                    enabled=True,
                )
            )
        rules[identifier] = rule
    return rules


def seed_insights_and_alerts(db: Session, accounts: dict[str, Account]) -> None:
    asha = accounts["asha"]
    rules = seed_alert_rules(db)
    insights = InsightService(db)
    repo = InsightRepository(db)
    if repo.find_for_metric(asha.id, "weight") is None:
        insights.generate(asha.id, "weight", 30)
    if repo.find_for_metric(asha.id, "steps") is None:
        insights.generate(asha.id, "steps", 7, min_readings=5)  # limited-data example
    alerts = AlertService(db)
    for identifier, metric in (("weight-change-pattern", "weight"), ("activity-pattern", "steps")):
        rule = rules[identifier]
        reading = db.scalar(
            select(Reading)
            .where(Reading.account_id == asha.id, Reading.metric_type == metric)
            .order_by(Reading.captured_at.desc(), Reading.id.desc())
        )
        if reading is None:
            continue
        reason = alerts._render(rule, reading)  # noqa: SLF001 - same module family, approved wording
        if reason is not None:
            alerts.create_if_absent(rule, reading, reason)
    db.flush()
