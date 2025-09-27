# Project Coding Rules (Non-Obvious Only)

- AI provider factory in `backend/common/ai.py` supports dynamic loading from `PROVIDERS` environment variable (comma-separated); custom providers loaded as `{provider_name}_provider.py`
- Always use `SecurityUtils.safe_debug_info()` from `backend/security_utils.py` for debug output (masks API keys automatically)
- Pattern matcher in `backend/pattern_matcher.py` uses `TOOL_*` environment variables for detecting tool commands with confidence scoring
- Conversation service in `backend/app/services/conversation_service.py` requires at least one file selected for first message
- System message inserted only at conversation start (not sent to AI API); persistent files used for subsequent messages
- Codebase content loaded lazily when >50 files to avoid memory issues
- API supports dual paths: `/api/v1/` (primary) and `/api/` (legacy compatibility)