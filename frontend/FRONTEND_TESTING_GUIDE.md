# Frontend Model Selection Testing Guide

## Overview

This guide describes how to test the model selection feature in the DiagramWizard component. The feature allows users to select from 4 AI models (GPT-5, Grok, Claude, Gemini) at the beginning of a diagram generation session.

---

## Test Infrastructure

### Setup
- **Test Runner:** Vitest (configured in `vitest.config.ts`)
- **Testing Library:** React Testing Library + Vitest
- **Environment:** jsdom
- **Setup File:** `src/test/setup.ts` (includes localStorage mock, EventSource mock, etc.)

### Run Tests
```bash
# Run all tests
npm run test

# Run tests in watch mode (development)
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

---

## 1. Unit Test: ModelSelector Component

### Test File Location
`frontend/src/components/DiagramWizard/ModelSelector.test.tsx`

### What to Test
- Component renders all 4 model cards with correct information
- Card details display (icon, name, description, strengths)
- onSelect callback is triggered with correct modelId
- Loading state disables buttons
- Visual styling and layout

### Sample Test Cases

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { vi, describe, test, expect } from 'vitest';
import { ModelSelector } from './ModelSelector';

describe('ModelSelector Component', () => {

  test('renders 4 model cards with correct titles', () => {
    render(<ModelSelector onSelect={vi.fn()} />);

    expect(screen.getByText('GPT-5')).toBeInTheDocument();
    expect(screen.getByText('Grok')).toBeInTheDocument();
    expect(screen.getByText('Claude Sonnet 4.5')).toBeInTheDocument();
    expect(screen.getByText('Gemini 2.5 Pro')).toBeInTheDocument();
  });

  test('renders model descriptions', () => {
    render(<ModelSelector onSelect={vi.fn()} />);

    expect(screen.getByText(/Deep contextual analysis/i)).toBeInTheDocument();
    expect(screen.getByText(/Fast, deterministic analysis/i)).toBeInTheDocument();
  });

  test('calls onSelect with modelId when button clicked', () => {
    const mockOnSelect = vi.fn();
    render(<ModelSelector onSelect={mockOnSelect} />);

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[0]); // Click first (GPT-5)

    expect(mockOnSelect).toHaveBeenCalledWith('gpt5');
  });

  test('disables buttons when loading=true', () => {
    render(<ModelSelector onSelect={vi.fn()} loading={true} />);

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    buttons.forEach(btn => expect(btn).toBeDisabled());
  });
});
```

---

## 2. Unit Test: DiagramWizard Model Selection

### Test File Location
`frontend/src/components/DiagramWizard/DiagramWizard.test.tsx`

### What to Test
- Shows ModelSelector when no model selected
- Shows system description form after model selection
- Model indicator displays correctly
- Model saved to and loaded from localStorage
- "Change Model" button works
- Cannot start without model selected
- Cannot start without system description

### Sample Test Cases

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { DiagramWizard } from './DiagramWizard';

describe('DiagramWizard - Model Selection', () => {

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  test('shows ModelSelector initially', () => {
    render(<DiagramWizard />);

    expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument();
  });

  test('shows system description form after model selection', async () => {
    render(<DiagramWizard />);

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[0]);

    await waitFor(() => {
      expect(screen.getByText('Describe Your System')).toBeInTheDocument();
    });
  });

  test('saves model to localStorage', async () => {
    render(<DiagramWizard />);

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[0]);

    await waitFor(() => {
      expect(localStorage.getItem('diagramWizard.selectedModel')).toBe('gpt5');
    });
  });

  test('loads model from localStorage on mount', () => {
    localStorage.setItem('diagramWizard.selectedModel', 'claude');
    render(<DiagramWizard />);

    expect(screen.getByText('Describe Your System')).toBeInTheDocument();
    expect(screen.getByText('CLAUDE')).toBeInTheDocument();
  });

  test('"Change Model" button returns to selector', async () => {
    localStorage.setItem('diagramWizard.selectedModel', 'grok');
    render(<DiagramWizard />);

    fireEvent.click(screen.getByRole('button', { name: /Change Model/i }));

    await waitFor(() => {
      expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument();
    });
  });

  test('prevents starting without model selection', async () => {
    render(<DiagramWizard />);

    fireEvent.click(screen.getByRole('button', { name: /Start Conversation/i }));

    await waitFor(() => {
      expect(screen.getByText(/Please select an AI model first/i)).toBeInTheDocument();
    });
  });

  test('prevents starting without system description', async () => {
    localStorage.setItem('diagramWizard.selectedModel', 'gpt5');
    render(<DiagramWizard />);

    fireEvent.click(screen.getByRole('button', { name: /Start Conversation/i }));

    await waitFor(() => {
      expect(screen.getByText(/Please enter a system description/i)).toBeInTheDocument();
    });
  });

  test('displays model in header', () => {
    localStorage.setItem('diagramWizard.selectedModel', 'claude');
    render(<DiagramWizard />);

    expect(screen.getByText('CLAUDE')).toBeInTheDocument();
  });
});
```

---

## 3. Unit Test: useDiagramSession Hook

### Test File Location
`frontend/src/components/DiagramWizard/hooks/useDiagramSession.test.ts`

### What to Test
- startSession accepts modelId parameter
- startSession passes modelId to API
- Hook works without modelId (backward compatibility)
- Hook logs modelId when starting

### Sample Test Cases

```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { useDiagramSession } from './useDiagramSession';
import DiagramApi from '../../../services/diagram/diagramApi';

describe('useDiagramSession Hook - Model Support', () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('passes modelId to startDiagramGeneration', async () => {
    const mockApi = vi.spyOn(DiagramApi, 'startDiagramGeneration')
      .mockResolvedValue({
        session_id: 'test-session',
        status: { status: 'started' }
      });

    const { result } = renderHook(() => useDiagramSession());

    await act(async () => {
      await result.current.startSession('Test prompt', 'Mermaid', 'gpt5');
    });

    expect(mockApi).toHaveBeenCalledWith('Test prompt', 'Mermaid', 'gpt5');
  });

  test('works without modelId', async () => {
    const mockApi = vi.spyOn(DiagramApi, 'startDiagramGeneration')
      .mockResolvedValue({
        session_id: 'test-session',
        status: { status: 'started' }
      });

    const { result } = renderHook(() => useDiagramSession());

    await act(async () => {
      await result.current.startSession('Test prompt', 'Mermaid');
    });

    expect(mockApi).toHaveBeenCalled();
  });
});
```

---

## 4. Unit Test: DiagramApi Service

### Test File Location
`frontend/src/services/diagram/diagramApi.test.ts`

### What to Test
- startDiagramGeneration includes modelId in request body when provided
- modelId omitted when not provided
- Correct HTTP method and headers
- Error handling

### Sample Test Cases

```typescript
import { vi, describe, test, expect, beforeEach } from 'vitest';
import DiagramApi from './diagramApi';

describe('DiagramApi - Model Support', () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('includes modelId in request body when provided', async () => {
    const mockFetch = vi.spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => ({ session_id: 'test', status: {} })
      } as any);

    await DiagramApi.startDiagramGeneration('Test', 'Mermaid', 'gpt5');

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body).toEqual({
      initial_prompt: 'Test',
      diagram_type: 'Mermaid',
      model_id: 'gpt5'
    });
  });

  test('omits modelId when not provided', async () => {
    const mockFetch = vi.spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => ({ session_id: 'test', status: {} })
      } as any);

    await DiagramApi.startDiagramGeneration('Test', 'Mermaid');

    const body = JSON.parse(mockFetch.mock.calls[0][1].body);
    expect(body.model_id).toBeUndefined();
  });

  test('sends correct POST request', async () => {
    const mockFetch = vi.spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => ({ session_id: 'test', status: {} })
      } as any);

    await DiagramApi.startDiagramGeneration('Test', 'D2', 'claude');

    expect(mockFetch.mock.calls[0][1].method).toBe('POST');
    expect(mockFetch.mock.calls[0][1].headers['Content-Type']).toBe('application/json');
  });
});
```

---

## 5. Integration Test: Complete Flow

### Test File Location
`frontend/src/components/DiagramWizard/DiagramWizard.integration.test.tsx`

### What to Test
- Complete user flow from model selection through session start
- Model persists across remounts
- Switching models works correctly
- localStorage errors handled gracefully

### Sample Test Cases

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { DiagramWizard } from './DiagramWizard';

describe('DiagramWizard - Integration', () => {

  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  test('complete flow: select model ’ describe ’ start', async () => {
    const mockFetch = vi.spyOn(global, 'fetch')
      .mockResolvedValue({
        ok: true,
        json: async () => ({
          session_id: 'test-session',
          status: { status: 'started' }
        })
      } as any);

    render(<DiagramWizard />);

    // Step 1: Select model
    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[1]); // Grok

    // Step 2: See form
    await waitFor(() => {
      expect(screen.getByText('Describe Your System')).toBeInTheDocument();
    });

    // Step 3: Enter description
    const textarea = screen.getByPlaceholderText(/Describe the system/i);
    fireEvent.change(textarea, { target: { value: 'My system' } });

    // Step 4: Start
    fireEvent.click(screen.getByRole('button', { name: /Start Conversation/i }));

    // Step 5: Verify API call
    await waitFor(() => {
      const body = JSON.parse(mockFetch.mock.calls[0][1].body);
      expect(body.model_id).toBe('grok');
    });
  });

  test('model persists across remounts', async () => {
    const { unmount } = render(<DiagramWizard />);

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[2]); // Claude

    unmount();

    render(<DiagramWizard />);

    await waitFor(() => {
      expect(screen.getByText('CLAUDE')).toBeInTheDocument();
    });
  });

  test('switching models works', async () => {
    localStorage.setItem('diagramWizard.selectedModel', 'gpt5');
    render(<DiagramWizard />);

    fireEvent.click(screen.getByRole('button', { name: /Change Model/i }));

    await waitFor(() => {
      expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument();
    });

    const buttons = screen.getAllByRole('button', { name: /Select/i });
    fireEvent.click(buttons[3]); // Gemini

    await waitFor(() => {
      expect(localStorage.getItem('diagramWizard.selectedModel')).toBe('gemini');
    });
  });
});
```

---

## Manual Testing Checklist

### Model Selection UI
- [ ] ModelSelector shows with gradient background
- [ ] All 4 model cards visible
- [ ] Model names correct: GPT-5, Grok, Claude Sonnet 4.5, Gemini 2.5 Pro
- [ ] Descriptions display for each model
- [ ] Strengths listed for each model
- [ ] "Select" button on each card

### Model Selection Flow
- [ ] Clicking Select hides ModelSelector
- [ ] System description form appears
- [ ] Model tag shows with "Using:" label
- [ ] "Change Model" button visible
- [ ] Model name correctly formatted in tag

### Data Persistence
- [ ] Model saved to localStorage after selection
- [ ] Refresh page ’ model selection restored
- [ ] Close browser ’ reopen ’ model selection restored
- [ ] localStorage values: 'gpt5', 'grok', 'claude', 'gemini'

### Session Start
- [ ] Clicking Start without model: warning "Please select an AI model first"
- [ ] Clicking Start without description: warning "Please enter a system description"
- [ ] With both filled: API call includes model_id
- [ ] Session ID displays in header
- [ ] Model indicator displays in header

### Error Handling
- [ ] localStorage quota error handled gracefully
- [ ] Component still renders if localStorage unavailable
- [ ] Console warnings shown for failures
- [ ] App doesn't crash on errors

### Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

---

## Running Tests

### Install Dependencies
```bash
cd frontend
npm install
```

### Run All Tests
```bash
npm run test
```

### Run Specific Test File
```bash
npm run test -- ModelSelector.test.tsx
npm run test -- DiagramWizard.test.tsx
npm run test -- diagramApi.test.ts
```

### Run Tests in Watch Mode
```bash
npm run test -- --watch
```

### Run Tests with UI Dashboard
```bash
npm run test:ui
```

### Generate Coverage Report
```bash
npm run test:coverage
```

### Check Coverage for Specific Files
```bash
npm run test:coverage -- ModelSelector.tsx
npm run test:coverage -- DiagramWizard.tsx
```

---

## Expected Coverage Goals

| File | Target Coverage |
|------|-----------------|
| ModelSelector.tsx | > 90% |
| DiagramWizard.tsx (model selection logic) | > 85% |
| useDiagramSession.ts | > 90% |
| diagramApi.ts | > 85% |

---

## Testing Summary Table

| Component | Unit Tests | Integration | E2E | Manual |
|-----------|-----------|-------------|-----|--------|
| ModelSelector | 7+ | 1+ | Optional |  |
| DiagramWizard | 10+ | 3+ | Optional |  |
| useDiagramSession | 3+ |  |  |  |
| DiagramApi | 4+ |  |  |  |

---

## Debugging Tips

### Console Logs to Check
```typescript
// Should appear when model selected:
[DiagramSession] Starting session { modelId: 'gpt5' }

// Should appear when API called:
=€ Starting new diagram session with model: gpt5

// Should appear for localStorage:
 Session started, waiting for AI analysis...
```

### Check localStorage in Browser DevTools
```javascript
// In console:
localStorage.getItem('diagramWizard.selectedModel') // Should return 'gpt5', 'grok', etc.
```

### Check Network Requests
1. Open DevTools ’ Network tab
2. Start diagram with model
3. Look for POST request to `/api/v1/diagram/start`
4. Check request body includes `model_id` field

---

## References

- [Vitest Docs](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
