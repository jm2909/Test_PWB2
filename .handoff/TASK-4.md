# TASK-4 handoff: sessions and consent (backend)

All paths are mounted under the `/api/v1` prefix. Bearer token required unless noted.

## Endpoints added
DELETE /api/v1/auth/tokens/current
- Revokes the caller's session and writes an audit event. Returns 204 with no body.
- Reusing the token returns 401 `{"detail":"Session is not active"}`.

GET /api/v1/consents/current
- 200 `{id, decision, notice_version, recorded_at, collection_allowed, data_rights_path}`.
- 404 `{"detail":"Consent record not found"}` when the account has no record.

PUT /api/v1/consents/current
- Body: `{decision: "granted"|"withdrawn", notice_version: string(1-64), data_categories: non-empty array of weight|body_composition|steps|sleep_duration|active_minutes, purpose: "wellness_support"}`.
- 200 same shape as GET. `collection_allowed` is true only for `granted`. `data_rights_path` is `/data-rights` when withdrawn, otherwise null.
- Each PUT appends a new record, and the latest record decides.
- 422 on invalid input.

## Existing behaviour used by the UI
- `POST /api/v1/auth/tokens` returns 429 when the per-IP limit is exceeded (`LOGIN_RATE_LIMIT`), and a uniform 401 `{"detail":"Invalid credentials"}` on failure.
- Inactive sessions get 401 "Session expired due to inactivity", so the UI should send the user to sign in.

## Backend reuse
- `app.deps.require_active_consent` is a dependency returning `CurrentUser`. It responds 403 `{"detail":"Active consent is required before connecting a source"}` without active consent. Later source, sync and manual-entry routes should use it.
- `ConsentService.require_active(account_id)` is the same check for services.

## Seeds (login with the password `Wellness-Demo-2026!`)
- asha@sapphire.example: consent granted, notice v1.0, so GET returns 200 with `collection_allowed` true.
- rohan@sapphire.example: no consent, so GET returns 404, which is the "consent needed" screen state. Use PUT to grant.
- To show the withdrawn state, PUT `withdrawn` as either user.
