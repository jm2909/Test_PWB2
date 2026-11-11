#!/usr/bin/env bash
# Service-local launcher: install if needed, then start the Vite dev server.
# Usage: ./run.sh [port]   (BACKEND_PORT tells the dev proxy where the API is; default 9000)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-${FRONTEND_PORT:-5173}}"
export BACKEND_PORT="${BACKEND_PORT:-9000}"
[ -d node_modules ] || npm ci
exec npm run dev -- --host 127.0.0.1 --port "$PORT" --strictPort
