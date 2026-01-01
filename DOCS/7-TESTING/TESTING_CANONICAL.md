# DiagramWizard Testing - Canonical Reference

**Last Updated:** 2025-11-17
**Status:** ✅ Production Ready
**Canonical Document:** This is the single source of truth for testing strategy

---

## Overview

DiagramWizard uses **comprehensive testing** across frontend (Vitest) and backend (Pytest) with focus on unit, integration, and E2E coverage.

---

## Testing Stack

### Frontend

**Framework:** Vitest + React Testing Library
**Config:** `frontend/vitest.config.ts`
**Setup:** `frontend/src/test/setup.ts`

**Coverage Target:**
- Hooks: 80%+
- Services: 75%+
- Components: 70%+
- Overall: 70%+

### Backend

**Framework:** Pytest
**Location:** `backend/tests/`
**Current:** 44/44 tests passing ✅

**Coverage Target:**
- Nodes: 80%+
- Providers: 90%+
- Services: 75%+
- Overall: 75%+

---

## Test Organization

### Frontend Tests

```
frontend/src/
├── components/DiagramWizard/
│   ├── __tests__/
│   │   ├── DiagramWizardRefactored.test.tsx
│   │   ├── ModelSelectionScreen.test.tsx
│   │   ├── SystemDescriptionScreen.test.tsx
│   │   └── GenerationScreen.test.tsx
│   ├── hooks/
│   │   └── __tests__/
│   │       └── useDiagramSession.test.ts
│   └── services/
│       └── __tests__/
│           ├── validationService.test.ts
│           └── exportService.test.ts
└── test/
    ├── setup.ts
    └── mocks/
        ├── sseMock.ts
        └── apiMock.ts
```

### Backend Tests

```
backend/tests/
├── 1-UNIT/
│   ├── providers/
│   │   ├── test_mermaid.py (7 tests)
│   │   ├── test_d2.py (7 tests)
│   │   ├── test_plantuml.py (6 tests)
│   │   ├── test_registry.py (12 tests)
│   │   └── test_config.py (12 tests)
│   └── diagram_wizard/
│       ├── test_nodes.py (pending)
│       └── test_graph_state.py (pending)
├── 2-INTEGRATION/
│   ├── test_diagram_workflow.py (pending)
│   └── test_sse_stream.py (pending)
└── 3-E2E/
    └── test_complete_flow.py (pending)
```

---

## Testing Strategies

### 1. Unit Tests

**Purpose:** Test individual functions/components in isolation

**Frontend Example:**
```typescript
describe('ModelSelectionScreen', () => {
  it('should render 4 model cards', () => {
    render(<ModelSelectionScreen onSelect={jest.fn()} />);

    expect(screen.getByText('GPT-5')).toBeInTheDocument();
    expect(screen.getByText('Grok')).toBeInTheDocument();
    expect(screen.getByText('Claude')).toBeInTheDocument();
    expect(screen.getByText('Gemini')).toBeInTheDocument();
  });

  it('should call onSelect when model clicked', () => {
    const handleSelect = jest.fn();
    render(<ModelSelectionScreen onSelect={handleSelect} />);

    fireEvent.click(screen.getByText('GPT-5'));
    expect(handleSelect).toHaveBeenCalledWith('gpt5');
  });
});
```

**Backend Example:**
```python
def test_mermaid_validation():
    provider = MermaidV1Provider()

    # Valid code
    result = provider.validate("graph TD\nA-->B")
    assert result.is_valid is True

    # Invalid code
    result = provider.validate("invalid syntax")
    assert result.is_valid is False
    assert "syntax error" in result.error_message.lower()
```

### 2. Integration Tests

**Purpose:** Test interaction between components

**Frontend Example:**
```typescript
describe('DiagramWizard Flow', () => {
  it('should complete model selection → description → generation', async () => {
    const { getByText, getByPlaceholderText } = render(<DiagramWizardRefactored />);

    // Step 1: Select model
    fireEvent.click(getByText('GPT-5'));

    // Step 2: Enter description
    const textarea = getByPlaceholderText(/Describe the system/);
    fireEvent.change(textarea, { target: { value: 'E-commerce system' } });
    fireEvent.click(getByText('Start Conversation'));

    // Step 3: Wait for generation
    await waitFor(() => {
      expect(getByText('Preview')).toBeInTheDocument();
    });
  });
});
```

**Backend Example:**
```python
@pytest.mark.asyncio
async def test_diagram_generation_workflow():
    # Create session
    session_id = await create_diagram_session("E-commerce system")

    # Verify analysis
    state = await get_session_state(session_id)
    assert state["current_state"] == "CLARIFYING"

    # Submit clarification
    await submit_clarification(session_id, "Web-based shopping")

    # Verify generation
    state = await get_session_state(session_id)
    assert state["current_state"] == "COMPLETED"
    assert len(state["diagram_code"]) > 0
```

### 3. E2E Tests

**Purpose:** Test complete user workflows

**Example:**
```typescript
describe('Complete Diagram Generation', () => {
  it('should generate and export diagram', async () => {
    // 1. Launch app
    cy.visit('http://localhost:5173');

    // 2. Select model
    cy.contains('GPT-5').click();

    // 3. Enter description
    cy.get('textarea').type('User authentication system');
    cy.contains('Start Conversation').click();

    // 4. Wait for AI response
    cy.contains('Ready to proceed', { timeout: 30000 });
    cy.contains('Confirm Ready').click();

    // 5. Wait for generation
    cy.contains('Complete', { timeout: 60000 });

    // 6. Export diagram
    cy.contains('Export').click();
    cy.contains('SVG').click();

    // Verify download
    cy.readFile('cypress/downloads/diagram.svg').should('exist');
  });
});
```

---

## Running Tests

### Frontend

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific file
npm test DiagramWizardRefactored.test.tsx

# Watch mode
npm test -- --watch

# UI mode
npm run test:ui
```

### Backend

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Run specific directory
python -m pytest tests/1-UNIT/providers/ -v

# Run specific file
python -m pytest tests/1-UNIT/providers/test_mermaid.py -v

# Run with logging
python -m pytest tests/ -v -s
```

---

## Test Coverage Requirements

### Frontend Coverage Targets

| Component Type | Target | Current |
|----------------|--------|---------|
| Hooks | 80% | TBD |
| Services | 75% | TBD |
| Components | 70% | TBD |
| Utils | 80% | TBD |
| **Overall** | **70%** | **TBD** |

### Backend Coverage Targets

| Module | Target | Current |
|--------|--------|---------|
| Nodes | 80% | TBD |
| Providers | 90% | 100% ✅ |
| Services | 75% | TBD |
| API Endpoints | 70% | TBD |
| **Overall** | **75%** | **~60%** |

---

## Mocking Strategies

### Mock SSE Connection

```typescript
// sseMock.ts
export const mockSSE = {
  connect: jest.fn(),
  disconnect: jest.fn(),
  sendMessage: jest.fn(),
  simulateUpdate: (update: DiagramUpdate) => {
    // Trigger onMessage callback
  }
};

// In test
jest.mock('../../hooks/useSSE', () => ({
  useSSE: () => ({
    isConnected: true,
    messages: [],
    error: null,
    ...mockSSE
  })
}));
```

### Mock API Calls

```typescript
// apiMock.ts
export const mockDiagramApi = {
  startSession: jest.fn().mockResolvedValue({
    session_id: 'test-123',
    status: 'started'
  }),
  submitClarification: jest.fn().mockResolvedValue({
    status: 'clarification_received'
  }),
  confirmReady: jest.fn().mockResolvedValue({
    status: 'generating'
  })
};
```

### Mock Providers (Backend)

```python
# conftest.py
@pytest.fixture
def mock_provider():
    provider = MagicMock(spec=BaseDiagramProvider)
    provider.validate.return_value = ValidationResult(
        is_valid=True,
        error_message=None
    )
    provider.render.return_value = RenderResult(
        svg_output="<svg>...</svg>",
        success=True
    )
    return provider
```

---

## Test Data

### Fixtures

```typescript
// fixtures.ts
export const mockSessionState = {
  sessionId: 'test-session-123',
  status: 'clarifying' as const,
  chatHistory: [
    { role: 'user', content: 'Create a diagram' },
    { role: 'assistant', content: 'What type of system?' }
  ],
  score: 6,
  clarifications: [
    { question: 'What type?', answer: 'E-commerce' }
  ]
};

export const mockDiagramCode = `
graph TD
  A[User] --> B[Frontend]
  B --> C[API]
  C --> D[Database]
`;

export const mockSvgOutput = '<svg>...</svg>';
```

---

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
      - run: cd frontend && npm run test:coverage

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: cd backend && pip install -r requirements.txt
      - run: cd backend && pytest tests/ -v --cov
```

---

## Best Practices

### ✅ Do's

1. **Write tests first** (TDD approach)
2. **Test behavior, not implementation**
3. **Use descriptive test names**
4. **Keep tests independent**
5. **Mock external dependencies**
6. **Test edge cases**
7. **Maintain high coverage**

### ❌ Don'ts

1. **Don't test implementation details**
2. **Don't skip error cases**
3. **Don't use real API calls in tests**
4. **Don't make tests dependent on each other**
5. **Don't ignore flaky tests**

---

## Related Documents

- **Architecture:** [ARCHITECTURE_CANONICAL.md](./ARCHITECTURE_CANONICAL.md)
- **SSE Implementation:** [SSE_CANONICAL.md](./SSE_CANONICAL.md)
- **Frontend Guide:** `frontend/TESTING_GUIDE.md`
- **Enhancement Plan:** [DIAGRAMWIZARD_ENHANCEMENT_PLAN.md](./DIAGRAMWIZARD_ENHANCEMENT_PLAN.md)

---

**Note:** This is a canonical reference. When testing strategy changes, update THIS document first, then update references in other documents.
