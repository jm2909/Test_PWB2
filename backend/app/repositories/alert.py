from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from app.models import AlertAcknowledgement, AlertRule, Reading, WellnessAlert


class AlertRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def list_active_for_owner(self, account_id: uuid.UUID, limit: int = 20) -> list[WellnessAlert]:
        return list(
            self.db.scalars(
                select(WellnessAlert)
                .where(WellnessAlert.account_id == account_id, WellnessAlert.state == "active")
                .order_by(WellnessAlert.event_at.desc(), WellnessAlert.id.desc())
                .limit(limit)
            )
        )

    def rules_for_metric(self, metric_type: str) -> list[AlertRule]:
        return list(
            self.db.scalars(
                select(AlertRule)
                .where(AlertRule.metric_type == metric_type, AlertRule.enabled.is_(True))
                .order_by(AlertRule.identifier)
            )
        )

    def get_rule(self, identifier: str) -> AlertRule | None:
        return self.db.scalar(select(AlertRule).where(AlertRule.identifier == identifier))

    def add_rule(self, rule: AlertRule) -> AlertRule:
        self.db.add(rule)
        self.db.flush()
        return rule

    def find_active(
        self, account_id: uuid.UUID, rule_id: uuid.UUID, reading_id: uuid.UUID
    ) -> WellnessAlert | None:
        return self.db.scalar(
            select(WellnessAlert).where(
                WellnessAlert.account_id == account_id,
                WellnessAlert.alert_rule_id == rule_id,
                WellnessAlert.source_reading_id == reading_id,
                WellnessAlert.state == "active",
            )
        )

    def add(self, alert: WellnessAlert) -> WellnessAlert:
        self.db.add(alert)
        self.db.flush()
        return alert

    def prior_values(
        self, account_id: uuid.UUID, metric_type: str, start: datetime, before: datetime
    ) -> list[float]:
        rows = self.db.scalars(
            select(Reading.value).where(
                Reading.account_id == account_id,
                Reading.metric_type == metric_type,
                Reading.captured_at >= start,
                Reading.captured_at < before,
            )
        )
        return [float(v) for v in rows]

    def list_page(
        self, account_id: uuid.UUID, state: str | None, limit: int, offset: int
    ) -> tuple[list[tuple[WellnessAlert, AlertRule]], int]:
        conditions = [WellnessAlert.account_id == account_id]
        if state is not None:
            conditions.append(WellnessAlert.state == state)
        total = self.db.scalar(select(func.count()).select_from(WellnessAlert).where(*conditions))
        rows = self.db.execute(
            select(WellnessAlert, AlertRule)
            .join(AlertRule, AlertRule.id == WellnessAlert.alert_rule_id)
            .where(*conditions)
            .order_by(WellnessAlert.event_at.desc(), WellnessAlert.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
        return [(a, r) for a, r in rows], int(total or 0)

    def get_owned(
        self, account_id: uuid.UUID, alert_id: uuid.UUID
    ) -> tuple[WellnessAlert, AlertRule] | None:
        row = self.db.execute(
            select(WellnessAlert, AlertRule)
            .join(AlertRule, AlertRule.id == WellnessAlert.alert_rule_id)
            .where(WellnessAlert.id == alert_id, WellnessAlert.account_id == account_id)
        ).first()
        return (row[0], row[1]) if row else None

    def find_acknowledgement(
        self, account_id: uuid.UUID, alert_id: uuid.UUID
    ) -> AlertAcknowledgement | None:
        return self.db.scalar(
            select(AlertAcknowledgement).where(
                AlertAcknowledgement.alert_id == alert_id,
                AlertAcknowledgement.account_id == account_id,
            )
        )

    def add_acknowledgement(self, entry: AlertAcknowledgement) -> AlertAcknowledgement:
        self.db.add(entry)
        self.db.flush()
        return entry
