#!/usr/bin/env bash
# Stops exactly the processes recorded in .pids by start.sh.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT/.pids"
if [ ! -f "$PID_FILE" ]; then
  echo "Nothing to stop (no .pids file)."
  exit 0
fi
while read -r pid; do
  if [ -n "$pid" ] && kill "$pid" 2>/dev/null; then
    echo "Stopped $pid"
  fi
done <"$PID_FILE"
rm -f "$PID_FILE"
