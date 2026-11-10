#!/usr/bin/env bash
# Run the backend alone. Env: BACKEND_PORT (default 9000), DATABASE_URL (default from .env/dev.env).
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate
elif [ -f .venv/bin/activate ]; then . .venv/bin/activate
else
  for c in python3 python; do
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then "$c" -m venv .venv; break; fi
  done
  if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate; else . .venv/bin/activate; fi
fi
[ -f .env ] || cp dev.env .env
pip install --quiet --disable-pip-version-check .
alembic upgrade head
python -m app.seed
exec python -m uvicorn app.main:app --host 127.0.0.1 --port "${BACKEND_PORT:-9000}"
