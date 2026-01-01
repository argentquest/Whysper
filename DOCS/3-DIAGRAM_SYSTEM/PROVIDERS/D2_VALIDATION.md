# D2 Diagram Validation

This document describes the D2 diagram validation approach used in this project.

## Overview

We use a multi-layered approach to validate D2 diagrams:

1. **Primary: D2 CLI Validation** - Uses the official D2 executable for reliable validation
2. **Fallback: Pattern-based Validation** - Custom regex patterns when CLI is not available
3. **Auto-correction** - Automatically fixes common syntax errors

## Components

### 1. D2 CLI Validator (`d2_cli_validator.py`)

The most reliable way to validate D2 syntax is using the official D2 CLI tool written in Go.

**Features:**
- Executes the actual D2 parser for 100% accurate validation
- Returns detailed error messages from the D2 compiler
- Includes timeout protection to prevent hanging
- Attempts to fix common issues after validation failures

**Installation:**
```bash
# Install from https://d2lang.com/
# Or using package managers:
# macOS: brew install d2
# Windows: scoop install d2
# Linux: See installation guide at d2lang.com
```

### 2. Pattern-based Validator (`d2_syntax_fixer.py`)

Custom validator that fixes common D2 syntax issues:

**Common Issues Fixed:**
- Unterminated connection labels (e.g., `"Uses` without closing quote)
- JSON-style object syntax
- Nested style objects
- Invalid arrow syntax
- Missing direction declarations
- Unmatched braces
- Invalid properties

### 3. Integration Points

**Diagram Validators (`diagram_validators.py`)**
- Coordinates between CLI and pattern-based validation
- Prefers CLI when available, falls back to patterns otherwise

**Rendering API (`rendering_api.py`)**
- Applies validation before rendering
- Uses corrected code for successful diagram generation

## Usage

### Basic Validation

```python
from mvp_diagram_generator.d2_cli_validator import validate_d2_with_cli

is_valid, message = validate_d2_with_cli(d2_code)
```

### Validation with Auto-fix

```python
from mvp_diagram_generator.d2_cli_validator import validate_and_fix_d2_with_cli

is_valid, fixed_code, message = validate_and_fix_d2_with_cli(
    d2_code, max_attempts=3
)
```

### Check CLI Availability

```python
from mvp_diagram_generator.d2_cli_validator import is_d2_cli_available

if is_d2_cli_available():
    print("D2 CLI is available for validation")
else:
    print("Using pattern-based validation")
```

## Testing

Run the test scripts to verify validation works:

```bash
# Test CLI validation
python backend/test_d2_cli_validation.py

# Test pattern-based fixes
python backend/test_d2_connection_label_fix.py

# Comprehensive test
python backend/test_d2_comprehensive_fix.py
```

## Error Handling

The validation system handles:

1. **Missing D2 CLI** - Gracefully falls back to pattern validation
2. **Timeouts** - 10-second timeout prevents hanging
3. **Temporary files** - Automatic cleanup of temp files
4. **Multiple attempts** - Tries to fix issues up to 3 times

## Common D2 Syntax Errors

### 1. Unterminated Strings
```
# Invalid
customer -> payment_system: "Uses
payment_system -> bank_api: Processes payments via

# Fixed
customer -> payment_system: "Uses"
payment_system -> bank_api: "Processes payments via"
```

### 2. JSON-style Objects
```
# Invalid
server: {
  shape: rectangle,
  label: "Web Server"
}

# Fixed
server: "Web Server" {
  shape: rectangle
}
```

### 3. Nested Styles
```
# Invalid
server: "Server" {
  style: {
    fill: "#ff0000",
    stroke: "#000000"
  }
}

# Fixed
server: "Server" {
  style.fill: "#ff0000"
  style.stroke: "#000000"
}
```

## Best Practices

1. **Install D2 CLI** for most reliable validation
2. **Test validation** with provided test scripts
3. **Check logs** for validation details and corrections
4. **Handle fallbacks** when D2 CLI is not available

## Troubleshooting

### D2 CLI Not Found
```
Error: D2 executable not found. Please install D2 CLI.
```
**Solution:** Install D2 from https://d2lang.com/

### Validation Timeout
```
D2 validation timed out (10s limit)
```
**Solution:** Check for infinite loops or complex diagrams

### Temporary File Issues
```
Failed to clean up temp file...
```
**Solution:** Check file permissions in temp directory