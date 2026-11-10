import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.base import RawReading
from app.database import utcnow
from app.models import SyncAttempt, WellnessReading
from app.seeds.users import user_id
from app.services.consent_service import ProcessingBlockedError
from app.services.sync_service import (
    ConnectionNotFoundError,
    SyncIngestionService,
    clear_post_ingest_hooks,
    normalize,
    register_post_ingest_hook,
)
from app.services.sync_status_service import SyncStatusRecoveryService
from tests.factories import make_connection, make_consent, make_user


@pytest.fixture(autouse=True)
def _hooks() -> Iterator[None]:
    clear_post_ingest_hooks()
    yield
    clear_post_ingest_hooks()


def _setup(db: Session, consent: str = "accepted", **conn: object):  # type: ignore[no-untyped-def]
    user = make_user(db)
    make_consent(db, user, purpose="device_processing", status=consent)
    c = make_connection(
        db,
        user,
        provider=str(conn.pop("provider", "wearable_platform_a")),
        permitted_categories=conn.pop("permitted_categories", ["sleep", "heart_rate", "activity"]),
        **conn,
    )
    return user, c


KEY = "key-0123456789abcdef"


def test_sync_normalizes_and_updates_state(db_session: Session) -> None:
    user, c = _setup(db_session)
    row, summary = SyncIngestionService(db_session).sync(user.id, c.id, KEY, "cid")
    assert summary.new_readings == 9 and summary.duplicates == 0
    assert set(summary.by_metric) == {"sleep_hours", "resting_heart_rate", "steps"}
    assert row.status == "connected" and row.last_successful_sync_at is not None
    sleep = db_session.scalars(
        select(WellnessReading).where(WellnessReading.metric_type == "sleep_hours")
    ).first()
    assert sleep is not None and sleep.unit == "h" and 6 < float(sleep.value_numeric) < 9
    assert sleep.observed_at.utcoffset().total_seconds() == 0  # type: ignore[union-attr]


def test_normalize_weight_to_kg() -> None:
    raw = RawReading("e1", "weight", 150.0, "lb", utcnow())
    r = normalize(raw, utcnow(), 1, uuid.uuid4())
    assert r is not None and r.unit == "kg" and abs(float(r.value_numeric) - 68.0389) < 0.001


def test_same_key_replays_original(db_session: Session) -> None:
    user, c = _setup(db_session)
    svc = SyncIngestionService(db_session)
    _, first = svc.sync(user.id, c.id, KEY, "cid")
    _, second = svc.sync(user.id, c.id, KEY, "cid")
    assert second == first
    assert db_session.scalar(select(func.count()).select_from(WellnessReading)) == 9


def test_new_key_same_events_counts_duplicates(db_session: Session) -> None:
    user, c = _setup(db_session)
    svc = SyncIngestionService(db_session)
    svc.sync(user.id, c.id, KEY, "cid")
    _, again = svc.sync(user.id, c.id, "other-key-0123456789", "cid")
    assert again.new_readings == 0 and again.duplicates == 9
    assert db_session.scalar(select(func.count()).select_from(WellnessReading)) == 9


def test_consent_declined_blocks_before_adapter(db_session: Session) -> None:
    user, c = _setup(db_session, consent="declined")

    class Boom:
        provider = "wearable_platform_a"
        supported_modes = ("authorize",)

        def fetch_readings(self, *a: object, **k: object) -> list[RawReading]:
            raise AssertionError("adapter must not be called")

    with pytest.raises(ProcessingBlockedError):
        SyncIngestionService(db_session, {"wearable_platform_a": Boom()}).sync(user.id, c.id, KEY, "cid")  # type: ignore[dict-item]
    assert db_session.scalar(select(func.count()).select_from(SyncAttempt)) == 0


def test_not_owner_is_not_found(db_session: Session) -> None:
    _, c = _setup(db_session)
    other = make_user(db_session)
    with pytest.raises(ConnectionNotFoundError):
        SyncIngestionService(db_session).sync(other.id, c.id, KEY, "cid")


@pytest.mark.parametrize(
    ("prefix", "status", "action"),
    [
        ("sim-fail", "failed", "Retry"),
        ("sim-revoke", "revoked", "Reconnect"),
        ("sim-permission", "action_required", "Review permissions"),
    ],
)
def test_failure_states(db_session: Session, prefix: str, status: str, action: str) -> None:
    user, c = _setup(db_session)
    row, summary = SyncIngestionService(db_session).sync(user.id, c.id, f"{prefix}-0123456789abc", "cid")
    assert (row.status, row.recovery_action) == (status, action) and row.failure_reason
    assert summary.new_readings == 0 and not SyncStatusRecoveryService.is_current(row)
    attempt = db_session.scalars(select(SyncAttempt)).one()
    assert attempt.status == "failed" and attempt.failure_reason


def test_failed_then_retry_clears_failure(db_session: Session) -> None:
    user, c = _setup(db_session)
    svc = SyncIngestionService(db_session)
    svc.sync(user.id, c.id, "sim-fail-0123456789abc", "cid")
    row, summary = svc.sync(user.id, c.id, "retry-0123456789abcd", "cid")
    assert row.status == "connected" and row.failure_reason is None and row.recovery_action is None
    assert summary.new_readings == 9


def test_hook_receives_new_ids_only(db_session: Session) -> None:
    calls: list[list[uuid.UUID]] = []
    register_post_ingest_hook(lambda db, uid, ids: calls.append(ids))
    user, c = _setup(db_session)
    svc = SyncIngestionService(db_session)
    svc.sync(user.id, c.id, KEY, "cid")
    svc.sync(user.id, c.id, "other-key-0123456789", "cid")
    assert len(calls) == 1 and len(calls[0]) == 9


def test_failing_hook_does_not_break_sync(db_session: Session) -> None:
    def bad(db: Session, uid: int, ids: list[uuid.UUID]) -> None:
        raise RuntimeError("x")

    register_post_ingest_hook(bad)
    user, c = _setup(db_session)
    row, summary = SyncIngestionService(db_session).sync(user.id, c.id, KEY, "cid")
    assert summary.new_readings == 9 and row.status == "connected"


def test_seed_user_helper_exists(seeded: Session) -> None:
    assert user_id(seeded, "asha") > 0
