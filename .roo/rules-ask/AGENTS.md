# Project Documentation Rules (Non-Obvious Only)

- Backend app code is in `backend/app/` directory (not `backend/` root); main entry point is `backend/main.py` importing from `backend.app.main`
- API supports dual paths: `/api/v1/` (primary) and `/api/` (legacy compatibility) - both serve same functionality
- AI providers loaded dynamically from `PROVIDERS` environment variable (comma-separated); falls back to static providers if not configured
- Conversation service requires file selection for first message; system message handling differs between API and internal storage
- Pattern matcher uses `TOOL_*` environment variables for tool command detection with configurable confidence thresholds
- Testing uses pytest with separate requirements file `backend/requirements-test.txt`; no frontend testing framework configured
- Security utilities in `backend/security_utils.py` automatically mask sensitive data in logs and debug output