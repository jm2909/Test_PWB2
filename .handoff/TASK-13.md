# TASK-13 handoff: alerts and recommendations

API prefix /api/v1; all routes need a bearer token (401 otherwise).

GET /api/v1/alerts?limit=20&offset=0
- Response `{items, total}`. Item: `{id, trend_name, urgency: "routine"|"urgent_direction", what_we_saw, recommended_next_action, care_direction|null, created_at}`.
- Materializes alerts for the user's unalerted deviation events first (idempotent, audited). Unsafe copy is suppressed and an operational failure audit row is written.
- `total` equals the dashboard `unread_alert_count`.
- urgent_direction carries care_direction: "If you feel unwell, contact your doctor or a qualified health professional. If you think it is an emergency, call your local emergency number now." No diagnosis, no dispatch button, no tel: link.

GET /api/v1/recommendations
- Response `RecommendationResponse`: `{status: "available"|"none", action_text, reason_text, insight_id, suggested_goal_type|null, items: [{id, insight_id, action_text, reason_text, suggested_goal_type}]}`.
- `none`: all text fields null, items empty (no insight, suppressed insight, or no relevant action).
- Derived from the latest published insight; sleep decline gives "Set a regular bedtime for the next 7 days" / "Your sleep duration has fallen over the last 2 weeks." with suggested_goal_type sleep_improvement.
- POST /api/v1/insights now also stores a recommendation when the insight is published.

Seeds (password correct-horse-battery)
- asha.menon@example.com: 2 alerts (routine, urgent_direction), recommendation available. Dashboard unread count is 2.
- meena.rao@example.com: no alerts, recommendation none. rohan.iyer@example.com: none.
