# Graph Report - test_pwb2  (2026-11-11)

## Corpus Check
- 231 files · ~48,758 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 14 file(s) not represented in the graph (top: (none) 5, .example 3, .ini 2)

## Summary
- 1543 nodes · 4364 edges · 97 communities (56 shown, 41 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `597a504a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Sapphire FitConnect
- backend
- http.py
- models/__init__.py
- test_pipeline_migration_parity.py
- test_insight_alert.py
- Factories
- middleware/errors.py
- ConnectionsPage.tsx
- ensure_utc
- services/goal.py
- services/consent.py
- Metrics
- App.tsx
- compilerOptions
- run.sh
- docker-entrypoint.sh
- ConnectionRepository
- sapphire-fitconnect-backend
- create_app
- GoalForm.tsx
- InsightRepository
- TrendsPage.tsx
- observability.py
- compilerOptions
- Clock
- logging_config.py
- healthcheck
- get_settings
- http.py
- scripts
- conftest.py
- security.py
- models/__init__.py
- @playwright/test
- frontend/run.sh
- simulated.py
- auth-context.tsx
- TASK-3 handoff: registration and dashboard
- Notice
- seed_support
- ConnectionsPage.test.tsx
- services/connection.py
- routers/goals.py
- DataRightsService
- DashboardPage.tsx
- build_engine
- services/insight.py
- index.ts
- sqlalchemy_orm
- backend
- test_connection_wearable.py
- seed.py
- services/auth.py
- Notice.tsx
- deps.py
- services/dashboard.py
- seed_consents
- TASK-8.md
- TASK-7 handoff: wearable connection (FR-007) and reading ingestion (FR-008)
- get_current_user
- sqlalchemy
- TrendsPage.test.tsx
- WellnessGoal
- dependencies
- test_demo_credentials_consistency.py
- TASK-13.md
- SupportForm.tsx
- package.json
- AccountRepository
- CurrentUser
- LoginPage.test.tsx
- GoalsPage.test.tsx
- start.sh
- stop.sh
- .record

## God Nodes (most connected - your core abstractions)
1. `Clock` - 53 edges
2. `CurrentUser` - 41 edges
3. `Notice()` - 40 edges
4. `utc_now()` - 34 edges
5. `login()` - 33 edges
6. `SystemClock` - 31 edges
7. `get_current_user()` - 29 edges
8. `get_settings()` - 29 edges
9. `ensure_utc()` - 29 edges
10. `react-router-dom` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Backend reuse` --references--> `CurrentUser`  [INFERRED]
  .handoff/TASK-4.md → backend/app/deps.py
- `TASK-5 handoff` --references--> `full_seed()`  [INFERRED]
  .handoff/TASK-5.md → backend/tests/conftest.py
- `Backend reuse` --references--> `require_active_consent()`  [INFERRED]
  .handoff/TASK-4.md → backend/app/deps.py
- `TASK-9 handoff` --references--> `create_app()`  [INFERRED]
  .handoff/TASK-9.md → backend/app/main.py
- `TASK-9 handoff` --references--> `register_alert_evaluation()`  [INFERRED]
  .handoff/TASK-9.md → backend/app/services/alert.py

## Import Cycles
- None detected.

## Communities (97 total, 41 thin omitted)

### Community 0 - "Sapphire FitConnect"
Cohesion: 0.25
Nodes (7): Docker, Environment variables, Quick start (Linux, macOS, Git Bash), Sapphire FitConnect, Seed credentials, Structure, Tests

### Community 1 - "backend"
Cohesion: 0.06
Nodes (35): defaults, env, runs-on, services, steps, run, DATABASE_URL, ENVIRONMENT (+27 more)

### Community 3 - "models/__init__.py"
Cohesion: 0.17
Nodes (5): Base, ReadingProcessingOutcome, InsightFeedback, json_default(), UTCDateTime

### Community 4 - "test_pipeline_migration_parity.py"
Cohesion: 0.08
Nodes (28): create_support_request(), get_support_service(), SupportRequestCreate, SupportRequestResponse, SupportService, test_insight_policy_blocks_persistence(), _alembic(), _annotation_kind() (+20 more)

### Community 5 - "test_insight_alert.py"
Cohesion: 0.14
Nodes (21): ContentPolicyError, ensure_allowed(), violations(), _grant(), _history(), _post(), _rule(), test_alert_evaluation_creates_alert_with_rule_version_and_wording() (+13 more)

### Community 6 - "Factories"
Cohesion: 0.07
Nodes (39): run_migrations_online(), get_dashboard(), DashboardAlertResponse, DashboardGoalResponse, DashboardInsightResponse, DashboardResponse, MeasurementResponse, SourceStatusResponse (+31 more)

### Community 7 - "middleware/errors.py"
Cohesion: 0.30
Nodes (6): _domain(), _http(), register_exception_handlers(), _unexpected(), _validation(), _value()

### Community 8 - "ConnectionsPage.tsx"
Cohesion: 0.14
Nodes (30): authorizationText(), BADGE, ConnectionCard(), connectionTitle(), Props, Props, ScaleConnectForm(), SCALES (+22 more)

### Community 9 - "ensure_utc"
Cohesion: 0.07
Nodes (16): ensure_utc(), Reading, ReadingRepository, create_reading(), get_reading_service(), list_readings(), get_trend(), ReadingRequest (+8 more)

### Community 10 - "services/goal.py"
Cohesion: 0.15
Nodes (8): create_goal(), update_goal_state(), GoalCreateRequest, GoalResponse, GoalStateRequest, GoalService, GoalValidationError, TASK-11 handoff: alerts (FR-016) and goals (FR-017)

### Community 11 - "services/consent.py"
Cohesion: 0.22
Nodes (13): require_active_consent(), NotFoundError, PermissionDeniedError, get_current_consent(), put_current_consent(), ConsentRequest, ConsentResponse, ConsentService (+5 more)

### Community 13 - "App.tsx"
Cohesion: 0.10
Nodes (34): App(), FieldError(), FieldErrors, RegisterForm(), validate(), LocationState, SignInForm(), RequireAuth() (+26 more)

### Community 14 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+10 more)

### Community 22 - "ConnectionRepository"
Cohesion: 0.25
Nodes (3): Connection, ConnectionRepository, seed_scale_connections()

### Community 25 - "create_app"
Cohesion: 0.13
Nodes (6): create_app(), lifespan(), setup_tracing(), run_seed(), _observer(), register_alert_evaluation()

### Community 26 - "GoalForm.tsx"
Cohesion: 0.15
Nodes (20): CATEGORY_LABEL, dateOnly, GoalCard(), goalTitle(), METRIC_PHRASE, Props, targetDate(), unitLabel() (+12 more)

### Community 27 - "InsightRepository"
Cohesion: 0.16
Nodes (4): ConflictError, Insight, InsightRepository, _fmt()

### Community 28 - "TrendsPage.tsx"
Cohesion: 0.16
Nodes (17): ChartPoint, dayFmt, Props, TrendChart(), dateFmt, Props, TrendTable(), getTrend() (+9 more)

### Community 30 - "compilerOptions"
Cohesion: 0.17
Nodes (11): compilerOptions, allowSyntheticDefaultImports, lib, module, moduleResolution, noEmit, skipLibCheck, strict (+3 more)

### Community 31 - "Clock"
Cohesion: 0.10
Nodes (4): Clock, SystemClock, AuditRepository, AuditService

### Community 32 - "logging_config.py"
Cohesion: 0.33
Nodes (4): get_correlation_id(), configure_logging(), CorrelationFilter, mask_email()

### Community 33 - "healthcheck"
Cohesion: 0.08
Nodes (25): PIP_TARGET, build, depends_on, environment, args, context, condition, environment (+17 more)

### Community 34 - "get_settings"
Cohesion: 0.17
Nodes (5): get_settings(), _protected_client(), test_get_current_user_paths(), test_login_through_real_endpoint(), test_rate_limit()

### Community 36 - "scripts"
Cohesion: 0.25
Nodes (8): scripts, build, dev, e2e, lint, preview, test, type-check

### Community 37 - "conftest.py"
Cohesion: 0.05
Nodes (46): auth_client(), auth_headers(), _headers(), client(), db_session(), factories(), _fresh_schema(), full_seed() (+38 more)

### Community 38 - "security.py"
Cohesion: 0.14
Nodes (17): create_token(), hash_password(), hash_token(), _prehash(), verify_password(), AuthService, _dummy_hash(), _cmd() (+9 more)

### Community 42 - "simulated.py"
Cohesion: 0.13
Nodes (10): AdapterAuthorizationDenied, AdapterPayloadInvalid, AdapterUnavailable, AuthorizationStart, ConnectionResult, NormalizedReading, ScaleAdapter, WearableAdapter (+2 more)

### Community 43 - "auth-context.tsx"
Cohesion: 0.12
Nodes (14): @testing-library/user-event@^14.5.2, renderWithProviders(), json(), mockApi(), emptyPage, granted, FULL, json() (+6 more)

### Community 48 - "TASK-3 handoff: registration and dashboard"
Cohesion: 0.50
Nodes (3): Endpoints, Seed logins (password Wellness-Demo-2026!), TASK-3 handoff: registration and dashboard

### Community 50 - "Notice"
Cohesion: 0.14
Nodes (21): ConsentForm(), NOTICE_CATEGORIES, NOTICE_VERSION, Props, DataRightsForm(), Props, statusLabel(), TYPE_LABEL (+13 more)

### Community 52 - "seed_support"
Cohesion: 0.39
Nodes (3): SupportRequest, SupportRepository, seed_support()

### Community 53 - "ConnectionsPage.test.tsx"
Cohesion: 0.38
Nodes (6): conn(), consent, items, json(), mockApi(), providers

### Community 55 - "services/connection.py"
Cohesion: 0.15
Nodes (17): CurrentUser, begin_wearable_authorization(), complete_wearable_authorization(), connect_scale(), get_connection_service(), list_connections(), list_providers(), AuthorizationResponse (+9 more)

### Community 56 - "routers/goals.py"
Cohesion: 0.16
Nodes (8): get_db(), get_clock(), acknowledge_alert(), list_alerts(), get_goal_service(), list_goals(), Page, PageParams

### Community 57 - "DataRightsService"
Cohesion: 0.15
Nodes (8): create_data_rights_request(), get_data_rights_service(), list_data_rights_requests(), DataRightsRequestCreate, DataRightsRequestResponse, DataRightsService, test_data_rights_list_is_owner_only_and_paginated(), test_data_rights_service_sets_reference_and_deadline()

### Community 58 - "DashboardPage.tsx"
Cohesion: 0.11
Nodes (37): AlertCard(), alertTitle(), TITLES, ConsentStatus(), AlertSummary(), DashboardInsight(), GoalProgressList(), UNITS (+29 more)

### Community 60 - "services/insight.py"
Cohesion: 0.22
Nodes (8): get_insight_service(), list_insights(), submit_feedback(), FeedbackRequest, FeedbackResponse, InsightResponse, ObservationPeriod, InsightService

### Community 61 - "index.ts"
Cohesion: 0.15
Nodes (16): Props, AlertState, WellnessAlert, ApiErrorBody, Page, ConnectionStatus, RecoveryAction, DashboardGoal (+8 more)

### Community 66 - "sqlalchemy_orm"
Cohesion: 0.24
Nodes (3): DataRightsRequest, DataRightsRepository, seed_data_rights()

### Community 67 - "backend"
Cohesion: 0.11
Nodes (19): BACKEND_HOST, build, env_file, environment, ports, volumes, x-preview-port, args (+11 more)

### Community 68 - "test_connection_wearable.py"
Cohesion: 0.31
Nodes (4): _begin(), test_connection_wearable_authorize_and_callback(), test_connection_wearable_bad_state_leaves_retry(), test_connection_wearable_denied_callback_and_isolation()

### Community 69 - "seed.py"
Cohesion: 0.19
Nodes (10): utc_now(), Session, seed_all(), seed_accounts(), seed_acknowledged_alert(), seed_goals(), seed_readings(), seed_wearables() (+2 more)

### Community 70 - "services/auth.py"
Cohesion: 0.19
Nodes (5): register_account(), AccountResponse, LoginRequest, RegisterRequest, TokenResponse

### Community 71 - "Notice.tsx"
Cohesion: 0.17
Nodes (13): dayFmt, fullFmt, InsightCard(), isLimitedData(), METRIC_NAMES, metricName(), periodDays(), IconName (+5 more)

### Community 72 - "deps.py"
Cohesion: 0.10
Nodes (12): Settings, client_ip(), get_auth_service(), get_consent_service(), get_token_issuer(), login_rate_limit(), AuthenticationError, DomainError (+4 more)

### Community 73 - "services/dashboard.py"
Cohesion: 0.10
Nodes (12): AlertAcknowledgement, AlertRule, WellnessAlert, AlertRepository, get_alert_service(), AlertResponse, seed_alert_rules(), seed_insights_and_alerts() (+4 more)

### Community 74 - "seed_consents"
Cohesion: 0.31
Nodes (3): ConsentRecord, ConsentRepository, seed_consents()

### Community 76 - "TASK-7 handoff: wearable connection (FR-007) and reading ingestion (FR-008)"
Cohesion: 0.40
Nodes (4): Endpoints (all Bearer, under /api/v1), For TASK-9, Notes, TASK-7 handoff: wearable connection (FR-007) and reading ingestion (FR-008)

### Community 80 - "sqlalchemy"
Cohesion: 0.10
Nodes (5): upgrade(), _goal(), test_alert_acknowledge_is_idempotent_and_keeps_history(), test_goal_create_progress_data_gap_and_available(), test_goal_create_validates_input()

### Community 81 - "TrendsPage.test.tsx"
Cohesion: 0.38
Nodes (6): insight, json(), mockApi(), page(), steps, weight

### Community 83 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, react@^18.3.1, react-dom@^18.3.1, react-router-dom@^6.28.0, react-dom

### Community 88 - "SupportForm.tsx"
Cohesion: 0.18
Nodes (14): LabelledSelect(), Props, CATEGORIES, CONTEXTS, DEFAULT_CATEGORY, MAX_DESCRIPTION, Props, SupportForm() (+6 more)

### Community 89 - "package.json"
Cohesion: 0.07
Nodes (41): devDependencies, autoprefixer@^10.4.20, eslint@^9.17.0, @eslint/js@^9.17.0, eslint-plugin-react-hooks@^5.1.0, globals@^15.14.0, jsdom@^25.0.1, postcss@^8.4.49 (+33 more)

### Community 91 - "CurrentUser"
Cohesion: 0.33
Nodes (5): Backend reuse, Endpoints added, Existing behaviour used by the UI, Seeds (login with the password `Wellness-Demo-2026!`), TASK-4 handoff: sessions and consent (backend)

### Community 92 - "LoginPage.test.tsx"
Cohesion: 0.47
Nodes (3): DEMO_ASHA_EMAIL, DEMO_PASSWORD, DEMO_ROHAN_EMAIL

### Community 93 - "GoalsPage.test.tsx"
Cohesion: 0.83
Nodes (3): goal(), json(), mockApi()

## Knowledge Gaps
- **2 isolated node(s):** `sapphire-fitconnect-backend`, `BACKEND_PORT`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 461 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CurrentUser` connect `services/connection.py` to `.record`, `get_settings`, `test_pipeline_migration_parity.py`, `conftest.py`, `services/auth.py`, `Factories`, `deps.py`, `ensure_utc`, `services/goal.py`, `services/consent.py`, `get_current_user`, `routers/goals.py`, `DataRightsService`, `CurrentUser`, `services/insight.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `CurrentUser` (e.g. with `revoke_current_token()` and `get_current_consent()`) actually correct?**
  _`CurrentUser` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `sapphire-fitconnect-backend`, `BACKEND_PORT` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `backend` be split into smaller, more focused modules?**
  _Cohesion score 0.06190476190476191 - nodes in this community are weakly interconnected._
- **Why does `get_settings()` connect `get_settings` to `sqlalchemy_orm`, `models/__init__.py`, `conftest.py`, `security.py`, `services/auth.py`, `deps.py`, `Factories`, `simulated.py`, `services/connection.py`, `create_app`, `Clock`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `test_pipeline_migration_parity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07597402597402597 - nodes in this community are weakly interconnected._
- **Why does `Clock` connect `Clock` to `sqlalchemy_orm`, `models/__init__.py`, `test_pipeline_migration_parity.py`, `Factories`, `models/__init__.py`, `deps.py`, `services/dashboard.py`, `simulated.py`, `ensure_utc`, `services/auth.py`, `services/consent.py`, `services/goal.py`, `get_current_user`, `services/connection.py`, `routers/goals.py`, `DataRightsService`, `services/insight.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._