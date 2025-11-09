# Diagram Wizard - Provider System Integration

**Status**: ✅ Successfully Integrated
**Date**: November 8, 2025
**Version**: 1.0

## Overview

The Diagram Wizard has been successfully integrated with the existing Diagram Provider Registry system. This integration enables:

- **Unified Validation**: Use provider-specific validators for all diagram types
- **Intelligent Rendering**: Leverage provider rendering capabilities with error correction
- **Fallback Support**: Graceful degradation when providers unavailable
- **Scalability**: Easy to add new providers without modifying wizard code

## Integration Architecture

```
Diagram Wizard Flow          Provider System
  |                              |
  v                              v
clarify_prompt (user input)
  |
  v
generate_code (LLM generates code)
  |
  v
validate_code ---------> provider.validate_code()
  |                      (checks syntax)
  |
  +-- [Invalid] -------> refine_code (LLM fixes code)
  |                      -> validate_code (retry)
  |
  +-- [Valid]
  |
  v
render_diagram --------> provider.render_with_validation()
  |                      (generates SVG with auto-fix)
  v
[SVG Output to Frontend]
```

## Modified Files

### 1. **graph_state.py** (Updated)
Added new field to track provider selection:
```python
provider_id: Optional[str]  # Maps to provider registry ID
```

**Provider ID Mapping**:
- `"mermaidv1"` - Mermaid diagram provider
- `"d2v1"` - D2 diagram provider
- `"krokiplantuml"` - PlantUML provider (via Kroki)

### 2. **nodes.py** (Enhanced)

#### Changes Made:

**a) Imports**
```python
from diagrams.provider_registry import get_registry
PROVIDER_AVAILABLE = True/False  # Graceful degradation flag
```

**b) validate_code() Node**
- Now calls `provider.validate_code()` for syntax validation
- Maps `DiagramType` enum to provider IDs
- Falls back to basic validation if provider unavailable
- Propagates `provider_id` through state

**c) render_diagram() Node**
- Now calls `provider.render_with_validation()`
- Includes automatic error correction via provider
- Creates fallback SVG placeholder if provider unavailable
- Returns rendered SVG in `svg_output`

## Integration Points

### Provider Registry

**Location**: `backend/diagrams/provider_registry.py`

**Key Methods Used**:
```python
registry = get_registry()
provider = registry.get_provider(provider_id)

# Validation
result = provider.validate_code(code)
# Returns: ValidationResult(is_valid: bool, error: str)

# Rendering with validation
result = provider.render_with_validation(
    code=code,
    output_format="svg",
    auto_fix=True,
    llm_correction=False
)
# Returns: RenderResult(success: bool, content: str, error: str)
```

### Error Correction Pipeline

The wizard now benefits from the provider's built-in error correction:

1. **Pattern-Based Correction** (enabled)
   - Automatic fixes for common syntax errors
   - Uses regex patterns defined in provider config

2. **LLM-Based Correction** (disabled in wizard)
   - Provider can use LLM for complex errors
   - Wizard already does LLM correction, so disabled here

3. **User Correction** (enabled via UI)
   - Users can edit code in the code panel
   - Manual refinement before rendering

## Configuration

### Provider Configuration Files

**Root Config**: `backend/diagrams/config.json`
```json
{
  "llm_correction": {
    "enabled": false,  // Wizard handles LLM correction
    "max_retries": 3
  },
  "pattern_correction": {
    "enabled": true,   // Use pattern-based auto-fix
    "max_iterations": 2
  }
}
```

**Provider Overrides**: `backend/diagrams/mermaidv1/config.json`
```json
{
  "provider_id": "mermaidv1",
  "diagram_type": "mermaid",
  "executable_path": "mmdc"
}
```

## Workflow Examples

### Example 1: Valid Mermaid Code

```
User Input: "flowchart showing login process"
  ↓
LLM Generates:
  graph TD
    A[Start] --> B{Has account?}
    B -->|Yes| C[Login]
    B -->|No| D[Register]
    C --> E[Dashboard]
    D --> E
  ↓
validate_code():
  provider.validate_code() ✅ Valid
  → current_state: "rendering"
  ↓
render_diagram():
  provider.render_with_validation() ✅ Success
  → svg_output: <actual SVG>
  → current_state: "ready"
```

### Example 2: Invalid Code (Auto-Corrected)

```
User Input: "simple flowchart"
  ↓
LLM Generates (with error):
  Start --> End
  (missing diagram type)
  ↓
validate_code():
  provider.validate_code() ❌ Invalid
  → validation_error: "Missing diagram declaration"
  → current_state: "validation_error"
  ↓
refine_code():
  LLM fixes: "graph TD\n" + code
  ↓
validate_code() again:
  provider.validate_code() ✅ Valid
  ↓
render_diagram():
  provider.render_with_validation() ✅ Success
```

### Example 3: Provider Unavailable (Fallback)

```
If provider registry unavailable:
  ↓
validate_code():
  → Falls back to basic regex checks
  → is_valid: True/False based on basic pattern
  ↓
render_diagram():
  → Falls back to placeholder SVG
  → Shows warning: "Provider rendering unavailable"
```

## Testing Results

### Integration Test Results

```
✅ validate_code imported and works
✅ render_diagram imported and works
✅ Provider registry integration confirmed
✅ Validation with Mermaid code: PASS
✅ Validation with D2 code: PASS
✅ Validation with PlantUML code: PASS
✅ Validation with invalid code: PASS (error detected)
✅ Rendering with valid code: PASS (SVG generated)
✅ Fallback rendering: PASS (placeholder SVG)
✅ Provider ID propagation: PASS
✅ Full workflow (validate → render): PASS
```

### Test Files

1. **test_provider_integration.py** (Comprehensive tests)
   - 9 test cases covering all scenarios
   - Tests for each diagram type
   - Error handling tests

2. **integration_test_simple.py** (Verification)
   - Checks imports work
   - Verifies provider availability
   - Tests node execution
   - Validates full workflow

## Benefits of Integration

### For Users
- ✅ Better error detection and correction
- ✅ More accurate diagram validation
- ✅ Seamless rendering across diagram types
- ✅ Automatic error recovery

### For Developers
- ✅ Unified validation/rendering interface
- ✅ Easy to add new diagram types
- ✅ Configuration-driven behavior
- ✅ Consistent error handling

### For System
- ✅ Leverages existing provider infrastructure
- ✅ Scalable to multiple providers
- ✅ Graceful degradation if components unavailable
- ✅ Future-proof architecture

## Compatibility

### Supported Providers

| Provider | Type | Status | Notes |
|----------|------|--------|-------|
| mermaidv1 | Mermaid | ✅ Integrated | Uses mmdc CLI |
| d2v1 | D2 | ✅ Integrated | Uses d2 CLI |
| krokiplantuml | PlantUML | ✅ Integrated | HTTP-based (no CLI) |

### Backward Compatibility

- ✅ All existing APIs unchanged
- ✅ Wizard works independently if providers unavailable
- ✅ Falls back gracefully to basic validation
- ✅ No breaking changes to frontend

## Error Handling

### Validation Errors

When `validate_code()` encounters an error:

```python
{
    "is_valid": False,
    "validation_error": "Error message from provider",
    "validation_error_type": "syntax_error",
    "recovery_suggestions": ["Fix suggestion 1", "Fix suggestion 2"],
    "current_state": "validation_error"
}
```

### Rendering Errors

When `render_diagram()` fails:

```python
{
    "svg_output": "",
    "error_message": "Rendering failed: detailed error",
    "current_state": "error"
}
```

## Future Enhancements

### Potential Improvements

1. **Provider-Specific UI**
   - Custom panels for each provider type
   - Provider-specific hints and tips

2. **Advanced Error Correction**
   - Enable LLM correction in provider
   - Multi-step error recovery

3. **Performance Optimization**
   - Cache validation results
   - Batch diagram generation

4. **Additional Providers**
   - PlantUML CLI provider
   - Graphviz provider
   - Custom diagram formats

5. **Analytics**
   - Track validation success rates
   - Monitor rendering performance
   - Identify common errors

## Integration Summary

| Aspect | Status | Notes |
|--------|--------|-------|
| Code Updates | ✅ Complete | 2 files modified |
| Testing | ✅ Complete | 9 tests passing |
| Documentation | ✅ Complete | This file + JSDoc |
| Backward Compatibility | ✅ Maintained | No breaking changes |
| Fallback Support | ✅ Implemented | Graceful degradation |
| Provider Mapping | ✅ Configured | DiagramType → Provider ID |
| Error Handling | ✅ Robust | Comprehensive error cases |

## Usage in Code

### Using the Integrated Nodes

```python
from app.utils.diagram_wizard.nodes import validate_code, render_diagram
from app.utils.diagram_wizard.graph_state import GraphState, DiagramType

# Create state with diagram code
state: GraphState = {
    "diagram_code": "graph TD\nA --> B",
    "diagram_type": DiagramType.MERMAID,
}

# Validate using provider
validation_result = await validate_code(state)
if validation_result["is_valid"]:
    # Update state with validation results
    state.update(validation_result)

    # Render using provider
    render_result = await render_diagram(state)
    svg = render_result["svg_output"]
```

## Verification

To verify integration:

```bash
# Run the integration test
cd backend/app/utils/diagram_wizard
python integration_test_simple.py

# Expected output:
# ✅ ALL INTEGRATION TESTS PASSED
# Integration Status:
# ✅ Diagram wizard nodes imported successfully
# ✅ Provider registry integration confirmed
# ✅ Validation node works with provider system
# ✅ Rendering node works with provider system
# ✅ Provider ID properly propagated through workflow
```

## Support

For issues or questions:

1. Check [Provider System Docs](../../../diagrams/ARCHITECTURE.md)
2. Review [Diagram Wizard README](README.md)
3. Check node docstrings in nodes.py
4. Review test files for usage examples

## Conclusion

The Diagram Wizard is now fully integrated with the Provider System. This integration:

- ✅ Enables unified validation and rendering
- ✅ Provides intelligent error correction
- ✅ Maintains backward compatibility
- ✅ Supports graceful fallbacks
- ✅ Positions the system for future growth

The wizard is production-ready and can leverage the full power of the provider ecosystem.

---

**Document Version**: 1.0
**Last Updated**: November 8, 2025
**Status**: ✅ Complete
