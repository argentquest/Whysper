# Diagram Provider System Architecture

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Architecture Components](#architecture-components)
4. [Configuration System](#configuration-system)
5. [Provider Implementation](#provider-implementation)
6. [Rendering Pipeline](#rendering-pipeline)
7. [Error Correction Workflow](#error-correction-workflow)
8. [API Design](#api-design)
9. [Frontend Integration](#frontend-integration)
10. [Extension Points](#extension-points)

---

## Overview

The Diagram Provider System is a modular, extensible architecture for rendering and validating diagram code across multiple diagram types (Mermaid, D2, PlantUML, etc.) with intelligent error correction.

### Key Features

- **Multi-Provider Support** - Multiple rendering engines for the same diagram type
- **Hierarchical Configuration** - Root defaults with provider-specific overrides
- **LLM-Based Correction** - Intelligent error fixing using AI
- **User Correction Workflow** - Manual editing and resubmission
- **Pattern-Based Auto-Fix** - Fast, deterministic syntax corrections
- **Unified API** - Single interface for all diagram types
- **Backward Compatible** - Runs alongside existing services

### Architecture Goals

1. **Modularity** - Each provider is self-contained
2. **Extensibility** - Easy to add new providers
3. **Configuration-Driven** - Behavior controlled by JSON config
4. **Type Safety** - Full Pydantic validation
5. **No Breaking Changes** - Gradual migration path

---

## Design Principles

### 1. Provider = Folder

```
backend/diagrams/
├── mermaidv1/          # Provider ID: "mermaidv1"
├── mermaidv2/          # Provider ID: "mermaidv2"
├── d2v1/               # Provider ID: "d2v1"
└── d2-playwright/      # Provider ID: "d2-playwright"
```

Each folder represents a unique provider. The folder name IS the provider ID.

### 2. Configuration Inheritance

```
Root config.json (defaults)
    ↓
Provider config.json (overrides)
    ↓
Final merged configuration
```

Providers inherit all defaults and override selectively using deep merge.

### 3. Separation of Concerns

```
Configuration Layer     →  JSON files + Config loader
Provider Interface      →  Abstract base class
Provider Implementation →  Concrete renderer classes
Service Layer          →  Business logic + orchestration
API Layer              →  HTTP endpoints
Frontend Layer         →  UI components + API client
```

### 4. Template Method Pattern

The base class defines the rendering pipeline; providers implement specific steps:

```python
def render_with_validation(code):
    1. Validate code
    2. Pattern-based auto-fix (if needed)
    3. LLM correction (if needed)
    4. Render diagram
    5. Return result with metadata
```

---

## Architecture Components

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  ┌────────────────┐         ┌─────────────────────┐    │
│  │ DiagramRenderer│ ◄──────►│   diagramApi.ts     │    │
│  │   Component    │         │   (API Client)      │    │
│  └────────────────┘         └─────────────────────┘    │
└───────────────────────────────────┬─────────────────────┘
                                    │ HTTP
                    ┌───────────────▼──────────────────┐
                    │         API Layer                │
                    │  /api/v1/diagrams/*             │
                    │  - render                        │
                    │  - validate                      │
                    │  - correct                       │
                    └───────────────┬──────────────────┘
                                    │
                    ┌───────────────▼──────────────────┐
                    │      Provider Registry           │
                    │  - Auto-discover providers       │
                    │  - Route requests                │
                    │  - Manage lifecycle              │
                    └───────────────┬──────────────────┘
                                    │
        ┌───────────────────────────┼─────────────────────────┐
        │                           │                         │
┌───────▼────────┐      ┌──────────▼────────┐    ┌──────────▼────────┐
│  mermaidv1     │      │      d2v1          │    │   Future Provider │
│  Provider      │      │    Provider        │    │   (mermaidv2,     │
│                │      │                    │    │    plantuml, etc) │
└───────┬────────┘      └──────────┬─────────┘    └───────────────────┘
        │                          │
        │  Inherits from           │
        │                          │
        └──────────┬───────────────┘
                   │
        ┌──────────▼──────────────────────────────┐
        │    BaseDiagramProvider                  │
        │  - Abstract interface                   │
        │  - Rendering pipeline template          │
        │  - Config management                    │
        │  - Error correction orchestration       │
        └──────────┬──────────────────────────────┘
                   │
        ┌──────────┴───────────┬──────────────────┐
        │                      │                  │
┌───────▼────────┐  ┌─────────▼───────┐  ┌──────▼──────────┐
│ Config System  │  │ LLM Correction  │  │ Session Manager │
│ - Hierarchical │  │ Service         │  │ - Track attempts│
│ - Deep merge   │  │ - AI processor  │  │ - User workflow │
└────────────────┘  └─────────────────┘  └─────────────────┘
```

### File Structure

```
backend/diagrams/
│
├── config.json                    # Root configuration (defaults)
├── provider_config.py             # Configuration loader + deep merge
├── models.py                      # Shared Pydantic models
├── base_diagram.py                # Abstract base provider class
├── provider_registry.py           # Provider discovery + factory
├── llm_correction_service.py      # LLM-based error correction
├── correction_session.py          # Session tracking for user corrections
├── __init__.py                    # Module exports
│
├── mermaidv1/                     # Mermaid CLI Provider
│   ├── config.json                # Provider overrides + custom settings
│   ├── mermaid_renderer.py        # Provider implementation
│   └── __init__.py
│
├── d2v1/                          # D2 CLI Provider
│   ├── config.json                # Provider overrides + custom settings
│   ├── d2_renderer.py             # Provider implementation
│   └── __init__.py
│
└── tests/                         # Test suite
    ├── test_config.py             # System tests
    ├── mermaidv1/
    │   └── test_mermaid_config.py
    └── d2v1/
        └── test_d2_config.py
```

---

## Configuration System

### Hierarchical Configuration

The configuration system uses a two-level hierarchy with deep merge:

#### Level 1: Root Configuration (`config.json`)

Defines **defaults** for all providers:

```json
{
  "version": "1.0",
  "defaults": {
    "llm_correction": {
      "enabled": true,
      "max_retries": 3,
      "temperature": 0.3,
      "max_tokens": 4000
    },
    "pattern_correction": {
      "enabled": true
    },
    "correction_strategy": "pattern_then_llm",
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
  },
  "global_settings": {
    "session_cleanup_interval_seconds": 300,
    "max_concurrent_renders": 10,
    "enable_metrics": true
  }
}
```

#### Level 2: Provider Configuration (`mermaidv1/config.json`)

Defines **overrides** and custom settings:

```json
{
  "provider_id": "mermaidv1",
  "provider_name": "Mermaid CLI Renderer v1",
  "description": "Mermaid diagram renderer using mmdc CLI",

  "diagram_type": "mermaid",
  "supported_output_formats": ["mermaid", "svg", "png"],

  "overrides": {
    "llm_correction": {
      "max_retries": 5,           // Override: 3 → 5
      "temperature": 0.2          // Override: 0.3 → 0.2
    },
    "validation": {
      "timeout_seconds": 180      // Override: 120 → 180
    }
  },

  "custom": {
    "executable_name": "mmdc",
    "executable_path": null,
    "supported_diagram_types": [
      "flowchart", "sequenceDiagram", "classDiagram"
    ]
  }
}
```

### Deep Merge Algorithm

The system performs **deep merge** of configurations:

```python
# Root says:
{
  "llm_correction": {
    "max_retries": 3,
    "temperature": 0.3,
    "max_tokens": 4000
  }
}

# Provider overrides just ONE field:
{
  "overrides": {
    "llm_correction": {
      "max_retries": 5
    }
  }
}

# Result after deep merge:
{
  "llm_correction": {
    "max_retries": 5,      // Overridden
    "temperature": 0.3,    // From default
    "max_tokens": 4000     // From default
  }
}
```

### Configuration Loading Flow

```
1. Load root config.json
   ↓
2. For each provider folder:
   ↓
3. Load provider config.json
   ↓
4. Deep merge: root defaults + provider overrides
   ↓
5. Create ProviderConfig object (Pydantic validation)
   ↓
6. Provider uses merged config
```

---

## Provider Implementation

### Base Provider Class

All providers inherit from `BaseDiagramProvider`:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import ValidationResult, RenderResult

class BaseDiagramProvider(ABC):
    """Abstract base for all diagram providers"""

    def __init__(self, provider_folder: Path):
        """Load config from provider folder"""
        self.config = load_provider_config(provider_folder)

    # ABSTRACT PROPERTIES (must implement)
    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique ID matching folder name"""
        pass

    @property
    @abstractmethod
    def diagram_type(self) -> str:
        """Primary diagram type: 'mermaid', 'd2', etc."""
        pass

    @property
    @abstractmethod
    def supported_output_formats(self) -> List[str]:
        """Formats this provider can output"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[ProviderCapability]:
        """What this provider can do"""
        pass

    # ABSTRACT METHODS (must implement)
    @abstractmethod
    def validate_code(self, code: str) -> ValidationResult:
        """Validate diagram syntax"""
        pass

    @abstractmethod
    def render(self, code: str, output_format: str) -> RenderResult:
        """Render diagram to specified format"""
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """Get renderer version"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if renderer is installed"""
        pass

    # OPTIONAL (can override)
    def auto_fix_pattern_based(self, code: str, error: str) -> ValidationResult:
        """Pattern-based syntax fixing"""
        pass

    def get_llm_correction_rules(self) -> Optional[str]:
        """Provider-specific LLM correction rules"""
        pass

    # PROVIDED BY BASE CLASS
    def render_with_validation(self, code: str, output_format: str):
        """
        Template method - orchestrates full pipeline:
        1. Validate
        2. Pattern fix (if enabled)
        3. LLM correction (if enabled)
        4. Render
        5. Return result
        """
        pass
```

### Example Provider Implementation

```python
# backend/diagrams/mermaidv1/mermaid_renderer.py

from pathlib import Path
from diagrams.base_diagram import BaseDiagramProvider
from diagrams.models import (
    ProviderCapability, ValidationResult, RenderResult
)

class MermaidV1Provider(BaseDiagramProvider):
    """Mermaid CLI-based renderer"""

    def __init__(self, provider_folder: Path):
        super().__init__(provider_folder)
        # Load executable from config
        self.executable = self.config.custom.get('executable_name', 'mmdc')

    @property
    def provider_id(self) -> str:
        return "mermaidv1"

    @property
    def provider_name(self) -> str:
        return self.config.provider_name

    @property
    def diagram_type(self) -> str:
        return "mermaid"

    @property
    def supported_output_formats(self) -> List[str]:
        return ["mermaid", "svg", "png"]

    @property
    def capabilities(self) -> List[ProviderCapability]:
        return [
            ProviderCapability.VALIDATE,
            ProviderCapability.RENDER_SVG,
            ProviderCapability.RENDER_PNG,
            ProviderCapability.AUTO_FIX,
            ProviderCapability.LLM_CORRECTION
        ]

    def validate_code(self, code: str, **options) -> ValidationResult:
        """Validate using mmdc CLI"""
        timeout = self.config.validation.timeout_seconds

        # Run mmdc validation
        result = subprocess.run(
            [self.executable, '--input', '-', '--output', '-'],
            input=code,
            capture_output=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return ValidationResult(is_valid=True, code_length=len(code))
        else:
            return ValidationResult(
                is_valid=False,
                error=result.stderr,
                code_length=len(code)
            )

    def render(self, code: str, output_format: str, **options) -> RenderResult:
        """Render using mmdc CLI"""
        timeout = self.config.rendering.timeout_seconds

        # Run mmdc rendering
        result = subprocess.run(
            [self.executable, '--input', '-', '--output', '-',
             '--outputFormat', output_format],
            input=code,
            capture_output=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return RenderResult(
                success=True,
                content=result.stdout,
                output_format=output_format,
                validation=ValidationResult(is_valid=True)
            )
        else:
            return RenderResult(
                success=False,
                output_format=output_format,
                error=result.stderr,
                validation=ValidationResult(is_valid=False, error=result.stderr)
            )

    def auto_fix_pattern_based(self, code: str, error: str) -> ValidationResult:
        """Mermaid-specific pattern fixes"""
        # Add diagram type if missing
        if not code.strip().startswith(('flowchart', 'graph', 'sequenceDiagram')):
            code = f"flowchart TD\n{code}"

        # Fix arrow syntax
        code = re.sub(r'(\w+)-->', r'\1 -->', code)

        # Re-validate
        return self.validate_code(code)

    def get_version(self) -> Optional[str]:
        """Get mmdc version"""
        result = subprocess.run(
            [self.executable, '--version'],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def is_available(self) -> bool:
        """Check if mmdc is installed"""
        try:
            subprocess.run([self.executable, '--version'],
                         capture_output=True, timeout=5)
            return True
        except:
            return False
```

---

## Rendering Pipeline

### Pipeline Flow

```
User Request
    ↓
┌───────────────────────────────────────────────┐
│ 1. VALIDATION                                 │
│    - Check syntax using provider validator   │
│    - Return validation result                 │
└───────────────┬───────────────────────────────┘
                │
                ↓ Valid?
               Yes ────────────────┐
                │                  │
               No                  │
                ↓                  │
┌───────────────────────────────┐ │
│ 2. PATTERN-BASED AUTO-FIX     │ │
│    - Apply deterministic fixes│ │
│    - Re-validate              │ │
└───────────────┬───────────────┘ │
                │                  │
                ↓ Fixed?           │
               Yes ────────────────┤
                │                  │
               No                  │
                ↓                  │
┌───────────────────────────────┐ │
│ 3. LLM CORRECTION             │ │
│    - Send error to LLM        │ │
│    - Get corrected code       │ │
│    - Re-validate              │ │
│    - Retry up to N times      │ │
└───────────────┬───────────────┘ │
                │                  │
                ↓ Fixed?           │
               Yes ────────────────┤
                │                  │
               No                  │
                ↓                  │
┌───────────────────────────────┐ │
│ 4. USER CORRECTION PROMPT     │ │
│    - Create correction session│ │
│    - Return session ID        │ │
│    - User can edit & resubmit │ │
└───────────────────────────────┘ │
                                  │
                ┌─────────────────┘
                ↓
┌───────────────────────────────────────────────┐
│ 5. RENDERING                                  │
│    - Render to requested format               │
│    - Track metadata (time, size, attempts)    │
│    - Return rendered content                  │
└───────────────────────────────────────────────┘
```

### Configuration-Driven Behavior

The pipeline respects configuration at each step:

```python
# From config:
config.pattern_correction.enabled = True/False
config.llm_correction.enabled = True/False
config.llm_correction.max_retries = 0-10
config.user_correction.enabled = True/False

# Pipeline adapts:
if not pattern_correction.enabled:
    skip_step_2()

if not llm_correction.enabled:
    skip_step_3()

if llm_correction.enabled:
    for attempt in range(max_retries):
        try_llm_correction()
        if success:
            break

if not user_correction.enabled:
    return_error_immediately()
else:
    create_correction_session()
```

---

## Error Correction Workflow

### Three-Tier Correction Strategy

#### Tier 1: Pattern-Based Auto-Fix (Fast)

**When**: Immediately after validation failure
**How**: Deterministic regex/string operations
**Config**: `pattern_correction.enabled`

**Examples**:
```python
# Missing diagram type
"A --> B" → "flowchart TD\nA --> B"

# Arrow spacing
"A-->B" → "A --> B"

# Quote syntax
"A[My Node]" → "A[\"My Node\"]"
```

**Advantages**:
- Fast (milliseconds)
- No external dependencies
- Predictable
- No cost

#### Tier 2: LLM Correction (Intelligent)

**When**: After pattern fix fails
**How**: Send error to LLM for correction
**Config**: `llm_correction.enabled`, `max_retries`, `temperature`

**Process**:
```
1. Build correction prompt:
   - Error message
   - Invalid code
   - Syntax rules
   - Provider-specific guidelines

2. Send to LLM (via AIProcessor)

3. Extract corrected code from response

4. Validate corrected code

5. If still invalid, retry (up to max_retries)

6. If valid, continue to rendering
```

**LLM Prompt Structure**:
```
FIX THIS MERMAID DIAGRAM SYNTAX ERROR:

**ERROR MESSAGE:**
```
Syntax error on line 5: unexpected token '>'
```

**INVALID CODE:**
```mermaid
graph TD
A->B
B -> C
```

**CORRECTION RULES:**
- Always use spaces around arrows: A --> B (not A->B)
- Start with diagram type (graph TD, flowchart, etc.)
- Quote labels with special characters

**INSTRUCTIONS:**
Return ONLY the corrected code block. No explanations.
```

**Advantages**:
- Intelligent corrections
- Handles complex errors
- Learns from context
- Can fix multiple errors at once

**Disadvantages**:
- Slower (seconds)
- API costs
- Requires LLM access

#### Tier 3: User Manual Correction

**When**: Both auto-fix methods fail
**How**: Create correction session, return to user
**Config**: `user_correction.enabled`, `session_timeout_seconds`

**Workflow**:
```
1. Create correction session
   - Generate session_id
   - Store: original code, current code, attempts
   - Set expiration timeout

2. Return to frontend:
   - Session ID
   - Current error
   - Correction history
   - Code editor with current state

3. User edits code manually

4. User submits correction via:
   POST /api/v1/diagrams/correct
   {
     "session_id": "...",
     "corrected_code": "..."
   }

5. Re-validate user's code
   - If valid: render and return
   - If invalid: optionally retry LLM
   - Track in session history

6. Session expires after timeout
```

**Correction Session Structure**:
```python
{
  "session_id": "abc123",
  "provider_id": "mermaidv1",
  "original_code": "...",
  "current_code": "...",
  "current_error": "...",

  "attempts": [
    {
      "attempt_number": 1,
      "type": "original",
      "code": "...",
      "is_valid": false,
      "error": "..."
    },
    {
      "attempt_number": 2,
      "type": "pattern",
      "code": "...",
      "is_valid": false,
      "error": "..."
    },
    {
      "attempt_number": 3,
      "type": "llm",
      "code": "...",
      "is_valid": false,
      "error": "..."
    }
  ],

  "llm_retries_used": 3,
  "llm_retries_remaining": 2,
  "expires_at": "2025-11-01T12:30:00Z"
}
```

### Correction Strategy Configuration

```json
{
  "correction_strategy": "pattern_then_llm"
}
```

**Available Strategies**:
- `none` - No auto-correction
- `pattern_only` - Only pattern-based fixes
- `llm_only` - Skip pattern, go straight to LLM
- `pattern_then_llm` - Try pattern first, then LLM (recommended)
- `user_only` - Skip all auto-correction, require user input

---

## API Design

### Unified API Endpoints

All diagram operations go through a single unified API:

```
POST   /api/v1/diagrams/render
POST   /api/v1/diagrams/validate
POST   /api/v1/diagrams/correct
GET    /api/v1/diagrams/sessions/{id}
GET    /api/v1/diagrams/providers
GET    /api/v1/diagrams/providers/{id}/config
PUT    /api/v1/diagrams/providers/{id}/config
```

### Request/Response Models

#### Render Request

```json
POST /api/v1/diagrams/render

{
  "provider": "mermaidv1",
  "code": "graph TD\nA --> B",
  "output_format": "svg",

  "auto_fix": true,
  "llm_correction": true,
  "max_llm_retries": null,

  "create_session_on_failure": true,
  "options": {
    "theme": "dark",
    "width": 800
  }
}
```

#### Render Response (Success)

```json
{
  "success": true,
  "content": "<svg>...</svg>",
  "output_format": "svg",

  "validation": {
    "is_valid": true,
    "auto_fixed": true,
    "correction_method": "pattern",
    "code_length": 123
  },

  "metadata": {
    "provider": "mermaidv1",
    "provider_name": "Mermaid CLI Renderer v1",
    "render_time": 0.45,
    "timestamp": "2025-11-01T12:00:00Z",
    "output_size": 4567
  },

  "error": null,
  "correction_session": null
}
```

#### Render Response (Failure with Session)

```json
{
  "success": false,
  "content": null,
  "output_format": "svg",

  "validation": {
    "is_valid": false,
    "error": "Syntax error on line 3: unexpected token",
    "auto_fixed": false,
    "llm_corrected": false,
    "code_length": 123
  },

  "metadata": {
    "provider": "mermaidv1",
    "render_time": 2.34,
    "timestamp": "2025-11-01T12:00:00Z"
  },

  "error": "Syntax error on line 3: unexpected token",

  "correction_session": {
    "session_id": "abc123",
    "provider_id": "mermaidv1",
    "current_code": "...",
    "current_error": "...",
    "llm_retries_used": 3,
    "llm_retries_remaining": 0,
    "total_attempts": 4,
    "expires_at": "2025-11-01T12:05:00Z",
    "message": "Automatic correction failed. Please edit the code manually."
  }
}
```

#### User Correction Request

```json
POST /api/v1/diagrams/correct

{
  "session_id": "abc123",
  "corrected_code": "graph TD\nA --> B\nB --> C",
  "output_format": "svg",
  "continue_on_failure": true
}
```

#### List Providers Response

```json
GET /api/v1/diagrams/providers

{
  "providers": [
    {
      "provider_id": "mermaidv1",
      "provider_name": "Mermaid CLI Renderer v1",
      "diagram_type": "mermaid",
      "supported_output_formats": ["mermaid", "svg", "png"],
      "capabilities": ["validate", "render_svg", "render_png", "auto_fix", "llm_correction"],
      "available": true,
      "version": "10.6.0",
      "requires_llm": true,
      "settings": {
        "llm_max_retries": 5,
        "correction_strategy": "pattern_then_llm",
        "allow_user_correction": true
      }
    },
    {
      "provider_id": "d2v1",
      "provider_name": "D2 CLI Renderer v1",
      "diagram_type": "d2",
      "supported_output_formats": ["d2", "svg"],
      "capabilities": ["validate", "render_svg", "batch", "llm_correction"],
      "available": true,
      "version": "0.7.1",
      "requires_llm": true,
      "settings": {
        "llm_max_retries": 8,
        "batch_enabled": true
      }
    }
  ]
}
```

---

## Frontend Integration

### Unified Diagram Component

```typescript
// frontend/src/components/chat/DiagramRenderer.tsx

interface DiagramRendererProps {
  code: string;
  diagramType?: string;  // Auto-detect if not provided
  provider?: string;      // Use default if not provided
  outputFormat?: string;  // Default: "svg"
}

export function DiagramRenderer({ code, diagramType, provider }: DiagramRendererProps) {
  const [renderResult, setRenderResult] = useState(null);
  const [correctionSession, setCorrectionSession] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    renderDiagram();
  }, [code]);

  async function renderDiagram() {
    const result = await diagramApi.render({
      provider: provider || await detectProvider(diagramType, code),
      code,
      output_format: "svg",
      auto_fix: true,
      llm_correction: true,
      create_session_on_failure: true
    });

    if (result.success) {
      setRenderResult(result);
    } else if (result.correction_session) {
      // Auto-correction failed, show manual editor
      setCorrectionSession(result.correction_session);
      setIsEditing(true);
    }
  }

  async function submitCorrection(correctedCode: string) {
    const result = await diagramApi.submitCorrection(
      correctionSession.session_id,
      correctedCode
    );

    if (result.success) {
      setRenderResult(result);
      setIsEditing(false);
    } else {
      // Still invalid, update session
      setCorrectionSession(result.session_summary);
    }
  }

  if (isEditing) {
    return (
      <CorrectionEditor
        session={correctionSession}
        onSubmit={submitCorrection}
        onCancel={() => setIsEditing(false)}
      />
    );
  }

  return (
    <div>
      <DiagramDisplay content={renderResult?.content} />
      <DiagramMetadata metadata={renderResult?.metadata} />
    </div>
  );
}
```

### API Client

```typescript
// frontend/src/services/diagramApi.ts

export const diagramApi = {
  async render(request: DiagramRenderRequest): Promise<DiagramRenderResponse> {
    const response = await fetch('/api/v1/diagrams/render', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    return response.json();
  },

  async submitCorrection(sessionId: string, correctedCode: string) {
    const response = await fetch('/api/v1/diagrams/correct', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        corrected_code: correctedCode,
        continue_on_failure: true
      })
    });
    return response.json();
  },

  async listProviders(): Promise<ProvidersResponse> {
    const response = await fetch('/api/v1/diagrams/providers');
    return response.json();
  }
};
```

---

## Extension Points

### Adding a New Provider

**Step 1**: Create provider folder and config

```bash
mkdir backend/diagrams/mermaid-playwright
```

```json
// backend/diagrams/mermaid-playwright/config.json
{
  "provider_id": "mermaid-playwright",
  "provider_name": "Mermaid Playwright Renderer",
  "description": "Browser-based Mermaid rendering using Playwright",

  "diagram_type": "mermaid",
  "supported_output_formats": ["mermaid", "svg", "png"],

  "overrides": {
    "llm_correction": {
      "max_retries": 2
    }
  },

  "custom": {
    "browser": "chromium",
    "headless": true
  }
}
```

**Step 2**: Implement provider class

```python
# backend/diagrams/mermaid-playwright/mermaid_renderer.py

from diagrams.base_diagram import BaseDiagramProvider

class MermaidPlaywrightProvider(BaseDiagramProvider):
    def __init__(self, provider_folder):
        super().__init__(provider_folder)
        self.browser = self.config.custom.get('browser', 'chromium')

    @property
    def provider_id(self) -> str:
        return "mermaid-playwright"

    # Implement all abstract methods...
    def validate_code(self, code: str):
        # Use browser to validate
        pass

    def render(self, code: str, output_format: str):
        # Use Playwright to render
        pass
```

**Step 3**: Provider auto-discovered on startup

The provider registry automatically discovers and registers the new provider.

### Adding a New Diagram Type

Example: Adding PlantUML support

```
backend/diagrams/
└── plantumlv1/
    ├── config.json
    └── plantuml_renderer.py
```

```json
// config.json
{
  "provider_id": "plantumlv1",
  "provider_name": "PlantUML Renderer",
  "diagram_type": "plantuml",
  "supported_output_formats": ["plantuml", "svg", "png"],

  "overrides": {
    "llm_correction": {
      "max_retries": 4,
      "temperature": 0.25
    }
  },

  "custom": {
    "plantuml_jar": "/usr/local/bin/plantuml.jar"
  }
}
```

### Extending Configuration

To add new configuration options:

**Step 1**: Update root config schema

```json
// backend/diagrams/config.json
{
  "defaults": {
    // ... existing defaults ...

    "new_feature": {
      "enabled": true,
      "option1": "value",
      "option2": 100
    }
  }
}
```

**Step 2**: Update Pydantic models

```python
# backend/diagrams/provider_config.py

class NewFeatureConfig(BaseModel):
    enabled: bool = True
    option1: str = "value"
    option2: int = 100

class DefaultConfig(BaseModel):
    # ... existing fields ...
    new_feature: NewFeatureConfig = Field(default_factory=NewFeatureConfig)
```

**Step 3**: Providers automatically inherit new config

Providers can override if needed:

```json
{
  "overrides": {
    "new_feature": {
      "option1": "custom_value"
    }
  }
}
```

---

## Performance Considerations

### Optimization Strategies

1. **Provider Registry Caching**
   - Load and instantiate providers once at startup
   - Singleton pattern for provider instances

2. **Configuration Caching**
   - Cache merged configurations
   - Reload only when config files change

3. **Concurrent Rendering**
   - Use asyncio for parallel renders
   - Respect `max_concurrent_renders` limit

4. **LLM Rate Limiting**
   - Exponential backoff on LLM failures
   - Cache LLM corrections for identical errors

5. **Session Cleanup**
   - Periodic background task
   - Remove expired correction sessions

---

## Security Considerations

### Configuration Security

- ✅ Validate all config values with Pydantic
- ✅ Limit max_retries to prevent resource exhaustion
- ✅ Timeout all subprocess calls
- ✅ Sanitize file paths in custom settings

### Code Execution Security

- ✅ Never use `eval()` or `exec()` on user code
- ✅ Run CLI tools with timeouts
- ✅ Validate output file paths
- ✅ Limit code size (`max_code_length_bytes`)

### API Security

- ✅ Rate limit render requests
- ✅ Validate session IDs
- ✅ Expire correction sessions
- ✅ Sanitize error messages (no sensitive info)

---

## Monitoring & Observability

### Metrics to Track

1. **Rendering Metrics**
   - Success rate by provider
   - Average render time by provider
   - Error rate by error type

2. **Correction Metrics**
   - Pattern fix success rate
   - LLM correction success rate
   - Average retries needed
   - User correction rate

3. **Provider Health**
   - Provider availability
   - CLI tool versions
   - Validation timeout rate

### Logging

```python
logger.info(f"[{provider_id}] Starting render pipeline")
logger.info(f"[{provider_id}] Step 1/4: Validating...")
logger.info(f"[{provider_id}] Step 2/4: Pattern fix...")
logger.info(f"[{provider_id}] Step 3/4: LLM correction...")
logger.info(f"[{provider_id}] Step 4/4: Rendering...")
logger.info(f"[{provider_id}] ✅ Success ({duration:.2f}s)")
```

---

## Migration Strategy

### Phase 1: Foundation (✅ Complete)
- Configuration system
- Base classes and models
- Test framework

### Phase 2: Core Services
- LLM correction service
- Correction session management
- Provider registry

### Phase 3: Provider Migration
- Migrate mermaidv1
- Migrate d2v1
- Test alongside existing services

### Phase 4: API Layer
- Implement unified endpoints
- Keep old endpoints for compatibility
- Add deprecation warnings

### Phase 5: Frontend
- Unified component
- API client
- Gradual rollout

### Phase 6: Deprecation
- Monitor usage of old endpoints
- Remove old endpoints
- Remove old services

---

## Conclusion

This architecture provides:

✅ **Modularity** - Self-contained providers
✅ **Extensibility** - Easy to add providers and features
✅ **Configuration-Driven** - Behavior controlled by JSON
✅ **Intelligent Correction** - Pattern + LLM + User workflow
✅ **Type Safety** - Full Pydantic validation
✅ **Backward Compatibility** - No breaking changes
✅ **Production Ready** - Comprehensive error handling and logging

The system is designed to scale from 2 providers to dozens, supporting multiple diagram types with intelligent error correction and user-friendly workflows.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: Foundation Complete, Implementation In Progress
