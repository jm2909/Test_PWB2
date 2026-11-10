# TASK-15 handoff: integration and end-to-end tests

- `backend/tests/test_e2e_journeys.py`: register -> onboarding -> consent -> pair scale -> sync -> dashboard -> trend -> explanation -> insight -> recommendation; consent-decline blocks; idempotent sync; failed -> retry; revoked stays revoked; deviation -> alert chain; goal valid/invalid; 401 sweep over every `/api/v1` operation (from OpenAPI); prefix and no-deferred-routes check; logout; owner isolation.
- `frontend/e2e/journey_new_user_to_dashboard.spec.ts`, `journey_sync_recovery.spec.ts`, `journey_insight_alert_action.spec.ts`: real backend, UI only. Each asserts the required disclaimer footer on every screen it visits.
- No product defects found. `playwright.config.ts` was already correct and is unchanged.
- Run Playwright with `E2E_PYTHON` set to the backend venv interpreter's real path.
- FR coverage: FR-001..004 (accounts, auth, onboarding, consent acceptance tests + journeys), FR-007..010 (device/sync tests + journeys), FR-013..015 (dashboard/trend/explanation), FR-017, FR-019, FR-020, FR-023, FR-024 (insight, deviation, alert, recommendation, goal tests + journeys).
