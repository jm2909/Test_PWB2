#!/usr/bin/env bash
# Stops exactly the processes recorded in .pids by start.sh.
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
if [ ! -f "$PIDS" ]; then echo "Nothing to stop."; exit 0; fi
while read -r pid; do
  if [ -n "$pid" ]; then kill_tree "$pid"; fi
done < "$PIDS"
rm -f "$PIDS"
echo "Stopped."
