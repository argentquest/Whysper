# Diagram Provider Tests

Comprehensive pytest test suite for testing diagram provider rendering (Mermaid, D2, etc.)

## Overview

These tests ensure that the diagram provider system works correctly for:
- Rendering diagrams via the `/api/v1/diagrams/v2/render` endpoint
- Validating diagram code via the `/api/v1/diagrams/v2/validate` endpoint
- Provider discovery and health checks
- Event logging
- Error handling and edge cases

## Test Structure

```
tests/providers/
├── __init__.py                      # Package init
├── conftest.py                      # Pytest fixtures
├── test_mermaid_provider.py         # Mermaid-specific tests
├── test_d2_provider.py              # D2-specific tests
├── test_provider_integration.py     # Cross-provider tests
└── README.md                        # This file
```

## Running Tests

### Run all provider tests
```bash
pytest tests/providers/ -v
```

### Run specific provider tests
```bash
# Mermaid tests only
pytest tests/providers/test_mermaid_provider.py -v

# D2 tests only
pytest tests/providers/test_d2_provider.py -v

# Integration tests only
pytest tests/providers/test_provider_integration.py -v
```

### Run by test class
```bash
pytest tests/providers/test_mermaid_provider.py::TestMermaidRenderingBasic -v
```

### Run specific test
```bash
pytest tests/providers/test_mermaid_provider.py::TestMermaidRenderingBasic::test_render_simple_flowchart -v
```

### Run with markers
```bash
pytest tests/providers/ -m rendering -v
pytest tests/providers/ -m validation -v
pytest tests/providers/ -m integration -v
```

### Run with coverage
```bash
pytest tests/providers/ --cov=app.api.v1.endpoints.diagram_provider --cov-report=html
```

## Test Coverage

### Test Files

#### `test_mermaid_provider.py`
- **TestMermaidRenderingBasic**: Basic rendering functionality
  - Simple and complex flowchart rendering
  - Auto-fix functionality
  - Response format validation

- **TestMermaidValidation**: Diagram validation
  - Valid diagram validation
  - Invalid diagram detection

- **TestMermaidErrorHandling**: Error scenarios
  - Missing required fields
  - Empty code handling
  - Invalid input handling

- **TestMermaidMetadata**: Provider metadata
  - Provider info endpoint
  - Health check endpoint

#### `test_d2_provider.py`
- **TestD2RenderingBasic**: Basic D2 rendering
  - Simple and complex diagram rendering
  - Auto-fix functionality
  - Response format validation

- **TestD2Validation**: D2 code validation
  - Valid diagram validation
  - Invalid diagram detection

- **TestD2ErrorHandling**: Error scenarios
  - Missing required fields
  - Empty code handling
  - Invalid input handling

- **TestD2Metadata**: Provider metadata
  - Provider info endpoint
  - Health check endpoint

#### `test_provider_integration.py`
- **TestProviderDiscovery**: Provider listing and discovery
  - List all providers
  - Verify provider presence
  - Check required fields

- **TestCrossProviderRendering**: Multi-provider scenarios
  - Rendering with different providers
  - Different output formats

- **TestProviderErrors**: Error handling across providers
  - Invalid provider types
  - Invalid output formats

- **TestProviderPerformance**: Performance metrics
  - Render time recording
  - Performance validation

- **TestEventLogging**: Event logging integration
  - Log render events
  - Log error events

## Fixtures

### Client
```python
@pytest.fixture
def client():
    """FastAPI test client."""
```

### Sample Code
```python
@pytest.fixture
def mermaid_code_simple()
    """Simple Mermaid flowchart."""

@pytest.fixture
def d2_code_simple()
    """Simple D2 diagram."""

@pytest.fixture
def mermaid_code_complex()
    """Complex Mermaid diagram."""

@pytest.fixture
def d2_code_complex()
    """Complex D2 diagram with styling."""

@pytest.fixture
def c4_code_simple()
    """Simple C4 diagram."""
```

### Invalid Code
```python
@pytest.fixture
def invalid_mermaid()
    """Invalid Mermaid code."""

@pytest.fixture
def invalid_d2()
    """Invalid D2 code."""
```

## Key Test Scenarios

### Rendering Tests
- ✅ Simple diagram rendering
- ✅ Complex diagram rendering
- ✅ Auto-fix during rendering
- ✅ Different output formats (SVG, PNG)
- ✅ Response format validation
- ✅ Metadata recording (render time, provider ID)

### Validation Tests
- ✅ Valid diagram validation
- ✅ Invalid diagram detection
- ✅ Error message handling

### Error Handling
- ✅ Missing diagram_type field
- ✅ Missing code field
- ✅ Empty code handling
- ✅ Invalid diagram types
- ✅ Invalid output formats

### Integration Tests
- ✅ Provider discovery
- ✅ Cross-provider rendering
- ✅ Event logging
- ✅ Performance monitoring

## API Endpoints Tested

### Render Endpoint
```
POST /api/v1/diagrams/v2/render
```

**Request:**
```json
{
  "code": "diagram code",
  "diagram_type": "mermaid|d2|c4",
  "output_format": "svg|png",
  "auto_fix": true,
  "use_llm": false
}
```

**Response:**
```json
{
  "success": true,
  "content": "<svg>...</svg>",
  "validation": {
    "is_valid": true,
    "errors": []
  },
  "provider_id": "mermaidv1",
  "metadata": {
    "render_time": 0.234,
    "version": "1.0"
  }
}
```

### Validate Endpoint
```
POST /api/v1/diagrams/v2/validate
```

### Provider Discovery
```
GET /api/v1/diagrams/v2/providers
GET /api/v1/diagrams/v2/providers/{id}
GET /api/v1/diagrams/v2/health
```

### Event Logging
```
POST /api/v1/diagrams/log-diagram-event
```

## Expected Behavior

### Successful Rendering
- Returns 200 OK
- SVG content included in response
- Provider ID specified
- Render time recorded

### Invalid Input
- Returns 422 for missing required fields
- Returns 400 for invalid format
- Returns 200 with error in validation for invalid diagrams

### Provider Health
- All providers should be available
- Health endpoint should respond
- Provider list should be non-empty

## Dependencies

Tests require:
- `pytest>=7.0.0`
- `pytest-asyncio>=0.21.0`
- `fastapi[all]>=0.100.0`
- `httpx>=0.24.0`

All dependencies are in `requirements.txt`

## Running from Root

```bash
# Run all provider tests
pytest backend/tests/providers/ -v

# Run with coverage
pytest backend/tests/providers/ --cov=app --cov-report=html

# Run in watch mode (requires pytest-watch)
ptw backend/tests/providers/
```

## CI/CD Integration

These tests are designed to be easily integrated into CI/CD pipelines:

```bash
# Simple exit code check
pytest backend/tests/providers/ --tb=short && echo "Tests passed"

# With coverage reporting
pytest backend/tests/providers/ --cov=app --cov-report=xml
```

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Add stress testing (many concurrent requests)
- [ ] Add rendering quality validation tests
- [ ] Add screenshot comparison tests
- [ ] Add PlantUML provider tests
- [ ] Add Graphviz provider tests
- [ ] Add test database fixtures for caching tests

## Contributing

When adding new provider tests:
1. Create new test file: `test_{provider}_provider.py`
2. Follow the same structure as existing test files
3. Add appropriate markers in pytest.ini
4. Update this README
5. Ensure all tests pass locally before committing
