# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Backend Commands
- Run backend: `python backend/main.py` (starts uvicorn server on port 8001)
- Test single file: `pytest backend/tests/test_specific_file.py::test_function_name`

## Critical Patterns
- AI providers loaded dynamically from `PROVIDERS` environment variable (comma-separated list); falls back to static providers if not set
- Always use `SecurityUtils.safe_debug_info()` for debug output to mask API keys and sensitive data
- Pattern matcher detects tool commands using `TOOL_*` environment variables with confidence scoring
- First conversation message requires at least one file selected for context
- System message inserted only at start of conversation history (not sent to API)
- Persistent files used for subsequent messages; codebase loaded lazily when >50 files
- Conversation history excludes system message when sending to AI API
- API supports dual paths: `/api/v1/` (primary) and `/api/` (legacy compatibility)