from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Account
from app.repositories.account import AccountRepository
from app.security import hash_password
from app.seeds.constants import DEMO_ACCOUNTS


def seed_accounts(db: Session) -> dict[str, Account]:
    """Create the demo personas if absent (natural key: email)."""
    repo = AccountRepository(db)
    result: dict[str, Account] = {}
    for persona, spec in DEMO_ACCOUNTS.items():
        account = repo.get_by_email(spec["email"])
        if account is None:
            account = repo.add(
                Account(
                    email=spec["email"],
                    password_hash=hash_password(spec["password"]),
                    display_name=spec["display_name"],
                )
            )
        result[persona] = account
    return result
