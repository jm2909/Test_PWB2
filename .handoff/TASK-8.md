# TASK-8 handoff
- GET /api/v1/connections: paginated, owner-only, disconnected excluded; status via app/services/freshness.py (shared with dashboard); recovery_action: stale->retry_sync, failed scale->contact_support, failed wearable->retry.
- GET /api/v1/trends/{metric_type}?range=7d|30d|90d|365d: {metric_type, unit, range, range_label, points, status, explanation}. Minimum points: 3/5/7/10. Unknown metric 404, bad range 422.
- Seeds: asha steps 4 days (insufficient at 365d), weight 24 days (available).
- Tests: tests/test_connection_status_trends.py
