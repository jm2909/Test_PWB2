from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.clock import utc_now
from app.database import Base
from app.models.types import JSONType, UTCDateTime


class SupportRequest(Base):
    __tablename__ = "support_requests"
    __table_args__ = (
        CheckConstraint(
            "category IN ('connection','data_quality','account','alert')", name="category"
        ),
        CheckConstraint("context_type IN ('device','account','alert')", name="context_type"),
        CheckConstraint("status = 'submitted'", name="status"),
        Index("ix_support_account_submitted", "account_id", "submitted_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    reference: Mapped[str] = mapped_column(String(40), unique=True)
    category: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(2000))
    context_type: Mapped[str] = mapped_column(String(16))
    context_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    status: Mapped[str] = mapped_column(String(24))
    submitted_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_account_occurred", "account_id", "occurred_at"),
        Index("ix_audit_correlation", "correlation_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id"), nullable=True
    )
    correlation_id: Mapped[str] = mapped_column(String(128))
    event_type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(16))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    event_metadata: Mapped[Any] = mapped_column("metadata", JSONType)
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime)
