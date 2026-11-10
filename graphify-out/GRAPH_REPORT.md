# Graph Report - test_pwb2  (2026-11-10)

## Corpus Check
- 253 files · ~49,055 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 13 file(s) not represented in the graph (top: (none) 5, .example 2, .ini 2)

## Summary
- 1682 nodes · 4548 edges · 104 communities (78 shown, 26 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 302 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `597a504a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Sapphire FitConnect
- http.py
- test_explanation_acceptance.py
- factories.py
- test_pipeline_migration_parity.py
- TASK-7 handoff: wearable connections and wellness goals
- DevicesPage.tsx
- with
- typing
- sqlalchemy_orm
- healthcheck
- recommendation_service.py
- fitconnect-backend
- SessionRepository
- AuditService
- database.py
- api-client.ts
- conftest.py
- TASK-3 handoff: sign in/out and onboarding
- .select
- compilerOptions
- compilerOptions
- package.json
- devDependencies
- rate_limiter.py
- auth.py
- eslint.config.js
- @testing-library/react
- scripts
- vite
- @playwright/test
- LoginPage.tsx
- OnboardingPage.tsx
- react-router-dom
- SyncStatusPage.tsx
- GoalsPage.tsx
- react-router-dom
- dashboard_service.py
- test_goal_service.py
- DeviceRepository
- base.py
- test_sync_service.py
- backend
- user_id
- Decimal
- test_explanation_service.py
- SyncRepository
- device_service.py
- TrendsPage.tsx
- logging_config.py
- registry.py
- test_deviation_integration.py
- test_insight_service.py
- TASK-9 handoff: sync and sync status
- TASK-10 handoff: dashboard and trends
- user_id
- routers/consents.py
- test_wearable_acceptance.py
- AlertRepository
- test_alert_acceptance.py
- readings.py
- seeds/__init__.py
- .evaluate_evidence
- TASK-12.md
- test_consent_acceptance.py
- test_device_scale_acceptance.py
- test_goal_acceptance.py
- test_trend_acceptance.py
- fastapi_testclient
- PlaceholderPage.tsx
- test_deviation_acceptance.py
- test_recommendation_acceptance.py
- insight_service.py
- test_smoke.py
- test_pipeline_seed_runs.py
- Recommendation
- goal_schemas.py
- RecommendationService
- env.py
- test_account_acceptance.py
- alert_schemas.py
- register
- get_trend
- build_engine
- TASK-15.md
- test_dashboard_service.py
- start.sh
- get_dashboard
- backend/run.sh
- stop.sh
- docker-entrypoint.sh
- frontend/run.sh

## God Nodes (most connected - your core abstractions)
1. `user_id()` - 72 edges
2. `User` - 54 edges
3. `make_user()` - 33 edges
4. `react-router-dom` - 31 edges
5. `ReadingRepository` - 29 edges
6. `SyncIngestionService` - 29 edges
7. `utcnow()` - 27 edges
8. `register()` - 27 edges
9. `Base` - 26 edges
10. `get_current_user()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `TASK-13 handoff: alerts and recommendations` --references--> `RecommendationResponse`  [INFERRED]
  .handoff/TASK-13.md → backend/app/schemas/recommendation_schemas.py
- `Auth` --references--> `get_current_user()`  [INFERRED]
  .handoff/TASK-2.md → backend/app/dependencies.py
- `Auth` --references--> `persona_headers()`  [INFERRED]
  .handoff/TASK-2.md → backend/tests/conftest.py
- `Auth` --references--> `issue_headers()`  [INFERRED]
  .handoff/TASK-2.md → backend/tests/conftest.py
- `RecommendationService` --uses--> `RecommendationRepository`  [INFERRED]
  backend/app/services/recommendation_service.py → backend/app/repositories/recommendation_repository.py

## Import Cycles
- None detected.

## Communities (104 total, 26 thin omitted)

### Community 0 - "Sapphire FitConnect"
Cohesion: 0.25
Nodes (7): Docker, Environment variables, Runtime contract, Sapphire FitConnect, Start / stop, Structure, Tests and CI

### Community 1 - "http.py"
Cohesion: 0.13
Nodes (7): CorrelationIdMiddleware, _detail(), register_exception_handlers(), http_exc(), unhandled_exc(), validation_exc(), SecurityHeadersMiddleware

### Community 2 - "test_explanation_acceptance.py"
Cohesion: 0.50
Nodes (5): test_body_fat_unavailable_without_guidance(), test_meena_insufficient(), test_requires_auth(), test_validation(), test_weight_explanation()

### Community 3 - "factories.py"
Cohesion: 0.06
Nodes (55): Base, DeviceConnection, ConsentRecord, OnboardingProgress, User, Alert, DeviationEvent, DeviationRepository (+47 more)

### Community 4 - "test_pipeline_migration_parity.py"
Cohesion: 0.19
Nodes (12): _alembic(), _annotation_kind(), _column_kind(), _env_py_text(), _foreign_key(), _has_alembic_version(), _last_name(), _mapped_columns() (+4 more)

### Community 5 - "TASK-7 handoff: wearable connections and wellness goals"
Cohesion: 0.40
Nodes (4): Changed behaviour of an existing route, Endpoints added, Seeds (password correct-horse-battery), TASK-7 handoff: wearable connections and wellness goals

### Community 6 - "DevicesPage.tsx"
Cohesion: 0.23
Nodes (13): CategoryChips(), Props, ScaleCard(), Props, StatusLine(), WearableList(), DevicesPage(), CATEGORY_LABELS (+5 more)

### Community 7 - "with"
Cohesion: 0.06
Nodes (38): defaults, env, runs-on, services, steps, run, DATABASE_URL, JWT_SECRET_KEY (+30 more)

### Community 8 - "typing"
Cohesion: 0.12
Nodes (10): OnboardingRepository, get_onboarding(), put_onboarding(), OnboardingResponse, OnboardingUpdate, seed_onboarding(), OnboardingService, test_new_account_is_not_started() (+2 more)

### Community 9 - "sqlalchemy_orm"
Cohesion: 0.09
Nodes (4): upgrade(), UTCDateTime, utcnow(), AuditLog

### Community 14 - "healthcheck"
Cohesion: 0.08
Nodes (25): PIP_TARGET, build, depends_on, environment, args, context, condition, environment (+17 more)

### Community 16 - "recommendation_service.py"
Cohesion: 0.19
Nodes (6): get_recommendations(), RecommendationItem, RecommendationResponse, derive(), is_safe_recommendation(), TASK-13 handoff: alerts and recommendations

### Community 18 - "SessionRepository"
Cohesion: 0.10
Nodes (16): AuthSession, SessionRepository, create_access_token(), decode_access_token(), hash_password(), hash_token(), verify_password(), AuthService (+8 more)

### Community 19 - "AuditService"
Cohesion: 0.12
Nodes (6): AuditRepository, UserRepository, AccountService, AuditService, test_register_creates_user_and_audit(), test_register_duplicate_raises()

### Community 20 - "database.py"
Cohesion: 0.20
Nodes (5): get_db(), get_current_user(), _unauthorized(), lifespan(), ErrorResponse

### Community 21 - "api-client.ts"
Cohesion: 0.07
Nodes (35): RequireAuth(), api, API_BASE, ApiError, clearSession(), detailFrom(), getStoredSession(), request() (+27 more)

### Community 22 - "conftest.py"
Cohesion: 0.05
Nodes (62): auth_client(), auth_headers(), client(), db_session(), _fresh_schema(), issue_headers(), login(), persona_headers() (+54 more)

### Community 23 - "TASK-3 handoff: sign in/out and onboarding"
Cohesion: 0.40
Nodes (4): Endpoints, Notes for the UI, Seed logins (password `correct-horse-battery`), TASK-3 handoff: sign in/out and onboarding

### Community 24 - ".select"
Cohesion: 0.21
Nodes (8): AlertResponse, SafeAlertPresentationService, is_safe_alert(), test_materialize_is_idempotent(), test_seeded_alerts_for_asha(), test_unsafe_text_suppresses_alert_and_records_failure(), test_urgent_copy_is_safe_and_non_diagnostic(), test_validator_rejects_unsafe()

### Community 25 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleDetection, moduleResolution (+10 more)

### Community 26 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 27 - "package.json"
Cohesion: 0.15
Nodes (12): autoprefixer@^10.4.20, @types/node@^22.10.0, @types/react@^18.3.12, engines, node, name, private, type (+4 more)

### Community 28 - "devDependencies"
Cohesion: 0.13
Nodes (15): devDependencies, eslint@^9.15.0, jsdom@^25.0.1, postcss@^8.4.49, tailwindcss@^3.4.15, @testing-library/react@^16.1.0, @testing-library/user-event@^14.5.2, @types/react-dom@^18.3.1 (+7 more)

### Community 29 - "rate_limiter.py"
Cohesion: 0.21
Nodes (3): FixedWindowLimiter, parse_limit(), test_fixed_window_limiter()

### Community 30 - "auth.py"
Cohesion: 0.10
Nodes (12): DatabaseSettings, get_settings(), Settings, create_account(), _correlation_id(), create_session(), delete_current_session(), AccountCreate (+4 more)

### Community 31 - "eslint.config.js"
Cohesion: 0.22
Nodes (8): @eslint/js@^9.15.0, eslint-plugin-react-hooks@^5.0.0, globals@^15.12.0, typescript-eslint@^8.16.0, @eslint/js, eslint-plugin-react-hooks, globals, typescript-eslint

### Community 32 - "@testing-library/react"
Cohesion: 0.33
Nodes (4): @testing-library/jest-dom@^6.6.3, vitest@^2.1.8, @testing-library/jest-dom, vitest

### Community 33 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, e2e, lint, preview, test, type-check

### Community 34 - "vite"
Cohesion: 0.40
Nodes (4): vite@^6.0.1, @vitejs/plugin-react@^4.3.4, vite, @vitejs/plugin-react

### Community 35 - "@playwright/test"
Cohesion: 0.09
Nodes (3): MONTHS, @playwright/test@^1.49.0, @playwright/test

### Community 36 - "LoginPage.tsx"
Cohesion: 0.15
Nodes (16): ArrowIcon(), AuthTab, AuthTabs(), ITEMS, PasswordField(), Props, DISCLAIMER, Footer() (+8 more)

### Community 37 - "OnboardingPage.tsx"
Cohesion: 0.12
Nodes (25): ConsentGroup(), formatRecordedDate(), MONTHS, Props, ORDER, ProgressSteps(), OnboardingPage(), finish() (+17 more)

### Community 41 - "react-router-dom"
Cohesion: 0.11
Nodes (19): dependencies, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, App(), AlertCard(), InsightCard(), RecommendationCard() (+11 more)

### Community 42 - "SyncStatusPage.tsx"
Cohesion: 0.11
Nodes (27): ACTION, CONNECTED, FAILED, Icon(), ICONS, Kind, KINDS, PENDING (+19 more)

### Community 43 - "GoalsPage.tsx"
Cohesion: 0.16
Nodes (17): ICON_FILL, ICON_PATH, Notification(), NotificationKind, Props, STYLES, ActiveGoalTile(), GoalForm() (+9 more)

### Community 44 - "react-router-dom"
Cohesion: 0.24
Nodes (13): AlertBanner(), EmptyTile(), SignalTile(), TILE_CLASS, DashboardPage(), formatSynced(), greeting(), nameFromEmail() (+5 more)

### Community 45 - "dashboard_service.py"
Cohesion: 0.23
Nodes (7): WellnessReading, DashboardResponse, SignalGroup, SourceGap, _avg(), DashboardCompositionService, _values()

### Community 46 - "test_goal_service.py"
Cohesion: 0.26
Nodes (9): GoalCreate, GoalService, InvalidGoalError, _Rule, goal(), test_each_type_saved(), test_guidance_text(), test_invalid_never_creates_row() (+1 more)

### Community 47 - "DeviceRepository"
Cohesion: 0.12
Nodes (6): DeviceRepository, SyncStatusRecoveryService, Endpoints, Flows, Seed logins (password `correct-horse-battery`), TASK-5 handoff: consent ledger write side and Sapphire scale connection

### Community 48 - "base.py"
Cohesion: 0.12
Nodes (11): AdapterError, ConnectResult, NonRetryableAdapterError, RetryableAdapterError, simulated_readings(), timezone_offset(), SapphireScaleAdapter, AuthorizationRevokedError (+3 more)

### Community 49 - "test_sync_service.py"
Cohesion: 0.15
Nodes (18): RawReading, clear_post_ingest_hooks(), normalize(), register_post_ingest_hook(), SyncIngestionService, _hooks(), _setup(), test_consent_declined_blocks_before_adapter() (+10 more)

### Community 50 - "backend"
Cohesion: 0.09
Nodes (22): BACKEND_HOST, build, env_file, environment, ports, volumes, x-preview-port, args (+14 more)

### Community 51 - "user_id"
Cohesion: 0.20
Nodes (12): DeviceConnectionCreate, DeviceService, UnsupportedConnectionError, req(), SpyAdapter, test_consent_gate_never_calls_adapter(), test_non_retryable_is_action_required(), test_success_upserts_single_row() (+4 more)

### Community 52 - "Decimal"
Cohesion: 0.20
Nodes (3): Goal, GoalRepository, seed_goals()

### Community 53 - "test_explanation_service.py"
Cohesion: 0.14
Nodes (7): explain_metric(), MetricExplanationRequest, MetricExplanationResponse, TrendPoint, TrendResponse, _aware(), UnsupportedMetricError

### Community 55 - "SyncRepository"
Cohesion: 0.22
Nodes (3): SyncAttempt, SyncRepository, seed_sync()

### Community 56 - "device_service.py"
Cohesion: 0.13
Nodes (10): create_device_connection(), list_device_connections(), run_sync(), DeviceConnectionListResponse, DeviceConnectionResponse, SyncSummary, SyncRequest, to_response() (+2 more)

### Community 57 - "TrendsPage.tsx"
Cohesion: 0.16
Nodes (19): ExplanationTile(), Props, MetricControls(), Props, bounds(), Props, TrendChart(), formatDate() (+11 more)

### Community 58 - "logging_config.py"
Cohesion: 0.43
Nodes (4): configure_logging(), _mask(), mask_text(), pii_mask_processor()

### Community 59 - "registry.py"
Cohesion: 0.15
Nodes (8): DeviceAdapter, build_registry(), WearableAdapter, WearablePlatformAAdapter, WearablePlatformBAdapter, WearablePlatformCAdapter, default_adapters(), test_registry_categories()

### Community 60 - "test_deviation_integration.py"
Cohesion: 0.15
Nodes (7): Criterion, post_ingest_hook(), _conn(), _sync(), test_failing_evaluation_is_suppressed(), test_hook_registered_and_fires_on_sync(), test_sync_with_unmet_criteria_creates_nothing()

### Community 61 - "test_insight_service.py"
Cohesion: 0.06
Nodes (28): AIInferenceAdapter, AIInferenceError, EvidenceSummary, _fmt(), InferenceResult, ConsentRepository, generate_insight(), list_insights() (+20 more)

### Community 62 - "TASK-9 handoff: sync and sync status"
Cohesion: 0.40
Nodes (4): Backend extension point, Endpoint, TASK-9 handoff: sync and sync status, Triggering each state (log in as asha.menon@example.com / correct-horse-battery)

### Community 63 - "TASK-10 handoff: dashboard and trends"
Cohesion: 0.50
Nodes (3): Endpoints (auth: bearer token; 401 otherwise), Seed states, TASK-10 handoff: dashboard and trends

### Community 64 - "user_id"
Cohesion: 0.27
Nodes (8): seed_alerts(), seed_recommendations(), user_id(), TrendExplanationService, test_asha_weight_trend_available_and_chronological(), test_meena_sleep_insufficient(), test_unknown_metric_rejected(), test_year_period_is_insufficient_for_asha()

### Community 66 - "routers/consents.py"
Cohesion: 0.17
Nodes (8): list_consents(), record_consent(), list_deviation_events(), ConsentCreate, ConsentListResponse, ConsentResponse, DeviationEventListResponse, DeviationEventResponse

### Community 67 - "test_wearable_acceptance.py"
Cohesion: 0.46
Nodes (6): body(), test_authorize_shows_connection_and_categories(), test_list_is_owner_scoped(), test_list_seeded_connections(), test_requires_auth(), test_revoked_and_failed_are_actionable()

### Community 69 - "test_alert_acceptance.py"
Cohesion: 0.52
Nodes (4): test_asha_alerts(), test_dashboard_unread_count(), test_meena_none_and_pagination(), test_requires_auth()

### Community 70 - "readings.py"
Cohesion: 0.48
Nodes (3): _connection(), seed_readings(), _series()

### Community 71 - "seeds/__init__.py"
Cohesion: 0.24
Nodes (6): main(), discover(), decorator(), registered(), run_all(), SeedEntry

### Community 72 - ".evaluate_evidence"
Cohesion: 0.23
Nodes (3): Insight, InsightRepository, seed_insights()

### Community 75 - "test_consent_acceptance.py"
Cohesion: 0.48
Nodes (5): test_accept_and_decline_dated_choice(), test_declined_purpose_blocks_dependent_processing(), test_invalid_enum_422(), test_owner_scoped(), test_requires_auth()

### Community 76 - "test_device_scale_acceptance.py"
Cohesion: 0.48
Nodes (5): test_declined_or_missing_consent_403(), test_pairing_associates_device(), test_pairing_failure_shows_state_and_recovery(), test_requires_auth(), test_unsupported_provider_or_mode_422()

### Community 77 - "test_goal_acceptance.py"
Cohesion: 0.48
Nodes (5): test_goal_saved_and_listed(), test_invalid_target_422_with_guidance_and_no_goal(), test_requires_auth(), test_seeded_goal_and_replacement(), test_unknown_type_and_long_unit_422()

### Community 78 - "test_trend_acceptance.py"
Cohesion: 0.43
Nodes (4): test_ac1_chronological_trend(), test_ac2_insufficient_history_message(), test_invalid_query_is_422(), test_trends_require_auth()

### Community 79 - "fastapi_testclient"
Cohesion: 0.47
Nodes (3): test_ac1_available_data_presented_together(), test_ac2_gap_explained_other_signals_usable(), test_dashboard_requires_auth()

### Community 81 - "test_deviation_acceptance.py"
Cohesion: 0.53
Nodes (3): test_asha_has_two_events(), test_meena_none_and_pagination(), test_requires_auth()

### Community 82 - "test_recommendation_acceptance.py"
Cohesion: 0.53
Nodes (3): test_asha_recommendation(), test_meena_none(), test_requires_auth()

### Community 83 - "insight_service.py"
Cohesion: 0.31
Nodes (5): contains_diagnostic_language(), is_safe_insight(), test_insufficient_data_shows_no_conclusion(), test_sufficient_data_cites_trend_and_implication(), test_safety_validator()

### Community 84 - "test_smoke.py"
Cohesion: 0.17
Nodes (8): create_app(), test_docs_hidden_unless_debug(), test_health(), test_login_with_seed_credentials(), test_migration_to_head_builds_every_model_table(), test_readiness_checks_database(), test_security_and_correlation_headers(), test_unknown_route_uses_detail_shape()

### Community 86 - "test_pipeline_seed_runs.py"
Cohesion: 0.23
Nodes (6): _env(), _is_async(), _run(), _seed_module(), seeded(), test_the_seed_runs_a_second_time()

### Community 88 - "goal_schemas.py"
Cohesion: 0.27
Nodes (4): create_goal(), list_goals(), GoalListResponse, GoalResponse

### Community 89 - "RecommendationService"
Cohesion: 0.62
Nodes (5): RecommendationService, test_asha_available(), test_create_is_idempotent(), test_irrelevant_insight_forces_nothing(), test_meena_none()

### Community 90 - "env.py"
Cohesion: 0.38
Nodes (3): get_url(), run_migrations_offline(), run_migrations_online()

### Community 91 - "test_account_acceptance.py"
Cohesion: 0.38
Nodes (3): test_duplicate_email_is_409_with_clear_error(), test_invalid_fields_are_422_and_do_not_echo_values(), test_valid_registration_creates_account()

### Community 93 - "register"
Cohesion: 0.19
Nodes (6): seed_consent_gate(), seed_consents(), _ensure(), seed_devices(), register(), seed_users()

### Community 97 - "test_dashboard_service.py"
Cohesion: 0.53
Nodes (4): test_asha_has_all_groups(), test_meena_other_signals_stay_usable(), test_missing_goal_reads_no_goal_set(), test_rohan_without_data_gets_gaps_not_failure()

### Community 98 - "start.sh"
Cohesion: 0.70
Nodes (4): find_port(), kill_tree(), set_env(), start.sh script

## Knowledge Gaps
- **1 isolated node(s):** `fitconnect-backend`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 486 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `user_id()` connect `user_id` to `test_dashboard_service.py`, `factories.py`, `readings.py`, `.evaluate_evidence`, `sqlalchemy_orm`, `typing`, `test_goal_service.py`, `test_sync_service.py`, `test_insight_service.py`, `Decimal`, `user_id`, `conftest.py`, `SyncRepository`, `.select`, `RecommendationService`, `test_deviation_integration.py`, `register`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **What connects `fitconnect-backend` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `http.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12554112554112554 - nodes in this community are weakly interconnected._
- **Why does `User` connect `factories.py` to `routers/consents.py`, `get_dashboard`, `typing`, `sqlalchemy_orm`, `test_account_acceptance.py`, `recommendation_service.py`, `SessionRepository`, `AuditService`, `database.py`, `test_explanation_service.py`, `register`, `device_service.py`, `get_trend`, `goal_schemas.py`, `alert_schemas.py`, `test_insight_service.py`, `auth.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `factories.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05960007765482431 - nodes in this community are weakly interconnected._
- **Why does `react-router-dom` connect `react-router-dom` to `LoginPage.tsx`, `OnboardingPage.tsx`, `DevicesPage.tsx`, `SyncStatusPage.tsx`, `GoalsPage.tsx`, `react-router-dom`, `api-client.ts`, `TrendsPage.tsx`, `package.json`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Should `with` be split into smaller, more focused modules?**
  _Cohesion score 0.05668016194331984 - nodes in this community are weakly interconnected._