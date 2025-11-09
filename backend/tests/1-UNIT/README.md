# Unit Tests

This directory contains unit tests that verify individual components and modules in isolation.

## Test Organization

### `/core/`
Core framework and base functionality tests.

### `/diagram_wizard/`
Tests for the diagram wizard LangGraph state machine:
- **integration_test_simple.py** - Basic integration test with provider registry
- **test_compilation.py** - Graph compilation and state initialization tests
- **test_provider_integration.py** - Comprehensive provider integration tests

### `/infrastructure/`
Infrastructure layer tests:
- AI providers and factory patterns
- Configuration and environment handling
- File utilities and path handling
- Logging infrastructure
- Security utilities

### `/providers/`
Provider configuration and unit tests:
- Individual provider config tests for each diagram type
- Provider registry unit tests
- LLM correction service tests

### `/utils/`
Utility function tests:
- Code extraction utilities
- Language detection
- Helper functions

## Running Unit Tests

```bash
# Run all unit tests
pytest tests/1-UNIT/ -v

# Run specific category
pytest tests/1-UNIT/diagram_wizard/ -v
pytest tests/1-UNIT/providers/ -v
pytest tests/1-UNIT/infrastructure/ -v

# Run with coverage
pytest tests/1-UNIT/ --cov=app --cov-report=html
```

## Test Guidelines

- Tests should be isolated and not depend on external services
- Use mocking for external dependencies
- Focus on testing individual function/class behavior
- Keep tests fast and deterministic