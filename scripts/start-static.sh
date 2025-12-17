#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/frontend"
backend_dir="$repo_root/backend"
static_dir="$backend_dir/static"
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

echo "Building frontend..."
(cd "$frontend_dir" && npm run build)

echo "Syncing dist -> backend/static ..."
rm -rf "$static_dir"
mkdir -p "$static_dir"
cp -R "$frontend_dir/dist/"* "$static_dir/"

echo "Stopping backend port $backend_port (if running)..."
kill_port "$backend_port"

echo "Starting backend on 0.0.0.0:$backend_port ..."
cd "$backend_dir"
python main.py
