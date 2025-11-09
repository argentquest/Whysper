# LLM Mermaid Diagram Generation and Validation Tests

Generate Mermaid diagrams using LLM prompts and validate them with the Mermaid CLI.

## Overview

This test suite:
- Loads test cases from JSON files (test25.json, test50.json)
- Generates Mermaid diagram code using LLM via the backend API
- Validates generated Mermaid code using the Mermaid CLI
- Renders valid diagrams to SVG files
- Reports validation results and errors

## Directory Structure

```
llmmermaidtest/
├── __init__.py                          # Package initialization
├── README.md                            # This file
├── validate_all_25_mermaid.py          # Main validation script
├── test25.json                          # 25 test cases for Mermaid generation
├── test50.json                          # 50 test cases for Mermaid generation
├── history/                             # Historical generated diagram code
├── test_results_25/                     # Results directory for test25
│   ├── errors/                          # Error details and logs
│   │   ├── test_001_error.txt
│   │   ├── test_002_error.txt
│   │   └── validation_results.json      # Summary of all results
│   └── svg/                             # Rendered SVG diagrams
│       ├── test_001_Basic_Flowchart.svg
│       ├── test_002_Sequence_Diagram.svg
│       └── ...
└── test_results_50/                     # Results directory for test50
    ├── errors/
    └── svg/
```

## Prerequisites

### Required Software

1. **Mermaid CLI** - For validating and rendering Mermaid diagrams
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

2. **Python 3.8+**
   - requests library (for API calls)
   - json (built-in)

3. **Whysper Backend** - Running on localhost:8003
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8003
   ```

### Installation

```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Verify Mermaid CLI is installed
mmdc --version

# Verify backend is running
curl http://localhost:8003/api/v1/system/health
```

## Usage

### Run Test Validation

Run the validation script to generate and validate Mermaid diagrams:

```bash
# Test with 25 test cases (default)
python validate_all_25_mermaid.py 25
# or
python validate_all_25_mermaid.py

# Test with 50 test cases
python validate_all_25_mermaid.py 50
```

### Script Output

The script will:

1. **Check Mermaid CLI** - Verify Mermaid CLI is installed and get version
2. **Load Test Cases** - Read test cases from JSON file
3. **Process Each Test**:
   - Check for existing generated code in history
   - Generate Mermaid code if not cached (using backend LLM)
   - Validate Mermaid syntax using Mermaid CLI
   - Render to SVG if valid
4. **Generate Report** - Create summary and error files

### Expected Output

```
Mermaid CLI Validator - Processing test25 tests
============================================================

[Mermaid CLI] Version: 10.6.1

Loading tests from: .../test25.json

Processing 25 tests...

============================================================
Test 1: Basic Flowchart
============================================================
  Generating code...
  Generated code (450 chars)
  Validating Mermaid code...
  [PASS] Validation successful
  Rendering SVG...
  [SVG] Saved to: test_001_Basic_Flowchart.svg

...

============================================================
VALIDATION SUMMARY
============================================================

Total tests: 25
Tests with diagram code: 25
Tests generated: 25
Tests valid: 23
Tests invalid: 2

Success rate: 92.0%

Detailed results saved to: .../test_results_25/errors/validation_results.json

Failed tests (2):
  - Test 5: ER Diagram
    Error file: test_005_error.txt
  - Test 12: Swimlane Flowchart
    Error file: test_012_error.txt

============================================================
MERMAID VALIDATION COMPLETE
============================================================
```

## Test Case Format

Test cases are defined in JSON files with the following structure:

```json
{
  "mermaid_capability_tests": [
    {
      "id": 1,
      "name": "Basic Flowchart",
      "description": "Generate a **Mermaid diagram** showing a simple flowchart where...",
      "tests": [
        "Basic Flow",
        "Labeled Relationships"
      ]
    },
    ...
  ]
}
```

## Output Files

### Error Files

When validation fails, an error file is created:

```
test_005_error.txt
─────────────────
Test ID: 5
Test Name: ER Diagram
Description: Generate a **Mermaid ER diagram** with...
Generated: true

Validation Error:
Mermaid Syntax Error:
  err: invalid syntax...

Diagram Code:
[Generated Mermaid code that failed]
```

### SVG Files

Valid diagrams are rendered to SVG:

```
test_001_Basic_Flowchart.svg (viewable in any browser)
test_002_Sequence_Diagram.svg
test_003_Class_Diagram.svg
...
```

### Summary Report

Detailed results saved to `validation_results.json`:

```json
{
  "timestamp": "2025-11-02T12:30:45.123456",
  "summary": {
    "total_tests": 25,
    "tests_with_code": 25,
    "tests_generated": 25,
    "tests_valid": 23,
    "tests_invalid": 2,
    "success_rate": 92.0
  },
  "results": [
    {
      "test_id": 1,
      "test_name": "Basic Flowchart",
      "has_code": true,
      "diagram_code": "...",
      "is_valid": true,
      "validation_error": "",
      "generated": true,
      "error_file": "",
      "svg_file": "test_001_Basic_Flowchart.svg"
    },
    ...
  ]
}
```

## API Endpoints Used

The script uses the following backend API endpoints:

### Generate Diagram Code
```
POST http://localhost:8003/mcp/tools/generate_diagram
Content-Type: application/json

{
  "prompt": "Generate a Mermaid diagram showing...",
  "diagram_type": "mermaid"
}

Response:
{
  "content": [
    {
      "text": "{\"diagram_code\": \"...\"}"
    }
  ]
}
```

## Troubleshooting

### Mermaid CLI Not Found

```
[ERROR] Mermaid CLI not available: [Errno 2] No such file or directory: 'mmdc'
```

**Solution:** Install Mermaid CLI

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version
```

### Backend API Errors

```
API error: 500
```

**Solution:** Ensure backend is running

```bash
curl http://localhost:8003/api/v1/system/health
```

### Generation Timeout

```
Generation error: HTTP 408
```

**Solution:** LLM is taking too long. Check backend logs and retry:

```bash
python validate_all_25_mermaid.py 25
```

### No History Files Found

If script is generating all diagrams (slow), results are being cached in the `history/` directory for future runs.

## Script Configuration

### Timeouts

- **Mermaid Validation**: 120 seconds (line 42)
- **Mermaid Rendering**: 120 seconds (line 92)
- **API Generation**: 60 seconds (line 133)

Adjust these in `validate_all_25_mermaid.py` if needed.

### Output Directories

Script automatically creates:
- `test_results_25/errors/` - For test25 error files
- `test_results_25/svg/` - For test25 rendered diagrams
- `test_results_50/errors/` - For test50 error files
- `test_results_50/svg/` - For test50 rendered diagrams

## Mermaid Diagram Types Supported

The test suite covers various Mermaid diagram types:

1. **Flowchart** - Basic and complex flows with decision nodes
2. **Sequence Diagram** - Actor interactions and message flow
3. **Class Diagram** - Object-oriented design and relationships
4. **State Diagram** - State machines and transitions
5. **ER Diagram** - Entity-relationship models
6. **Gantt Chart** - Project timelines and task scheduling
7. **Pie Chart** - Data distribution visualization
8. **Bar Chart** - Comparative data representation
9. **Git Graph** - Version control flow
10. **User Journey** - Customer experience mapping
11. **Mindmap** - Hierarchical topic organization
12. **Timeline** - Temporal sequence visualization
13. **Quadrant Chart** - Two-axis data positioning

## Integration with Pytest

To integrate with pytest, create a wrapper test:

```python
# tests/llmmermaidtest/test_llm_mermaid_generation.py
import subprocess
import pytest

@pytest.mark.slow
def test_generate_25_diagrams():
    """Test LLM-based Mermaid diagram generation (25 test cases)"""
    result = subprocess.run(
        ["python", "validate_all_25_mermaid.py", "25"],
        cwd="backend/tests/llmmermaidtest"
    )
    assert result.returncode == 0, "Mermaid validation failed"

@pytest.mark.slow
def test_generate_50_diagrams():
    """Test LLM-based Mermaid diagram generation (50 test cases)"""
    result = subprocess.run(
        ["python", "validate_all_25_mermaid.py", "50"],
        cwd="backend/tests/llmmermaidtest"
    )
    assert result.returncode == 0, "Mermaid validation failed"
```

Then run with pytest:

```bash
# Run Mermaid tests with slow tests
pytest backend/tests/llmmermaidtest/ -m slow -v

# Run only the Mermaid tests
pytest backend/tests/llmmermaidtest/test_llm_mermaid_generation.py -v
```

## Performance Notes

### First Run (Test25)
- Duration: 5-15 minutes (depends on LLM speed)
- Reason: All 25 diagrams need to be generated
- Output: ~200+ MB of SVG files

### Subsequent Runs (Test25)
- Duration: 30-60 seconds
- Reason: Code is cached in history/
- Output: Validation results only

### Test50
- Duration: 10-30 minutes (first run)
- Duration: 1-2 minutes (cached)

## Future Enhancements

- [ ] Cache rendered SVGs to avoid re-rendering
- [ ] Add incremental validation (only new tests)
- [ ] Parallel processing for multiple test cases
- [ ] Integration with CI/CD pipelines
- [ ] Visual comparison of rendered diagrams
- [ ] Retry mechanism for failed API calls
- [ ] Support for custom diagram styles
- [ ] Automated diagram quality scoring

## Author Notes

This test suite validates the backend's LLM integration for Mermaid diagram generation. Use it to:
- Verify diagram generation quality
- Identify LLM prompt issues
- Monitor Mermaid compatibility
- Track rendering performance
- Compare Mermaid vs D2 generation capabilities

## Related Documentation

- [D2 Test Suite](../llmd2test/README.md) - Similar tests for D2 diagrams
- [Diagram Provider Tests](../providers/README.md) - Pytest-based rendering tests
- [Mermaid Documentation](https://mermaid.js.org)
- [Backend API Docs](../../app/api/v1/README.md)

---

**Generated**: November 2, 2025
**Status**: Ready for Testing
