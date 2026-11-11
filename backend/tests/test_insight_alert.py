from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models import AlertRule, AuditLog, Insight, InsightFeedback, WellnessAlert
from app.services.alert import AlertService
from app.services.content_policy import ContentPolicyError, ensure_allowed
from app.services.insight import InsightService


def _grant(client, headers):
    r = client.put(
        "/api/v1/consents/current",
        headers=headers,
        json={
            "decision": "granted",
            "notice_version": "v1.0",
            "data_categories": ["weight"],
            "purpose": "wellness_support",
        },
    )
    assert r.status_code in (200, 201), r.text


def _post(client, headers, value, hours_ago, key):
    h = {**headers, "Idempotency-Key": key}
    return client.post(
        "/api/v1/readings",
        headers=h,
        json={
            "metric_type": "weight",
            "value": str(value),
            "unit": "kg",
            "source": "manual",
            "captured_at": (datetime.now(UTC) - timedelta(hours=hours_ago)).isoformat(),
        },
    )


def _rule(factories, **kw):
    return factories.alert_rule(
        identifier="t-weight",
        version="2.1",
        definition={"window_days": 30, "min_prior": 3, "threshold_pct": 3, "direction": "any"},
        content_template="Your {metric} on {event_date} differs from your pattern. "
        "This is wellness guidance only; consider a qualified professional.",
        **kw,
    )


def _history(client, headers):
    for i, v in enumerate((70, 70.2, 69.8)):
        assert _post(client, headers, v, 50 - i, f"h{i}").status_code == 201


# ---- insights -------------------------------------------------------------------------
def test_insight_requires_auth(client):
    assert client.get("/api/v1/insights").status_code == 401


def test_insight_list_owner_only_and_shape(
    client, auth_client, db_session, factories, seeded_accounts
):
    factories.insight(seeded_accounts["asha"])
    factories.insight(seeded_accounts["rohan"], observation="Rohan only.")
    body = auth_client.get("/api/v1/insights").json()
    assert body["total"] == 1
    item = body["items"][0]
    assert set(item) == {
        "id", "metric_type", "observation_period", "observation",
        "wellness_guidance", "uncertainty", "created_at",
    }  # fmt: skip
    assert set(item["observation_period"]) == {"start", "end"}


def test_insight_generate_with_data_separates_measured_from_guidance(
    db_session, factories, seeded_accounts
):
    asha = seeded_accounts["asha"]
    now = datetime.now(UTC)
    for i, v in enumerate((70, 69.5, 69)):
        factories.reading(asha, value=v, captured_at=now - timedelta(days=3 - i))
    insight = InsightService(db_session).generate(asha.id, "weight", 30)
    assert "averaged" in insight.observation
    assert insight.wellness_guidance and insight.wellness_guidance != insight.observation
    assert insight.uncertainty


def test_insight_insufficient_data_has_no_guidance(db_session, seeded_accounts):
    insight = InsightService(db_session).generate(seeded_accounts["asha"].id, "steps", 7)
    assert "Only 0" in insight.observation
    assert "not offered" in insight.wellness_guidance


@pytest.mark.parametrize(
    "text",
    ["This may be a diagnosis", "Seek treatment", "Call emergency services", "clinical advice"],
)
def test_insight_content_policy_rejects_clinical_wording(text):
    with pytest.raises(ContentPolicyError):
        ensure_allowed(text)


def test_insight_policy_blocks_persistence(db_session, seeded_accounts):
    svc = InsightService(db_session)
    with pytest.raises(ContentPolicyError):
        svc._persist(  # noqa: SLF001
            seeded_accounts["asha"].id, "weight", datetime.now(UTC), datetime.now(UTC),
            "Possible diabetes", "ok", "ok",
        )  # fmt: skip
    assert db_session.scalar(select(func.count()).select_from(Insight)) == 0


def test_insight_feedback_created_once_and_foreign_404(
    client, auth_client, db_session, factories, seeded_accounts
):
    mine = factories.insight(seeded_accounts["asha"])
    theirs = factories.insight(seeded_accounts["rohan"])
    r = auth_client.post(f"/api/v1/insights/{mine.id}/feedback", json={"useful": False})
    assert r.status_code == 201, r.text
    assert set(r.json()) == {"id", "insight_id", "useful", "submitted_at"}
    assert r.json()["useful"] is False
    assert (
        auth_client.post(f"/api/v1/insights/{mine.id}/feedback", json={"useful": True}).status_code
        == 409
    )
    assert (
        auth_client.post(
            f"/api/v1/insights/{theirs.id}/feedback", json={"useful": True}
        ).status_code
        == 404
    )
    assert db_session.scalar(select(func.count()).select_from(InsightFeedback)) == 1


def test_insight_feedback_validates_body(auth_client, factories, seeded_accounts):
    mine = factories.insight(seeded_accounts["asha"])
    assert (
        auth_client.post(
            f"/api/v1/insights/{mine.id}/feedback", json={"useful": "maybe"}
        ).status_code
        == 422
    )


# ---- alert evaluation -----------------------------------------------------------------
def test_alert_evaluation_creates_alert_with_rule_version_and_wording(
    client, auth_headers, db_session, factories
):
    h = auth_headers("rohan")
    _grant(client, h)
    rule = _rule(factories)
    _history(client, h)
    assert _post(client, h, 80, 1, "spike").status_code == 201
    alert = db_session.scalars(select(WellnessAlert)).one()
    assert alert.alert_rule_id == rule.id and alert.state == "active"
    assert "wellness guidance" in alert.reason and "professional" in alert.reason
    assert alert.metric_type == "weight" and alert.event_at is not None
    audit = db_session.scalars(select(AuditLog).where(AuditLog.event_type == "alert.created")).one()
    assert audit.event_metadata["rule_identifier"] == "t-weight"
    assert audit.event_metadata["rule_version"] == "2.1"
    assert "80" not in str(audit.event_metadata.values())


def test_alert_evaluation_no_alert_for_normal_reading(client, auth_headers, db_session, factories):
    h = auth_headers("rohan")
    _grant(client, h)
    _rule(factories)
    _history(client, h)
    assert _post(client, h, 70.1, 1, "ok").status_code == 201
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 0


def test_alert_evaluation_disabled_rule_or_thin_history(
    client, auth_headers, db_session, factories
):
    h = auth_headers("rohan")
    _grant(client, h)
    rule = _rule(factories)
    assert _post(client, h, 80, 5, "first").status_code == 201  # no prior history
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 0
    _history(client, h)
    rule.enabled = False
    db_session.commit()
    assert _post(client, h, 90, 1, "off").status_code == 201
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 0


def test_alert_evaluation_dedupe_retains_existing(client, db_session, factories, seeded_accounts):
    asha = seeded_accounts["asha"]
    rule = _rule(factories)
    reading = factories.reading(asha)
    svc = AlertService(db_session)
    first, created = svc.create_if_absent(rule, reading, "Wellness guidance only.")
    again, created_again = svc.create_if_absent(rule, reading, "Wellness guidance only.")
    db_session.commit()
    assert created and not created_again and again.id == first.id
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 1


def test_alert_evaluation_replay_does_not_reevaluate(client, auth_headers, db_session, factories):
    h = auth_headers("rohan")
    _grant(client, h)
    _rule(factories)
    _history(client, h)
    body_args = (80, 1, "spike")
    assert _post(client, h, *body_args).status_code == 201
    # replaying the same payload at a different time is rejected as mismatch or replayed
    db_session.expire_all()
    before = db_session.scalar(select(func.count()).select_from(WellnessAlert))
    replay = client.post(
        "/api/v1/readings",
        headers={**h, "Idempotency-Key": "spike"},
        json=client.get("/api/v1/readings", headers=h).json()["items"][0]
        | {"source": "manual", "connection_id": None},
    )
    assert replay.status_code in (200, 409)
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == before == 1


def test_alert_evaluation_wording_policy_rejects_clinical_template(
    client, auth_headers, db_session, factories
):
    h = auth_headers("rohan")
    _grant(client, h)
    factories.alert_rule(
        identifier="bad",
        metric_type="weight",
        definition={"window_days": 30, "min_prior": 3, "threshold_pct": 3},
        content_template="Possible diagnosis detected on {event_date}.",
    )
    _history(client, h)
    assert _post(client, h, 90, 1, "spike").status_code == 201
    assert db_session.scalar(select(func.count()).select_from(WellnessAlert)) == 0


def test_alert_evaluation_seed_rules_and_alerts(full_seed, db_session):
    ids = set(db_session.scalars(select(AlertRule.identifier)))
    assert {"weight-change-pattern", "activity-pattern"} <= ids
    active = select(func.count()).select_from(WellnessAlert).where(WellnessAlert.state == "active")
    assert db_session.scalar(active) == 2
    assert db_session.scalar(select(func.count()).select_from(Insight)) == 2
    from app.seed import seed_all

    seed_all(db_session)
    active = select(func.count()).select_from(WellnessAlert).where(WellnessAlert.state == "active")
    assert db_session.scalar(active) == 2
    assert db_session.scalar(select(func.count()).select_from(Insight)) == 2
