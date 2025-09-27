# Project Debug Rules (Non-Obvious Only)

- Always use `SecurityUtils.safe_debug_info()` from `backend/security_utils.py` for debug output (automatically masks API keys and sensitive data)
- AI provider debug info in `backend/common/ai.py` includes masked provider-specific details via `get_secure_debug_info()`
- Pattern matcher in `backend/pattern_matcher.py` provides detailed analysis with `get_analysis_details()` for debugging tool command detection
- Codebase lazy loading threshold in `backend/app/services/conversation_service.py` triggers at >50 files (affects memory usage debugging)
- API dual paths `/api/v1/` and `/api/` may behave differently for debugging legacy compatibility issues