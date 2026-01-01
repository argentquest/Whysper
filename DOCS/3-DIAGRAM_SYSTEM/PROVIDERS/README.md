# Diagram Provider Architecture

New modular architecture for diagram rendering with hierarchical configuration, LLM-based correction, and multi-provider support.

## Status: ✅ Configuration System Implemented

This runs in **parallel** with existing mermaid/d2 services - no breaking changes.

## Architecture Overview

### Folder Structure

```
backend/diagrams/
├── config.json                  # DEFAULT settings for all providers
├── base_diagram.py              # Abstract base class
├── provider_config.py           # Configuration loading with deep merge
├── models.py                    # Shared data models
├── __init__.py
│
├── mermaidv1/
│   ├── config.json              # OVERRIDES only
│   ├── __init__.py
│   └── mermaid_renderer.py      # Implementation (TODO)
│
└── d2v1/
    ├── config.json              # OVERRIDES only
    ├── __init__.py
    └── d2_renderer.py           # Implementation (TODO)
```

## Configuration System

### Hierarchical Configuration

1. **Root config.json** (`/diagrams/config.json`)
   - Defines DEFAULT settings for all providers
   - Common settings: LLM retries, timeouts, correction strategy, etc.

2. **Provider config.json** (e.g., `/diagrams/mermaidv1/config.json`)
   - Contains only OVERRIDES of specific settings
   - Uses deep merge - can override nested fields
   - Plus provider identity and custom settings

### Example: Override System

**Root config says:**
```json
{
  "defaults": {
    "llm_correction": {
      "max_retries": 3,
      "temperature": 0.3,
      "max_tokens": 4000
    }
  }
}
```

**mermaidv1/config.json says:**
```json
{
  "provider_id": "mermaidv1",
  "overrides": {
    "llm_correction": {
      "max_retries": 5,
      "temperature": 0.2
    }
  }
}
```

**Final merged config for mermaidv1:**
- `llm_correction.max_retries` = **5** (overridden)
- `llm_correction.temperature` = **0.2** (overridden)
- `llm_correction.max_tokens` = **4000** (from default)

## Test Structure

Tests are organized by provider in the `tests/` folder:

```
backend/diagrams/tests/
├── __init__.py
├── test_config.py                    # Overall system tests
├── mermaidv1/
│   ├── __init__.py
│   └── test_mermaid_config.py        # mermaidv1-specific tests
└── d2v1/
    ├── __init__.py
    └── test_d2_config.py             # d2v1-specific tests
```

### Run Tests

```bash
# Run all config tests
cd backend/diagrams/tests
py test_config.py

# Run provider-specific tests
cd backend/diagrams/tests/mermaidv1
py test_mermaid_config.py

cd backend/diagrams/tests/d2v1
py test_d2_config.py
```

## Test Results

✅ Root config loading
✅ Provider config loading with overrides
✅ Deep merge functionality
✅ mermaidv1: 5 LLM retries, 0.2 temperature, 180s validation timeout
✅ d2v1: 8 LLM retries, 6000 max tokens, batch enabled

### Current Test Output

```
mermaidv1 Overrides:
  llm_correction.max_retries: 3 -> 5 [OVERRIDDEN]
  llm_correction.temperature: 0.3 -> 0.2 [OVERRIDDEN]
  validation.timeout_seconds: 120 -> 180 [OVERRIDDEN]

d2v1 Overrides:
  llm_correction.max_retries: 3 -> 8 [OVERRIDDEN]
  llm_correction.max_tokens: 4000 -> 6000 [OVERRIDDEN]
  batch.enabled: False -> True [OVERRIDDEN]
  batch.max_items: 50 -> 100 [OVERRIDDEN]
```

## Configuration Options

### Default Settings (all providers)

```json
{
  "llm_correction": {
    "enabled": true,
    "max_retries": 3,              // 0-10 LLM correction attempts
    "temperature": 0.3,            // 0.0-2.0
    "max_tokens": 4000,            // 100-32000
    "model_override": null
  },

  "pattern_correction": {
    "enabled": true                // Pattern-based auto-fix
  },

  "correction_strategy": "pattern_then_llm",  // or "none", "pattern_only", "llm_only", "user_only"

  "user_correction": {
    "enabled": true,
    "session_timeout_seconds": 300
  },

  "validation": {
    "timeout_seconds": 120,
    "max_code_length_bytes": 512000
  },

  "rendering": {
    "timeout_seconds": 120,
    "default_output_format": "svg"
  },

  "batch": {
    "enabled": false,
    "max_items": 50
  }
}
```

### Provider-Specific Settings

Each provider can:
- Override any default setting (deep merge)
- Define custom settings (executable paths, themes, etc.)
- Specify diagram type and output formats
- Set capabilities (VALIDATE, RENDER_SVG, AUTO_FIX, etc.)

## Next Steps

### TODO: Implementation

1. **LLM Correction Service** - Integrate with existing AI processor
2. **Correction Session Management** - Track user correction attempts
3. **Provider Registry** - Auto-discover and register providers
4. **mermaidv1 Implementation** - Migrate existing mermaid_render_service
5. **d2v1 Implementation** - Migrate existing d2_render_service
6. **Unified API Endpoints** - Create `/api/v1/diagrams/*` endpoints
7. **Frontend Integration** - Unified diagram rendering component

### TODO: Features

- [ ] LLM-based error correction with retry limits
- [ ] User correction workflow (manual edit + resubmit)
- [ ] Correction session tracking
- [ ] Batch rendering support
- [ ] Multiple providers for same diagram type
- [ ] Runtime config reload
- [ ] Metrics and monitoring

## Benefits

✅ **DRY Configuration** - Common settings defined once
✅ **Easy to Extend** - Add new provider = new folder + config
✅ **Minimal Configs** - Providers only specify differences
✅ **Deep Override** - Partial overrides (just max_retries, not whole llm_correction)
✅ **Type Safe** - Pydantic validation
✅ **Self-Documenting** - Root config shows all options
✅ **Backward Compatible** - Existing services unchanged

## Architecture Principles

1. **Provider = Folder Name** - `mermaidv1/` creates provider "mermaidv1"
2. **Config Inheritance** - Providers inherit from root, override selectively
3. **No Breaking Changes** - New system runs alongside existing code
4. **Gradual Migration** - Move providers one at a time
5. **Future-Proof** - Easy to add mermaidv2, d2-playwright, etc.
