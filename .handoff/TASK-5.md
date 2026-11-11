# TASK-5 handoff
- POST/GET /api/v1/data-rights-requests (DataRightsService, reference `DR-<16 hex>`, due date from `data_rights_fulfillment_days`; audit holds type+reference only; description rejects numeric measurements).
- POST /api/v1/connections/scale (ConnectionService.link_scale): 403 without consent; 201 current, 202 pending, 200 for duplicate or safe `failed` (recovery_action `retry_or_contact_support`, message). Retrying a failed link re-attempts on the same row. Idempotency-Key is accepted; uniqueness collapses duplicates.
- SimulatedScaleAdapter: id containing FAIL -> failure, PENDING -> pending, else current.
- Seeds: asha rights requests (export submitted, deletion in_review); scale Bathroom SSC-0482 (current; renamed from SEED-SCALE-1), Bedroom SSC-0517 (stale, 8 days).
- tests/conftest.py gained `full_seed` fixture.
