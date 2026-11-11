from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.clock import utc_now
from app.database import Base
from app.models.types import JSONType, UTCDateTime


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    identifier: Mapped[str] = mapped_column(String(64), unique=True)
    version: Mapped[str] = mapped_column(String(32))
    metric_type: Mapped[str] = mapped_column(String(64))
    definition: Mapped[Any] = mapped_column(JSONType)
    content_template: Mapped[str] = mapped_column(String(1000))
    enabled: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)


class WellnessAlert(Base):
    __tablename__ = "wellness_alerts"
    __table_args__ = (
        CheckConstraint("state IN ('active','acknowledged')", name="state"),
        UniqueConstraint(
            "account_id", "alert_rule_id", "source_reading_id", "state", name="uq_alerts_dedup"
        ),
        Index("ix_alerts_account_state_event", "account_id", "state", "event_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    alert_rule_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alert_rules.id"))
    source_reading_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("readings.id"))
    metric_type: Mapped[str] = mapped_column(String(64))
    event_at: Mapped[datetime] = mapped_column(UTCDateTime)
    reason: Mapped[str] = mapped_column(String(1000))
    state: Mapped[str] = mapped_column(String(16))
    acknowledged_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)


class AlertAcknowledgement(Base):
    __tablename__ = "alert_acknowledgements"
    __table_args__ = (
        UniqueConstraint("alert_id", "account_id", name="uq_alert_ack_owner"),
        Index("ix_alert_ack_account_time", "account_id", "acknowledged_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("wellness_alerts.id"))
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    acknowledged_at: Mapped[datetime] = mapped_column(UTCDateTime)
