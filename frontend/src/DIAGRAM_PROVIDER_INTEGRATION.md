# Frontend Diagram Provider Integration

## Overview

The frontend has been refactored to use the unified **Diagram Provider Service** which communicates with the backend's modular diagram provider system (mermaidv1, d2v1, etc.).

This integration provides:
- **Single source of truth**: All diagram rendering delegates to backend providers
- **Consistent validation**: Uses provider auto-fix capabilities (pattern-based + LLM)
- **Provider metadata**: Access to provider info, capabilities, and performance metrics
- **Type safety**: Full TypeScript support with detailed interfaces
- **Backwards compatibility**: Still supports client-side Mermaid.js as fallback

---

## Architecture

### File Structure

```
frontend/src/
├── services/
│   ├── diagramProviderService.ts          [NEW] Unified provider interface
│   ├── api.ts                              (existing, updated)
│   └── d2Api.ts                            (legacy, still available)
│
├── components/chat/
│   ├── BaseDiagramRenderer.tsx             [NEW] Abstract base class
│   ├── MermaidDiagram.tsx                  (updated)
│   ├── D2DiagramBackend.tsx                (updated)
│   └── C4Diagram.tsx                       (ready for update)
│
└── [other components]
```

### Data Flow

```
User Input (code)
    ↓
ChatView detects diagram type
    ↓
Routes to MermaidDiagram or D2DiagramBackend
    ↓
Component uses diagramProviderService
    ↓
Service calls /diagram-provider/* endpoints
    ↓
Backend provider (mermaidv1 or d2v1)
    ↓
Validation → Auto-fix → Rendering
    ↓
Response with SVG + metadata
    ↓
Component renders SVG + shows provider info
```

---

## Services

### DiagramProviderService (`diagramProviderService.ts`)

**Purpose**: Unified interface for all diagram operations

**Key Methods**:

```typescript
// Render a diagram
async render(request: DiagramRenderRequest): Promise<DiagramRenderResponse>

// Validate diagram code
async validate(request: DiagramValidationRequest): Promise<DiagramValidationResponse>

// Get provider information
async getProviderInfo(diagramType: DiagramType, providerId?: string): Promise<ProviderInfo>

// List all providers
async listProviders(): Promise<ProvidersListResponse>

// Get providers for a specific type
async getProvidersByType(diagramType: DiagramType): Promise<ProviderInfo[]>

// Check provider availability
async isProviderAvailable(diagramType: DiagramType, providerId?: string): Promise<boolean>

// Check system health
async checkHealth(): Promise<HealthStatus>

// Clear cached provider info
clearCache(): void
```

**Type Definitions**:

```typescript
type DiagramType = 'mermaid' | 'd2' | 'c4';
type OutputFormat = 'svg' | 'png' | 'native';

interface DiagramRenderRequest {
  code: string;
  diagram_type: DiagramType;
  provider_id?: string;
  output_format?: OutputFormat;
  metadata?: Record<string, any>;
  save_to_file?: boolean;
}

interface DiagramRenderResponse {
  success: boolean;
  content?: string;
  output_format: string;
  validation: ValidationResult;
  metadata: {
    provider_id: string;
    provider_name: string;
    render_time: number;
    timestamp: string;
    code_length: number;
    [key: string]: any;
  };
  error?: string;
  file_path?: string;
}

interface ValidationResult {
  is_valid: boolean;
  error?: string;
  auto_fixed: boolean;
  llm_corrected: boolean;
  fixed_code?: string;
  correction_method?: string;
}

interface ProviderInfo {
  provider_id: string;
  provider_name: string;
  diagram_type: DiagramType;
  description?: string;
  supported_output_formats: OutputFormat[];
  capabilities: string[];
  version?: string;
  available: boolean;
  requires_llm: boolean;
}
```

**Features**:
- Singleton pattern (thread-safe instance)
- 5-minute cache for provider metadata
- Automatic provider type mapping (mermaid/d2/c4)
- Debug logging with emoji prefixes
- Error handling and normalization

---

## Base Diagram Renderer (`BaseDiagramRenderer.tsx`)

**Purpose**: Abstract base class with common functionality for all diagram components

**Key Features**:

1. **Core Methods** (override in subclasses):
   - `getDiagramType()`: Return diagram type handled by component
   - `renderToDOM()`: Render SVG to DOM container
   - `validateDiagram()`: Validate using provider service
   - `renderDiagram()`: Render using provider service

2. **Utility Methods** (use in subclasses):
   - `exportAsSvg()`: Download diagram as SVG file
   - `exportAsPng()`: Download diagram as PNG
   - `copyCodeToClipboard()`: Copy diagram code
   - `supportsFormat()`: Check if provider supports output format
   - `supportsAutoFix()`: Check auto-fix capability
   - `supportsLLMCorrection()`: Check LLM capability
   - `formatErrorMessage()`: Standardize error messages
   - `extractProviderMetadata()`: Parse render response metadata
   - `logDiagramEvent()`: Log diagram events

3. **React Hook** `useDiagramRenderer()`:
   ```typescript
   const { state, render, validate, getProviderInfo, updateState } =
     useDiagramRenderer('mermaid');
   ```

   State includes:
   - `isRendering`: Currently rendering
   - `isValidating`: Currently validating
   - `error`: Error message
   - `svg`: Rendered SVG content
   - `png`: Rendered PNG content
   - `validation`: Validation result
   - `providerInfo`: Provider metadata
   - `renderResult`: Full render response

---

## Updated Components

### MermaidDiagram Component

**Changes**:
- ✅ Imports `diagramProviderService`
- ✅ Adds provider info state and effect
- ✅ Uses `diagramProviderService.validate()` for validation
- ✅ Uses `diagramProviderService.render()` for rendering
- ✅ Displays provider name and render time in Card title
- ✅ Shows auto-fix notification if code was corrected
- ✅ Maintains fallback to client-side mermaid.js parse

**Key Features**:
- Dual validation: Server-side (via provider) + client-side (via mermaid.js)
- Auto-fix via provider (pattern-based + LLM)
- Provider metadata displayed in UI
- Full zoom and pan support
- SVG/PNG export
- Code copy to clipboard

**Rendering Flow**:
```
Code input
  ↓
Validate via provider (with auto-fix)
  ↓
Client-side parse check (fallback)
  ↓
Render via provider
  ↓
Display SVG + provider info
```

### D2DiagramBackend Component

**Changes**:
- ✅ Imports `diagramProviderService`
- ✅ Replaces `d2Api` with provider service
- ✅ Adds provider info state and effect
- ✅ Uses `diagramProviderService.validate()` for validation
- ✅ Uses `diagramProviderService.render()` for rendering
- ✅ Displays provider name and render time in Card title
- ✅ Shows auto-fix notification if code was corrected
- ✅ Updated logging with 🎯 emoji prefix

**Key Features**:
- Single unified endpoint for all diagram operations
- Provider auto-fix capabilities
- Responsive container resize handling
- Debug panel with full metadata
- SVG export and copy
- Expandable viewer

**Rendering Flow**:
```
Code input
  ↓
Validate via provider (with auto-fix)
  ↓
Render via provider
  ↓
Display SVG + provider info
```

---

## API Endpoints

All operations route to the unified provider endpoint at `/api/v1/diagram-provider/`:

### Render
```
POST /api/v1/diagram-provider/render
```
**Request**:
```json
{
  "code": "flowchart TD\n  A --> B",
  "diagram_type": "mermaid",
  "output_format": "svg",
  "metadata": {}
}
```
**Response**: `DiagramRenderResponse` with SVG content and metadata

### Validate
```
POST /api/v1/diagram-provider/validate
```
**Request**:
```json
{
  "code": "flowchart TD\n  A --> B",
  "diagram_type": "mermaid",
  "auto_fix": true,
  "use_llm": false
}
```
**Response**: `DiagramValidationResponse` with fix status

### Get Providers
```
GET /api/v1/diagram-provider/providers
GET /api/v1/diagram-provider/providers/{provider_id}
```
**Response**: Provider metadata with capabilities

### Health Check
```
GET /api/v1/diagram-provider/health
```
**Response**: System health status

---

## Usage Examples

### Example 1: Rendering a Mermaid Diagram

```typescript
import diagramProviderService from '@/services/diagramProviderService';

// In a component
const [svg, setSvg] = useState('');
const [error, setError] = useState('');

const render = async (code: string) => {
  try {
    const result = await diagramProviderService.render({
      code,
      diagram_type: 'mermaid',
      output_format: 'svg'
    });

    if (result.success) {
      setSvg(result.content!);
      console.log('Rendered by:', result.metadata.provider_name);
      console.log('Time:', result.metadata.render_time, 'ms');
    } else {
      setError(result.error || 'Unknown error');
    }
  } catch (err) {
    setError(err.message);
  }
};
```

### Example 2: Validation with Auto-fix

```typescript
const validateAndFix = async (code: string) => {
  const result = await diagramProviderService.validate({
    code,
    diagram_type: 'd2',
    auto_fix: true,
    use_llm: false
  });

  if (!result.is_valid) {
    console.log('Validation failed:', result.error);

    if (result.auto_fixed) {
      console.log('But we fixed it:', result.fixed_code);
      console.log('Method:', result.correction_method);
    }
  }
};
```

### Example 3: Checking Provider Capabilities

```typescript
const checkCapabilities = async () => {
  const provider = await diagramProviderService.getProviderInfo('mermaid');

  console.log('Provider:', provider.provider_name);
  console.log('Capabilities:', provider.capabilities);

  if (provider.capabilities.includes('auto_fix')) {
    console.log('Auto-fix available');
  }

  if (provider.capabilities.includes('llm_correction')) {
    console.log('LLM correction available');
  }
};
```

---

## Benefits of This Integration

### For Developers
✅ **Type Safety**: Full TypeScript interfaces for all API interactions
✅ **Single Source of Truth**: All rendering logic in backend providers
✅ **Easy to Test**: Provider service can be mocked for testing
✅ **Consistent Errors**: Standardized error handling across all diagram types
✅ **Extensible**: Easy to add new diagram types (PlantUML, Graphviz, etc.)

### For Users
✅ **Better Error Messages**: Provider-level validation with auto-fixes
✅ **Provider Transparency**: See which provider rendered the diagram
✅ **Performance Metrics**: View render time for each diagram
✅ **Smart Corrections**: Pattern-based and LLM corrections work automatically
✅ **Consistent UI**: All diagram types have same controls and experience

### For System
✅ **Reduced Code Duplication**: No more separate rendering logic
✅ **Easier Maintenance**: All rendering handled by unified providers
✅ **Better Scaling**: Easy to add parallel rendering via batch API
✅ **Monitoring**: All operations go through single service
✅ **Caching**: Provider metadata cached for performance

---

## Migration Guide

### For C4Diagram Component (Next)

1. Import the service:
```typescript
import diagramProviderService from '@/services/diagramProviderService';
```

2. Convert C4 to D2:
```typescript
// Already have convertC4ToD2() function
const d2Code = convertC4ToD2(c4Code);
```

3. Render via provider:
```typescript
const result = await diagramProviderService.render({
  code: d2Code,
  diagram_type: 'd2',
  output_format: 'svg'
});
```

### For Custom Diagram Components

Extend `BaseDiagramRenderer`:
```typescript
class CustomDiagramRenderer extends BaseDiagramRenderer<CustomProps> {
  getDiagramType() {
    return 'custom' as DiagramType; // Add to type definition
  }

  renderToDOM(container, svg) {
    container.innerHTML = svg;
  }
}
```

---

## Troubleshooting

### "Provider not found"
- Check if provider is installed/available
- Call `diagramProviderService.checkHealth()`
- Verify diagram type spelling (mermaid, d2, c4)

### "Render failed with auto-fix"
- Check browser console for provider response
- Verify code isn't completely invalid
- Try calling `/diagram-provider/validate` directly

### "SVG not rendering"
- Check if content is actually SVG (not error message)
- Verify container has proper height/width
- Check browser console for rendering errors

### Slow renders
- Check `render_time` in metadata
- Verify backend provider is healthy
- Look for LLM correction delays (slow)

---

## Logging & Debugging

### Debug Prefixes
- 🎨 = Mermaid operations
- 🎯 = D2 operations
- 📊 = Provider service operations
- 🏗️ = C4 operations (when updated)

### Enable Debug Info
```typescript
// In console
localStorage.setItem('debug', '*'); // Enable all logs
// Or specific:
localStorage.setItem('debug', 'diagram*');
```

### Check Provider System Health
```typescript
const health = await diagramProviderService.checkHealth();
console.log(health);
```

### List All Available Providers
```typescript
const providers = await diagramProviderService.listProviders();
console.table(providers.providers);
```

---

## Files Modified

1. **Created**:
   - `frontend/src/services/diagramProviderService.ts` (420 lines)
   - `frontend/src/components/chat/BaseDiagramRenderer.tsx` (400 lines)
   - `frontend/src/DIAGRAM_PROVIDER_INTEGRATION.md` (this file)

2. **Updated**:
   - `frontend/src/components/chat/MermaidDiagram.tsx`
     - Added provider service integration
     - Improved validation logic
     - Enhanced metadata display

   - `frontend/src/components/chat/D2DiagramBackend.tsx`
     - Replaced d2Api with diagramProviderService
     - Improved validation and rendering
     - Better logging and error handling

3. **Not Changed** (but still available):
   - `frontend/src/services/d2Api.ts` (legacy, can deprecate)
   - `frontend/src/services/api.ts` (still used for logging)

---

## Next Steps

1. **Test the changes**:
   - Test Mermaid diagrams
   - Test D2 diagrams
   - Verify provider info displays correctly
   - Test auto-fix functionality

2. **Update C4Diagram** to use provider service

3. **Add unit tests** for `DiagramProviderService`

4. **Consider deprecating** `d2Api.ts` in favor of `diagramProviderService`

5. **Monitor performance** and collect feedback

---

## Summary

The frontend now has a unified, type-safe interface for all diagram operations through the **DiagramProviderService**. This integrates seamlessly with the backend's modular provider system, providing:

- Single point of contact for all diagram operations
- Automatic validation and auto-fix
- Rich metadata about providers and performance
- Extensible architecture for adding new diagram types
- Better error handling and user feedback

The refactoring maintains backwards compatibility while providing a modern, scalable foundation for diagram handling in Whysper.
