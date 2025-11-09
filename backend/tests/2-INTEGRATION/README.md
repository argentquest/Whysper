# Integration Tests

This directory contains integration tests that verify interactions between components and with external services.

## Test Organization

### `/api/`
API endpoint integration tests:
- **v1/endpoints/** - FastAPI endpoint tests with real HTTP requests
- Tests API contracts, request/response handling, error codes

### `/llm_testing/`
Large Language Model integration tests with diagram providers:
- **d2/** - LLM-generated D2 diagram validation (25 test cases)
- **mermaid/** - LLM-generated Mermaid diagram validation (25 test cases) 
- **kroki_***/** - Kroki provider variants testing
  - **kroki_c4/** - C4 diagrams via Kroki
  - **kroki_d2/** - D2 diagrams via Kroki
  - **kroki_mermaid/** - Mermaid diagrams via Kroki
  - **kroki_plantuml/** - PlantUML diagrams via Kroki
  - **kroki_structurizr/** - Structurizr diagrams via Kroki

Each LLM testing directory contains:
- `test25.json` - 25 diverse test cases
- `test_results_25/` - Generated SVG outputs and error logs
- `validate_*.py` - Validation scripts for provider testing

### `/provider_core/`
Provider system integration tests:
- Provider registry operations
- Cross-provider interactions
- Provider diagnostic tests
- Real diagram rendering tests

### `/services/`
Service layer integration tests:
- Conversation service tests
- Inter-service communication

### `/workflows/`
End-to-end workflow tests:
- Performance testing
- Multi-step workflow validation

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/2-INTEGRATION/ -v

# Run specific category
pytest tests/2-INTEGRATION/api/ -v
pytest tests/2-INTEGRATION/provider_core/ -v

# Run LLM testing for specific provider
pytest tests/2-INTEGRATION/llm_testing/mermaid/ -v

# Run with timeout for long-running tests
pytest tests/2-INTEGRATION/ -v --timeout=300
```

## LLM Testing Results

The `/llm_testing/` directories contain validation results for LLM-generated diagrams:

- **Success Rate**: Track validation success across 25 test cases
- **Error Analysis**: Review `test_results_25/errors/` for failure patterns
- **Visual Verification**: Check `test_results_25/svg/` for generated outputs

## Test Guidelines

- Tests may use external services (Kroki, local providers)
- Expect longer execution times than unit tests
- Tests verify component interactions work correctly
- Use real data and configurations when possible