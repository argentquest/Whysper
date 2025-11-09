# How to Add a New Diagram Provider

This guide explains how to add a new diagram type (e.g., PlantUML, Graphviz, Mermaid v2) to the provider system.

## Table of Contents
- [Quick Start](#quick-start)
- [Provider Architecture](#provider-architecture)
- [Step-by-Step Guide](#step-by-step-guide)
- [Testing Your Provider](#testing-your-provider)
- [Configuration Options](#configuration-options)
- [Pattern-Based Auto-Fix](#pattern-based-auto-fix)
- [LLM Correction Rules](#llm-correction-rules)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

**TL;DR**: Copy `d2v1/` folder, rename it, update 4 files, write tests, done!

```bash
# 1. Copy an existing provider as template
cd backend/diagrams
cp -r d2v1/ plantumlv1/

# 2. Edit these 4 files:
#    - plantumlv1/config.json (provider metadata)
#    - plantumlv1/plantuml_renderer.py (implementation)
#    - plantumlv1/README.md (documentation)
#    - tests/test_plantumlv1_provider.py (unit tests)

# 3. Run tests
pytest backend/diagrams/tests/test_plantumlv1_provider.py -v

# 4. Your provider is auto-discovered!
#    No manual registration needed - the ProviderRegistry finds it automatically
```

---

## Provider Architecture

### What is a Provider?

A provider is a **self-contained module** that knows how to:
1. **Validate** diagram code (check syntax)
2. **Render** diagrams to output formats (SVG, PNG, etc.)
3. **Auto-fix** common errors (pattern-based and LLM-based)
4. **Report** capabilities and metadata

### Provider Structure

Each provider is a **folder** in `backend/diagrams/` with this structure:

```
backend/diagrams/
├── your_provider_name/          # Folder name = provider_id
│   ├── config.json              # REQUIRED: Provider configuration
│   ├── {name}_renderer.py       # REQUIRED: Implementation
│   └── README.md                # RECOMMENDED: Usage docs
├── base_diagram.py              # Base class you inherit from
├── provider_registry.py         # Auto-discovers your provider
└── tests/
    └── test_your_provider.py    # Unit tests
```

### Auto-Discovery

**You don't manually register providers!** The `ProviderRegistry` automatically:
1. Scans `backend/diagrams/` for folders
2. Looks for `config.json` in each folder
3. Imports the renderer module
4. Instantiates the provider class
5. Makes it available via `registry.get_provider("your_provider_id")`

**This means**: Just create the folder with correct structure, and it works!

---

## Step-by-Step Guide

### Step 1: Create Provider Folder

Choose a descriptive name with version number (allows multiple versions):

```bash
cd backend/diagrams
mkdir plantumlv1  # Example: provider_id = "plantumlv1"
```

**Naming Convention**: `{diagram_type}v{version_number}`
- Good: `plantumlv1`, `mermaidv2`, `graphvizv1`
- Bad: `plantuml`, `my_provider`, `diagram_renderer`

### Step 2: Create config.json

**File**: `plantumlv1/config.json`

```json
{
  "provider_id": "plantumlv1",
  "provider_name": "PlantUML CLI Renderer v1",
  "diagram_type": "plantuml",
  "description": "Renders PlantUML diagrams using official CLI",
  "version": "1.0.0",
  "supported_output_formats": ["plantuml", "svg", "png"],

  "overrides": {
    "pattern_correction": {
      "enabled": true,
      "max_attempts": 3
    },
    "llm_correction": {
      "enabled": true,
      "max_retries": 8,
      "temperature": 0.1,
      "max_tokens": 6000
    },
    "batch": {
      "enabled": true,
      "max_items": 100
    }
  },

  "custom": {
    "executable_path": null,
    "jar_path": null,
    "java_options": "-Djava.awt.headless=true"
  }
}
```

**Config Fields Explained:**

| Field | Required | Description |
|-------|----------|-------------|
| `provider_id` | ✅ Yes | Must match folder name |
| `provider_name` | ✅ Yes | Human-readable name shown in UI |
| `diagram_type` | ✅ Yes | Primary diagram type (e.g., "plantuml") |
| `description` | ⚠️ Recommended | Brief description of provider |
| `version` | ⚠️ Recommended | Provider version (semantic versioning) |
| `supported_output_formats` | ✅ Yes | Array of formats: ["svg", "png", etc.] |
| `overrides` | ⚠️ Optional | Override root config settings |
| `custom` | ⚠️ Optional | Provider-specific settings |

**Note**: The `custom` section is passed to your provider's `__init__()` method via `self.config.custom`.

### Step 3: Implement the Provider Class

**File**: `plantumlv1/plantuml_renderer.py`

```python
"""
PlantUML v1 Provider Implementation
"""

from pathlib import Path
from typing import Optional, List, Tuple
import subprocess
import tempfile
import os
import logging

from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import (
    ProviderCapability,
    ValidationResult,
    RenderResult
)

logger = logging.getLogger(__name__)


# =====================================================================
# HELPER FUNCTIONS (Optional but recommended)
# =====================================================================

def validate_plantuml_with_cli(code: str, jar_path: str) -> Tuple[bool, str]:
    """
    Validate PlantUML code by running the CLI.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.puml', delete=False) as f:
        f.write(code)
        temp_path = f.name

    try:
        # Run PlantUML in check mode
        result = subprocess.run(
            ['java', '-jar', jar_path, '-checkonly', temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return (True, "PlantUML syntax is valid")
        else:
            return (False, result.stderr or result.stdout)

    except Exception as e:
        return (False, f"Validation error: {str(e)}")

    finally:
        os.unlink(temp_path)


def render_plantuml(code: str, jar_path: str, format: str = "svg") -> Tuple[bool, str, Optional[str]]:
    """
    Render PlantUML to specified format.

    Returns:
        Tuple[bool, str, Optional[str]]: (success, message, output_content)
    """
    # Implementation here...
    pass


# =====================================================================
# PROVIDER CLASS
# =====================================================================

class PlantUMLV1Provider(BaseDiagramProvider):
    """
    PlantUML CLI Provider v1

    Renders PlantUML diagrams using the official PlantUML JAR.
    """

    # ===== Required Properties =====

    @property
    def provider_id(self) -> str:
        """Must match folder name and config"""
        return "plantumlv1"

    @property
    def provider_name(self) -> str:
        return "PlantUML CLI Renderer v1"

    @property
    def diagram_type(self) -> str:
        return "plantuml"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["plantuml", "svg", "png"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.RENDER_PNG,
            ProviderCapability.AUTO_FIX,
            ProviderCapability.LLM_CORRECTION
        ]

    # ===== Initialization =====

    def __init__(self, provider_folder: Path):
        """Initialize PlantUML provider"""
        super().__init__(provider_folder)

        # Get settings from config
        custom = self.config.custom or {}

        # IMPORTANT: Use `or` to handle null values!
        self.jar_path = custom.get("jar_path") or "/usr/local/lib/plantuml.jar"
        self.java_options = custom.get("java_options") or "-Djava.awt.headless=true"

        self._cli_available = None

        self.logger.info(f"PlantUML provider using JAR: {self.jar_path}")

    # ===== Required Methods =====

    def is_available(self) -> bool:
        """Check if PlantUML CLI is available"""
        if self._cli_available is None:
            try:
                result = subprocess.run(
                    ['java', '-jar', self.jar_path, '-version'],
                    capture_output=True,
                    timeout=5
                )
                self._cli_available = (result.returncode == 0)
            except Exception:
                self._cli_available = False

        return self._cli_available

    def get_version(self) -> Optional[str]:
        """Get PlantUML version"""
        if not self.is_available():
            return None

        try:
            result = subprocess.run(
                ['java', '-jar', self.jar_path, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return "Unknown"

    def validate_code(self, code: str, **options) -> ValidationResult:
        """Validate PlantUML code"""
        if not self.is_available():
            return ValidationResult(
                is_valid=False,
                error="PlantUML CLI not available",
                code_length=len(code)
            )

        is_valid, message = validate_plantuml_with_cli(code, self.jar_path)

        return ValidationResult(
            is_valid=is_valid,
            error=None if is_valid else message,
            code_length=len(code)
        )

    def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
        """Render PlantUML diagram"""
        if not self.is_available():
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error="PlantUML CLI not available",
                    code_length=len(code)
                ),
                metadata={},
                error="PlantUML CLI not available"
            )

        # If output format is 'plantuml', return raw code
        if output_format.lower() == "plantuml":
            return RenderResult(
                success=True,
                content=code,
                output_format="plantuml",
                validation=ValidationResult(is_valid=True, code_length=len(code)),
                metadata={"provider": self.provider_id}
            )

        # Render using CLI
        success, message, content = render_plantuml(code, self.jar_path, output_format)

        if success:
            return RenderResult(
                success=True,
                content=content,
                output_format=output_format,
                validation=ValidationResult(is_valid=True, code_length=len(code)),
                metadata={
                    "provider": self.provider_id,
                    "output_size_bytes": len(content) if content else 0
                }
            )
        else:
            return RenderResult(
                success=False,
                content=None,
                output_format=output_format,
                validation=ValidationResult(
                    is_valid=False,
                    error=message,
                    code_length=len(code)
                ),
                metadata={"provider": self.provider_id},
                error=message
            )

    # ===== Optional: Pattern-Based Auto-Fix =====

    def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
        """
        Attempt pattern-based auto-fix for common PlantUML errors.

        Common fixes:
        - Add missing @startuml/@enduml tags
        - Fix arrow syntax (e.g., -> vs -->)
        - Fix common typos
        """
        corrected = code
        corrections = []

        # Fix 1: Add missing @startuml/@enduml
        if "@startuml" not in corrected:
            corrected = "@startuml\n" + corrected
            corrections.append("Added @startuml")

        if "@enduml" not in corrected:
            corrected = corrected + "\n@enduml"
            corrections.append("Added @enduml")

        # Validate the fixed code
        validation_result = self.validate_code(corrected)

        if validation_result.is_valid:
            validation_result.auto_fixed = True
            validation_result.fixed_code = corrected
            validation_result.correction_method = "pattern"
            self.logger.info(f"Pattern-based fix successful: {corrections}")

        return validation_result

    # ===== Optional: LLM Correction Rules =====

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provider-specific rules for LLM correction"""
        return """
PLANTUML-SPECIFIC RULES:
- Always start with @startuml and end with @enduml
- Use proper arrow syntax: -> for solid, --> for dashed
- Participant names must be declared before use in sequence diagrams
- Use quotes for labels with spaces: A -> B : "my label"
- Keep syntax simple and standard - avoid experimental features
- Do not use reserved keywords as identifiers
        """.strip()
```

### Step 4: Write Tests

**File**: `tests/test_plantumlv1_provider.py`

```python
"""
Unit tests for PlantUML v1 Provider
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from diagrams.plantumlv1.plantuml_renderer import PlantUMLV1Provider


@pytest.fixture
def plantuml_provider():
    """Create PlantUML provider instance"""
    provider_folder = Path(__file__).parent.parent / "plantumlv1"
    return PlantUMLV1Provider(provider_folder)


def test_provider_initialization(plantuml_provider):
    """Test provider initializes correctly"""
    assert plantuml_provider.provider_id == "plantumlv1"
    assert plantuml_provider.diagram_type == "plantuml"
    assert "svg" in plantuml_provider.supported_output_formats


def test_provider_availability(plantuml_provider):
    """Test CLI availability check"""
    is_available = plantuml_provider.is_available()
    # Skip if not installed
    if not is_available:
        pytest.skip("PlantUML CLI not available")

    # If available, should have version
    version = plantuml_provider.get_version()
    assert version is not None


def test_validate_code_valid(plantuml_provider):
    """Test validation with valid PlantUML code"""
    if not plantuml_provider.is_available():
        pytest.skip("PlantUML CLI not available")

    code = """
@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi
@enduml
    """

    result = plantuml_provider.validate_code(code)
    assert result.is_valid == True
    assert result.error is None


def test_validate_code_invalid(plantuml_provider):
    """Test validation with invalid PlantUML code"""
    if not plantuml_provider.is_available():
        pytest.skip("PlantUML CLI not available")

    code = "invalid plantuml code"

    result = plantuml_provider.validate_code(code)
    assert result.is_valid == False
    assert result.error is not None


def test_render_svg(plantuml_provider):
    """Test SVG rendering"""
    if not plantuml_provider.is_available():
        pytest.skip("PlantUML CLI not available")

    code = """
@startuml
Alice -> Bob: Hello
@enduml
    """

    result = plantuml_provider.render(code, output_format="svg")
    assert result.success == True
    assert result.content is not None
    assert "<svg" in result.content or "<?xml" in result.content


def test_auto_fix_pattern(plantuml_provider):
    """Test pattern-based auto-fix"""
    code = "Alice -> Bob: Hello"  # Missing @startuml/@enduml

    result = plantuml_provider.auto_fix_pattern_based(code, "Missing tags")

    if result.auto_fixed:
        assert "@startuml" in result.fixed_code
        assert "@enduml" in result.fixed_code


# Add 5-10 more tests covering:
# - Different diagram types (sequence, class, component, etc.)
# - Error cases
# - Edge cases
# - Configuration options
```

### Step 5: Test Your Provider

```bash
# Run your provider tests
pytest backend/diagrams/tests/test_plantumlv1_provider.py -v

# Run all provider tests
pytest backend/diagrams/tests/ -v

# Test auto-discovery
python -c "
from backend.diagrams.provider_registry import get_provider_registry
registry = get_provider_registry()
provider = registry.get_provider('plantumlv1')
print(f'Provider: {provider.provider_name}')
print(f'Available: {provider.is_available()}')
"
```

### Step 6: Document Your Provider

**File**: `plantumlv1/README.md`

```markdown
# PlantUML CLI Provider v1

Renders PlantUML diagrams using the official PlantUML JAR.

## Installation

1. Install Java Runtime Environment (JRE 8+)
2. Download PlantUML JAR from https://plantuml.com/download
3. Place JAR in `/usr/local/lib/plantuml.jar` (or configure path in config.json)

## Configuration

Edit `plantumlv1/config.json`:

```json
{
  "custom": {
    "jar_path": "/path/to/plantuml.jar",
    "java_options": "-Djava.awt.headless=true -Xmx1024m"
  }
}
```

## Supported Diagram Types

- Sequence diagrams
- Class diagrams
- Use case diagrams
- Activity diagrams
- Component diagrams
- State diagrams
- Object diagrams
- Deployment diagrams
- Timing diagrams

## Usage Examples

### Python API

```python
from backend.diagrams.provider_registry import get_provider_registry

registry = get_provider_registry()
provider = registry.get_provider("plantumlv1")

# Render diagram
result = provider.render_with_validation(
    code="""
    @startuml
    Alice -> Bob: Hello
    @enduml
    """,
    output_format="svg"
)

if result.success:
    print(result.content)
```

### REST API

```bash
curl -X POST http://localhost:8003/api/v1/diagrams/v2/render \
  -H "Content-Type: application/json" \
  -d '{
    "provider_id": "plantumlv1",
    "code": "@startuml\nAlice -> Bob: Hello\n@enduml",
    "output_format": "svg"
  }'
```

## Troubleshooting

**Error: "PlantUML CLI not available"**
- Ensure Java is installed: `java -version`
- Verify JAR path is correct in config.json
- Test JAR manually: `java -jar /path/to/plantuml.jar -version`

**Error: "OutOfMemoryError"**
- Increase Java heap size in config: `"-Xmx2048m"`
```

---

## Configuration Options

### Root Configuration

Located at `backend/diagrams/config.json` (applies to all providers):

```json
{
  "pattern_correction": {
    "enabled": true,
    "max_attempts": 3
  },
  "llm_correction": {
    "enabled": true,
    "max_retries": 5,
    "temperature": 0.1,
    "max_tokens": 4000
  },
  "batch": {
    "enabled": false,
    "max_items": 50
  },
  "correction_strategy": "pattern_first"
}
```

### Provider-Specific Overrides

Your provider's `config.json` can override root settings:

```json
{
  "overrides": {
    "llm_correction": {
      "max_retries": 8,  // Override: more retries for this provider
      "max_tokens": 6000  // Override: more tokens allowed
    }
  }
}
```

### Custom Settings

Use the `custom` section for provider-specific settings:

```json
{
  "custom": {
    "executable_path": "/custom/path/to/binary",
    "theme": "dark",
    "layout_engine": "dot",
    "any_custom_setting": "value"
  }
}
```

Access in Python:
```python
custom = self.config.custom or {}
my_setting = custom.get("any_custom_setting") or "default_value"
```

---

## Pattern-Based Auto-Fix

Pattern-based fixes are **fast, deterministic corrections** that don't require AI.

### When to Use

Use pattern-based fixes for:
- ✅ Missing declarations (e.g., `@startuml`, `direction: right`)
- ✅ Syntax normalization (e.g., fixing arrow spacing)
- ✅ Bracket/brace matching
- ✅ Quote fixing for labels
- ✅ Common typos with regex patterns

**Do NOT use for**:
- ❌ Semantic errors (requires understanding context)
- ❌ Logic restructuring
- ❌ Complex multi-line fixes

### Implementation Pattern

```python
def auto_fix_pattern_based(self, code: str, error_message: str, **options) -> ValidationResult:
    """
    Apply fast, deterministic fixes.

    Strategy:
    1. Apply regex-based corrections
    2. Validate corrected code
    3. Return ValidationResult with fixed code if successful
    """
    corrected = code
    corrections = []

    # Fix 1: Missing diagram declaration
    if not re.search(r'^@start\w+', corrected, re.MULTILINE):
        corrected = "@startuml\n" + corrected
        corrections.append("Added @startuml")

    # Fix 2: Missing end tag
    if not re.search(r'^@end\w+', corrected, re.MULTILINE):
        corrected = corrected + "\n@enduml"
        corrections.append("Added @enduml")

    # Fix 3: Arrow spacing (A->B to A -> B)
    if re.search(r'\w+->\w+', corrected):
        corrected = re.sub(r'(\w+)->(\w+)', r'\1 -> \2', corrected)
        corrections.append("Fixed arrow spacing")

    # Validate the fixed code
    validation_result = self.validate_code(corrected)

    if validation_result.is_valid:
        validation_result.auto_fixed = True
        validation_result.fixed_code = corrected
        validation_result.correction_method = "pattern"
        self.logger.info(f"Pattern fixes applied: {corrections}")
    else:
        self.logger.debug("Pattern fixes did not resolve errors")

    return validation_result
```

### Testing Pattern Fixes

```python
def test_auto_fix_missing_tags():
    """Test that missing tags are auto-added"""
    code = "Alice -> Bob: Hello"

    result = provider.auto_fix_pattern_based(code, "Missing tags")

    assert result.auto_fixed == True
    assert "@startuml" in result.fixed_code
    assert "@enduml" in result.fixed_code
    assert result.correction_method == "pattern"
```

---

## LLM Correction Rules

LLM correction uses AI to fix complex errors that pattern-based fixes can't handle.

### How It Works

1. **User submits invalid code**
2. **Pattern-based fix fails** (or disabled)
3. **LLM receives**:
   - Invalid code
   - Error message from CLI
   - Provider-specific correction rules (your `get_llm_correction_rules()`)
   - Max tokens and temperature settings
4. **LLM returns corrected code**
5. **System validates corrected code**
6. **If still invalid, retry** (up to `max_retries`)
7. **Return final result** (success or show error to user)

### Writing Effective Rules

Your `get_llm_correction_rules()` should provide:

```python
def get_llm_correction_rules(self) -> Optional[str]:
    """
    Provide provider-specific rules for LLM correction.

    Guidelines:
    - Be specific and prescriptive
    - Include common pitfalls
    - List syntax requirements
    - Mention reserved keywords to avoid
    - Keep concise (LLM has token limits)
    """
    return """
PLANTUML-SPECIFIC RULES:

REQUIRED STRUCTURE:
- MUST start with @startuml
- MUST end with @enduml
- All content must be between these tags

ARROW SYNTAX:
- Solid arrow: A -> B
- Dashed arrow: A --> B
- Bidirectional: A <-> B
- With label: A -> B : "label text"

RESERVED KEYWORDS (do not use as names):
- class, interface, abstract, enum
- start, end, if, else, endif
- Note that these are case-sensitive

COMMON ERRORS:
- Missing participant declaration in sequence diagrams
- Using -> instead of --> for dashed lines
- Forgetting quotes around labels with spaces
- Mixing tabs and spaces (use spaces only)

STYLE GUIDELINES:
- Keep diagrams simple and readable
- Avoid experimental syntax
- Use standard PlantUML features only
- Test complex diagrams at plantuml.com/online first
    """.strip()
```

### Testing LLM Correction

See `test_integration_with_llm.py` for examples of testing with running server.

---

## Troubleshooting

### "Provider not found"

**Problem**: `registry.get_provider("myproviderId")` returns None

**Solutions**:
1. Check folder name matches `provider_id` in config.json
2. Ensure config.json is valid JSON (no trailing commas!)
3. Verify renderer file exists and has correct class name
4. Check logs for import errors: `tail -f backend/logs/structured.log`

### "CLI not available"

**Problem**: `provider.is_available()` returns False

**Solutions**:
1. Install the CLI tool (d2, mmdc, plantuml, etc.)
2. Check executable path in config: `custom.executable_path`
3. Test CLI manually: `d2 --version` or `mmdc --version`
4. For Java-based tools (PlantUML): Ensure Java is installed

### "Pattern fix not working"

**Problem**: `auto_fix_pattern_based()` returns `auto_fixed=False`

**Debug**:
1. Add print statements to see what corrections are attempted
2. Check if regex patterns match your code structure
3. Validate the fixed code manually
4. Look at error message from CLI for clues

### "LLM correction failing"

**Problem**: `llm_corrected=False` after multiple retries

**Solutions**:
1. Check LLM service is running and accessible
2. Verify `get_llm_correction_rules()` is clear and specific
3. Increase `max_retries` in config (try 10-15)
4. Check LLM response for hints (logs show each attempt)
5. Simplify the diagram (LLM may struggle with very complex code)

### "Tests failing"

**Common issues**:
1. CLI not installed: Tests check `is_available()` and skip if False
2. Wrong file paths: Use `Path(__file__).parent` for relative paths
3. Timeouts: Increase subprocess timeout for slow CLIs
4. Platform differences: Use `os.path.join()` not hardcoded `/` or `\`

---

## Advanced Topics

### Batch Rendering

If your provider can optimize batch operations:

```python
def render_batch(self, codes: List[str], output_format: str = "svg", **options) -> List[RenderResult]:
    """
    Render multiple diagrams efficiently.

    Override this for providers that support batch mode.
    """
    # Example: PlantUML can render multiple files in one Java process
    results = []

    # Write all codes to temp files
    temp_files = [self._write_temp(code) for code in codes]

    # Single Java invocation for all files
    subprocess.run(['java', '-jar', self.jar_path] + temp_files)

    # Read results
    for temp_file in temp_files:
        result = self._read_output(temp_file)
        results.append(result)

    return results
```

### Custom Output Formats

Support additional formats beyond SVG/PNG:

```python
@property
def supported_output_formats(self) -> List[str]:
    return ["plantuml", "svg", "png", "pdf", "eps", "latex"]

def render(self, code: str, output_format: str = "svg", **options) -> RenderResult:
    # Map format to CLI flag
    format_flags = {
        "svg": "-tsvg",
        "png": "-tpng",
        "pdf": "-tpdf",
        "eps": "-teps",
        "latex": "-tlatex"
    }

    flag = format_flags.get(output_format.lower())
    if not flag:
        return RenderResult(success=False, error=f"Unsupported format: {output_format}")

    # Render with appropriate flag...
```

### Performance Optimization

For providers with slow CLIs:

```python
def __init__(self, provider_folder: Path):
    super().__init__(provider_folder)

    # Cache validation results for identical code
    from functools import lru_cache
    self.validate_code = lru_cache(maxsize=100)(self.validate_code)

    # Pre-warm CLI (start background process)
    if self.is_available():
        self._start_background_server()
```

---

## Examples of Real Providers

Study these for reference:

1. **D2V1** (`backend/diagrams/d2v1/`):
   - Simple CLI integration
   - Good pattern-based fixes
   - Handles null config values correctly

2. **MermaidV1** (`backend/diagrams/mermaidv1/`):
   - Complex syntax fixing
   - Error message cleaning
   - Multiple diagram types

---

## Checklist

Before submitting your provider:

- [ ] Folder name matches `provider_id` in config.json
- [ ] `config.json` has all required fields
- [ ] Renderer class inherits from `BaseDiagramProvider`
- [ ] All abstract methods implemented
- [ ] `is_available()` checks CLI installation
- [ ] `validate_code()` returns actual validation results
- [ ] `render()` generates real output (not mocks)
- [ ] Unit tests cover happy path and error cases
- [ ] README.md documents installation and usage
- [ ] Pattern-based fixes implemented (if applicable)
- [ ] LLM correction rules provided (if applicable)
- [ ] Tests pass: `pytest backend/diagrams/tests/test_your_provider.py -v`

---

## Getting Help

If you're stuck:

1. **Check logs**: `backend/logs/structured.log`
2. **Compare with existing providers**: D2V1 and MermaidV1
3. **Run tests with verbose output**: `pytest -vv -s`
4. **Ask in discussions**: Include error messages and config.json

---

## Congratulations!

You've created a new diagram provider! 🎉

Your provider is now:
- ✅ Auto-discovered by the registry
- ✅ Available via Python API
- ✅ Accessible through REST endpoints at `/api/v1/diagrams/v2/`
- ✅ Integrated with pattern-based and LLM correction
- ✅ Fully tested and documented

**Next steps:**
- Add more diagram samples to your tests
- Optimize performance for your specific CLI
- Add more pattern-based fixes based on user feedback
- Consider contributing your provider back to the project!
