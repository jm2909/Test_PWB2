# Sapphire FitConnect

Wellness-tracking web app: React + TypeScript (Vite) SPA and a FastAPI backend (sync SQLAlchemy 2, Alembic).
Wellness support only; it is not a medical product.

## Structure

- `backend/` FastAPI app (`app/`), Alembic migrations (`alembic/`), tests (`tests/`), `dev.env` local config
- `frontend/` Vite SPA, vitest unit tests, Playwright e2e
- `start.sh` / `stop.sh` local launcher; `docker-compose.yml` containers; `.github/workflows/ci.yml` CI

## Quick start (Linux, macOS, Git Bash)

Needs Python 3.11+ and Node `^20.19.0 || >=22.12.0` with npm.

```
./start.sh     # venv, install, migrate, seed, start both servers
./stop.sh      # stops exactly the PIDs in .pids
```

Backend starts at the first free port from 9000, frontend from 5173; both are printed. Logs go to `.logs/`.
Each surface also runs alone: `backend/run.sh [port]`, `frontend/run.sh [port]`.

| Item | URL |
|---|---|
| App | http://localhost:5173 |
| API | http://localhost:9000/api/v1 |
| Swagger docs | http://localhost:9000/docs |
| Health | `/health`, `/health/ready`, `/metrics` (backend root) |

## Seed credentials

Canonical source: `backend/app/seeds/constants.py` (mirrored in `frontend/src/lib/demo-credentials.ts`).

| Persona | Email | Password |
|---|---|---|
| Asha | asha@sapphire.example | Wellness-Demo-2026! |
| Rohan | rohan@sapphire.example | Wellness-Demo-2026! |

## Environment variables

Set in `backend/.env` (copied from the committed `backend/dev.env` if absent). Template: `.env.example`.

| Variable | Required | Default | Notes |
|---|---|---|---|
| `ENVIRONMENT` | no | `development` | `production` enforces a real secret |
| `DEBUG` | no | `false` | |
| `DATABASE_URL` | no | `sqlite:///./app.db` | PostgreSQL: `postgresql+psycopg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | production | dev value in `dev.env` | >= 32 chars; `python -c "import secrets;print(secrets.token_urlsafe(48))"` |
| `JWT_ALGORITHM` | no | `HS256` | |
| `SESSION_TTL_MINUTES` | no | `480` | absolute session life |
| `SESSION_INACTIVITY_MINUTES` | no | `30` | |
| `CORS_ORIGINS` | no | `http://localhost:5173` | comma-separated; start.sh sets it to the chosen frontend port |
| `DATA_RIGHTS_FULFILLMENT_DAYS` | no | `30` | |
| `FRESHNESS_STALE_AFTER_HOURS` | no | `24` | |
| `WEARABLE_PROVIDERS` | no | `fitband,pulsewear` | |
| `LOGIN_RATE_LIMIT` | no | `10/minute` | per source IP |
| `RATE_LIMIT_ENABLED` | no | `true` | disable only in tests |
| `TRUST_FORWARDED_FOR` | no | `false` | enable only behind a trusted proxy |
| `AUDIT_RETENTION_DAYS` | no | `365` | |
| `SEED_ON_STARTUP` | no | `false` (`true` in dev.env) | idempotent demo seed |
| `BACKEND_PORT` | no | `9000` | frontend dev proxy target; set by start.sh |
| `VITE_API_URL` | no | unset | leave unset; the browser calls relative `/api` |

## Tests

```
cd backend && pip install ".[dev]" && python -m pytest tests -q && ruff check app tests && mypy app
cd frontend && npm ci && npm run lint && npm run type-check && npx vitest --run && npm run build
```

## Docker

```
docker compose up --build      # SQLite in the named volume backend-data; app on http://localhost
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build   # PostgreSQL 16
```

The `frontend` image (nginx) serves the SPA and forwards `/api/` to `backend:9000` (build arg `BACKEND_HOST`).
The backend entrypoint runs `alembic upgrade head`; the demo seed runs at app startup (`SEED_ON_STARTUP`).
Swagger is at http://localhost:9000/docs. For production set `ENVIRONMENT=production`, a strong `JWT_SECRET_KEY`,
explicit `CORS_ORIGINS`, and replace the demo Postgres password in the override file.
CI (`.github/workflows/ci.yml`) runs backend (Postgres) and frontend checks.
