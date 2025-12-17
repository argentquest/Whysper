## December 16 Changes

### Backend
- Added SSL helper (`backend/app/utils/ssl_utils.py`) to build uvicorn SSL kwargs and auto-generate self-signed certs when `SSL_SELF_SIGNED` is true.
- Updated backend entrypoints (`backend/main.py`, `backend/app/main.py`) to use the SSL helper; CORS now includes HTTPS localhost/127.0.0.1 origins.
- Added `SSL_SELF_SIGNED` env flag to `.envTemplate` and `backend/.env.example`; added `cryptography` dependency for cert generation.
- Diagram provider config now carries `provider_preferences` and `enabled_providers`; registry uses case-insensitive IDs and allowlist filtering. Updated `backend/diagrams/config.json` and expanded registry tests.

### Frontend
- Centralized API base resolution in `src/utils/apiBase.ts`; all API/SSE/diagram/status/static callers now use HTTPS-aware base URLs.
- Vite dev server binds to `0.0.0.0` and reads `VITE_DEV_PORT` (added to `frontend/.env`).
- Fixed TypeScript errors and completed `npm run build`.

### Tooling
- Added `scripts/generate-selfsigned-cert.ps1` to generate self-signed cert/key (defaults to `backend/certs/selfsigned.*`).
- Added `scripts/start-dev.sh` and `scripts/start-static.sh` for Linux dev/static workflows.
- Added `scripts/build-and-run-monolith.ps1` to set frontend env for the backend origin, build/copy the static bundle, and start the backend from one command; fixed param ordering.
- Added `scripts/build-and-run-monolith.sh` Linux equivalent for the monolithic static run (supports `--https` override).

### Notes
- Health endpoint is `https://<host>:8003/api/v1/system/health` (not `/api/v1/health`).
- To enable HTTPS: set `SSL_ENABLED=true`, `SSL_SELF_SIGNED=true`, and cert/key paths in `backend/.env` (or env vars); start backend normally.
