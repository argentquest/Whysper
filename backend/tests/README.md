# Whysper Backend Test Suite

This directory contains the complete test suite for the Whysper backend, organized into three testing levels following modern testing pyramid practices.

## Test Architecture

```
tests/
├── 1-UNIT/           # Unit Tests (Fast, Isolated)
├── 2-INTEGRATION/    # Integration Tests (Component Interactions) 
├── 3-END_TO_END/     # End-to-End Tests (Full Workflows)
└── conftest.py       # Shared test configuration
```

## Test Categories

### 🔬 Unit Tests (`1-UNIT/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast (< 1 second each)
- **Dependencies**: Minimal, use mocking
- **Coverage**: Individual functions, classes, modules

### 🔗 Integration Tests (`2-INTEGRATION/`)
- **Purpose**: Test component interactions and service integration
- **Speed**: Medium (1-30 seconds each)
- **Dependencies**: May use external services
- **Coverage**: API endpoints, provider integration, workflows

### 🎯 End-to-End Tests (`3-END_TO_END/`)
- **Purpose**: Test complete user workflows and system behavior
- **Speed**: Slow (30+ seconds each)
- **Dependencies**: Full system, external services
- **Coverage**: Complete user journeys, system validation

## Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run by category
pytest tests/1-UNIT/ -v          # Unit tests only
pytest tests/2-INTEGRATION/ -v   # Integration tests only  
pytest tests/3-END_TO_END/ -v    # End-to-end tests only

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/1-UNIT/diagram_wizard/test_provider_integration.py -v
```

## Test Configuration

### Environment Setup
- Tests use the same configuration system as the main application
- Environment variables can override test settings
- See `conftest.py` for shared test fixtures and configuration

### External Dependencies
Some tests require external services:
- **Kroki Service** (kroki.io) - For Kroki provider tests
- **D2 CLI** - For local D2 rendering tests
- **Network Access** - For external API validation

### Test Data
- Sample diagrams in `tests/samplediagrams/`
- Test case definitions in JSON files
- Generated artifacts in `tests/providers_test_artifacts/`

## Development Guidelines

### Writing Tests
1. **Unit Tests**: Fast, isolated, no external dependencies
2. **Integration Tests**: Test component interactions, limited external calls  
3. **End-to-End Tests**: Full workflows, real external services

### Test Organization
- Use descriptive test class and method names
- Group related tests in classes
- Add docstrings explaining test purpose
- Use appropriate test level for the scenario

### Performance
- Unit tests should complete in milliseconds
- Integration tests should complete within 30 seconds
- End-to-end tests may take several minutes

## Test Results

### Artifacts
- **SVG Files**: Generated in `providers_test_artifacts/`
- **Error Logs**: Captured in test result directories
- **Coverage Reports**: Generated with `--cov-report=html`

### Monitoring
- Track test success rates across providers
- Monitor performance regression in E2E tests
- Review error patterns in integration tests

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure `PYTHONPATH` includes backend directory
2. **Provider Failures**: Check external service availability
3. **Timeout Errors**: Increase timeout for slow network conditions
4. **Unicode Errors**: Tests handle Windows encoding issues automatically

### Debug Mode
```bash
# Run with verbose output and no capture
pytest tests/ -v -s

# Run single test with full traceback
pytest tests/path/to/test.py::test_function -vvv --tb=long

# Run with debugger on failure
pytest tests/ --pdb
```