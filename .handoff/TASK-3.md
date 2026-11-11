# TASK-3 handoff: registration and dashboard

All routes are mounted under /api/v1.

## Endpoints
POST /api/v1/auth/accounts  (no auth, shares the login rate limit)
- Body: {email (lower-cased, max 254), password (12-128 chars), display_name (1-100, nonblank)}
- 201: {id, email, display_name, next_step: "consent_setup", created_at}. The UI should route to consent setup.
- 400 {"detail": "Email address is already registered"} for a duplicate email. 422 {"detail":[{loc,msg,type}]} for an invalid body (input is never echoed).
- The password is hashed with bcrypt, never returned or logged. Registration writes an audit event, `auth.account_registered`.

GET /api/v1/dashboard  (Bearer required; 401 {"detail"} otherwise)
- 200 DashboardResponse:
  - measurements[]: {metric_type, value (decimal), unit, source (manual|scale|wearable), captured_at, status ("current"|"stale")}. Only metrics that have readings appear. Metrics covered: weight, steps, sleep_duration, active_minutes.
  - source_statuses[]: {id, source, provider, display_label, status (pending|current|stale|failed|disconnected), last_successful_sync_at|null}. A "current" connection with no sync, or one older than FRESHNESS_STALE_AFTER_HOURS (24 by default), is reported "stale".
  - alerts[]: active alerts only, {id, metric_type, event_at, reason, state}.
  - goals[]: active goals only, {id, category, metric_type, target_value, target_unit, target_date, state}.
  - insights[]: {id|null, metric_type, status ("available"|"insufficient_data"), observation_period_start|null, observation_period_end|null, observation, wellness_guidance, uncertainty}. A metric with fewer than 3 readings and no stored insight gets an insufficient_data card with a null id.
  - unavailable_categories[]: {metric_type, status: "unavailable"} for every metric with no readings. The value is never substituted.
- Lists are empty when there are no rows. The endpoint makes no adapter calls. The simplified preference is not stored (FR-004 is deferred), so the UI should reduce detail client-side and keep alerts and statuses visible.

## Seed logins (password Wellness-Demo-2026!)
- asha@sapphire.example: scale and wearable connections (status current), plus 13 readings. Weight has 4 and steps, sleep_duration and active_minutes have 3 each. The dashboard shows 4 measurements ("current" for about 24h after seeding), no unavailable categories, and no alerts, goals or stored insights.
- rohan@sapphire.example: no readings or connections, so the dashboard shows 4 unavailable categories and empty lists.
- `python -m app.seed` is idempotent. Readings use the idempotency keys seed-<metric>-<n>.
