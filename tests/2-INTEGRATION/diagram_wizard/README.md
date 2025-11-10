# DiagramWizard Integration Tests

This directory contains integration tests for the DiagramWizard feature. These tests validate complete workflows from initial prompts through diagram generation to SVG output.

## Test Files

### Workflow Tests
- `simple_flow_test.py` - Basic workflow test that successfully generates D2 code (1881 chars)
- `debug_test.py` - Detailed workflow debugging with comprehensive logging
- `perfect_score_test.py` - Tests workflow with perfect information score to trigger immediate generation
- `fixed_workflow_test.py` - Tests corrected workflow patterns
- `explicit_commands_test.py` - Tests explicit command handling

### Complete End-to-End Tests
- `test_complete_svg_workflow.py` - Full SVG generation workflow test
- `test_diagram_wizard_workflow.py` - Complete DiagramWizard workflow validation

### Test Runners
- `run_simple_test.py` - Quick validation and test runner
- `run_svg_test.py` - SVG-focused test runner

## How to Run

From the project root:

```bash
# Run individual tests
python tests/2-INTEGRATION/diagram_wizard/simple_flow_test.py

# Run with test runner
python tests/2-INTEGRATION/diagram_wizard/run_simple_test.py
```

## Expected Behavior

These tests validate:
1. Information scoring and clarification flow
2. LangGraph state transitions
3. AI integration and response handling
4. Diagram code generation
5. SVG rendering pipeline
6. Error handling and recovery

The `simple_flow_test.py` is known to successfully generate diagram code and should be used as a reference for working functionality.