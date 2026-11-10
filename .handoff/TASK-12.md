# TASK-12 handoff: metric explanations and deviation events

API prefix: /api/v1. Both routes need a bearer token.

POST /api/v1/metric-explanations
- Request: `{metric_type, period_days}`. metric_type is one of weight, body_fat, sleep_duration, resting_heart_rate, steps. period_days is 7-365. Anything else gives 422.
- Response 200: `{status: "available"|"unavailable"|"insufficient_history", direction: "up"|"down"|"steady"|null, explanation, reading_count, source_label}`.
- body_fat always returns `unavailable` with "We can't explain this metric yet. We would rather not guess."
- Explanation text is non-diagnostic and passes the safety validator.

GET /api/v1/deviation-events
- Query: `limit` 1-100 (default 20), `offset` >= 0.
- Response 200: `{items, total}`. Each item is `{id, criterion_code, trend_name, created_at, wellness_reading_id}`. Newest first, own events only.

Flow: after `POST /api/v1/sync` stores new readings, the post-ingest hook runs deviation detection. It creates one deviation_events row per (reading, criterion) when criteria are met and none otherwise. Failures are logged and do not affect the sync.

Criteria codes: rhr_rise_14d (>= 5 bpm rise), rhr_sustained_14d (above 65 bpm over a window of at least 10 days), sleep_decline_14d (>= 45 min), weight_change_14d (>= 2 kg).

Seeds: asha (asha.menon@example.com) has two events (rhr_rise_14d, rhr_sustained_14d). meena (meena.rao@example.com) and rohan have none. For explanations, asha's weight over 30 days gives `available`/`down`; meena gives `insufficient_history`.
