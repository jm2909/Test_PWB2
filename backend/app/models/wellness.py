"""Wellness outputs: insights, deviation_events, alerts, recommendations, goals; audit_logs."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, UTCDateTime, utcnow


class Insight(Base):
    __tablename__ = "insights"
    __table_args__ = (
        CheckConstraint("status IN ('published','suppressed')", name="ck_insight_status"),
        Index("ix_insights_user_created", "user_id", "created_at"),
        {"info": {"health_data": True, "retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    observed_trend: Mapped[str | None] = mapped_column(Text, nullable=True)
    wellness_implication: Mapped[str | None] = mapped_column(Text, nullable=True)
    suppression_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class DeviationEvent(Base):
    __tablename__ = "deviation_events"
    __table_args__ = (
        UniqueConstraint("wellness_reading_id", "criterion_code", name="uq_deviation_reading_criterion"),
        Index("ix_deviation_user_created", "user_id", "created_at"),
        {"info": {"health_data": True, "retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    wellness_reading_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("wellness_readings.id"), nullable=False
    )
    criterion_code: Mapped[str] = mapped_column(String(64), nullable=False)
    trend_name: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("urgency IN ('routine','urgent_direction')", name="ck_alert_urgency"),
        Index("ix_alerts_user_created", "user_id", "created_at"),
        {"info": {"health_data": True, "retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    deviation_event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("deviation_events.id"), nullable=False, unique=True
    )
    urgency: Mapped[str] = mapped_column(String(24), nullable=False)
    recommended_next_action: Mapped[str] = mapped_column(Text, nullable=False)
    care_direction: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (
        Index("ix_recommendations_user_created", "user_id", "created_at"),
        {"info": {"retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    insight_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("insights.id"), nullable=False)
    action_text: Mapped[str] = mapped_column(Text, nullable=False)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)


class Goal(Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("status = 'active'", name="ck_goal_status"),
        Index("ix_goals_user_status", "user_id", "status"),
        {"info": {"retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(48), nullable=False)
    target_value: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    target_unit: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    """Who did what, when. Holds no PII values: only ids, action names and outcomes."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_correlation_time", "correlation_id", "occurred_at"),
        {"info": {"append_only": True, "retention_days": 2555}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(96), nullable=False)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(24), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(96), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
