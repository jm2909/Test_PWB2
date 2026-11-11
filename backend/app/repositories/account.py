from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.models import Account


class AccountRepository:
    def __init__(self, db: DbSession) -> None:
        self.db = db

    def get_by_email(self, email: str) -> Account | None:
        return self.db.scalar(select(Account).where(Account.email == email.lower()))

    def get(self, account_id: uuid.UUID) -> Account | None:
        return self.db.get(Account, account_id)

    def add(self, account: Account) -> Account:
        self.db.add(account)
        self.db.flush()
        return account
