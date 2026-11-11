from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models import Reading, ReadingProcessingOutcome
from app.services import reading as reading_module


def _body(**kw):
    data = {
        "metric_type": "weight",
        "value": "70.5",
        "unit": "kg",
        "source": "manual",
        "captured_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
    }
    data.update(kw)
    return data


def _consent(client, headers):
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


def _post(client, headers, body, key="k1"):
    h = dict(headers)
    if key is not None:
        h["Idempotency-Key"] = key
    return client.post("/api/v1/readings", headers=h, json=body)


def test_reading_requires_auth(client):
    assert client.post("/api/v1/readings", json=_body()).status_code == 401
    assert client.get("/api/v1/readings").status_code == 401


def test_reading_no_consent_denied(client, auth_headers):
    r = _post(client, auth_headers("rohan"), _body())
    assert r.status_code == 403


def test_reading_accepted_and_replayed(client, db_session, auth_headers):
    h = auth_headers("rohan")
    _consent(client, h)
    payload = _body()
    first = _post(client, h, payload)
    assert first.status_code == 201, first.text
    body = first.json()
    assert body["metric_type"] == "weight" and body["connection_id"] is None
    assert body["ingested_at"] and body["captured_at"]
    again = _post(client, h, payload)
    assert again.status_code == 200
    assert again.json()["id"] == body["id"]
    assert len(db_session.scalars(select(Reading)).all()) == 1
    outcomes = {o.outcome for o in db_session.scalars(select(ReadingProcessingOutcome))}
    assert outcomes == {"accepted", "duplicate"}


def test_reading_idempotency_mismatch(client, auth_headers):
    h = auth_headers("rohan")
    _consent(client, h)
    payload = _body()
    assert _post(client, h, payload).status_code == 201
    r = _post(client, h, {**payload, "value": "71.0"})
    assert r.status_code == 409
    assert r.json() == {"detail": "Idempotency key payload mismatch"}


def test_reading_requires_idempotency_key(client, auth_headers):
    h = auth_headers("rohan")
    _consent(client, h)
    assert _post(client, h, _body(), key=None).status_code == 400


def test_reading_rejections_record_reason_only(client, db_session, auth_headers):
    h = auth_headers("rohan")
    _consent(client, h)
    future = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    cases = [
        (_body(value="9999"), "value_out_of_range"),
        (_body(unit="lb"), "unit_not_allowed"),
        (_body(metric_type="mood"), "unsupported_metric"),
        (_body(source="fax"), "unsupported_source"),
        (_body(captured_at=future), "timestamp_in_future"),
        (_body(captured_at="2026-01-01T10:00:00"), "timestamp_not_utc"),
        (_body(source="wearable"), "connection_required"),
    ]
    for i, (body, reason) in enumerate(cases):
        r = _post(client, h, body, key=f"bad-{i}")
        assert r.status_code == 400, (reason, r.text)
        assert "9999" not in r.text
    rows = db_session.scalars(select(ReadingProcessingOutcome)).all()
    assert {o.reason_code for o in rows} == {reason for _, reason in cases}
    assert all(o.outcome == "rejected" for o in rows)
    assert db_session.scalars(select(Reading)).all() == []


def test_reading_external_requires_owned_connection(
    client, db_session, auth_headers, factories, seeded_accounts
):
    h = auth_headers("rohan")
    _consent(client, h)
    other = factories.connection(seeded_accounts["asha"])
    mine = factories.connection(
        seeded_accounts["rohan"], last_successful_sync_at=None, status="stale"
    )
    r = _post(client, h, _body(source="scale", connection_id=str(other.id)), key="x1")
    assert r.status_code == 400
    ok = _post(client, h, _body(source="scale", connection_id=str(mine.id)), key="x2")
    assert ok.status_code == 201, ok.text
    db_session.refresh(mine)
    assert mine.last_successful_sync_at is not None and mine.status == "current"


def test_reading_list_order_filters_isolation(client, auth_headers):
    h = auth_headers("rohan")
    _consent(client, h)
    base = datetime.now(UTC) - timedelta(days=3)
    for i in range(3):
        stamp = (base + timedelta(days=i)).isoformat()
        assert _post(client, h, _body(captured_at=stamp), key=f"w{i}").status_code == 201
    assert (
        _post(
            client, h, _body(metric_type="steps", unit="count", value="5000"), key="s1"
        ).status_code
        == 201
    )
    page = client.get("/api/v1/readings?metric_type=weight&limit=2", headers=h).json()
    assert page["total"] == 3 and len(page["items"]) == 2
    stamps = [i["captured_at"] for i in page["items"]]
    assert stamps == sorted(stamps, reverse=True)
    window = client.get(
        "/api/v1/readings",
        headers=h,
        params={"metric_type": "weight", "from": (base + timedelta(hours=1)).isoformat()},
    ).json()
    assert window["total"] == 2
    asha = client.get("/api/v1/readings", headers=auth_headers("asha")).json()
    assert all(i["metric_type"] != "steps" or i["value"] != "5000.0000" for i in asha["items"])
    mine_ids = {x["id"] for x in page["items"]}
    assert all(i["id"] not in mine_ids for i in asha["items"])


def test_reading_observer_runs_once_per_accepted(client, auth_headers):
    calls = []
    reading_module.on_reading_accepted.append(lambda db, r: calls.append(r.id))
    try:
        h = auth_headers("rohan")
        _consent(client, h)
        payload = _body()
        _post(client, h, payload)
        _post(client, h, payload)
    finally:
        reading_module.on_reading_accepted.clear()
    assert len(calls) == 1
