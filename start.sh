#!/usr/bin/env bash
# Local launcher (Linux, macOS, Git Bash on Windows): prepares both surfaces and starts them.
# Run from anywhere: ./start.sh      Stop with: ./stop.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT/.pids"
LOG_DIR="$ROOT/.logs"
cd "$ROOT"

# --- stop anything a previous run left behind ---------------------------------
if [ -f "$PID_FILE" ]; then
  while read -r old_pid; do
    [ -n "$old_pid" ] && kill "$old_pid" 2>/dev/null || true
  done <"$PID_FILE"
  rm -f "$PID_FILE"
fi
mkdir -p "$LOG_DIR"

# --- prerequisites -------------------------------------------------------------
PYTHON=""
for c in python3 python; do
  if "$c" -c 'import sys' >/dev/null 2>&1; then
    if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
      PYTHON=$c
      break
    fi
  fi
done
if [ -z "$PYTHON" ]; then
  echo "ERROR: Python 3.11+ is required but was not found on PATH." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: Node.js and npm are required (see engines.node in frontend/package.json)." >&2
  exit 1
fi
# engines.node is "^20.19.0 || >=22.12.0"
if ! node -e '
const [a, b] = process.versions.node.split(".").map(Number);
process.exit((a === 20 && b >= 19) || a > 22 || (a === 22 && b >= 12) ? 0 : 1);
'; then
  echo "ERROR: Node $(node -v) is too old; need ^20.19.0 or >=22.12.0." >&2
  exit 1
fi

# --- free port finder (no lsof) ------------------------------------------------
find_port() {
  "$PYTHON" - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
while port < 65535:
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        print(port)
        break
    except OSError:
        s.close()
        port += 1
PY
}

BACKEND_PORT="$(find_port 9000)"
FRONTEND_PORT="$(find_port 5173)"
if [ "$FRONTEND_PORT" = "$BACKEND_PORT" ]; then
  FRONTEND_PORT="$(find_port $((BACKEND_PORT + 1)))"
fi

# --- backend ---------------------------------------------------------------------
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi
if [ -f .venv/Scripts/activate ]; then
  # shellcheck disable=SC1091
  . .venv/Scripts/activate
else
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

[ -f .env ] || cp dev.env .env

# CORS must be in .env BEFORE the backend starts.
CORS="http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT}"
TMP_CFG="$(mktemp)"
{ grep -v "^CORS_ORIGINS=" .env || true; } >"$TMP_CFG"
echo "CORS_ORIGINS=${CORS}" >>"$TMP_CFG"
cat "$TMP_CFG" >.env && rm -f "$TMP_CFG"

python -m pip install --quiet --disable-pip-version-check .
alembic upgrade head
python -m app.seed

python -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" >"$LOG_DIR/backend.log" 2>&1 &
echo "$!" >>"$PID_FILE"

# --- frontend --------------------------------------------------------------------
cd "$ROOT/frontend"
if [ -f package-lock.json ]; then
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi
BACKEND_PORT="$BACKEND_PORT" npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT" --strictPort >"$LOG_DIR/frontend.log" 2>&1 &
echo "$!" >>"$PID_FILE"

cd "$ROOT"
echo
echo "Sapphire FitConnect is starting."
echo "  Frontend : http://localhost:${FRONTEND_PORT}"
echo "  Backend  : http://localhost:${BACKEND_PORT}   (API under /api/v1)"
echo "  API docs : http://localhost:${BACKEND_PORT}/docs"
echo "  Health   : http://localhost:${BACKEND_PORT}/health"
echo "  Seed accounts (password Wellness-Demo-2026!):"
echo "    asha@sapphire.example"
echo "    rohan@sapphire.example"
echo "  Logs: .logs/   Stop with ./stop.sh"

wait
