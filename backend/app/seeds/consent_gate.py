"""Consent-gate personas: meena has declined device_processing (paused); rohan has no device consent."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import ConsentRecord
from app.seeds import register
from app.seeds.consents import POLICY_VERSION
from app.seeds.users import user_id

PURPOSE = "device_processing"


@register("consent_gate", order=25)
def seed_consent_gate(db: Session) -> None:
    meena = user_id(db, "meena")
    latest = db.scalar(
        select(ConsentRecord)
        .where(ConsentRecord.user_id == meena, ConsentRecord.purpose == PURPOSE)
        .order_by(ConsentRecord.recorded_at.desc(), ConsentRecord.created_at.desc())
        .limit(1)
    )
    if latest is None or latest.status != "declined":
        db.add(ConsentRecord(user_id=meena, purpose=PURPOSE, version=POLICY_VERSION, status="declined"))
    # Seed-only reset of the baseline row so rohan starts with no device consent on record.
    # seed_consents (order 20) re-adds it each run, so this must stay after it.
    db.execute(
        delete(ConsentRecord).where(
            ConsentRecord.user_id == user_id(db, "rohan"), ConsentRecord.purpose == PURPOSE
        )
    )
    db.flush()
