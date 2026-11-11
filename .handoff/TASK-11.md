# TASK-11 handoff: alerts (FR-016) and goals (FR-017)

- `GET /api/v1/alerts?state=` (owner-only page), `POST /api/v1/alerts/{alert_id}/acknowledgements` (idempotent, 200; foreign/unknown 404; one `alert_acknowledgements` row and one `alert.acknowledged` audit event; alert kept).
- `POST/GET /api/v1/goals`, `PATCH /api/v1/goals/{id}` (`active` only to resume a paused goal; closed is terminal -> 409; same state is a no-op). Readings are never touched.
- Goal validation (422): metric must fit category, unit must match the metric's canonical unit, `target_date` must be after today (UTC), target > 0.
- Progress: `available` with `current_value` when the latest reading of the metric was captured at/after the goal's `created_at`; otherwise `data_gap`.
- Dashboard alerts/goals now come from `AlertService.list_alerts` / `GoalService.list_active` (active only; goals carry `progress_status`, `current_value`).
- Seeds (asha): 2 active alerts + 1 acknowledged with its acknowledgement row; goals weight active (available), sleep paused, steps active (data gap), active_minutes closed.
- Tests: `tests/test_alert_goal_api.py`; `test_insight_alert.py` now counts active alerts (seed adds an acknowledged one).
