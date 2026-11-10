# TASK-10 handoff: dashboard and trends

## Endpoints (auth: bearer token; 401 otherwise)
GET /api/v1/dashboard
- 200: `{display_name, last_synced_at|null, signal_groups[], source_gaps[], active_goals[], unread_alert_count}`.
- `signal_groups[]` item: `{key, group, title, value|null, unit|null, details[], metrics{}}`. Keys: `body_composition`, `sleep`, `heart_rate`, `activity`, `goals` (group `goal_signals`).
- `source_gaps[]` item: `{key, group, title, reason, recovery_action, link}`. A missing source gives a gap, e.g. sleep: "Your wearable has not synced sleep readings." / "Check wearable connection" / link `/devices`. No goal gives key `goals`, reason "No goal set", link `/goals`.
- `active_goals[]` items are `{id, goal_type, target_value, target_unit, status}`.
- `unread_alert_count` counts alert rows (0 until alerts are seeded). Database only; never calls a provider.

GET /api/v1/trends?metric_type=&period_days=
- metric_type: weight, body_fat, sleep_duration, resting_heart_rate, steps. period_days: integer 7-365. Anything else is 422.
- 200: `{metric_type, period_days, status: "available"|"insufficient_history", points[{observed_at,value}] (chronological), explanation, reading_count, source_label}`.
- Insufficient history (under 3 readings, or span under max(3 days, 25% of period)) has explanation starting "A reliable trend is not available yet."

## Seed states
- asha.menon@example.com / correct-horse-battery: all groups, goal 65 kg, weight 30d available, steps 365d insufficient.
- rohan.iyer@example.com: no readings, so gaps for every group plus "No goal set" in the dashboard.
- meena.rao@example.com: 3 days of sleep only (trend insufficient); other groups gap; no goal.
