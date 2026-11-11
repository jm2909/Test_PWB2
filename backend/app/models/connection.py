from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.clock import utc_now
from app.database import Base
from app.models.types import UTCDateTime


class Connection(Base):
    __tablename__ = "connections"
    __table_args__ = (
        CheckConstraint("source IN ('scale','wearable')", name="source"),
        CheckConstraint(
            "authorization_state IN ('pending','authorized','failed','revoked')",
            name="authorization_state",
        ),
        CheckConstraint(
            "status IN ('pending','current','stale','failed','disconnected')", name="status"
        ),
        UniqueConstraint(
            "account_id", "source", "provider", "external_identifier", name="uq_connections_device"
        ),
        Index("ix_connections_account_status", "account_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    source: Mapped[str] = mapped_column(String(16))
    provider: Mapped[str] = mapped_column(String(64))
    external_identifier: Mapped[str] = mapped_column(String(128))
    display_label: Mapped[str] = mapped_column(String(100))
    authorization_state: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(24))
    last_successful_sync_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    last_failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = (
        CheckConstraint("source IN ('manual','scale','wearable')", name="source"),
        UniqueConstraint("account_id", "source", "idempotency_key", name="uq_readings_idempotency"),
        Index("ix_readings_owner_metric_capture", "account_id", "metric_type", "captured_at"),
        Index("ix_readings_connection_capture", "connection_id", "captured_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("connections.id"), nullable=True
    )
    metric_type: Mapped[str] = mapped_column(String(64))
    value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    unit: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(16))
    captured_at: Mapped[datetime] = mapped_column(UTCDateTime)
    ingested_at: Mapped[datetime] = mapped_column(UTCDateTime)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)


class ReadingProcessingOutcome(Base):
    __tablename__ = "reading_processing_outcomes"
    __table_args__ = (
        CheckConstraint("outcome IN ('accepted','rejected','duplicate')", name="outcome"),
        Index("ix_reading_outcomes_account_occurred", "account_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    connection_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("connections.id"), nullable=True
    )
    idempotency_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    outcome: Mapped[str] = mapped_column(String(16))
    reason_code: Mapped[str] = mapped_column(String(64))
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime)
