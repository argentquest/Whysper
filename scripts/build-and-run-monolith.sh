#!/usr/bin/env bash
set -euo pipefail

# Build frontend with API URL pointing to the backend, copy static assets, and start the backend.
# Usage: ./scripts/build-and-run-monolith.sh [--https]

use_https=false
if [[ "${1-}" == "--https" || "${1-}" == "-https" || "${1-}" == "-s" ]]; then
  use_https=true
  shift || true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $(basename "$0") [--https]" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
frontend_dir="$repo_root/frontend"
backend_dir="$repo_root/backend"
backend_env="$backend_dir/.env"
frontend_env="$frontend_dir/.env"
static_dir="$backend_dir/static"

get_env_value() {
  local key="$1" default="$2"
  if [[ -f "$backend_env" ]]; then
    local line
    line="$(grep -E "^${key}=" "$backend_env" | head -n1 || true)"
    if [[ -n "$line" ]]; then
      line="${line#*=}"
      line="${line%\"}"
      line="${line#\"}"
      line="${line%\'}"
      line="${line#\'}"
      echo "$line"
      return
    fi
  fi
  echo "$default"
}

set_or_replace_line() {
  local file="$1" key="$2" value="$3"
  touch "$file"
  local tmp
  tmp="$(mktemp)"
  grep -vE "^${key}=" "$file" >"$tmp" || true
  echo "${key}=${value}" >>"$tmp"
  mv "$tmp" "$file"
}

kill_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti tcp:"${port}" | xargs -r kill -9
  fi
}

api_port="$(get_env_value "API_PORT" "8003")"
ssl_enabled="$(get_env_value "SSL_ENABLED" "false")"
protocol="http"
if $use_https || [[ "${ssl_enabled,,}" == "true" ]]; then
  protocol="https"
fi
vite_api_url="${protocol}://localhost:${api_port}/api/v1"

echo "Configuring frontend env..."
set_or_replace_line "$frontend_env" "VITE_API_URL" "$vite_api_url"
set_or_replace_line "$frontend_env" "VITE_BACKEND_PORT" "$api_port"
set_or_replace_line "$frontend_env" "VITE_BACKEND_PROTOCOL" "$protocol"

echo "Ensuring frontend dependencies..."
if [[ ! -d "$frontend_dir/node_modules" ]]; then
  (cd "$frontend_dir" && npm install)
fi

echo "Building frontend..."
(cd "$frontend_dir" && npm run build)

echo "Copying dist -> backend/static ..."
rm -rf "$static_dir"
mkdir -p "$static_dir"
cp -R "$frontend_dir/dist/"* "$static_dir/" || true

echo "Stopping backend port ${api_port} (if running)..."
kill_port "$api_port"

echo "Starting backend on ${protocol}://0.0.0.0:${api_port} ..."
cd "$backend_dir"
python main.py
