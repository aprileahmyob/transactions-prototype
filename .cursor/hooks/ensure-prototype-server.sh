#!/bin/bash
# Ensure banking-screen prototype is served on :8765 before agent work.
set -euo pipefail

cat >/dev/null # consume hook stdin JSON if present

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

URL="http://localhost:8765/banking-screen"
PORT=8765
LOG="$ROOT/.cursor/prototype-server.log"
PIDFILE="$ROOT/.cursor/prototype-server.pid"

mkdir -p "$ROOT/.cursor"

if curl -sf -o /dev/null --max-time 2 "$URL" 2>/dev/null; then
  exit 0
fi

if lsof -iTCP:"$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
  exit 0
fi

if [[ -f "$PIDFILE" ]]; then
  old_pid="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
    exit 0
  fi
fi

nohup npx --yes serve -l 8765 . >>"$LOG" 2>&1 &
echo "$!" >"$PIDFILE"
exit 0
