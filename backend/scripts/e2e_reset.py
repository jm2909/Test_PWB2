"""Reset a migrated database to its seeded state (used by browser E2E specs that mutate shared data)."""

from app import models  # noqa: F401  (registers every table on Base.metadata)
from app.database import Base, SessionLocal
from app.seeds import run_all


def main() -> None:
    with SessionLocal() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
        run_all(db)
        db.commit()


if __name__ == "__main__":
    main()
