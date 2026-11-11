#!/usr/bin/env bash
# Service-local launcher: migrate, then serve. Usage: ./run.sh [port]
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-${BACKEND_PORT:-9000}}"
[ -f .env ] || cp dev.env .env
if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate; elif [ -f .venv/bin/activate ]; then . .venv/bin/activate; fi
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
