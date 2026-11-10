# Sapphire FitConnect

Wellness web app (not a diagnostic or emergency system): React + Vite frontend, FastAPI backend, SQLite locally, PostgreSQL optional.

## Structure

```
backend/    FastAPI app (app/), Alembic migrations (alembic/), tests, Dockerfile, dev.env, .env.example, run.sh
frontend/   React + Vite + Tailwind, vitest + Playwright, Dockerfile, nginx.conf.template, run.sh
start.sh    Local launcher           stop.sh   Stops the PIDs in .pids
docker-compose.yml, docker-compose.postgres.yml, .github/workflows/ci.yml
```

## Runtime contract

- Backend: `http://localhost:<BACKEND_PORT>` (first free port from 9000). All API routes live under `/api/v1`; health is `/health` and `/health/ready`.
- Frontend: `http://localhost:<FRONTEND_PORT>` (first free port from 5173). It calls relative `/api/v1/...`; the Vite dev proxy (and nginx in Docker) forwards `/api` unchanged to the backend. No `VITE_*` URL is ever written.
- `/docs` and `/openapi.json` exist only when `DEBUG=true` (local `dev.env` sets it; Docker sets it false).
- Config: `backend/dev.env` is committed with working local values; `start.sh` copies it to the gitignored `backend/.env` if missing, generates `JWT_SECRET_KEY` if empty, and writes `CORS_ORIGINS` for the chosen frontend port.
- Ports are chosen at start and printed.

## Start / stop

Requires Python 3.11+, Node 20.19+ or 22.12+, npm. Docker is not needed.

```
./start.sh     # venv, pip install ., alembic upgrade head, seed, backend, frontend
./stop.sh
```

Windows: run under Git Bash (`start.bat` wraps it). Single services: `backend/run.sh` (env `BACKEND_PORT`, `DATABASE_URL`) and `frontend/run.sh` (env `FRONTEND_PORT`, `BACKEND_PORT`). Logs go to `logs/`.

Seed credentials: `asha.menon@example.com` / `correct-horse-battery` (rohan.iyer@example.com and meena.rao@example.com share the same password).

## Docker

```
docker compose up --build                    # SQLite on the named volume /data; app on http://localhost (port 80), API proxied at /api
POSTGRES_PASSWORD=... docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build
```

The backend entrypoint runs `alembic upgrade head`, then `python -m app.seed` when `SEED_ON_START=true`.

## Tests and CI

```
cd backend && .venv/bin/python -m pytest -q      # plus: ruff check app tests; mypy app
cd frontend && npx vitest --run && npm run lint && npm run type-check && npm run build
```

`.github/workflows/ci.yml` runs the backend (Postgres service, `alembic upgrade head`, ruff, mypy, pytest --cov) and frontend (`npm ci`, lint, type-check, vitest, build) jobs.

## Environment variables

See `backend/.env.example` and `frontend/.env.example`, each listing every variable with required flag, default and source. `JWT_SECRET_KEY` (required): `python -c "import secrets;print(secrets.token_urlsafe(48))"`.
