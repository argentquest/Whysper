#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/frontend"
backend_dir="$repo_root/backend"

frontend_port="${VITE_DEV_PORT:-5173}"
backend_port="${API_PORT:-8003}"

kill_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti tcp:"${port}" | xargs -r kill -9
  fi
}

echo "Ensuring frontend dependencies..."
if [ ! -d "$frontend_dir/node_modules" ]; then
  (cd "$frontend_dir" && npm install)
fi

echo "Stopping ports $backend_port and $frontend_port (if running)..."
kill_port "$backend_port"
kill_port "$frontend_port"

echo "Starting backend on 0.0.0.0:$backend_port ..."
(cd "$backend_dir" && python main.py) &
backend_pid=$!

cleanup() {
  kill "$backend_pid" >/dev/null 2>&1 || true
  kill "$frontend_pid" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Starting frontend dev server on 0.0.0.0:$frontend_port ..."
(cd "$frontend_dir" && npm run dev -- --host --port "$frontend_port") &
frontend_pid=$!

wait
