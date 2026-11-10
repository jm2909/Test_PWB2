# TASK-9 handoff: sync and sync status

## Endpoint
POST /api/v1/sync
- Auth: bearer token. Header `Idempotency-Key` is required, 16-128 chars (422 otherwise).
- Body: `{"device_connection_id": "<uuid>"}`.
- 200 returns DeviceConnectionResponse: `{id, provider, status, permitted_categories, last_successful_sync_at, failure_reason, recovery_action, last_sync_summary}`.
- `last_sync_summary` is `{new_readings, by_metric: {metric: count}, duplicates}`. It is also returned (null) by the device-connection POST/GET routes; the old string form is gone.
- 404 connection not owned or unknown; 403 device-processing consent not accepted (adapter is never called); 422 bad header/body.
- Same (connection, key) again returns the original result and adds no readings. A new key re-delivering known events reports them as `duplicates`.
- A failed sync still returns 200 with the connection's new status, `failure_reason` and `recovery_action` ("Retry", "Reconnect" or "Review permissions"). Retry with a NEW Idempotency-Key.
- Use a fresh key (e.g. a uuid) per user-initiated sync. Success sets status `connected`, `last_successful_sync_at`, and clears failure.

## Triggering each state (log in as asha.menon@example.com / correct-horse-battery)
- Success: sync asha's wearable_platform_a or sapphire_scale connection with any key. New metrics: sleep_hours, resting_heart_rate, steps, weight (kg), body_fat.
- Duplicate: sync again with a different key -> new_readings 0, duplicates > 0. Same key -> original summary.
- Retryable failure (`failed`, "Retry"): any key starting `sim-fail`. Asha's wearable_platform_b is seeded `failed`; a normal key then recovers it to `connected`.
- Revoked (`revoked`, "Reconnect"): asha's wearable_platform_c is seeded revoked; any sync keeps it revoked. Or a key starting `sim-revoke`. Reconnect via POST /api/v1/device-connections.
- Permission issue (`action_required`, "Review permissions"): key starting `sim-permission`, or asha's seeded fitband connection.
- Consent declined 403: log in as meena.rao@example.com or rohan.iyer@example.com (no accepted device-processing consent) and sync a connection.
- 404: sync one user's connection id as another user.

Seed: `seeds/sync.py` adds sync_attempts history for asha (succeeded for connected ones, failed for platform B and C).

## Backend extension point
`app.services.sync_service.register_post_ingest_hook(hook)`; hook(db, user_id, new_reading_ids) runs after a sync stores new readings. Hook errors are logged and swallowed.
