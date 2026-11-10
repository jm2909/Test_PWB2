# TASK-5 handoff: consent ledger write side and Sapphire scale connection

API prefix: /api/v1. All routes need `Authorization: Bearer <token>` (401 otherwise).

## Endpoints

POST /api/v1/consents
- Request: `{purpose: "device_processing"|"personalized_insights", version: string (1-32 chars), status: "accepted"|"declined"}`
- 201: `{id, purpose, version, status, recorded_at}`. 422 for an invalid enum or version. Append-only; writes an audit event.

GET /api/v1/consents
- 200: `{items, total, latest}`. `items` is the full history, newest first (`total` = its length). `latest` is the current choice per purpose. Each entry has the same shape as the POST response.

POST /api/v1/device-connections
- Request: `{provider: "sapphire_scale"|"wearable_platform_a"|"wearable_platform_b"|"wearable_platform_c", connection_mode: "pair"|"authorize", authorization_code: string|null}`
- Only `sapphire_scale` + `pair` is supported now; any other provider/mode gives 422.
- 201: `{id, provider, status, permitted_categories[], last_successful_sync_at|null, failure_reason|null, recovery_action|null, last_sync_summary}`
  - success: status `connected`, categories `["weight","body_fat"]`.
  - `authorization_code: "fail"`: status `failed`, `failure_reason` set, `recovery_action: "Try again"`. Still 201, so the UI shows the failure state.
  - A non-retryable adapter error gives `action_required`.
- 403 `{detail: <explanation>}` when device_processing consent is declined or missing. The adapter is never called.
- One row per (user, provider): a retry updates the same row/id.
- Each attempt writes an audit event. The list route for connections is added by a later task and is not mounted here (repository `DeviceRepository.list_for_user` already exists).

## Seed logins (password `correct-horse-battery`)
- asha.menon@example.com: both consents accepted, can pair (has a seeded connection with readings).
- meena.rao@example.com: device_processing latest = declined (consent paused) -> POST device-connections returns 403.
- rohan.iyer@example.com: no device_processing record -> 403; onboarding now lists `consent` among remaining steps (Task 3 tests updated accordingly).

## Flows
- Accepting/declining writes a new dated ledger row; `assert_permitted` reads the latest row per purpose.
- Connecting a device checks consent first, then calls the adapter, then upserts the connection and audits it.
