# Architecture Gen Studio - Implementation Plan & Roadmap

## Executive Summary

The **Architecture Gen Studio** is a specialized three-column web application for generating and editing architectural diagrams using AI-powered agents. All critical questions have been answered through systematic planning sessions (Q3-Q9), and this document provides the comprehensive implementation roadmap.

**Status:** ✅ Planning Phase Complete - Ready for Implementation Phase

---

## Phase 1: Core Infrastructure Setup (Week 1-2)

### 1.1 Route & Page Structure
- [ ] Create new route `/studio` in frontend
- [ ] Create `StudioUI.tsx` main page component
- [ ] Integrate with existing `ThemeProvider` wrapper
- [ ] Ensure header and footer are properly integrated

### 1.2 Layout Framework
- [ ] Implement three-column resizable layout using `react-resizable-panels`
  - Left Column: Prompt Control Panel
  - Center Column: Diagram Rendering & Visualization
  - Right Column: Code Editor & Validation
- [ ] Add independent scrollbars for each column
- [ ] Implement collapse/expand functionality for each column
- [ ] Style columns to match Ant Design system

### 1.3 Header Component (Reuse & Extend)
- [ ] Extend existing header with:
  - Well Fargo branding (left-aligned, two lines)
  - Agent selector dropdown (center/right area)
  - Navigation menu (Home >> Current Home | Architecture Gen Studio > New Page | Settings \ Help)
  - User account menu (existing Avatar/Dropdown)
  - Notification badges (existing Badge component)
  - Sticky positioning
- [ ] Integrate with theme system using existing `useTheme()` hook

### 1.4 Footer Component
- [ ] Create sticky footer with three-column layout
- [ ] **Column 1:** Current Status display
  - Default: "Idle"
  - States: "LLM Execution...", "Rendering...", "Diagram Generated", "Error: [message]"
  - Show last 50 messages with scroll
- [ ] **Column 2:** SSE Backend Messages
  - Real-time streaming display
  - Auto-scroll to latest
  - Timestamps on each message
  - Max height with scrolling
- [ ] **Column 3:** Links & Disclaimer
  - About link (opens new tab)
  - Help link (opens new tab)
  - Disclaimer text: "Information was AI Generated"
- [ ] Add vertical dividers between columns
- [ ] Ensure sticky positioning at bottom

---

## Phase 2: Backend Integration & Data Loading (Week 2-3)

### 2.1 Agent System Integration
- [ ] Load agents from backend API (not YAML at startup)
  - Endpoint: `/api/v1/agents` (or existing endpoint)
  - Static list, no refresh mechanism
- [ ] Create `useAgents()` hook to manage agent loading and state
- [ ] Implement agent caching in localStorage for performance

### 2.2 AgentOption Data Type Implementation
- [ ] Define backend model for `AgentOption`:
  ```typescript
  interface AgentOption {
    id: string;
    name: string;
    description?: string;
    helpContent: string;      // NEW
    template: string;          // NEW - default prompt value
    tags?: string[];
  }
  ```
- [ ] Load AgentOptions for selected agent from backend
  - Endpoint: `/api/v1/agents/{agentId}/options` (or similar)
  - Tied one-to-many to Agent
- [ ] Cache AgentOptions in component state
- [ ] Create `useAgentOptions(agentId)` hook

### 2.3 API Endpoints Verification
- [ ] Verify existing endpoints work as expected:
  - `/api/v1/diagrams/v2/validate` - Code validation
  - `/api/v1/diagrams/v2/render` - Diagram rendering
  - `/api/v1/diagrams/v2/fix` - Auto-fix with LLM
  - `/api/v1/logs/stream` - SSE real-time streaming
  - `/api/v1/chat` - Message processing (for prompt submission)
- [ ] Create TypeScript types for request/response payloads
- [ ] Integrate with existing `APIService` from `services/api.ts`

### 2.4 SSE (Server-Sent Events) Integration
- [ ] Reuse existing `sseClient.ts` from `services/`
- [ ] Create `useSSEMessages()` hook for real-time message streaming
- [ ] Format SSE messages with timestamps
- [ ] Implement auto-scroll behavior for latest messages
- [ ] Handle SSE connection lifecycle (open, close, error)

---

## Phase 3: Left Column - Prompt Control Panel (Week 3-4)

### 3.1 Agent Selector in Header
- [ ] Implement Select dropdown for agent selection
  - Populated from loaded agents
  - Use existing `antd` Select component
  - Display agent name/description
  - Remember selected agent in localStorage

### 3.2 AgentOption List Component
- [ ] Create `AgentOptionList.tsx` component
  - Vertical list of clickable items (menu/list style)
  - Single selection only
  - Show AgentOption name and help content on hover
  - Visual highlight for active option
  - Independent scrollbar within column
- [ ] When AgentOption is clicked:
  - Load its `template` field
  - Auto-populate Monaco editor with template
  - Update left column state

### 3.3 Monaco Prompt Editor
- [ ] Integrate Monaco Editor into left column
  - Use existing Monaco integration from `editor/` folder
  - Configuration:
    - No line numbers
    - Word wrap: Yes
    - Syntax highlighting: No (plain text)
    - No code completion/IntelliSense
    - No mini-map
    - Expands to fill available space
    - Placeholder: "Enter your prompt here or select an Agent Option template above"
  - Allow free editing of template
  - No character limit
- [ ] Connect editor to component state

### 3.4 Submit/Cancel Buttons
- [ ] Create button container below editor
- [ ] **Submit Button:**
  - Normal state: "Submit"
  - Enabled initially
  - On click: Submit prompt to LLM
- [ ] **Cancel Button:**
  - Hidden by default
  - Appears during LLM processing
  - On click: Cancel ongoing LLM request
  - Re-enable editor
- [ ] Implement button state management:
  - Disabled during processing
  - Show loading spinner
  - Text changes to "Generating..."
- [ ] Success indication:
  - Diagram appears in center column
  - Toast notification: "Diagram Generated Successfully"
  - Button returns to normal state
  - Editor becomes editable again

### 3.5 State Management for Left Column
- [ ] Create context or use useState for:
  - Selected agent
  - Selected AgentOption
  - Prompt text (editor content)
  - Is processing (loading state)
  - Selected diagram type (synced with center column)

---

## Phase 4: Center Column - Diagram Rendering & Visualization (Week 4-5)

### 4.1 Diagram Type Tabs
- [ ] Implement Ant Design Tabs component
  - Four tabs: Mermaid, D2, Structurizr, PlantUML
  - Initially show requested diagram type tab
  - Also show Mermaid as default option
- [ ] Tab behavior:
  - Only one diagram type generated at a time
  - Ungenerated tabs show empty state
  - Click tab to request new generation for that type
  - Right column syncs to show code for selected tab
  - Automatic format conversion: NOT supported

### 4.2 Diagram Rendering Area
- [ ] Create SVG display container
  - Renders diagram SVG from backend
  - Responsive sizing within column
  - Empty state message for ungenerated tabs
- [ ] Implement zoom controls:
  - Zoom in button
  - Zoom out button
  - Zoom level indicator
  - Reset zoom button
- [ ] Implement SVG download:
  - Download button
  - Save as SVG file
  - Use diagram filename or generated name

### 4.3 Minimize/Maximize Controls
- [ ] Add minimize button to collapse rendering area
- [ ] Add maximize button to expand rendering area
- [ ] Maintain diagram state when minimized

### 4.4 Empty State & Loading
- [ ] Empty state when tab not yet generated:
  - Message: "Select 'Render' in the right column to generate [diagram type]"
- [ ] Loading state while rendering:
  - Spinner or loading animation
  - "Rendering..." message

### 4.5 State Management for Center Column
- [ ] Create context or use useState for:
  - Current diagram type (active tab)
  - Generated diagrams map (one per type)
  - Diagram SVG content
  - Is rendering (loading state)

---

## Phase 5: Right Column - Code Editor & Validation (Week 5-6)

### 5.1 Monaco Code Editor
- [ ] Integrate Monaco Editor for code editing
  - Configuration:
    - No line numbers
    - No word wrap
    - Syntax highlighting: No (plain text)
    - No code completion/IntelliSense
    - No mini-map
    - **Bracket matching: Yes**
    - Expands to fill available space
    - Auto-populated from selected diagram type's code
  - Allow free editing
  - No character limit

### 5.2 Validate Button
- [ ] Implement Validate button below editor
- [ ] On click:
  - Call `/api/v1/diagrams/v2/validate` endpoint
  - Send current diagram type and code
  - Display validation result
- [ ] If valid: Show success message
- [ ] If invalid: Show error details in collapsible error section

### 5.3 Render Button
- [ ] Implement Render button below editor
- [ ] On click:
  - Call `/api/v1/diagrams/v2/render` endpoint
  - Send current diagram type and edited code
  - Update center column with new SVG
  - Update right column code editor with rendered code
  - Show SSE messages in footer
  - Update footer status: "Rendering...", then "Diagram Generated"

### 5.4 Error Display Area (Collapsible)
- [ ] Use Ant Design Collapse component
- [ ] Title: "Errors" or "Validation Errors"
- [ ] Collapsed by default
- [ ] Display validation/rendering errors
- [ ] Use Alert component for error styling
- [ ] Support multi-line error messages

### 5.5 Right Column Behavior
- [ ] When user switches center column tabs:
  - Right column code updates to show new diagram type's code
  - Right column locked to center column (no independent viewing)
- [ ] If user edited code and switches tabs:
  - Warn user about unsaved changes (optional)
  - Changes are lost unless user Renders first
- [ ] Support both initial generated code and user-edited code

### 5.6 State Management for Right Column
- [ ] Create context or use useState for:
  - Current code (editor content)
  - Code by diagram type (map)
  - Validation errors
  - Is validating/rendering

---

## Phase 6: State Management & Communication (Week 6)

### 6.1 Global State Architecture
- [ ] Design state structure (use React Context + Hooks pattern):
  ```typescript
  interface StudioUIState {
    // Agent selection
    selectedAgent: Agent | null;
    selectedAgentOption: AgentOption | null;

    // Prompt
    promptText: string;

    // Processing state
    isProcessing: boolean;
    currentStatus: string;

    // Diagram state
    selectedDiagramType: 'mermaid' | 'd2' | 'structurizr' | 'plantuml';
    generatedDiagrams: Map<DiagramType, DiagramResult>;

    // Code editor state
    codeByType: Map<DiagramType, string>;
    validationErrors: string[];

    // SSE messages
    sseMessages: Message[];
  }
  ```

### 6.2 Create Context & Hooks
- [ ] `StudioUIContext` for global state
- [ ] `useStudioUI()` hook to access context
- [ ] Separate hooks for specific features:
  - `usePromptSubmit()` - Handle prompt submission
  - `useDiagramRendering()` - Handle diagram rendering
  - `useCodeValidation()` - Handle code validation
  - `useTabSwitching()` - Handle diagram type tab switching

### 6.3 Communication Between Columns
- [ ] Left → Center: Submit prompt
  - Trigger LLM call
  - Stream SSE messages to footer
  - Display generated diagram in center
- [ ] Center → Right: Tab switching
  - Update right column code to selected diagram type
  - Update state to reflect current tab
- [ ] Right → Center: Render button
  - Send edited code to backend
  - Update center column SVG
  - Update status in footer

### 6.4 localStorage Persistence
- [ ] Persist:
  - Selected agent
  - Selected AgentOption
  - User preferences (not edits)
- [ ] Load on page mount

---

## Phase 7: Integration & Testing (Week 7)

### 7.1 Component Integration
- [ ] Verify all columns work together
- [ ] Test data flow between columns
- [ ] Test SSE message streaming
- [ ] Test Submit/Cancel/Render flows

### 7.2 Ant Design Theme Integration
- [ ] Verify styling matches Ant Design theme
- [ ] Test with all 11 theme variants
- [ ] Ensure dark mode compatibility
- [ ] Verify color consistency

### 7.3 API Integration Testing
- [ ] Test agent loading
- [ ] Test AgentOption loading
- [ ] Test diagram validation
- [ ] Test diagram rendering
- [ ] Test SSE message streaming
- [ ] Test error handling

### 7.4 User Flow Testing
- [ ] Test complete user flow (Q3-Q9 requirements):
  1. Select agent
  2. View AgentOptions
  3. Select AgentOption (template auto-populate)
  4. Edit prompt
  5. Click Submit
  6. Wait for generation
  7. Select different diagram type
  8. View generated code
  9. Edit code
  10. Click Validate/Render
  11. View results

### 7.5 Unit Tests
- [ ] Test components individually
- [ ] Test hooks
- [ ] Test state management
- [ ] Test API service calls
- [ ] Test data transformations

### 7.6 End-to-End Tests
- [ ] Test complete application flows
- [ ] Test error scenarios
- [ ] Test edge cases

---

## Phase 8: Polish & Optimization (Week 8)

### 8.1 Performance Optimization
- [ ] Optimize Monaco Editor rendering
- [ ] Lazy load diagram renderers
- [ ] Optimize SSE message handling
- [ ] Implement message batching if needed

### 8.2 Accessibility (WCAG 2.1 AA)
- [ ] Add ARIA labels to buttons
- [ ] Ensure keyboard navigation works
- [ ] Verify color contrast
- [ ] Test with screen readers

### 8.3 Error Handling
- [ ] Handle network errors gracefully
- [ ] Show user-friendly error messages
- [ ] Implement error boundaries
- [ ] Log errors for debugging

### 8.4 Loading States
- [ ] Add meaningful loading indicators
- [ ] Show progress for long operations
- [ ] Prevent double submissions

### 8.5 Documentation
- [ ] Component documentation
- [ ] API documentation
- [ ] User guide
- [ ] Developer setup guide

---

## Technology Stack (Reusing Whysper)

### Frontend
- **Framework:** React 18.3.1 + TypeScript 5.8.3
- **Build:** Vite 7.1.7
- **UI Components:** Ant Design 5.27.4
- **Editor:** Monaco Editor 0.53.0
- **API:** Axios 1.12.2
- **State:** React Context + Hooks (no Redux)
- **Styling:** Ant Design CSS-in-JS (emotion/styled-components)
- **Theme:** Existing ThemeProvider with 11 variants

### Backend (Existing Endpoints)
- **Framework:** FastAPI (async)
- **Diagram Providers:** Mermaid CLI, D2 CLI, Kroki API (7 total)
- **Validation:** 3-tier (pattern-based, LLM-based, manual)
- **Real-time:** SSE for progress streaming

---

## Critical Design Decisions

### 1. AgentOption Template Auto-Population
- When user selects AgentOption, the `template` string immediately populates the Monaco editor
- Allows user to quickly start with a pre-configured prompt
- User can edit or clear the template

### 2. Single Diagram Type Processing
- Only one diagram type generated at a time
- User must explicitly request generation for other types
- Reduces backend load and improves perceived performance
- Right column always syncs to center column tab

### 3. No Automatic Format Conversion
- User cannot simply click to convert D2 to Mermaid
- Must submit prompt again or edit code and render
- Reduces complexity and backend calls

### 4. Editor Read-Only During Processing
- Monaco editor becomes read-only while LLM is processing
- User must click Cancel to edit again
- Prevents accidental edits or confusion during processing

### 5. Sticky Footer
- Footer always visible at bottom
- User can monitor status and SSE messages at all times
- Important for UX during long-running operations

### 6. Toast Notifications for Errors
- Validation/rendering errors show as toast (not in status bar)
- Keeps status bar clean for operational status
- Allows toast to auto-dismiss

---

## Success Criteria

✅ All critical questions answered (Q3-Q9)
✅ Specification complete and detailed
✅ Implementation plan created
✅ Technology stack defined
✅ Data flow documented
✅ User workflows defined

---

## Next Steps

1. **Review Plan:** Present this plan to stakeholders for approval
2. **Begin Development:** Start with Phase 1 (Route & Layout)
3. **Iterative Development:** Complete phases 1-8 over 8 weeks
4. **Testing:** Continuous testing throughout development
5. **Deployment:** Deploy to production after Phase 8

---

## Appendix: File Structure

```
frontend/
├── src/
│   ├── pages/
│   │   └── studio-ui/
│   │       ├── StudioUI.tsx (main page)
│   │       ├── context/
│   │       │   └── StudioUIContext.tsx
│   │       ├── hooks/
│   │       │   ├── useStudioUI.ts
│   │       │   ├── usePromptSubmit.ts
│   │       │   ├── useDiagramRendering.ts
│   │       │   ├── useCodeValidation.ts
│   │       │   └── useTabSwitching.ts
│   │       ├── components/
│   │       │   ├── Header/
│   │       │   │   └── HeaderComponent.tsx
│   │       │   ├── Footer/
│   │       │   │   ├── FooterComponent.tsx
│   │       │   │   ├── StatusColumn.tsx
│   │       │   │   └── SSEMessagesColumn.tsx
│   │       │   ├── LeftColumn/
│   │       │   │   ├── LeftColumn.tsx
│   │       │   │   ├── AgentSelector.tsx
│   │       │   │   ├── AgentOptionList.tsx
│   │       │   │   └── PromptEditor.tsx
│   │       │   ├── CenterColumn/
│   │       │   │   ├── CenterColumn.tsx
│   │       │   │   ├── DiagramTabs.tsx
│   │       │   │   └── DiagramRenderer.tsx
│   │       │   └── RightColumn/
│   │       │       ├── RightColumn.tsx
│   │       │       ├── CodeEditor.tsx
│   │       │       └── ErrorDisplay.tsx
│   │       └── types/
│   │           └── index.ts (local types)
│   └── services/
│       └── studio-ui.ts (API service)
```

---

**Document Created:** 2025-11-03
**Status:** Ready for Implementation
