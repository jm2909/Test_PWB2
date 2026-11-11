from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.clock import utc_now
from app.database import Base
from app.models.types import JSONType, UTCDateTime


class ConsentRecord(Base):
    __tablename__ = "consent_records"
    __table_args__ = (
        CheckConstraint("decision IN ('granted','withdrawn')", name="decision"),
        CheckConstraint("purpose = 'wellness_support'", name="purpose"),
        Index("ix_consent_records_account_recorded", "account_id", "recorded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    decision: Mapped[str] = mapped_column(String(16))
    notice_version: Mapped[str] = mapped_column(String(64))
    data_categories: Mapped[Any] = mapped_column(JSONType)
    purpose: Mapped[str] = mapped_column(String(64))
    recorded_at: Mapped[datetime] = mapped_column(UTCDateTime)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)


class DataRightsRequest(Base):
    __tablename__ = "data_rights_requests"
    __table_args__ = (
        CheckConstraint("request_type IN ('export','deletion')", name="request_type"),
        CheckConstraint(
            "status IN ('submitted','in_review','fulfilled','rejected')", name="status"
        ),
        Index("ix_rights_requests_account_requested", "account_id", "requested_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.id"))
    reference: Mapped[str] = mapped_column(String(40), unique=True)
    request_type: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(24))
    requested_at: Mapped[datetime] = mapped_column(UTCDateTime)
    fulfillment_due_at: Mapped[datetime] = mapped_column(UTCDateTime)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)
