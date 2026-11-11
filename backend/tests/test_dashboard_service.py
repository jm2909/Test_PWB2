from datetime import UTC, datetime, timedelta

from app.clock import utc_now
from app.services.dashboard import DashboardCompositionService
from tests.conftest import Factories


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def utc_now(self) -> datetime:
        return self.now


def test_empty_account_all_unavailable(db_session):
    acct = Factories(db_session).account()
    out = DashboardCompositionService(db_session).compose(acct.id)
    assert out.measurements == []
    assert {u.metric_type for u in out.unavailable_categories} == {
        "weight",
        "steps",
        "sleep_duration",
        "active_minutes",
    }
    assert out.alerts == [] and out.goals == [] and out.insights == [] and out.source_statuses == []


def test_latest_reading_and_status(db_session):
    f = Factories(db_session)
    acct = f.account()
    now = utc_now()
    f.reading(acct, value=70, captured_at=now - timedelta(days=3))
    f.reading(acct, value=69, captured_at=now - timedelta(hours=1))
    out = DashboardCompositionService(db_session).compose(acct.id)
    (m,) = out.measurements
    assert float(m.value) == 69 and m.status == "current"
    future = FixedClock(now + timedelta(days=5))
    later = DashboardCompositionService(db_session, future).compose(acct.id)
    assert later.measurements[0].status == "stale"
    assert "weight" not in {u.metric_type for u in out.unavailable_categories}


def test_connection_freshness_and_insufficient_insight(db_session):
    f = Factories(db_session)
    acct = f.account()
    now = utc_now()
    f.connection(acct, last_successful_sync_at=now - timedelta(days=3))
    f.reading(acct)
    out = DashboardCompositionService(db_session, FixedClock(now)).compose(acct.id)
    assert out.source_statuses[0].status == "stale"
    assert out.insights[0].status == "insufficient_data"


def test_owner_isolation_and_active_only(db_session):
    f = Factories(db_session)
    a, b = f.account(), f.account()
    f.goal(a)
    f.goal(a, state="closed")
    f.goal(b)
    f.insight(b)
    r = f.reading(b)
    rule = f.alert_rule()
    f.alert(b, rule, r)
    out = DashboardCompositionService(db_session).compose(a.id)
    assert len(out.goals) == 1
    assert out.alerts == [] and out.measurements == []
    assert all(i.metric_type != "weight" or i.id is None for i in out.insights)
    assert datetime.now(UTC)
