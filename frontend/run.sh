#!/usr/bin/env bash
# Run the frontend dev server alone. Env: FRONTEND_PORT (default 5173), BACKEND_PORT (default 9000; proxy target for /api).
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ -f package-lock.json ]; then npm ci; else npm install; fi
BACKEND_PORT="${BACKEND_PORT:-9000}" exec npm run dev -- --port "${FRONTEND_PORT:-5173}"
