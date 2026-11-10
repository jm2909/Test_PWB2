"""Seed consent choices: all three personas accepted both purposes (dated ledger rows)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ConsentRecord
from app.seeds import register
from app.seeds.users import SEED_EMAILS, user_id

POLICY_VERSION = "2024-01"
PURPOSES = ("device_processing", "personalized_insights")


@register("consents", order=20)
def seed_consents(db: Session) -> None:
    for persona in SEED_EMAILS:
        uid = user_id(db, persona)
        for purpose in PURPOSES:
            exists = db.scalar(
                select(ConsentRecord.id).where(ConsentRecord.user_id == uid, ConsentRecord.purpose == purpose)
            )
            if exists is None:
                db.add(ConsentRecord(user_id=uid, purpose=purpose, version=POLICY_VERSION, status="accepted"))
    db.flush()
