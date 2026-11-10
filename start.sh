#!/usr/bin/env bash
# Local launcher: installs, migrates, seeds and starts backend + frontend. Safe to rerun.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PIDS="$ROOT/.pids"

kill_tree() { # kill_tree PID : kill PID and its descendants (best effort, no pgrep needed)
  local child
  if [ -d /proc ]; then
    for st in /proc/[0-9]*/stat; do
      child="${st#/proc/}"; child="${child%/stat}"
      if [ "$(awk '{print $4}' "$st" 2>/dev/null)" = "$1" ]; then kill_tree "$child"; fi
    done
  elif command -v pkill >/dev/null 2>&1; then
    pkill -P "$1" 2>/dev/null || true
  fi
  kill "$1" 2>/dev/null || true
}

# 1. Stop anything a previous run started.
if [ -f "$PIDS" ]; then
  while read -r pid; do
    if [ -n "$pid" ]; then kill_tree "$pid"; fi
  done < "$PIDS"
  rm -f "$PIDS"
fi

# 2. Prerequisites (Docker is never required).
PYTHON=""
for c in python3 python; do
  if "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then PYTHON=$c; break; fi
done
[ -n "$PYTHON" ] || { echo "Python 3.11+ is required." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js 20.19+ or 22.12+ is required." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required." >&2; exit 1; }
if ! node -e 'const [a,b]=process.versions.node.split(".").map(Number);process.exit((a===20&&b>=19)||(a===22&&b>=12)||a>22?0:1)'; then
  echo "Node.js $(node -v) is too old: need ^20.19.0 || >=22.12.0." >&2; exit 1
fi

# 3. Free port finder (no lsof): try to bind with Python.
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
[ "$FRONTEND_PORT" = "$BACKEND_PORT" ] && FRONTEND_PORT="$(find_port $((FRONTEND_PORT + 1)))"

# 4. Backend setup.
cd "$ROOT/backend"
[ -d .venv ] || "$PYTHON" -m venv .venv
if [ -f .venv/Scripts/activate ]; then . .venv/Scripts/activate; else . .venv/bin/activate; fi
[ -f .env ] || cp dev.env .env

set_env() { # set_env KEY VALUE : replace or append in backend/.env
  python - "$1" "$2" <<'PY'
import sys
key, value = sys.argv[1], sys.argv[2]
lines = [l for l in open(".env").read().splitlines() if not l.startswith(key + "=")]
lines.append(f"{key}={value}")
open(".env", "w").write("\n".join(lines) + "\n")
PY
}
current_secret="$(grep '^JWT_SECRET_KEY=' .env | head -n1 | cut -d= -f2- || true)"
if [ -z "$current_secret" ]; then
  set_env JWT_SECRET_KEY "$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
fi
set_env CORS_ORIGINS "http://localhost:$FRONTEND_PORT,http://127.0.0.1:$FRONTEND_PORT"

pip install --quiet --disable-pip-version-check .
alembic upgrade head
python -m app.seed
DEBUG_VALUE="$(grep '^DEBUG=' .env | head -n1 | cut -d= -f2- | tr '[:upper:]' '[:lower:]' || true)"

mkdir -p "$ROOT/logs"
python -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" > "$ROOT/logs/backend.log" 2>&1 &
echo $! >> "$PIDS"

# 5. Frontend.
cd "$ROOT/frontend"
if [ -f package-lock.json ]; then npm ci; else npm install; fi
BACKEND_PORT=$BACKEND_PORT npm run dev -- --port "$FRONTEND_PORT" --host 127.0.0.1 > "$ROOT/logs/frontend.log" 2>&1 &
echo $! >> "$PIDS"

echo ""
echo "Frontend:  http://localhost:$FRONTEND_PORT"
echo "API:       http://localhost:$BACKEND_PORT/api/v1"
if [ "$DEBUG_VALUE" = "true" ]; then echo "API docs:  http://localhost:$BACKEND_PORT/docs"; fi
echo "Health:    http://localhost:$BACKEND_PORT/health"
echo "Sign in:   asha.menon@example.com / correct-horse-battery"
echo "Stop with: ./stop.sh   (logs in ./logs)"
