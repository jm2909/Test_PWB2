"""Seed users. The canonical demo password lives in SEED_PASSWORD only."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password
from app.seeds import register

SEED_PASSWORD = "correct-horse-battery"  # noqa: S105 - documented demo credential
SEED_EMAILS = {
    "asha": "asha.menon@example.com",
    "rohan": "rohan.iyer@example.com",
    "meena": "meena.rao@example.com",
}


@register("users", order=10)
def seed_users(db: Session) -> None:
    password_hash: str | None = None
    for email in SEED_EMAILS.values():
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            continue
        password_hash = password_hash or hash_password(SEED_PASSWORD)
        db.add(User(email=email, password_hash=password_hash))
    db.flush()


def user_id(db: Session, persona: str) -> int:
    found = db.scalar(select(User.id).where(User.email == SEED_EMAILS[persona]))
    if found is None:
        raise LookupError(f"seed user {persona} missing")
    return int(found)
