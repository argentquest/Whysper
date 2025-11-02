# LLM D2 Diagram Generation and Validation Tests

Generate D2 diagrams using LLM prompts and validate them with the D2 CLI.

## Overview

This test suite:
- Loads test cases from JSON files (test25.json, test50.json)
- Generates D2 diagram code using LLM via the backend API
- Validates generated D2 code using the D2 CLI
- Renders valid diagrams to SVG files
- Reports validation results and errors

## Directory Structure

```
llmd2test/
├── __init__.py                          # Package initialization
├── README.md                            # This file
├── validate_all_25_d2.py               # Main validation script
├── test25.json                         # 25 test cases for D2 generation
├── test50.json                         # 50 test cases for D2 generation
├── history/                            # Historical generated diagram code
├── test_results_25/                    # Results directory for test25
│   ├── errors/                         # Error details and logs
│   │   ├── test_001_error.txt
│   │   ├── test_002_error.txt
│   │   └── validation_results.json     # Summary of all results
│   └── svg/                            # Rendered SVG diagrams
│       ├── test_001_Business_Process.svg
│       ├── test_002_System_Architecture.svg
│       └── ...
└── test_results_50/                    # Results directory for test50
    ├── errors/
    └── svg/
```

## Prerequisites

### Required Software

1. **D2 CLI** - For validating and rendering D2 diagrams
   ```bash
   # macOS
   brew install d2

   # Linux
   curl -fsSL https://d2lang.com/install.sh | sh -s --

   # Windows (via choco)
   choco install d2
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
# Install D2 CLI
d2 --version

# Verify backend is running
curl http://localhost:8003/api/v1/system/health
```

## Usage

### Run Test Validation

Run the validation script to generate and validate D2 diagrams:

```bash
# Test with 25 test cases (default)
python validate_all_25_d2.py 25
# or
python validate_all_25_d2.py

# Test with 50 test cases
python validate_all_25_d2.py 50
```

### Script Output

The script will:

1. **Check D2 CLI** - Verify D2 is installed and get version
2. **Load Test Cases** - Read test cases from JSON file
3. **Process Each Test**:
   - Check for existing generated code in history
   - Generate D2 code if not cached (using backend LLM)
   - Validate D2 syntax using D2 CLI
   - Render to SVG if valid
4. **Generate Report** - Create summary and error files

### Expected Output

```
D2 CLI Validator - Processing test25 tests
============================================================

[D2 CLI] Version: 0.7.1

Loading tests from: .../test25.json

Processing 25 tests...

============================================================
Test 1: Business Process Flow
============================================================
  Generating code...
  Generated code (450 chars)
  Validating D2 code...
  [PASS] Validation successful
  Rendering SVG...
  [SVG] Saved to: test_001_Business_Process_Flow.svg

...

============================================================
VALIDATION SUMMARY
============================================================

Total tests: 25
Tests with diagram code: 25
Tests generated: 18
Tests valid: 23
Tests invalid: 2

Success rate: 92.0%

Detailed results saved to: .../test_results_25/errors/validation_results.json

Failed tests (2):
  - Test 5: Complex State Machine
    Error file: test_005_error.txt

============================================================
D2 VALIDATION COMPLETE
============================================================
```

## Test Case Format

Test cases are defined in JSON files with the following structure:

```json
{
  "d2_capability_tests": [
    {
      "id": 1,
      "name": "Business Process Flow",
      "category": "Process Flow",
      "complexity": "beginner",
      "description": "Create a business process flow diagram showing order processing steps...",
      "key_features": ["shapes", "connections", "labels"],
      "expected_elements": 5
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
Test Name: Complex State Machine
Description: Create a complex state machine...
Generated: true

Validation Error:
D2 Syntax Error:
  err: failed to compile...

Diagram Code:
[Generated D2 code that failed]
```

### SVG Files

Valid diagrams are rendered to SVG:

```
test_001_Business_Process_Flow.svg (viewable in any browser)
test_002_System_Architecture.svg
test_003_Entity_Relationship.svg
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
    "tests_generated": 18,
    "tests_valid": 23,
    "tests_invalid": 2,
    "success_rate": 92.0
  },
  "results": [
    {
      "test_id": 1,
      "test_name": "Business Process Flow",
      "has_code": true,
      "diagram_code": "...",
      "is_valid": true,
      "validation_error": "",
      "generated": true,
      "error_file": "",
      "svg_file": "test_001_Business_Process_Flow.svg"
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
  "prompt": "Create a business process flow...",
  "diagram_type": "d2"
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

### D2 CLI Not Found

```
[ERROR] D2 CLI not available: [Errno 2] No such file or directory: 'd2'
```

**Solution:** Install D2 CLI and ensure it's in your PATH

```bash
d2 --version
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
python validate_all_25_d2.py 25
```

### No History Files Found

If script is generating all diagrams (slow), results are being cached in the `history/` directory for future runs.

## Script Configuration

### Timeouts

- **D2 Validation**: 120 seconds (line 42)
- **D2 Rendering**: 120 seconds (line 92)
- **API Generation**: 60 seconds (line 133)

Adjust these in `validate_all_25_d2.py` if needed.

### Output Directories

Script automatically creates:
- `test_results_25/errors/` - For test25 error files
- `test_results_25/svg/` - For test25 rendered diagrams
- `test_results_50/errors/` - For test50 error files
- `test_results_50/svg/` - For test50 rendered diagrams

## Integration with Pytest

To integrate with pytest, create a wrapper test:

```python
# tests/llmd2test/test_llm_d2_generation.py
import subprocess
import pytest

@pytest.mark.slow
def test_generate_25_diagrams():
    """Test LLM-based D2 diagram generation (25 test cases)"""
    result = subprocess.run(
        ["python", "validate_all_25_d2.py", "25"],
        cwd="backend/tests/llmd2test"
    )
    assert result.returncode == 0, "D2 validation failed"

@pytest.mark.slow
def test_generate_50_diagrams():
    """Test LLM-based D2 diagram generation (50 test cases)"""
    result = subprocess.run(
        ["python", "validate_all_25_d2.py", "50"],
        cwd="backend/tests/llmd2test"
    )
    assert result.returncode == 0, "D2 validation failed"
```

Then run with pytest:

```bash
# Run LLM tests with slow tests
pytest backend/tests/llmd2test/ -m slow -v

# Run only the LLM tests
pytest backend/tests/llmd2test/test_llm_d2_generation.py -v
```

## Performance Notes

### First Run (Test25)
- Duration: 5-15 minutes (depends on LLM speed)
- Reason: All 25 diagrams need to be generated
- Output: ~150 MB of SVG files

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
- [ ] Support for other diagram types (Mermaid, PlantUML)

## Author Notes

This test suite validates the backend's LLM integration for diagram generation. Use it to:
- Verify diagram generation quality
- Identify LLM prompt issues
- Monitor D2 compatibility
- Track rendering performance

## Related Documentation

- [Diagram Provider Tests](../providers/README.md) - Pytest-based rendering tests
- [D2 Documentation](https://d2lang.com/tour/intro)
- [Backend API Docs](../../app/api/v1/README.md)

---

**Generated**: November 2, 2025
**Status**: Production Ready
