# End-to-End Tests

This directory contains end-to-end tests that verify complete user workflows and system behavior.

## Test Organization

### `/diagram_providers/`
Complete diagram provider testing with real rendering:
- **d2/** - D2 provider end-to-end tests
- **mermaid/** - Mermaid provider end-to-end tests  
- **kroki_***/** - Kroki provider variants
  - **kroki_c4/** - C4 diagrams via Kroki service
  - **kroki_d2/** - D2 diagrams via Kroki service
  - **kroki_mermaid/** - Mermaid diagrams via Kroki service
  - **kroki_plantuml/** - PlantUML diagrams via Kroki service
  - **kroki_structurizr/** - Structurizr diagrams via Kroki service

Each provider directory tests:
- Full render pipeline (code → validation → SVG)
- Error handling and recovery
- Provider-specific features and limitations

### `/validation/`
System validation and verification tests:
- **comprehensive_d2_test.py** - Comprehensive D2 system validation
- **render_samples.py** - Sample diagram rendering verification
- **run_all_provider_tests.py** - Cross-provider validation suite
- **test_with_samples.py** - Sample-based system testing
- **validate_all_25_d2.py** - 25-case D2 validation suite
- **test25.json** & **test50.json** - Test case definitions

## Running End-to-End Tests

```bash
# Run all end-to-end tests
pytest tests/3-END_TO_END/ -v

# Run specific provider tests
pytest tests/3-END_TO_END/diagram_providers/mermaid/ -v
pytest tests/3-END_TO_END/diagram_providers/d2/ -v

# Run validation suite
python tests/3-END_TO_END/validation/comprehensive_d2_test.py
python tests/3-END_TO_END/validation/run_all_provider_tests.py

# Run with extended timeout
pytest tests/3-END_TO_END/ -v --timeout=600
```

## Test Data

The `/validation/` directory contains test datasets:
- **test25.json** - 25 diverse diagram test cases
- **test50.json** - Extended 50-case test suite
- **samplediagrams/** - Reference sample diagrams

## System Requirements

End-to-end tests require:
- External service access (Kroki at kroki.io)
- Local D2 CLI installation (if testing d2v1 provider)
- Network connectivity for Kroki-based providers
- Sufficient timeout settings for complex diagrams

## Test Guidelines

- Tests verify complete user workflows
- Include real external service calls
- Test error scenarios and edge cases
- Validate actual SVG output quality
- Measure end-to-end performance
- Test system resilience and recovery