# TASK-7 handoff: wearable connections and wellness goals

API prefix: /api/v1. All routes need a bearer token.

## Endpoints added
- GET /api/v1/device-connections -> 200 `{items, total}`; each item: id, provider, status (pending|connected|action_required|failed|revoked), permitted_categories, last_successful_sync_at, failure_reason, recovery_action, last_sync_summary.
- POST /api/v1/goals -> 201 `{id, goal_type, target_value, target_unit, status:"active"}`. Request: goal_type (weight_loss|muscle_gain|sleep_improvement|blood_pressure_control|other_supported), target_value (number), target_unit (max 24). Invalid target -> 422 `{detail: "<guidance>"}`, e.g. "Enter a target above 0 kg that is realistic for you, for example 65." Nothing is saved.
- GET /api/v1/goals -> 200 `{items, total}` of the user's active goals. One active goal per type; a new target of the same type replaces it.

Units: weight_loss/muscle_gain kg (30-250), sleep_improvement h (4-12), blood_pressure_control mmHg (70-200), other_supported any unit with a value above 0.

## Changed behaviour of an existing route
POST /api/v1/device-connections now also accepts providers wearable_platform_a, wearable_platform_b, wearable_platform_c with connection_mode "authorize" (still 201, requires device-processing consent else 403).
- authorization_code absent or "ok": connected, with categories (A: sleep, heart_rate, activity; B: those plus weight; C: sleep, activity).
- "revoke": status revoked, recovery_action "Reconnect", failure_reason "Access was revoked at the provider."
- "fail": status failed, recovery_action "Try again", failure_reason "The provider did not respond."
- Re-posting with a valid code restores connected (same row/id).
Each connect and each goal save writes an audit event.

## Seeds (password correct-horse-battery)
- asha.menon@example.com: sapphire_scale connected; wearable_platform_a connected; fitband action_required ("Permissions need to be updated.", "Review permissions"); platform B failed; platform C revoked; goal weight_loss 65 kg.
- meena.rao@example.com: wearable_platform_a connected with heart_rate and activity (no sleep readings); fitband sleep only; no goals.
- rohan.iyer@example.com: no connections or goals. Rohan and meena have no accepted device-processing consent (consent_gate seed), so POST device-connections returns 403 for them; asha can connect.
