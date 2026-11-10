# TASK-2 handoff: accounts and insights

API prefix /api/v1 (routers mounted once in app/main.py). Errors are `{"detail": "..."}`.

## Endpoints
POST /api/v1/accounts
- No auth. Body `{email, password}` (email valid, password 12-128 chars).
- 201 `{id:int, email, onboarding_status:"not_started"}`; 409 duplicate email; 422 invalid field (no submitted values echoed).
- Creates the user (bcrypt cost 12, email lowercased) and an `account.created` audit event.

POST /api/v1/insights
- Bearer auth, no body. 200 `{id:uuid, status:"published"|"suppressed", observed_trend|null, wellness_implication|null, suppression_reason|null}`.
- The result is always persisted (suppressed rows keep an id). 403 `{detail}` with an explanation when `personalized_insights` consent is missing or declined. 401 when unauthenticated.
- suppression_reason values: insufficient_evidence, stale_data, no_clear_trend, ai_unavailable, safety_blocked.

GET /api/v1/insights
- Bearer auth. Query `limit` (1-100, default 20), `offset` (>=0). 200 `{items: InsightResponse[], total:int}`, owner-scoped, newest first.

## Auth
`Authorization: Bearer <jwt>`; validated by `get_current_user` (signature, exp, stored SHA-256 session hash, revocation, inactivity). Login arrives in Task 3; tests use `SessionService(db).issue(user_id)` via `issue_headers` / `persona_headers` in tests/conftest.py.

## Seed records (password for all: correct-horse-battery)
- asha.menon@example.com: consents accepted; scale + band connections; 30-day weight 70.1->68.4, body fat, 14-day sleep 7h10->6h05, resting HR 62->68, steps; one published sleep insight. POST /insights -> published (sleep).
- rohan.iyer@example.com: consents accepted, no readings; POST /insights -> suppressed (insufficient_evidence).
- meena.rao@example.com: consents accepted, 3 days of sleep only; one suppressed insight; POST /insights -> suppressed.

## Flows
- Register -> user + audit event; onboarding itself is Task 4.
- Generate insight -> consent check -> evidence sufficiency (>=5 readings, >=7 day span, latest within 3 days, valid range, >=1% change) -> AI adapter (local deterministic unless AI_PROVIDER_URL) -> safety validator -> insight row + `insight.generated` audit event.
