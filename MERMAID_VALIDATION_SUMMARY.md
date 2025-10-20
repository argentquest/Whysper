# Mermaid Backend Validation Implementation

## Overview

I've implemented a complete backend validation and rendering system for Mermaid diagrams using the Mermaid CLI (`mmdc`), similar to how D2 diagrams are validated. This allows you to:

1. **Validate Mermaid syntax on the backend** using the official Mermaid CLI
2. **Get detailed error messages** when diagrams are invalid
3. **Automatically fix common syntax errors**
4. **Ask AI to regenerate diagrams** based on validation errors
5. **Render diagrams to SVG or PNG** on the backend

---

## New Files Created

### Backend Validation Core

1. **[backend/mvp_diagram_generator/mermaid_cli_validator.py](backend/mvp_diagram_generator/mermaid_cli_validator.py)**
   - Validates Mermaid code using mmdc CLI
   - Functions:
     - `validate_mermaid_with_cli()` - Validate syntax
     - `is_mermaid_cli_available()` - Check if mmdc is installed
     - `validate_and_fix_mermaid_with_cli()` - Validate and auto-fix
     - `validate_mermaid_and_render()` - Validate and render to SVG/PNG

2. **[backend/mvp_diagram_generator/mermaid_syntax_fixer.py](backend/mvp_diagram_generator/mermaid_syntax_fixer.py)**
   - Auto-fixes common Mermaid syntax errors
   - Fixes:
     - Missing diagram type declarations
     - Arrow syntax issues
     - Node syntax problems
     - Subgraph syntax errors
     - Sequence diagram syntax
     - Formatting issues

### Backend API

3. **[backend/app/services/mermaid_render_service.py](backend/app/services/mermaid_render_service.py)**
   - Service layer for Mermaid validation and rendering
   - Handles metadata tracking and error handling

4. **[backend/app/api/v1/endpoints/mermaid_render.py](backend/app/api/v1/endpoints/mermaid_render.py)**
   - FastAPI endpoints for Mermaid operations
   - Endpoints:
     - `POST /api/v1/mermaid/render` - Render Mermaid to SVG/PNG
     - `POST /api/v1/mermaid/validate` - Validate Mermaid code
     - `GET /api/v1/mermaid/info` - Get mmdc CLI info
     - `GET /api/v1/mermaid/health` - Health check
     - `GET /api/v1/mermaid/download/{filename}` - Download rendered diagrams

### Testing

5. **[backend/test_mermaid_validation.py](backend/test_mermaid_validation.py)**
   - Comprehensive test suite for CLI validation
   - Tests validation, auto-fix, rendering

6. **[test_mermaid_api.py](test_mermaid_api.py)**
   - API endpoint testing script
   - Tests all REST endpoints

### Updated Files

7. **[backend/mvp_diagram_generator/diagram_validators.py](backend/mvp_diagram_generator/diagram_validators.py)**
   - Updated `is_valid_mermaid_diagram()` to use CLI validation

8. **[backend/app/api/v1/api.py](backend/app/api/v1/api.py)**
   - Registered Mermaid endpoints at `/api/v1/mermaid/*`

---

## How It Works

### 1. Validation Flow

```
User submits Mermaid code
    ↓
Backend validates using mmdc CLI
    ↓
If invalid → Try auto-fix
    ↓
If still invalid → Return error to user
    ↓
User can ask AI to regenerate with error info
```

### 2. Auto-Fix Examples

**Missing Diagram Type:**
```mermaid
# Before (Invalid)
A --> B
B --> C

# After (Auto-fixed)
flowchart TD
A --> B
B --> C
```

**Bad Arrow Spacing:**
```mermaid
# Before
A-->B
B->>C

# After
A --> B
B->>C
```

---

## API Endpoints

### POST /api/v1/mermaid/validate

Validates Mermaid code without rendering.

**Request:**
```json
{
  "code": "flowchart TD\n  A --> B",
  "auto_fix": true
}
```

**Response:**
```json
{
  "is_valid": true,
  "error": null,
  "code_length": 20,
  "auto_fixed": false,
  "fixed_code": null,
  "fix_message": null
}
```

### POST /api/v1/mermaid/render

Renders Mermaid diagram to SVG or PNG.

**Request:**
```json
{
  "code": "flowchart TD\n  A --> B",
  "return_svg": true,
  "save_to_file": false,
  "output_format": "svg"
}
```

**Response:**
```json
{
  "success": true,
  "svg_content": "<svg>...</svg>",
  "validation": {
    "is_valid": true,
    "error": null,
    "code_length": 20
  },
  "metadata": {
    "render_time": 1.23,
    "timestamp": "2025-10-20T12:00:00"
  },
  "error": null
}
```

---

## Testing

### Test CLI Validation Directly

```bash
py backend/test_mermaid_validation.py
```

**Output:**
```
✅ Mermaid CLI (mmdc) is available!
✅ Valid Diagram
✅ Invalid Detection
✅ Auto-Fix
✅ Sequence Diagram
✅ Render SVG
```

### Test API Endpoints

```bash
# Make sure backend is running first
py test_mermaid_api.py
```

**Output:**
```
✅ Health Check
✅ Info Endpoint
✅ Validate Valid
✅ Validate & Auto-Fix
✅ Render SVG
✅ Error Handling
```

---

## Integration with AI Error Recovery

When a Mermaid diagram fails validation, you can now:

1. **Get the error message** from the backend validation
2. **Show it to the AI** in the conversation context
3. **Ask the AI to regenerate** the diagram with the error information

### Example Flow

```typescript
// Frontend code
const response = await fetch('/api/v1/mermaid/validate', {
  method: 'POST',
  body: JSON.stringify({ code: mermaidCode, auto_fix: true })
});

const result = await response.json();

if (!result.is_valid && !result.auto_fixed) {
  // Send error to AI
  const aiPrompt = `The Mermaid diagram has an error:\n${result.error}\n\nPlease regenerate a corrected version.`;
  // ... send to AI
}
```

---

## Dependencies

### Required
- **Mermaid CLI (`mmdc`)** - Already installed on your system (v11.9.0)
  - Install via: `npm install -g @mermaid-js/mermaid-cli`

### Python Packages
All required packages are already in your environment:
- `fastapi` - API framework
- `pydantic` - Request/response models
- `subprocess` - CLI execution

---

## Comparison: D2 vs Mermaid Validation

| Feature | D2 | Mermaid |
|---------|-------|---------|
| CLI Tool | `d2` | `mmdc` |
| Backend Validation | ✅ | ✅ |
| Auto-Fix | ✅ | ✅ |
| Render to SVG | ✅ | ✅ |
| Render to PNG | ❌ | ✅ |
| Error Messages | ✅ Detailed | ✅ Detailed |
| API Endpoints | ✅ `/api/v1/d2/*` | ✅ `/api/v1/mermaid/*` |

---

## Next Steps

You can now:

1. ✅ **Validate Mermaid diagrams** before showing them to users
2. ✅ **Get detailed error messages** for syntax issues
3. ✅ **Auto-fix common errors** automatically
4. ✅ **Ask AI to regenerate** diagrams based on validation errors
5. ✅ **Render diagrams** on the backend to SVG or PNG

### Optional Enhancements

- Add frontend integration to call `/api/v1/mermaid/validate` before rendering
- Show validation errors in the UI
- Add "Regenerate" button that sends errors to AI
- Cache rendered diagrams for performance
- Add batch validation for multiple diagrams

---

## Example Usage in Your App

When the AI generates a Mermaid diagram:

1. **Validate on backend** using `/api/v1/mermaid/validate`
2. If **invalid**: Show error message and offer to regenerate
3. If **valid**: Render using `/api/v1/mermaid/render`
4. Display the SVG to the user

This gives you the same robust error handling you have for D2 diagrams!
