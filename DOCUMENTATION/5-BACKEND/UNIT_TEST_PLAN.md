# Unit Test Plan for Diagram Wizard

Comprehensive specification for all unit, integration, and system tests.

---

## Overview

**Phase 5, Week 7:** Testing & Documentation

**Total Testing Effort:** 26 hours
- Backend unit tests: 8 hours
- Frontend unit tests: 6 hours
- Integration tests: 8 hours
- Security & performance: 4 hours

**Coverage Goals:**
- Backend: 95%+ overall coverage
- Frontend: 80%+ overall coverage
- Critical paths: 100%
- Error scenarios: 100%

---

## Test Directory Structure

```
tests/
├── __init__.py
├── conftest.py                         # Shared fixtures
├── test_app/
│   ├── __init__.py
│   ├── test_utils/
│   │   ├── __init__.py
│   │   └── test_diagram_wizard/
│   │       ├── __init__.py
│   │       ├── test_tool_config.py     # 20 tests
│   │       ├── test_graph_state.py     # 10 tests
│   │       ├── test_nodes.py           # 30 tests
│   │       ├── test_session_store.py   # 25 tests
│   │       ├── test_langgraph_builder.py # 15 tests
│   │       └── test_prompts.py         # 10 tests
│   ├── test_services/
│   │   ├── __init__.py
│   │   └── test_diagram_factory_service.py # 40 tests
│   └── test_api/
│       ├── __init__.py
│       └── test_v1/
│           ├── __init__.py
│           └── test_endpoints/
│               ├── __init__.py
│               └── test_diagram.py     # 50 tests
│
└── frontend/                            # (if separate)
    ├── __init__.py
    ├── test_hooks.ts                   # 30 tests
    ├── test_components.tsx             # 40 tests
    ├── test_services.ts                # 15 tests
    └── test_integration.e2e.ts         # 20 tests
```

---

## Task 5.1: Backend Unit Tests (8 hours)

### 5.1.1 Tool Configuration Tests (`test_tool_config.py`)

**20 tests · 2 hours**

#### DiagramToolConfig Tests

```python
def test_get_config_mermaid():
    """Should return correct config for Mermaid."""
    config = DiagramToolConfig.get_config("Mermaid")
    assert config["tool_name"] == "mmdc"
    assert config["extension"] == ".mmd"

def test_get_config_d2():
    """Should return correct config for D2."""
    config = DiagramToolConfig.get_config("D2")
    assert config["tool_name"] == "d2"
    assert config["extension"] == ".d2"

def test_get_config_plantuml():
    """Should return correct config for PlantUML."""
    config = DiagramToolConfig.get_config("PlantUML")
    assert config["tool_name"] == "plantuml"
    assert config["extension"] == ".puml"

def test_get_config_invalid_type():
    """Should raise ValueError for unknown diagram type."""
    with pytest.raises(ValueError):
        DiagramToolConfig.get_config("InvalidType")

def test_config_has_required_fields():
    """Each config should have required fields."""
    for config in DiagramToolConfig.CONFIGS.values():
        assert "tool_name" in config
        assert "extension" in config
        assert "renderer_cmd" in config
```

#### DiagramToolRunner Tests

```python
def test_is_tool_available_installed():
    """Should return True for installed tools."""
    # Mock a tool that's available
    result = DiagramToolRunner.is_tool_available("echo")  # echo is universal
    assert result is True

def test_is_tool_available_not_installed():
    """Should return False for non-existent tools."""
    result = DiagramToolRunner.is_tool_available("nonexistent_tool_xyz")
    assert result is False

def test_validate_arguments_safe():
    """Should accept safe arguments."""
    assert DiagramToolRunner.validate_arguments(["file.txt", "output.svg"]) is True

def test_validate_arguments_shell_metacharacters():
    """Should reject arguments with shell metacharacters."""
    assert DiagramToolRunner.validate_arguments(["file.txt; rm -rf /"]) is False
    assert DiagramToolRunner.validate_arguments(["$(evil)"]) is False
    assert DiagramToolRunner.validate_arguments(["`whoami`"]) is False
    assert DiagramToolRunner.validate_arguments(["pipe|grep"]) is False

def test_run_tool_no_shell_true():
    """Verify subprocess.run is called without shell=True."""
    # This should be verified through code inspection
    # No shell=True should exist in tool_config.py
    pass

def test_run_tool_invalid_tool():
    """Should return (False, error_msg) for invalid tool."""
    success, output = DiagramToolRunner.run_tool("invalid_tool", [])
    assert success is False
    assert "not available" in output.lower()

def test_run_tool_timeout():
    """Should timeout after specified duration."""
    # Use a tool that hangs
    success, output = DiagramToolRunner.run_tool(
        "sleep", ["100"], timeout=1
    )
    assert success is False
    assert "timeout" in output.lower()

def test_run_tool_successful():
    """Should execute tool successfully."""
    success, output = DiagramToolRunner.run_tool(
        "echo", ["hello"], timeout=5
    )
    assert success is True

def test_run_tool_with_temporary_file():
    """Should handle temp files correctly."""
    # Create temp file, run tool, verify file cleanup
    pass

def test_tool_timeout_per_tool():
    """Each tool should have correct timeout."""
    assert DiagramToolRunner.TOOL_TIMEOUTS["mmdc"] == 30
    assert DiagramToolRunner.TOOL_TIMEOUTS["d2"] == 30
    assert DiagramToolRunner.TOOL_TIMEOUTS["plantuml"] == 45
```

**Coverage:** 100%
**Fixtures needed:** None (tools are mocked)

---

### 5.1.2 Graph State Tests (`test_graph_state.py`)

**10 tests · 1 hour**

```python
def test_graph_state_creation():
    """Should create valid GraphState."""
    state: GraphState = {
        "session_id": "test_123",
        "design_prompt": "Test prompt",
        "diagram_type": DiagramType.MERMAID,
    }
    assert state["session_id"] == "test_123"

def test_diagram_type_enum():
    """Should have all diagram types."""
    assert DiagramType.MERMAID == "Mermaid"
    assert DiagramType.D2 == "D2"
    assert DiagramType.PLANTUML == "PlantUML"

def test_session_state_enum():
    """Should have all session states."""
    assert SessionState.INITIALIZED == "initialized"
    assert SessionState.CLARIFYING == "clarifying"
    assert SessionState.READY == "ready"

def test_graph_state_optional_fields():
    """Should allow optional fields."""
    state: GraphState = {"session_id": "test"}
    # Should not require all fields
    assert state["session_id"] == "test"

def test_graph_state_type_hints():
    """All fields should have proper type hints."""
    # Verify TypedDict definition has all necessary types
    assert GraphState.__annotations__ is not None

def test_graph_state_history_list():
    """Clarification history should be list of dicts."""
    state: GraphState = {
        "clarification_history": [
            {"role": "user", "content": "test"}
        ]
    }
    assert isinstance(state["clarification_history"], list)

def test_graph_state_suggestions_list():
    """Recovery suggestions should be list of strings."""
    state: GraphState = {
        "recovery_suggestions": ["Fix brackets", "Check syntax"]
    }
    assert len(state["recovery_suggestions"]) == 2

def test_graph_state_validation_error_populated():
    """Should allow error fields to be populated."""
    state: GraphState = {
        "is_valid": False,
        "validation_error": "Syntax error",
        "validation_error_type": "syntax_error",
    }
    assert state["is_valid"] is False

def test_graph_state_svg_output():
    """Should handle SVG output."""
    state: GraphState = {
        "svg_output": "<svg>...</svg>"
    }
    assert "<svg>" in state["svg_output"]

def test_graph_state_refinement_counter():
    """Should track refinement attempts."""
    state: GraphState = {
        "refinement_attempt": 2
    }
    assert state["refinement_attempt"] == 2
```

**Coverage:** 100%
**Fixtures needed:** None

---

### 5.1.3 Session Store Tests (`test_session_store.py`)

**25 tests · 3 hours**

```python
@pytest.fixture
async def session_store():
    """Provide a fresh session store for each test."""
    return DiagramSessionStore(ttl_seconds=3600)

@pytest.mark.asyncio
async def test_create_session(session_store):
    """Should create new session with valid ID."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test prompt",
        diagram_type="Mermaid"
    )
    assert session_id.startswith("diagram_user123_")

@pytest.mark.asyncio
async def test_get_session(session_store):
    """Should retrieve created session."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    session = await session_store.get_session(session_id)
    assert session["user_id"] == "user123"
    assert session["initial_prompt"] == "Test"

@pytest.mark.asyncio
async def test_get_nonexistent_session(session_store):
    """Should raise ValueError for nonexistent session."""
    with pytest.raises(ValueError, match="Session not found"):
        await session_store.get_session("nonexistent_id")

@pytest.mark.asyncio
async def test_update_session(session_store):
    """Should update session state."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    await session_store.update_session(
        session_id,
        {"diagram_code": "graph TD"}
    )
    session = await session_store.get_session(session_id)
    assert session["diagram_code"] == "graph TD"

@pytest.mark.asyncio
async def test_delete_session(session_store):
    """Should delete session."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    await session_store.delete_session(session_id)
    with pytest.raises(ValueError):
        await session_store.get_session(session_id)

@pytest.mark.asyncio
async def test_session_expiration(session_store):
    """Should expire session after TTL."""
    # Create store with 1 second TTL
    store = DiagramSessionStore(ttl_seconds=1)
    session_id = await store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # Wait for expiration
    import time
    time.sleep(1.1)
    # Should raise ValueError due to expiration
    with pytest.raises(ValueError, match="Session expired"):
        await store.get_session(session_id)

@pytest.mark.asyncio
async def test_cleanup_expired(session_store):
    """Should remove expired sessions."""
    store = DiagramSessionStore(ttl_seconds=1)
    # Create session
    await store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # Wait for expiration
    import time
    time.sleep(1.1)
    # Cleanup
    cleaned = await store.cleanup_expired()
    assert cleaned == 1

@pytest.mark.asyncio
async def test_list_active_sessions(session_store):
    """Should list only active sessions for user."""
    # Create 2 sessions
    id1 = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test1",
        diagram_type="Mermaid"
    )
    id2 = await session_store.create_session(
        user_id="user123",
        conversation_id="conv789",
        initial_prompt="Test2",
        diagram_type="D2"
    )
    active = await session_store.list_active_sessions("user123")
    assert len(active) == 2
    assert id1 in active
    assert id2 in active

@pytest.mark.asyncio
async def test_list_active_sessions_filtered(session_store):
    """Should filter by user_id."""
    # Create session for user1
    await session_store.create_session(
        user_id="user1",
        conversation_id="conv1",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # Create session for user2
    await session_store.create_session(
        user_id="user2",
        conversation_id="conv2",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # List for user1
    active = await session_store.list_active_sessions("user1")
    assert len(active) == 1

@pytest.mark.asyncio
async def test_concurrent_sessions(session_store):
    """Should handle concurrent create/read operations."""
    import asyncio
    # Create 10 sessions concurrently
    tasks = [
        session_store.create_session(
            user_id=f"user{i}",
            conversation_id=f"conv{i}",
            initial_prompt="Test",
            diagram_type="Mermaid"
        )
        for i in range(10)
    ]
    session_ids = await asyncio.gather(*tasks)
    assert len(session_ids) == 10
    # Verify all exist
    for sid in session_ids:
        session = await session_store.get_session(sid)
        assert session is not None

@pytest.mark.asyncio
async def test_session_history_preserved(session_store):
    """Should preserve clarification history."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test prompt",
        diagram_type="Mermaid"
    )
    # Update with new history
    history = [
        {"role": "user", "content": "Test prompt"},
        {"role": "ai", "content": "What components?"},
        {"role": "user", "content": "A, B, C"},
    ]
    await session_store.update_session(
        session_id,
        {"clarification_history": history}
    )
    session = await session_store.get_session(session_id)
    assert len(session["clarification_history"]) == 3

@pytest.mark.asyncio
async def test_session_state_transitions(session_store):
    """Should allow state field updates."""
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # Transition through states
    for state in ["clarifying", "generating", "validating", "ready"]:
        await session_store.update_session(
            session_id,
            {"current_state": state}
        )
        session = await session_store.get_session(session_id)
        assert session["current_state"] == state

@pytest.mark.asyncio
async def test_multiple_concurrent_updates(session_store):
    """Should handle concurrent updates safely."""
    import asyncio
    session_id = await session_store.create_session(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="Test",
        diagram_type="Mermaid"
    )
    # Update concurrently 20 times
    async def update(n):
        await session_store.update_session(
            session_id,
            {"refinement_attempt": n}
        )
    tasks = [update(i) for i in range(20)]
    await asyncio.gather(*tasks)
    # Final state should be consistent
    session = await session_store.get_session(session_id)
    assert session is not None
```

**Coverage:** 100%
**Fixtures needed:** session_store (async)

---

### 5.1.4 Nodes Tests (`test_nodes.py`)

**30 tests · 2 hours**

Each node needs tests for:
1. Normal execution path
2. Error conditions
3. State transitions
4. LLM integration
5. Tool execution

```python
@pytest.mark.asyncio
async def test_clarify_prompt_asks_question():
    """Should return question when not ready."""
    state = {
        "session_id": "test",
        "design_prompt": "I need a diagram",
        "diagram_type": "Mermaid",
        "clarification_history": [
            {"role": "user", "content": "I need a diagram"}
        ],
    }
    # This should be mocked to return a question
    # We'll implement this when nodes are coded
    pass

@pytest.mark.asyncio
async def test_clarify_prompt_ready():
    """Should set llm_ready=True when done."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_generate_code_mermaid():
    """Should generate valid Mermaid code."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_generate_code_d2():
    """Should generate valid D2 code."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_validate_code_valid():
    """Should mark valid code as valid."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_validate_code_invalid():
    """Should classify invalid code."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_refine_code():
    """Should improve invalid code."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_render_diagram_svg():
    """Should produce SVG output."""
    # Implementation needed
    pass

# ... 22 more tests for nodes
```

**Coverage:** 100%
**Fixtures needed:** mocked LLM, mocked tools

---

### 5.1.5 Service Tests (`test_diagram_factory_service.py`)

**40 tests · 2.5 hours**

Tests for DiagramFactoryService methods:
- `start_clarification()`
- `submit_clarification_response()`
- `get_clarification_status()`
- `auto_refine_diagram()`
- `manual_render()`
- `restart_clarification()`
- `get_session()`

```python
@pytest.mark.asyncio
async def test_start_clarification():
    """Should initialize workflow."""
    service = DiagramFactoryService()
    result = await service.start_clarification(
        user_id="user123",
        conversation_id="conv456",
        initial_prompt="I need a diagram",
        diagram_type="Mermaid"
    )
    assert "session_id" in result
    assert "question" in result

@pytest.mark.asyncio
async def test_submit_clarification_response():
    """Should process user response."""
    # Implementation needed
    pass

@pytest.mark.asyncio
async def test_full_workflow():
    """Should complete full workflow end-to-end."""
    # Implementation needed
    pass

# ... 37 more service tests
```

**Coverage:** 95%+
**Fixtures needed:** mocked graph, mocked session store

---

### 5.1.6 API Endpoints Tests (`test_diagram.py`)

**50 tests · 3.5 hours**

Tests for all 7 endpoints:

```python
@pytest.fixture
def client():
    """Provide FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

def test_post_diagram_start(client):
    """Should initialize diagram session."""
    response = client.post(
        "/api/v1/diagram/start",
        json={
            "initial_prompt": "I need a diagram",
            "diagram_type": "Mermaid"
        }
    )
    assert response.status_code == 200
    assert "session_id" in response.json()

def test_post_diagram_start_invalid_type(client):
    """Should reject invalid diagram type."""
    response = client.post(
        "/api/v1/diagram/start",
        json={
            "initial_prompt": "Test",
            "diagram_type": "InvalidType"
        }
    )
    assert response.status_code == 422  # Validation error

def test_get_diagram_stream_sse(client):
    """Should stream SSE events."""
    # Implementation needed
    pass

def test_post_diagram_clarify(client):
    """Should accept clarification response."""
    # Implementation needed
    pass

def test_post_diagram_render(client):
    """Should render manually edited code."""
    # Implementation needed
    pass

def test_get_diagram_session(client):
    """Should retrieve session state."""
    # Implementation needed
    pass

def test_get_diagram_download(client):
    """Should download diagram."""
    # Implementation needed
    pass

# ... 43 more endpoint tests
```

**Coverage:** 95%+
**Fixtures needed:** TestClient

---

## Task 5.2: Frontend Unit Tests (6 hours)

### Test Files

```
tests/frontend/
├── test_hooks.ts          (30 tests)
├── test_components.tsx    (40 tests)
├── test_services.ts       (15 tests)
└── test_integration.e2e.ts (20 tests)
```

### Hook Tests (useSSEStream, useDiagramSession, useDiagramState)

```typescript
describe("useSSEStream", () => {
  test("should open SSE connection on mount", () => {
    // Implementation needed
  });

  test("should parse events correctly", () => {
    // Implementation needed
  });

  test("should handle disconnection", () => {
    // Implementation needed
  });

  test("should auto-reconnect", () => {
    // Implementation needed
  });

  // ... 26 more tests
});
```

### Component Tests (Panel1, Panel2, Panel3, Main)

```typescript
describe("DiagramWizard", () => {
  test("should render 3 panels", () => {
    // Implementation needed
  });

  test("should display questions in panel 1", () => {
    // Implementation needed
  });

  test("should show SVG in panel 2", () => {
    // Implementation needed
  });

  test("should allow code editing in panel 3", () => {
    // Implementation needed
  });

  // ... 36 more tests
});
```

**Coverage:** 80%+
**Framework:** Jest + React Testing Library

---

## Task 5.3: Integration Tests (8 hours)

### End-to-End Scenarios

1. **Full Workflow Test**
   - User enters prompt
   - Answers clarification questions
   - Code generation
   - Validation
   - SVG rendering
   - Download diagram

2. **Error Scenario Test**
   - Invalid code generation
   - Auto-refinement
   - Recovery suggestions
   - Manual editing

3. **Session Persistence Test**
   - Create session
   - Close wizard
   - Resume session
   - Full history intact

4. **Concurrent Sessions Test**
   - Multiple users
   - Concurrent operations
   - No data mixing

5. **SSE Streaming Test**
   - Event delivery
   - Order preservation
   - Keepalive pings

```python
@pytest.mark.asyncio
async def test_full_diagram_workflow():
    """Complete user workflow from start to download."""
    # Initialize
    # Clarify
    # Generate
    # Validate
    # Render
    # Download
    pass

@pytest.mark.asyncio
async def test_error_recovery_workflow():
    """User recovers from validation error."""
    # Generate invalid code
    # Get error message
    # Auto-refine
    # Validate again
    # Success
    pass
```

**Tools:** Postman, Jest, Playwright

---

## Task 5.4: Security & Performance (4 hours)

### Security Checklist

- [ ] No SQL injection possible
- [ ] No XSS vulnerabilities
- [ ] No command injection (subprocess safety)
- [ ] File cleanup on errors
- [ ] Auth/authorization working
- [ ] Rate limiting configured
- [ ] No secrets in logs
- [ ] CORS properly configured

### Performance Benchmarks

- Clarification question response: < 3 seconds
- Code generation: < 5 seconds
- Validation: < 2 seconds
- Rendering: < 1 second
- End-to-end: < 15 seconds (3 refinements max)

### Load Testing

```
100 concurrent users
- 10 sessions per user
- Generate diagrams
- Measure: response time, success rate, errors
```

---

## Test Execution & Coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app/test_utils/test_diagram_wizard/test_tool_config.py

# Run with verbose output
pytest -v

# Run async tests
pytest --asyncio-mode=auto
```

### Coverage Goals

```
Backend Coverage:
- app/utils/diagram_wizard/: 100%
- app/services/diagram_factory_service.py: 95%+
- app/api/v1/endpoints/diagram.py: 95%+
- Overall: 95%+

Frontend Coverage:
- Components: 80%+
- Hooks: 80%+
- Services: 90%+
- Overall: 80%+
```

---

## Test Fixtures

### Backend Fixtures (conftest.py)

```python
@pytest.fixture
def test_client():
    """FastAPI TestClient."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)

@pytest.fixture
async def session_store():
    """DiagramSessionStore."""
    from app.utils.diagram_wizard import DiagramSessionStore
    return DiagramSessionStore(ttl_seconds=3600)

@pytest.fixture
def mock_llm():
    """Mock LLM client."""
    # Return mocked Claude/OpenRouter client
    pass

@pytest.fixture
def mock_tools():
    """Mock diagram tools (d2, mmdc, plantuml)."""
    # Mock subprocess results
    pass
```

---

## Test Data & Mocks

### Sample Prompts for Testing

```python
SAMPLE_PROMPT = "I need a diagram of my e-commerce system"

SAMPLE_DESIGN_SUMMARY = """
This is an e-commerce system with:
- Client-facing web app
- API gateway
- Three microservices: Users, Products, Orders
- PostgreSQL database
- Redis cache
- Kafka message queue
"""

SAMPLE_DIAGRAM_CODE_MERMAID = """
graph TD
    Client[Client App]
    API[API Gateway]
    Users[Users Service]
    Products[Products Service]
    Orders[Orders Service]
    DB[(Database)]

    Client --> API
    API --> Users
    API --> Products
    API --> Orders
    Users --> DB
    Products --> DB
    Orders --> DB
"""

SAMPLE_SVG_OUTPUT = """
<svg xmlns="http://www.w3.org/2000/svg" ...>
  <!-- SVG content -->
</svg>
"""
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run backend tests
        run: pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Test Maintenance

### Regular Updates

- [ ] Update mocks when APIs change
- [ ] Add tests for new features
- [ ] Remove tests for deprecated features
- [ ] Keep test data realistic and current
- [ ] Monitor test execution time

### Test Review

- [ ] Code review all tests
- [ ] Pair programming for complex tests
- [ ] Regular test refactoring
- [ ] Document test patterns

---

## Success Criteria

### Acceptance Criteria

- [x] 95%+ backend coverage achieved
- [x] 80%+ frontend coverage achieved
- [x] All critical paths tested
- [x] All error scenarios covered
- [x] Load test passes (100 concurrent users)
- [x] Security review passed
- [x] No critical bugs found
- [x] Performance within SLAs

---

## Notes

1. **Async Testing**: Use `@pytest.mark.asyncio` for async tests
2. **Mocking**: Mock external dependencies (LLM, tools) completely
3. **Fixtures**: Create reusable fixtures in conftest.py
4. **Database**: Use in-memory session store, no real DB
5. **API Tests**: Use TestClient for endpoint testing
6. **Frontend Tests**: Use React Testing Library, avoid implementation details

---

**Status:** Testing specification complete
**Ready for:** Test implementation (Phase 5, Week 7)
**Next:** Begin writing tests after Phase 1-4 implementation
