# TASK-3 handoff: sign in/out and onboarding

API prefix: /api/v1

## Endpoints
POST /api/v1/auth/sessions
- No auth. Body `{email, password}` (password min length 1).
- 200 `{access_token, token_type:"bearer", expires_at, user:{id, email, onboarding_status}}`.
- 401 `{detail:"Invalid email or password."}` for any bad credential. 422 invalid body.
- 429 `{detail:"Too many attempts. Try again later."}` per-IP fixed window (LOGIN_RATE_LIMIT, default 10/minute; RATE_LIMIT_ENABLED).
- Writes an audit event (success or failure, no email).

DELETE /api/v1/auth/sessions/current
- Bearer required. 204, revokes the session; the token is 401 afterwards.

GET /api/v1/onboarding
- Bearer required. 200 `{profile, goal_intent, device_next_step, status, remaining_steps[]}`.
- status: not_started | in_progress | complete. Steps: profile, goal, device, consent.
- Before any save: empty profile, empty strings, all four steps remaining.

PUT /api/v1/onboarding
- Bearer required. Body `{profile: object, goal_intent: string<=80, device_next_step: scale|wearable|later}`, all required.
- Partial saves allowed: empty profile / empty goal_intent leave those steps remaining. Returns the same shape as GET. 422 on invalid.
- `consent` stays remaining until both purposes (device_processing, personalized_insights) have a consent record.

## Seed logins (password `correct-horse-battery`)
- asha.menon@example.com: onboarding complete.
- rohan.iyer@example.com: in_progress, profile, goal (build_muscle) and device (wearable) saved; only `consent` remains (no device_processing record; Task 6 changed this seed).
- meena.rao@example.com: complete.

## Notes for the UI
Store the token in memory; send `Authorization: Bearer <token>`. Any 401 means signed out: clear state and show sign-in.
