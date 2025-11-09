# Unit Test Plan Summary

Comprehensive testing specification for Diagram Wizard implementation.

---

## Quick Overview

| Aspect | Details |
|--------|---------|
| **Total Test Effort** | 26 hours |
| **Backend Tests** | 165+ test cases |
| **Frontend Tests** | 105+ test cases |
| **Coverage Target (Backend)** | 95%+ |
| **Coverage Target (Frontend)** | 80%+ |
| **Phase** | Phase 5 (Week 7) |

---

## Test Breakdown

### Backend Unit Tests (8 hours)

**6 Test Files · 165 test cases**

| File | Tests | Hours | Coverage |
|------|-------|-------|----------|
| `test_tool_config.py` | 20 | 2.0 | 100% |
| `test_graph_state.py` | 10 | 1.0 | 100% |
| `test_session_store.py` | 25 | 3.0 | 100% |
| `test_nodes.py` | 30 | 2.0 | 100% |
| `test_langgraph_builder.py` | 15 | 1.0 | 100% |
| `test_prompts.py` | 10 | 1.0 | 100% |
| **Backend API** | **50** | **3.5** | **95%+** |
| **Backend Service** | **40** | **2.5** | **95%+** |

### Frontend Unit Tests (6 hours)

**4 Test Files · 105 test cases**

| Component | Tests | Hours | Coverage |
|-----------|-------|-------|----------|
| Hooks | 30 | 1.5 | 80%+ |
| Components | 40 | 2.5 | 80%+ |
| Services | 15 | 1.0 | 90%+ |
| Integration | 20 | 1.0 | 80%+ |

### Integration Tests (8 hours)

**7 Major Scenarios · 60+ test cases**

1. Full workflow (prompt → render → download)
2. Error recovery (invalid → refine → valid)
3. Session persistence (close → resume)
4. Concurrent users (multiple simultaneous sessions)
5. SSE streaming (real-time events)
6. Manual editing (code changes → preview)
7. Multi-format diagrams (Mermaid, D2, PlantUML)

### Security & Performance (4 hours)

**Checklist + Load Testing**

Security:
- Command injection prevention ✓
- File safety ✓
- No hardcoded secrets ✓
- Auth/authz ✓

Performance:
- Clarification < 3s
- Generation < 5s
- Validation < 2s
- Rendering < 1s
- End-to-end < 15s

---

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_app/
│   ├── test_utils/
│   │   └── test_diagram_wizard/
│   │       ├── test_tool_config.py         ← 20 tests
│   │       ├── test_graph_state.py         ← 10 tests
│   │       ├── test_session_store.py       ← 25 tests
│   │       ├── test_nodes.py               ← 30 tests
│   │       ├── test_langgraph_builder.py   ← 15 tests
│   │       └── test_prompts.py             ← 10 tests
│   ├── test_services/
│   │   └── test_diagram_factory_service.py ← 40 tests
│   └── test_api/
│       └── test_v1/
│           └── test_endpoints/
│               └── test_diagram.py         ← 50 tests
│
└── frontend/
    ├── test_hooks.ts                       ← 30 tests
    ├── test_components.tsx                 ← 40 tests
    ├── test_services.ts                    ← 15 tests
    └── test_integration.e2e.ts             ← 20 tests
```

---

## Test Categories by Type

### Unit Tests (155 tests)

Test individual components in isolation:
- Tool configuration
- Graph state schema
- Session store operations
- LangGraph nodes
- Graph builder
- Service methods
- API endpoints

### Integration Tests (60+ tests)

Test components working together:
- Full workflows
- Error recovery
- Session lifecycle
- Concurrent operations
- SSE streaming
- Multi-format support

### System Tests (Included)

Test entire system:
- End-to-end workflows
- Performance benchmarks
- Load testing (100 concurrent users)
- Security posture

---

## Backend Test Details

### 1. Tool Configuration Tests (20 tests)

**What's tested:**
- ✓ Tool configs for each format (Mermaid, D2, PlantUML)
- ✓ Safe subprocess execution (NO shell=True)
- ✓ Argument validation (rejects shell metacharacters)
- ✓ Timeout enforcement
- ✓ File cleanup
- ✓ Tool availability detection

**Example tests:**
```python
test_get_config_mermaid()
test_get_config_d2()
test_validate_arguments_safe()
test_validate_arguments_shell_metacharacters()
test_run_tool_timeout()
test_run_tool_successful()
test_tool_cleanup()
```

**Coverage:** 100%

---

### 2. Graph State Tests (10 tests)

**What's tested:**
- ✓ TypedDict creation
- ✓ Enum values (DiagramType, SessionState)
- ✓ Optional fields
- ✓ Type hints
- ✓ List/dict fields
- ✓ State transitions

**Example tests:**
```python
test_graph_state_creation()
test_diagram_type_enum()
test_session_state_enum()
test_graph_state_optional_fields()
test_graph_state_history_list()
```

**Coverage:** 100%

---

### 3. Session Store Tests (25 tests)

**What's tested:**
- ✓ Create/read/update/delete operations
- ✓ TTL expiration
- ✓ Async operations
- ✓ Thread safety (asyncio.Lock)
- ✓ Concurrent access
- ✓ History preservation
- ✓ State transitions
- ✓ List active sessions

**Example tests:**
```python
test_create_session()
test_get_session()
test_update_session()
test_delete_session()
test_session_expiration()
test_cleanup_expired()
test_concurrent_sessions()
test_list_active_sessions()
```

**Coverage:** 100%

---

### 4. Node Tests (30 tests)

**What's tested for each of 5 nodes:**
- ✓ Normal execution path
- ✓ Error conditions
- ✓ State transitions
- ✓ LLM integration (mocked)
- ✓ Tool execution (mocked)

**Nodes tested:**
1. `clarify_prompt()` - 6 tests
2. `generate_code()` - 6 tests
3. `validate_code()` - 6 tests
4. `refine_code()` - 6 tests
5. `render_diagram()` - 6 tests

**Coverage:** 100%

---

### 5. Service Tests (40 tests)

**What's tested:**
- ✓ start_clarification()
- ✓ submit_clarification_response()
- ✓ auto_refine_diagram()
- ✓ manual_render()
- ✓ restart_clarification()
- ✓ get_session()
- ✓ Full workflows
- ✓ Error handling
- ✓ State management

**Coverage:** 95%+

---

### 6. API Endpoint Tests (50 tests)

**What's tested for each of 7 endpoints:**

1. **POST /diagram/start** (5 tests)
   - Valid request
   - Invalid diagram type
   - Missing fields
   - Response format
   - Error handling

2. **GET /diagram/stream/{id}** (8 tests)
   - SSE connection
   - Event parsing
   - Event ordering
   - Disconnection
   - Reconnection
   - Keepalive pings
   - Multiple subscribers
   - Error events

3. **POST /diagram/clarify** (7 tests)
   - Valid response
   - Invalid session
   - Response ordering
   - State progression
   - Error handling
   - Concurrent responses
   - Timeout handling

4. **POST /diagram/render** (6 tests)
   - Valid code
   - Invalid code
   - Quick feedback
   - Error display
   - Concurrent renders
   - File cleanup

5. **POST /diagram/restart** (5 tests)
   - Restart logic
   - Session reset
   - History preservation
   - State reset
   - Error handling

6. **GET /diagram/session/{id}** (7 tests)
   - Session retrieval
   - Complete state
   - History included
   - Current state
   - Error on missing
   - Error on expired
   - Concurrent reads

7. **GET /diagram/{id}/download** (7 tests)
   - SVG download
   - PNG download
   - PDF download
   - File generation
   - Error handling
   - Cleanup
   - Concurrent downloads

**Coverage:** 95%+

---

## Frontend Test Details

### Hooks Tests (30 tests)

**useSSEStream Hook:**
- Connection establishment
- Event parsing
- Disconnection handling
- Auto-reconnect
- Error handling

**useDiagramSession Hook:**
- Session loading
- State updates
- Resume functionality
- Error handling

**useDiagramState Hook:**
- State transitions
- Event processing
- Invalid transitions
- State consistency

---

### Component Tests (40 tests)

**DiagramWizard (Main):**
- 3-panel layout renders
- Panel sizing correct
- State propagation
- Event handling
- Error boundaries
- Closing behavior

**Panel1_Chat:**
- Question display
- Answer input
- Submit button
- History scrolling
- Phase indicator
- Restart button

**Panel2_Preview:**
- SVG rendering
- Download button
- Error display
- Recovery suggestions
- Loading state
- Sizing/centering

**Panel3_CodeEditor:**
- Code display
- Syntax highlighting
- Editability states
- Line numbers
- Language selection
- Save functionality

---

### Service Tests (15 tests)

**diagramApi service:**
- startDiagram()
- submitClarification()
- renderCode()
- restartClarification()
- getSession()
- downloadDiagram()

**Error handling:**
- API errors
- Network errors
- Validation errors
- Proper error messages

---

### Integration Tests (20 tests)

**E2E Workflows:**
1. User fills prompt, answers questions, sees diagram
2. User edits code, sees live preview
3. User downloads diagram in multiple formats
4. User closes and resumes session
5. Error recovery workflow

**Tools:** Playwright

---

## Integration Test Scenarios

### Scenario 1: Full Workflow
```
User enters prompt
  ↓
Selects diagram type
  ↓
Answers clarification questions
  ↓
AI generates code
  ↓
Code validated
  ↓
SVG rendered
  ↓
User downloads
```
**Duration:** < 15 seconds
**Tests:** 12 checkpoints

### Scenario 2: Error Recovery
```
Code generation fails
  ↓
Error message displayed
  ↓
Auto-refinement triggered
  ↓
Code re-validated
  ↓
Success
```
**Duration:** < 10 seconds
**Tests:** 8 checkpoints

### Scenario 3: Manual Editing
```
Diagram displayed
  ↓
User edits code in Panel 3
  ↓
Live preview updates
  ↓
Valid/invalid feedback
  ↓
Can save/revert
```
**Duration:** < 5 seconds
**Tests:** 6 checkpoints

### Scenario 4: Session Persistence
```
Create session
  ↓
Progress through clarification
  ↓
Close browser
  ↓
Reopen & resume
  ↓
Full history intact
```
**Duration:** Session lifetime
**Tests:** 5 checkpoints

---

## Test Fixtures

### Backend Fixtures

```python
@pytest.fixture
def test_client():
    """FastAPI TestClient"""

@pytest.fixture
async def session_store():
    """DiagramSessionStore instance"""

@pytest.fixture
def mock_llm():
    """Mocked LLM client"""

@pytest.fixture
def mock_tools():
    """Mocked diagram tools"""
```

### Frontend Fixtures

```typescript
@beforeEach(() => {
  // Setup mock SSE
  // Setup mock API
  // Clear state
});
```

---

## Test Execution

### Running Backend Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific file
pytest tests/test_app/test_utils/test_diagram_wizard/test_tool_config.py

# Async tests
pytest --asyncio-mode=auto
```

### Running Frontend Tests
```bash
# All tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Running Integration Tests
```bash
# All integration tests
pytest tests/test_integration/ -v

# Specific scenario
pytest tests/test_integration/test_full_workflow.py
```

---

## Coverage Report Structure

```
Backend Coverage:
├── app/utils/diagram_wizard/
│   ├── __init__.py: 100%
│   ├── graph_state.py: 100%
│   ├── tool_config.py: 100%
│   ├── nodes.py: 100%
│   ├── session_store.py: 100%
│   └── langgraph_builder.py: 100%
├── app/services/diagram_factory_service.py: 95%+
├── app/api/v1/endpoints/diagram.py: 95%+
└── TOTAL: 95%+

Frontend Coverage:
├── components/: 80%+
├── hooks/: 80%+
├── services/: 90%+
└── TOTAL: 80%+
```

---

## Performance Benchmarks (Task 5.4)

### Response Times

| Operation | Target | Acceptable |
|-----------|--------|-----------|
| Clarification question | < 3s | < 5s |
| Code generation | < 5s | < 7s |
| Validation | < 2s | < 3s |
| Rendering | < 1s | < 2s |
| **End-to-end** | **< 15s** | **< 20s** |

### Load Test (100 concurrent users)

- Success rate: > 95%
- p95 latency: < 8s
- p99 latency: < 15s
- Error rate: < 1%
- No memory leaks

---

## Security Validation (Task 5.4)

### Checklist

- [x] No command injection (subprocess safety)
- [x] File cleanup on errors
- [x] No hardcoded secrets
- [x] CORS configured properly
- [x] Auth/authorization working
- [x] Rate limiting in place
- [x] Input validation
- [x] Output encoding

---

## Success Criteria Summary

| Criterion | Target | Status |
|-----------|--------|--------|
| Backend coverage | 95%+ | Planned |
| Frontend coverage | 80%+ | Planned |
| All critical paths tested | 100% | Planned |
| Error scenarios covered | 100% | Planned |
| Load test passes | 100 users | Planned |
| Security review passed | All items | Planned |
| Performance SLAs met | All targets | Planned |
| No critical bugs | 0 found | Planned |

---

## Timeline

| Task | Duration | Week | Deliverables |
|------|----------|------|--------------|
| 5.1 Backend unit | 8h | 7 | 165 tests, 95%+ coverage |
| 5.2 Frontend unit | 6h | 7 | 105 tests, 80%+ coverage |
| 5.3 Integration | 8h | 7 | 60+ tests, all scenarios |
| 5.4 Security & perf | 4h | 7 | Audit report, benchmarks |
| 5.5 Documentation | 4h | 7 | All guides & references |

---

## Related Documents

- **IMPLEMENTATION_PLAN.MD** - Task 5.1-5.5 specifications
- **UNIT_TEST_PLAN.md** - This detailed plan
- **UPGRADEPLAN.MD** - System architecture

---

**Status:** Test planning complete
**Ready for:** Test implementation (Phase 5, Week 7)
**Total Test Cases:** 270+
**Estimated Execution Time:** ~45 minutes (all tests)
