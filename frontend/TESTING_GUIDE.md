# DiagramWizard Testing Guide

## Overview

This guide outlines the testing strategy for DiagramWizard after removing ArchitectureGenStudio and implementing new features.

## Test Framework Setup Required

Currently, the project does not have a test framework configured. To enable testing, you need to install one of the following:

### Option 1: Vitest (Recommended)

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/user-event jsdom
npm install -D @vitest/ui
```

Add to `package.json`:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

Create `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
});
```

### Option 2: Jest

```bash
cd frontend
npm install -D jest @testing-library/react @testing-library/jest-dom


```

## Test Coverage Plan

### 1. Unit Tests

#### Hooks
- **`useSSE.test.ts`**
  - Connection establishment
  - Automatic reconnection with exponential backoff
  - Keep-alive timeout handling
  - Message tracking and state management
  - Cleanup on unmount

- **`useLocalStorage.test.ts`**
  - Read/write operations
  - JSON serialization/deserialization
  - Cross-tab synchronization via storage events
  - Error handling (quota exceeded)
  - Clear functionality

- **`useDiagramSession.test.ts`**
  - Session initialization
  - Status updates via SSE
  - Clarification workflow
  - Diagram rendering
  - Session cleanup
  - Error handling
  - Callback hooks (onUpdate, onError, onComplete)

- **`useKeyboardNavigation.test.ts`**
  - Keyboard event handlers
  - Focus management
  - Focus trap for modals
  - Accessibility compliance

#### Services
- **`validationService.test.ts`**
  - Backend API validation
  - Fallback client-side validation
  - Mermaid syntax validation
  - D2 syntax validation
  - PlantUML syntax validation
  - Debounce functionality

- **`exportService.test.ts`**
  - SVG export
  - PNG export with html2canvas
  - PDF export with jsPDF
  - Different orientations (landscape/portrait)
  - Custom backgrounds and quality settings
  - Error handling

#### Components
- **`ErrorPanel.test.tsx`**
  - Error display
  - Warning display
  - Suggestions display
  - Jump to line functionality
  - Auto-fix button

- **`ExportModal.test.tsx`**
  - Format selection (SVG/PNG/PDF)
  - Filename customization
  - Quality settings for PNG
  - Background color selection
  - Export execution

- **`Footer.test.tsx`**
  - Session status display
  - SSE connection indicator
  - Statistics display (total sessions, success rate)
  - Success rate calculation

- **`PreviewPanel.test.tsx`**
  - SVG rendering
  - Zoom controls (in/out/reset)
  - Pan/drag functionality
  - Keyboard shortcuts (Ctrl +/-/0)
  - Mouse wheel zoom
  - Loading states

- **`CodeEditorPanel.test.tsx`**
  - Code display
  - Real-time validation
  - Validation tab switching
  - Edit mode toggle
  - Save functionality

### 2. Integration Tests

#### Full Workflow Tests
- **`DiagramWizard.integration.test.tsx`**
  - Complete user journey: input → clarification → generation → render
  - Diagram type selection
  - Code editing and re-rendering
  - Export workflow
  - Session persistence to localStorage
  - Error recovery and retry
  - SSE connection states

#### End-to-End Scenarios
- **User creates Mermaid flowchart**
  1. Enter prompt
  2. Answer clarifications
  3. View generated code
  4. Preview diagram
  5. Export as PNG

- **User creates D2 architecture diagram**
  1. Enter system description
  2. Select D2 type
  3. Iterate with clarifications
  4. Export as PDF

- **Error handling and recovery**
  1. Trigger validation error
  2. View error panel
  3. Fix code manually
  4. Re-render successfully

### 3. Accessibility Tests

- **Keyboard Navigation**
  - Tab order correctness
  - Focus indicators
  - Keyboard shortcuts work
  - No keyboard traps

- **Screen Reader Support**
  - ARIA labels present
  - Live regions for status updates
  - Semantic HTML structure

- **WCAG 2.1 AA Compliance**
  - Color contrast ratios
  - Focus management
  - Error messages associated with inputs

## Test File Structure

```
frontend/src/
├── components/
│   └── DiagramWizard/
│       ├── __tests__/
│       │   ├── DiagramWizard.integration.test.tsx
│       │   ├── components.test.tsx
│       │   └── useDiagramSession.test.ts
│       ├── components/
│       ├── hooks/
│       └── panels/
├── hooks/
│   └── __tests__/
│       ├── useSSE.test.ts
│       ├── useLocalStorage.test.ts
│       └── useKeyboardNavigation.test.ts
└── services/
    └── diagram/
        └── __tests__/
            ├── validationService.test.ts
            └── exportService.test.ts
```

## Running Tests

Once the framework is installed:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run specific test file
npm test -- useSSE.test.ts

# Run tests with UI (vitest only)
npm run test:ui
```

## Coverage Goals

- **Unit Tests**: > 80% coverage
- **Integration Tests**: All critical user paths
- **Accessibility**: WCAG 2.1 AA compliance

## Continuous Integration

Add to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
```

## Mock Data

Create `src/test/mocks/` directory with:

- `mockDiagramSession.ts` - Sample session data
- `mockSSEMessages.ts` - Sample SSE events
- `mockDiagramCode.ts` - Sample Mermaid/D2/PlantUML code

## Testing Best Practices

1. **Test behavior, not implementation**
2. **Use meaningful test descriptions**
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Mock external dependencies**
5. **Test error paths, not just happy paths**
6. **Keep tests isolated and independent**
7. **Use data-testid for stable selectors**

## Next Steps

1. Install test framework (Vitest recommended)
2. Create test setup file
3. Implement unit tests first (hooks, services)
4. Add component tests
5. Complete with integration tests
6. Set up CI/CD integration
7. Monitor coverage metrics

## Removed Components

The following components were removed from testing scope:

- `architectureGenStudio/` - Entire module deleted
- All ArchitectureGenStudio tests removed
- No backward compatibility tests needed

## Changed Components Requiring Tests

These components have significant changes and need comprehensive testing:

- `DiagramWizard.tsx` - Enhanced with SSE, localStorage, export
- `useDiagramSession.ts` - Refactored to use new SSE hook
- `Panel2_Preview.tsx` - Added zoom/pan functionality
- `Panel3_CodeEditor.tsx` - Added validation integration

All new tests should be created following the structure outlined above.
