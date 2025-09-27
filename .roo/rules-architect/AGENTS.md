# Project Architecture Rules (Non-Obvious Only)

- Service layer architecture in `backend/app/services/` encapsulates business logic separate from API handlers
- AI provider factory pattern in `backend/common/ai.py` enables dynamic provider loading via `PROVIDERS` environment variable
- Configuration management uses Pydantic v2 with environment variable overrides and secure credential handling
- API versioning strategy maintains dual paths `/api/v1/` and `/api/` for backward compatibility during migration
- Modular design splits monolithic API into focused modules with clear separation of concerns
- Testing architecture mirrors application structure with unit tests for services and integration tests for endpoints
- Security utilities enforce automatic masking of sensitive data in logs and debug output across the system
- Conversation management requires file context for first messages and uses persistent files for subsequent interactions