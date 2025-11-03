# Architecture Gen Studio - Implementation Quick Start Guide

**Version:** 1.0
**Date:** 2025-11-03

---

## 📋 OVERVIEW

This is a detailed implementation guide for the Architecture Gen Studio - a specialized three-column web application for generating and editing architectural diagrams using AI.

**Key Files:**
- `WEBPAGE_LAYOUT_SPECIFICATION.md` - UI/UX layout specification
- `ARCHITECTURE_GEN_STUDIO_SPECIFICATION.md` - Technical & feature specification
- `WEBPAGE_LAYOUT_TECHNICAL_REVIEW.md` - Q&A clarifications (all 81 questions resolved)
- `TASKS_LAYOUT.md` - Detailed implementation tasks (85+ tasks in 8 phases)

---

## 🎯 PROJECT STRUCTURE

```
frontend/src/pages/ArchitectureGenStudio/
├── components/
│   ├── Header/
│   │   ├── Header.tsx
│   │   ├── BrandingSection.tsx
│   │   ├── AgentSelector.tsx
│   │   ├── NavigationMenu.tsx
│   │   ├── UserAccountMenu.tsx
│   │   └── NotificationBadge.tsx
│   ├── LeftColumn/
│   │   ├── LeftColumn.tsx
│   │   ├── AgentOptionList.tsx
│   │   ├── PromptEditor.tsx
│   │   └── SubmitButton.tsx
│   ├── CenterColumn/
│   │   ├── CenterColumn.tsx
│   │   ├── DiagramTabs.tsx
│   │   ├── DiagramRenderingArea.tsx
│   │   ├── ZoomControls.tsx
│   │   ├── ExportButton.tsx
│   │   └── MinimizeButton.tsx
│   ├── RightColumn/
│   │   ├── RightColumn.tsx
│   │   ├── CodeEditor.tsx
│   │   ├── ValidateButton.tsx
│   │   ├── RenderButton.tsx
│   │   └── ErrorPanel.tsx
│   └── Footer/
│       ├── Footer.tsx
│       ├── StatusColumn.tsx
│       ├── SSEMessagesColumn.tsx
│       └── LinksColumn.tsx
├── hooks/
│   ├── useArchitectureStudioState.ts
│   ├── useLocalStorage.ts
│   └── useAPIClient.ts
├── services/
│   ├── apiClient.ts
│   └── sseClient.ts (reuse existing)
├── types/
│   └── architectureStudio.ts
├── utils/
│   └── helpers.ts
├── styles/
│   └── architectureStudio.css
└── index.tsx (main page component)
```

---

## 🔧 KEY TECHNOLOGIES

### Frontend Stack (Reuse from Whysper)
- **React 18.3.1** + TypeScript 5.8.3
- **Ant Design 5.27.4** - UI components
- **Monaco Editor 0.53.0** - Code editing
- **React Resizable Panels** - Column resizing
- **Axios 1.12.2** - API calls
- **Mermaid 11.12.0** - Diagram rendering

### Backend Integration (Existing)
- **FastAPI** - REST API endpoints
- **SSE** - Real-time message streaming
- **Diagram Providers:**
  - Mermaid CLI
  - D2 CLI
  - Kroki API (D2, Mermaid, C4, PlantUML, Structurizr)

### State Management
- React Hooks (useState, useEffect)
- Custom hooks for logic
- localStorage for persistence
- Props-based communication

---

## 📊 MAIN CONCEPTS

### Three-Column Layout
```
┌─────────────────────────────────────────────────────────┐
│                      HEADER                              │
├──────────────────┬──────────────────┬──────────────────┤
│                  │                  │                  │
│  LEFT COLUMN     │  CENTER COLUMN   │  RIGHT COLUMN    │
│                  │                  │                  │
│ • AgentOptions   │ • Diagram Tabs   │ • Code Editor    │
│ • Prompt Editor  │ • SVG Rendering  │ • Validate Btn   │
│ • Submit Button  │ • Zoom Controls  │ • Render Btn     │
│                  │ • Export Button  │ • Error Panel    │
│                  │ • Minimize Btn   │                  │
│                  │                  │                  │
├──────────────────┴──────────────────┴──────────────────┤
│                      FOOTER (3 columns)                 │
│ Status | SSE Messages (scrollable) | About/Help/Info   │
└─────────────────────────────────────────────────────────┘
```

### State Flow
```
User Input
    ↓
Component State Update
    ↓
API Call (if needed)
    ↓
Response Handler
    ↓
State Update
    ↓
Component Re-render
    ↓
UI Update
    ↓
localStorage Persist (if applicable)
```

### Data Types

**Agent**
```typescript
{
  id: string
  name: string
  description: string
}
```

**AgentOption**
```typescript
{
  id: string
  agentId: string
  name: string
  description: string
  template: string                  // Auto-populated into prompt editor
  validationRules: string[]
  outputFormat: string
  enabled: boolean
}
```

**DiagramResponse**
```typescript
{
  svg: string                       // SVG markup for rendering
  provider: string                  // mermaid, d2, kroki-*, etc.
  code: string                      // Diagram source code
  metadata: {
    provider: string
    generationParameters: object
  }
  status: string                    // success, error, etc.
  timestamp: string                 // ISO 8601 format
}
```

---

## 🔌 API ENDPOINTS

### Agents & Options
- `GET /api/v1/agents` - Fetch all agents
- `GET /api/v1/agents/{agentId}/options` - Fetch agent options

### Diagrams
- `POST /api/v1/diagrams/v2/generate` - Generate diagram from prompt
- `POST /api/v1/diagrams/v2/validate` - Validate diagram code
- `POST /api/v1/diagrams/v2/render` - Render diagram code
- `POST /api/v1/diagrams/v2/cancel` - Cancel in-progress request

### Real-time
- `GET /api/v1/logs/stream` - SSE streaming for progress messages

---

## 🎨 UI/UX DECISIONS

### Key Decisions Made
1. **Standalone Route** - Not integrated with chat, separate page
2. **Single-Select SubAgents** - Simpler UX, no multi-select
3. **Props-Based State** - No Context API for small component tree
4. **localStorage Persistence** - Agent selection, last prompt, column widths
5. **SVG Only** - All diagrams render as SVG from backend
6. **Explicit Render** - No auto-render on keystroke, requires button click
7. **Toast Notifications** - Only for important events (not badges)
8. **Theme from .env** - All colors driven by Whysper theme system

### Color System
- Primary actions: Theme primary color
- Errors: Theme error color
- Success: Theme success color
- Warnings: Theme warning color
- Backgrounds: Theme background color

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Setup (2-3 days)
- Project structure
- Routing
- State management
- API client
- Type definitions

### Phase 2: Header (2-3 days)
- Branding section
- Agent selector
- Navigation menu
- User account menu
- Notifications

### Phase 3: Left Column (3-4 days)
- AgentOption list
- Prompt editor
- Submit button + states
- Cancel functionality
- localStorage

### Phase 4: Center Column (4-5 days)
- Diagram tabs
- SVG rendering
- Zoom controls
- Export (SVG/PDF/code)
- Minimize/maximize

### Phase 5: Right Column (3-4 days)
- Monaco code editor
- Validate button
- Render button
- Error panel
- Syntax highlighting

### Phase 6: Footer (2-3 days)
- Status bar (3 columns)
- SSE integration
- About/Help links
- Disclaimer

### Phase 7: Integration (3-5 days)
- Connect all components
- Complete state management
- Resizable columns
- API integration testing
- User workflow testing
- Error handling
- Performance testing

### Phase 8: Polish (2-3 days)
- Accessibility review
- Theme testing
- Cross-browser testing
- Documentation
- Bug fixes
- Deployment prep

**Total: 22-30 days (4-6 weeks)**

---

## ✅ CRITICAL CHECKLIST

Before starting each phase:

### Phase 1 Prerequisites
- [ ] All 81 clarification questions answered
- [ ] Layout specification finalized
- [ ] Technical specification approved
- [ ] File structure planned

### Phase 2-6 Prerequisites (per phase)
- [ ] Parent component complete
- [ ] Type definitions ready
- [ ] Parent state updated
- [ ] API functions available

### Phase 7 Prerequisites
- [ ] All components complete
- [ ] No import errors
- [ ] All props defined
- [ ] Layout renders

### Phase 8 Prerequisites
- [ ] All workflows tested
- [ ] No known bugs
- [ ] Performance acceptable
- [ ] All features working

---

## 🔍 TESTING STRATEGY

### Unit Tests
- Component rendering
- Props validation
- Event handlers
- State updates

### Integration Tests
- Component communication
- API calls
- State management
- Error handling

### E2E Tests
- Complete user workflows
- Agent selection → diagram generation → export
- Tab switching with code editing
- Cancel workflow

### Performance Tests
- Large prompts (5000 chars)
- Large diagrams (1000+ nodes)
- Virtual scrolling
- Memory usage

---

## 📝 IMPORTANT NOTES

### Do NOT Do
❌ Add Context API (not needed for this component tree)
❌ Use Redux (keep it simple with hooks)
❌ Hardcode colors (use theme system)
❌ Create new diagram providers (use existing Kroki/Mermaid/D2)
❌ Persist diagrams (session-only)
❌ Share diagrams to chat (separate features)
❌ Add persistence beyond agent/prompt/widths
❌ Build own SVG renderer (use backend providers)

### DO Do
✅ Reuse Whysper components (Layout, Monaco, etc.)
✅ Follow Ant Design patterns
✅ Use TypeScript everywhere
✅ Handle all error cases
✅ Show loading states
✅ Implement all keyboard shortcuts
✅ Test on multiple themes
✅ Document as you go
✅ Commit frequently
✅ Keep components focused

---

## 🎓 LEARNING RESOURCES

### Ant Design
- https://ant.design/components/overview/
- Form, Select, Button, Tabs, Alert, Badge

### Monaco Editor
- https://github.com/suren-atoyan/monaco-react
- Existing usage in Whysper codebase

### React Resizable Panels
- https://www.npmjs.com/package/react-resizable-panels
- Column divider implementation

### TypeScript
- Use strict mode
- Define all interfaces
- No `any` types unless necessary

---

## 🐛 DEBUGGING TIPS

### Console Logging
```typescript
// State changes
console.log('State updated:', { agent, prompt, diagramType });

// API calls
console.log('API Request:', { method, endpoint, payload });
console.log('API Response:', response);

// User actions
console.log('User Action:', { action, timestamp });
```

### React DevTools
- Inspect component hierarchy
- Check props/state values
- Track re-renders

### Network Tab
- Check API requests/responses
- Monitor SSE connection
- Check payload sizes

### Performance Tab
- Profile rendering performance
- Check for memory leaks
- Monitor memory usage

---

## 📞 SUPPORT & ESCALATION

### Questions to Ask
- What diagram types should we support first?
- Any special validation rules for agents?
- Specific performance requirements?
- Custom branding besides Wells Fargo?

### Potential Blockers
- Backend API changes
- Monaco Editor version compatibility
- Kroki service availability
- Browser compatibility issues

---

## 🎉 SUCCESS CRITERIA

✅ **Phase Complete When:**
1. All tasks in phase marked complete
2. No outstanding bugs
3. All user workflows tested
4. Code reviewed and merged
5. No console errors
6. Performance acceptable

✅ **Project Complete When:**
1. All 8 phases complete
2. Comprehensive testing passed
3. Accessibility reviewed
4. Documentation complete
5. Deployed to production
6. Monitoring in place

---

**Next Step:** Start Phase 1 - Project Setup & Architecture

Review `TASKS_LAYOUT.md` for detailed task breakdown.

