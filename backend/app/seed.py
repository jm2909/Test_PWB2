"""Seed runner: `python -m app.seed`. Idempotent; schema must already be migrated."""

from app.database import SessionLocal
from app.middleware.logging_config import configure_logging
from app.seeds import run_all


def main() -> None:
    configure_logging()
    with SessionLocal() as db:
        ran = run_all(db)
    print(f"Seed complete ({len(ran)} modules): {', '.join(ran) or 'none registered yet'}")  # noqa: T201


if __name__ == "__main__":
    main()
