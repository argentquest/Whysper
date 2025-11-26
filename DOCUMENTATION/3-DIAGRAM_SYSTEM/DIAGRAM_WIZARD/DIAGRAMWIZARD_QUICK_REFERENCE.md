# DiagramWizard: Quick Reference Guide

**Last Updated:** November 15, 2025
**Version:** 2.0

---

## 🚀 Quick Start (5 minutes)

### Start Development Servers

```bash
# Terminal 1: Frontend
cd frontend
npm install
npm run dev
# Opens http://localhost:5173

# Terminal 2: Backend
cd backend
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8003
```

### Run Tests

```bash
# Frontend tests
cd frontend
npm test                  # Run all tests
npm run test:ui          # Interactive UI
npm run test:coverage    # Coverage report

# Backend tests
cd backend
python -m pytest tests/1-UNIT/providers/ -v
```

### Build Production

```bash
# Frontend
cd frontend
npm run build            # Creates dist/

# Backend (with Gunicorn)
cd backend
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## 📋 File Locations

### Frontend Key Files

| File | Purpose |
|------|---------|
| `frontend/src/components/DiagramWizard/DiagramWizard.tsx` | Main component |
| `frontend/src/hooks/useSSE.ts` | Real-time SSE streaming |
| `frontend/src/hooks/useLocalStorage.ts` | Session persistence |
| `frontend/src/services/diagram/validationService.ts` | Code validation |
| `frontend/src/services/diagram/exportService.ts` | Export to SVG/PNG/PDF |
| `frontend/vitest.config.ts` | Test configuration |
| `frontend/package.json` | Dependencies & scripts |

### Backend Key Files

| File | Purpose |
|------|---------|
| `backend/app/utils/diagram_wizard/nodes.py` | 7 LangGraph nodes |
| `backend/app/utils/diagram_wizard/graph_state.py` | State schema |
| `backend/diagrams/provider_registry.py` | Provider management |
| `backend/diagrams/base_diagram.py` | Provider interface |
| `backend/app/api/v1/endpoints/diagram.py` | REST endpoints |
| `backend/tests/1-UNIT/providers/` | 44 backend tests |

---

## 🔑 Key Concepts

### Architecture: LangGraph + Provider System

```
User Input
    ↓
LangGraph Workflow (Orchestration)
├─ analyze_request
├─ clarify_prompt (loop)
├─ determine_diagram_type
├─ generate_code
├─ validate_code
├─ refine_code
└─ render_diagram
    ↓
Provider System (Execution)
├─ Mermaid (CLI + Kroki)
├─ D2 (CLI + Kroki)
└─ PlantUML (Kroki)
    ↓
Output (SVG/PNG/PDF)
```

### Workflow Phases

1. **ANALYSIS**: Score fitness, generate initial JSON
2. **CLARIFICATION**: Ask questions until clarity_score >= 8
3. **TYPE DETECTION**: Keyword analysis selects best diagram type
4. **GENERATION**: Generate diagram code
5. **VALIDATION**: Validate using provider system
6. **REFINEMENT**: Auto-fix errors (up to 3 attempts)
7. **RENDERING**: Convert to SVG/PNG/PDF

### Real-Time Communication

- **Frontend → Backend**: HTTP POST for actions
- **Backend → Frontend**: SSE stream for updates
- **Reconnection**: Automatic with exponential backoff (2s, 4s, 8s, 16s, 32s)

### State Persistence

- **localStorage**: Saves sessions for resume/history
- **Cross-Tab Sync**: Changes sync across browser tabs
- **Session Storage**: Up to 10 completed sessions retained

---

## 🎯 Common Tasks

### Add a New Diagram Provider

1. **Create provider folder:**
   ```
   backend/diagrams/mynewprovider/
   ├── __init__.py
   ├── config.json           # Provider configuration
   ├── keywords.txt          # Diagram-specific keywords
   └── provider.py           # Provider implementation
   ```

2. **Implement provider class:**
   ```python
   from diagrams.base_diagram import BaseDiagramProvider

   class MyNewProvider(BaseDiagramProvider):
       def validate(self, code: str) -> ValidationResult:
           # Validate diagram code
           pass

       def render(self, code: str, format: str) -> RenderResult:
           # Render to SVG/PNG/PDF
           pass
   ```

3. **Register in registry:**
   ```python
   # backend/diagrams/provider_registry.py
   registry.register("mynewprovider", MyNewProvider())
   ```

### Customize Clarification Questions

1. **Edit prompt:**
   ```
   backend/app/utils/diagram_wizard/prompts/CLARIFY_PROMPTS.md
   ```

2. **Update prompt loader cache:**
   ```bash
   # Restart backend to reload prompts
   ```

### Add New Export Format

1. **Extend exportService.ts:**
   ```typescript
   export async function exportDiagram(
     svgElement: HTMLElement,
     options: ExportOptions & { format: 'webp' | 'svg' | 'png' | 'pdf' }
   )
   ```

2. **Add format-specific handler in switch statement

### Monitor Session Performance

```bash
# Check backend logs
tail -f backend/logs/structured.log

# Monitor specific session
python -c "
from backend.app.utils.diagram_wizard.session_store import session_store
sessions = session_store.get_active_sessions()
for s in sessions:
    print(f'{s.session_id}: {s.state}')
"
```

---

## 🛠️ Debugging Guide

### Frontend Issues

**SSE not connecting:**
```typescript
// Check browser Network tab
// Verify API_URL in .env
// Check backend is running on http://localhost:8003
```

**Validation not working:**
```typescript
// Check validationService.ts
// Verify provider endpoints are accessible
// Check browser console for CORS errors
```

**Export fails:**
```typescript
// Check if html2canvas/jsPDF are installed
// Verify SVG container is rendered
// Check browser storage quota
```

### Backend Issues

**Provider validation fails:**
```bash
# Check if tool is installed
which d2          # or: where d2 (Windows)
which mmdc

# Check provider config
cat backend/diagrams/d2v1/config.json

# Test validation directly
python -c "
from diagrams.provider_registry import get_provider_registry
provider = get_provider_registry().get_provider('d2v1')
result = provider.validate('graph LR; A --> B')
print(result)
"
```

**LLM calls failing:**
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check API quota/limits
# See backend logs for error details
tail -f backend/logs/structured.log | grep error
```

**Tests failing:**
```bash
# Run specific test with verbose output
pytest tests/1-UNIT/providers/test_config.py -vvs

# Run with coverage
pytest --cov=app tests/

# Run specific test function
pytest tests/1-UNIT/providers/test_config.py::test_root_config -vvs
```

---

## 📊 Architecture Decisions

| Decision | Reasoning |
|----------|-----------|
| **LangGraph for orchestration** | State machine ensures consistent workflow |
| **Provider system for execution** | Extensible, testable, maintainable |
| **SSE for real-time** | Better than polling, works with firewalls |
| **Exponential backoff reconnection** | Prevents server overload during outages |
| **localStorage for persistence** | Client-side, no server state needed |
| **Keyword-based type detection** | Fast, no LLM call, fully transparent |
| **3-tier validation** | CLI fast + Pattern good + LLM accurate |
| **Prompts in markdown** | Easier to maintain, version control friendly |

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Frontend build time | < 60s | 33.5s ✅ |
| Backend test time | < 2s | 0.62s ✅ |
| SSE latency | < 100ms | ~50ms ✅ |
| Validation time | < 1s | < 500ms ✅ |
| Export time | < 2s | < 1s ✅ |
| Session load | < 100ms | < 50ms ✅ |

---

## 🧪 Test Commands

```bash
# All tests
npm test                          # Frontend
python -m pytest                  # Backend

# Specific test file
npm run test -- useSSE.test.ts
pytest tests/1-UNIT/providers/test_config.py -v

# With coverage
npm run test:coverage
pytest --cov=app tests/

# Interactive UI
npm run test:ui

# Watch mode
npm test -- --watch
```

---

## 🔒 Security Checklist

- [ ] No shell=True in subprocess calls (tool_config.py)
- [ ] Input validation on all API endpoints
- [ ] CORS properly configured
- [ ] API keys not in version control
- [ ] XSS protection (sanitize SVG output)
- [ ] CSRF protection on state-changing endpoints
- [ ] Rate limiting on API endpoints
- [ ] SQL injection prevention (use ORM/parameterized queries)
- [ ] Session tokens validated on every request
- [ ] Logging doesn't expose sensitive data

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **DIAGRAMWIZARD_COMPLETE.md** | Full technical documentation |
| **DIAGRAMWIZARD_QUICK_REFERENCE.md** | This file - quick lookup |
| **IMPLEMENTATION_SIMPLIFIED.md** | Implementation status & history |
| **TESTING_INFRASTRUCTURE_COMPLETE.md** | Test setup details |
| **frontend/TESTING_GUIDE.md** | Detailed test specifications |
| **backend/app/utils/diagram_wizard/README.md** | Backend architecture |

---

## 🎓 Learning Path

**New to DiagramWizard?**

1. Read **DIAGRAMWIZARD_COMPLETE.md** Overview section (5 min)
2. Review **System Architecture** diagram (5 min)
3. Run development servers (5 min)
4. Try creating a simple diagram (5 min)
5. Examine **frontend/src/components/DiagramWizard/DiagramWizard.tsx** (10 min)
6. Examine **backend/app/utils/diagram_wizard/nodes.py** (10 min)

**Want to extend it?**

1. Read **Adding a New Diagram Provider** section
2. Review provider implementation examples (mermaidv1, d2v1)
3. Write tests first (TDD approach)
4. Implement provider class
5. Register in provider_registry

**Need to debug?**

1. Check **Debugging Guide** above
2. Enable DEBUG logging in backend config
3. Use browser DevTools Network tab
4. Read error messages carefully
5. Check relevant test file for expected behavior

---

## 🆘 Getting Help

1. **Check existing documentation** (this file + DIAGRAMWIZARD_COMPLETE.md)
2. **Look at test files** for usage examples
3. **Check error logs** (browser console + backend logs)
4. **Review recent commits** to understand changes
5. **Run tests** to identify breaking changes

---

## 📞 Common Contacts/Resources

- **API Docs**: http://localhost:8003/docs (Swagger UI)
- **LangGraph Docs**: https://docs.smith.langchain.com/langgraph
- **Mermaid Docs**: https://mermaid.js.org/
- **D2 Docs**: https://d2lang.com/
- **PlantUML Docs**: https://plantuml.com/

---

**Last Updated**: November 15, 2025
**Status**: ✅ Production Ready
**Test Status**: 44/44 tests passing ✅
