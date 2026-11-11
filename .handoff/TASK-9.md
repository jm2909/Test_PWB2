# TASK-9 handoff

- `GET /api/v1/insights` (paged, owner-only), `POST /api/v1/insights/{id}/feedback` (201; foreign 404; second submission 409).
- `InsightService.generate(account_id, metric_type, period_days, min_readings=3)`: deterministic; below the minimum it stores an insufficient-data insight with fixed "not offered" guidance. All text passes `content_policy.ensure_allowed` before persistence (422 `ContentPolicyError`).
- `AlertService.evaluate` is registered by `register_alert_evaluation()` (called in `create_app`) on `reading.on_reading_accepted`. Replays never reach the hook. Rule `definition`: `{window_days, min_prior, threshold_pct, direction}` (change vs mean of prior readings). Wording comes from `alert_rules.content_template` (placeholders `{metric}`, `{event_date}`) and is dropped if it violates the policy. `create_if_absent` pre-checks, then relies on the unique constraint in a savepoint. Audit `alert.created` holds rule identifier and version only.
- Seeds (`app/seeds/alerts.py`): rules `weight-change-pattern` and `activity-pattern` (v1.0), asha insights (weight 30d, steps 7d limited-data), and two active alerts on her latest weight and steps readings (the second is the acknowledgement-ready one for TASK-11).
- The alerts listing and acknowledgement endpoints are NOT part of this task (TASK-11 builds them); no alerts route is mounted here. Assumptions: duplicate feedback returns 409; the policy word list is in `app/services/content_policy.py`.
- Tests: `tests/test_insight_alert.py`.
