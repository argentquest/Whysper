# Quick Reference Guide - Diagram Provider System

## 🎯 System Overview

Single unified provider system for all diagram rendering via `/api/v1/diagrams/v2/*`

```
User Chat → Backend (generates diagrams) → Frontend (renders diagrams)
             └─ Response contains: ```mermaid, ```d2, ```c4 code blocks
                                  ↓
                           diagramProviderService
                                  ↓
                    /api/v1/diagrams/v2/validate
                    /api/v1/diagrams/v2/render
                                  ↓
                           SVG in Component
```

---

## 📁 Key Files

### Backend (Server-Side)
| File | Purpose | Status |
|------|---------|--------|
| `backend/app/api/v1/api.py` | API router config | ✅ Routes to `/diagrams/v2` |
| `backend/app/services/conversation_service.py` | Chat processing | ✅ Detects diagrams, passes to frontend |
| `backend/diagrams/` | Provider implementations | ✅ D2v1, Mermaidv1 providers |

### Frontend (Client-Side)
| File | Purpose | Status |
|------|---------|--------|
| `frontend/src/services/diagramProviderService.ts` | Unified service | ✅ Single entry point for all diagrams |
| `frontend/src/components/chat/MermaidDiagram.tsx` | Mermaid renderer | ✅ Uses provider service |
| `frontend/src/components/chat/D2DiagramBackend.tsx` | D2 renderer | ✅ Uses provider service |
| `frontend/src/components/chat/C4Diagram.tsx` | C4 renderer | ✅ Uses provider service |

---

## 🔗 API Endpoints

### Active Endpoints (V2)
```
POST /api/v1/diagrams/v2/render       - Render diagram
POST /api/v1/diagrams/v2/validate     - Validate code
GET  /api/v1/diagrams/v2/providers    - List providers
GET  /api/v1/diagrams/v2/providers/{id} - Get provider info
GET  /api/v1/diagrams/v2/health       - Health check
```

### Request Format
```json
{
  "code": "flowchart TD\n  A --> B",
  "diagram_type": "mermaid",
  "output_format": "svg",
  "auto_fix": true,
  "use_llm": false
}
```

### Response Format
```json
{
  "success": true,
  "content": "<svg>...</svg>",
  "validation": {"is_valid": true, "errors": []},
  "provider_id": "mermaidv1",
  "metadata": {"render_time": 0.234, "version": "10.6.1"}
}
```

---

## 🛠️ Common Workflows

### Adding a New Diagram Type

1. **Create Provider** in `backend/diagrams/newtype/`
2. **Register Provider** in provider registry
3. **Update Frontend** detection in `mermaidUtils.ts`
4. **Update Component** to route to new provider
5. **Test** render/validate endpoints

### Debugging a Diagram Rendering Issue

1. Check frontend logs: `console.log` for diagramProviderService calls
2. Check backend logs: `/api/v1/diagrams/v2/health`
3. Test endpoint directly: `curl -X POST http://localhost:8001/api/v1/diagrams/v2/render`
4. Check provider health: `GET /api/v1/diagrams/v2/providers`

### Testing Diagram Generation

```javascript
// Frontend test
const result = await diagramProviderService.render({
  code: 'flowchart TD\n  A --> B',
  diagram_type: 'mermaid',
  output_format: 'svg',
  auto_fix: true,
  use_llm: false
});

console.log('Success:', result.success);
console.log('SVG:', result.content);
```

---

## ⚠️ Common Issues

### Issue: 404 Not Found
**Cause**: Using old endpoints (e.g., `/api/v1/d2/render`)
**Fix**: Use `/api/v1/diagrams/v2/render` instead

### Issue: 422 Unprocessable Entity
**Cause**: Missing required `diagram_type` field
**Fix**: Always include: `diagram_type: 'mermaid'` or `diagram_type: 'd2'`

### Issue: ModuleNotFoundError in conversation_service
**Cause**: Method trying to import deleted service
**Status**: ✅ FIXED - All imports removed

### Issue: Response has `svg_content` instead of `content`
**Cause**: Old API response format
**Fix**: Use `response.content` for v2 endpoint

---

## 📊 System Architecture

### Single Responsibility
- **Backend**: Content generation + Diagram detection
- **Frontend**: Diagram rendering + UI operations
- **Provider**: Validation + Rendering engine

### Flow
```
1. User: "Create a flowchart"
2. Backend: Generates chat response with ```mermaid code
3. Backend: _validate_and_fix_mermaid_diagrams() detects it
4. Backend: Passes response unchanged to frontend
5. Frontend: Detects ```mermaid code block
6. Frontend: Routes to MermaidDiagram component
7. Frontend: Calls diagramProviderService.render()
8. Frontend: Receives SVG, displays in component
9. User: Sees rendered diagram with controls
```

---

## 🧪 Verification Commands

### Test Backend Import
```bash
py -c "from app.services.conversation_service import ConversationSession; print('OK')"
```

### Test API Health
```bash
curl http://localhost:8001/api/v1/diagrams/v2/health
```

### Test Render Endpoint
```bash
curl -X POST http://localhost:8001/api/v1/diagrams/v2/render \
  -H "Content-Type: application/json" \
  -d '{"code":"A->B","diagram_type":"d2","output_format":"svg"}'
```

### Test Providers
```bash
curl http://localhost:8001/api/v1/diagrams/v2/providers
```

---

## 📝 Key Changes (This Session)

### Fixed Methods
1. `_validate_and_fix_d2_diagrams()` - 150→37 lines
2. `_validate_and_fix_mermaid_diagrams()` - 130→35 lines
3. `_pre_render_d2_diagrams()` - 150→33 lines

### Removed Complexity
- ❌ Complex retry loops
- ❌ AI feedback mechanisms
- ❌ Server-side rendering
- ❌ File I/O operations
- ❌ Deleted service imports

### New Behavior
- ✅ Simple diagram detection
- ✅ Pass-through to frontend
- ✅ Unified provider API
- ✅ Frontend handles rendering

---

## 🚀 Deployment Checklist

- ✅ No import errors
- ✅ All methods verified
- ✅ Backend loads successfully
- ✅ Frontend components working
- ✅ Provider system operational
- ✅ All tests passing
- ✅ Documentation complete

**Status**: Ready for Production ✅

---

## 📚 Documentation Files

- `CLEANUP_COMPLETE.md` - Backend cleanup details
- `FRONTEND_CLEANUP_COMPLETE.md` - Frontend cleanup details
- `CONVERSATION_SERVICE_FIX.md` - Critical import fixes
- `DIAGRAM_PROVIDER_INTEGRATION.md` - Architecture guide
- `FULL_MIGRATION_SUMMARY.md` - Complete migration overview
- `SESSION_COMPLETION_REPORT.md` - This session's work
- `QUICK_REFERENCE_GUIDE.md` - This document

---

## 💡 Tips

1. **Always use `diagram_type` in requests** - It's required!
2. **Check provider health** before debugging - Rule out infrastructure issues
3. **Use frontend logs** for client-side debugging
4. **Use backend logs** for server-side issues
5. **Test endpoints directly** with curl before debugging frontend code

---

**Last Updated**: November 2, 2025
**Status**: Production Ready ✅
