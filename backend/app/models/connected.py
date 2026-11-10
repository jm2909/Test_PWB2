"""Connected-data models: device_connections, sync_attempts, wellness_readings."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, UTCDateTime, utcnow


class DeviceConnection(Base):
    __tablename__ = "device_connections"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','connected','action_required','failed','revoked')",
            name="ck_connection_status",
        ),
        UniqueConstraint("user_id", "provider", name="uq_connection_user_provider"),
        Index("ix_connections_user_status", "user_id", "status"),
        {"info": {"retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(48), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    permitted_categories: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    last_successful_sync_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    recovery_action: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow, onupdate=utcnow)


class SyncAttempt(Base):
    __tablename__ = "sync_attempts"
    __table_args__ = (
        UniqueConstraint("device_connection_id", "idempotency_key", name="uq_sync_connection_key"),
        CheckConstraint("status IN ('started','succeeded','failed')", name="ck_sync_status"),
        Index("ix_sync_connection_started", "device_connection_id", "started_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    device_connection_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("device_connections.id"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(String(256), nullable=True)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)


class WellnessReading(Base):
    __tablename__ = "wellness_readings"
    __table_args__ = (
        UniqueConstraint("device_connection_id", "source_event_id", name="uq_reading_connection_event"),
        Index("ix_readings_user_metric_time", "user_id", "metric_type", "observed_at"),
        {"info": {"health_data": True, "retention_days": 1095}},
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    device_connection_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("device_connections.id"), nullable=False
    )
    source_event_id: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(64), nullable=False)
    value_numeric: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(24), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False)
    normalized_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, nullable=False, default=utcnow)
