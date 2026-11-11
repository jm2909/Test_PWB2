# TASK-7 handoff: wearable connection (FR-007) and reading ingestion (FR-008)

## Endpoints (all Bearer, under /api/v1)
- GET /connections/providers -> [{provider, display_name, authorization_mode}] (from WEARABLE_PROVIDERS)
- POST /connections/wearables/{provider}/authorizations -> 201 {connection_id, authorization_url, expires_at}; 404 unsupported; 403 no consent
- POST /connections/wearables/{provider}/callbacks body {connection_id, state, code?, error?} -> 200 ConnectionResponse
  (failure: status failed, recovery_action `retry_or_disconnect`). Bearer is required in addition to the signed state (stricter than the LLD).
- POST /readings (Idempotency-Key required; missing -> 400) -> 201 / 200 replay / 400 / 403 / 409
- GET /readings?metric_type&from&to&limit&offset -> Page, `captured_at DESC, id DESC`

## For TASK-9
`app.services.reading.on_reading_accepted` is a list of `(db, reading) -> None` observers. They run after persist and before commit, once per accepted reading, never on replay.

## Notes
- Metric config: `METRICS` in services/reading.py (weight kg, body_fat_percentage percent, steps count, sleep_duration hours, active_minutes minutes, resting_heart_rate bpm). Future tolerance 5 min.
- Wearable adapter state is now an HMAC of account+provider (jwt secret).
- ConnectionResponse gained `provider` and `authorization_state`.
- Dashboard hides `disconnected` connections; they only appear in the connection list.
- Seeds (seeds/wearables.py): asha has pulsewear pending, fitband failed, stridelink disconnected, 30 days of readings for 4 metrics, 3 rejected outcomes.
- There is no separate disconnect endpoint in this task; the recovery action code is returned only.
