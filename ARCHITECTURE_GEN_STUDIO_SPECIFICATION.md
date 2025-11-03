# Architecture Gen Studio - Final Technical Specification

**Status:** ✅ All 81 clarification questions resolved
**Date:** 2025-11-03
**Version:** 1.0

---

## EXECUTIVE SUMMARY

Architecture Gen Studio is a **standalone web application** (separate route) that allows users to:
1. Select a SubAgent from a dropdown
2. Write/paste a prompt (max 5000 characters)
3. Generate diagrams in multiple formats (D2, Mermaid, etc.)
4. Edit the generated code in Monaco editor
5. Validate and render diagrams
6. Export as SVG, PDF, or diagram code

The UI consists of 3 resizable columns (Left: Prompts, Center: Diagram, Right: Code Editor) with a header, footer status bar, and theme support.

---

## SECTION 1: HEADER

### 1.1 Agent Selector
- **Type:** Searchable Select dropdown component
- **Behavior on selection change:**
  - Show confirmation dialog if unsaved prompt exists
  - Dialog message: "You have unsaved prompt. Switching agents will discard it. Continue?"
  - If confirmed: clear the prompt
  - Navigation breadcrumb updates: "Home >> [Agent Name]"
- **Breadcrumb style:** Display labels only (non-interactive)

### 1.2 Notification Badge
- **Display type:** Toast notifications only (not badge count or dropdown panel)
- **Trigger events:**
  - Diagram generation complete
  - Errors occurred
  - System alerts

### 1.3 User Account Menu
- **Functionality:** Logout only
- **Authentication:** Rely on OAuth2 SSO
- **No API key management, theme selection, or subscription info**

---

## SECTION 2: LEFT COLUMN (Prompt Control Panel)

### 2.1 SubAgent List Display
- **Format:** Simple list items (no icons, no descriptions, no cards)
- **Selection model:** Single-select only
- **No custom subagent creation**
- **Selected subagent effects:**
  - Auto-populate prompt hints/templates
  - Change validation rules
  - Modify available diagram types

### 2.2 Prompt Editor
- **Editor type:** Monaco editor
- **Syntax highlighting:** Auto-detect based on selected diagram type tab
- **Features:**
  - Auto-complete: No
  - Prompt templates: Use Template field from SubAgent
  - Character limit: 5000 characters max
  - No persistence (localStorage, session storage, or in-memory)

### 2.3 Submit Button
- **Behavior:** Immediate LLM call (no validation, no confirmation dialog)
- **Processing time:** 30-60 seconds typical
- **User can cancel:** Yes
- **Loading state:** Show disabled button during processing
- **Error handling:**
  - Display in error panel (bottom right)
  - Show toast notification
  - No retry mechanism

---

## SECTION 3: CENTER COLUMN (Diagram Rendering)

### 3.1 Diagram Type Tabs
- **Selection model:** One at a time via tabs
- **Behavior on tab change:**
  - If not rendered yet: show empty placeholder
  - If already rendered: switch view of existing SVG
  - Regenerate with different provider only if needed

### 3.2 Diagram Rendering
- **Format:** SVG only
- **Source:** Always from backend provider (Kroki or other)
- **Error handling:**
  - Show error message in error panel
  - Show toast notification
  - No partial diagram display, no fallback text

### 3.3 Zoom Controls
- **Range:** 20% to 300%
- **Step size:** 20%
- **Keyboard shortcuts:** Yes (Ctrl+/-, Ctrl+scroll, reset to fit)
- **Persistence:** Do NOT persist zoom level when switching diagram types

### 3.4 Export/Download
- **Supported formats:**
  - SVG: Yes
  - PDF: Yes (standard 8.5" x 11" paper size)
  - PNG: No
  - Code export (D2, Mermaid text): Yes (with proper file extensions)

### 3.5 Minimize Button
- **Behavior:**
  - Hide rendering area completely
  - Show toggle button in column header
  - Collapse to 1/3 of overall screen width
  - Allow user to unhide via header button
- **Persistence:** Do NOT persist minimize state across page navigation

### 3.6 Infinite Scroll
- **Status:** NOT IMPLEMENTED (out of scope for single diagram renderer)

---

## SECTION 4: RIGHT COLUMN (Code Editor)

### 4.1 Monaco Editor
- **Language mode:** Auto-detect based on active diagram type tab
- **Features:**
  - Line numbers: No
  - Code folding: No
  - Search/replace: Yes
  - Git diff: No
  - Minimap: Yes
  - Bracket matching/highlighting: Yes
  - Auto-indentation: Yes
- **Max size:** Can handle 100K+ lines
- **Auto-save:** No (require explicit save)

### 4.2 Validate Button
- **Validation types:**
  - Syntax validation via backend provider: Yes
  - Schema validation: Yes
- **Behavior:**
  - Show loading state: Yes
  - Timeout: 30 seconds

### 4.3 Render Button
- **Process:** Syntax check + schema check + generation
- **Requirement:** Must validate first before render
- **Behavior:**
  - Show disabled state while processing
  - Time estimate: ~10 seconds
  - No progress bar, no step indicators

### 4.4 Error Display
- **Error types to show:**
  - Syntax errors: Yes
  - Validation errors: Yes
  - Render errors: Yes
  - LLM errors: Yes
- **Display options:**
  - Error code/ID: Yes
  - Stack trace: No
  - User-friendly message: Yes
  - Suggested fix: No
  - Documentation link: No

### 4.5 Auto-fix Feature (3-Tier Validation)
- **Process:** Invisible backend retries with error context (up to 3 attempts)
- **User visibility:** Yes, shown via SSE messages in footer
- **No dedicated "Auto-fix" button in UI**

---

## SECTION 5: FOOTER (Status Bar)

### 5.1 Column 1: Current Status
- **Display:**
  - Processing state (e.g., "Processing diagram...")
  - Last operation result (e.g., "Render complete")
  - System health indicator
- **No timestamps**

### 5.2 Column 2: SSE Backend Messages
- **Message types:**
  - Progress updates: Yes
  - Info logs: Yes
  - Warning logs: No
  - Error logs: Yes
- **Display:**
  - Real-time streamed text: Yes
  - Not categorized/filtered: No
  - Scrollable history: Yes
  - Auto-scroll: Yes when new messages arrive
  - User cannot clear log: No

### 5.3 Column 3: Links
- **About link:** New tab (external URL)
- **Help link:** New tab to documentation
- **No chat support, no FAQ**

---

## SECTION 6: STATE MANAGEMENT & DATA FLOW

### 6.1 Component State Architecture
- **Global state (App.tsx):** currentAgent, currentPrompt, selectedDiagramType
- **Local state:** Individual columns manage their own UI state
- **No Context API needed initially**
- **Props-based communication**

### 6.2 Persistence (localStorage)
- **Persist:** Current agent selection, last prompt
- **Do NOT persist:** Diagram history, user preferences

### 6.3 Real-time Updates (SSE)
- **Auto-scroll footer:** Yes
- **Toast notification on SSE:** No
- **Auto-update diagram:** No

---

## SECTION 7: INTEGRATION WITH WHYSPER

### 7.1 Architecture
- **Page structure:** Separate route (not tab, not modal)
- **Diagram sharing:** NOT SUPPORTED (no sharing to chat conversations)

### 7.2 Agent System
- **Source:** Backend API (YAML files in `prompts/` folder on backend)
- **Loading:** At application startup
- **Runtime updates:** Not supported (requires page reload)
- **Caching:** Frontend caches agent list

### 7.3 API Integration
- **Endpoints:** Multiple as needed
- **Streaming:** Yes (for LLM and SSE)
- **Error handling:** Standard Python logging

### 7.4 SSE Reconnection
- **Strategy:** Exponential backoff with maximum retry attempts
- **Message queue:** Max 100 messages

---

## SECTION 8: COLUMN RESIZING

### 8.1 Width Constraints
- **Minimum width:** Each column minimum 1/3 of available screen space
- **Maximum width:** Can expand to fill remaining space
- **Persistence:** Save to localStorage
- **Safety:** At least one column must remain open

### 8.2 Collapse Behavior
- **Implementation:** Hidden via header button toggle (just a button, not sidebar)
- **Content:** Completely hidden when collapsed
- **Unhide:** Click header button to restore
- **Constraint:** Cannot collapse all 3 columns

---

## SECTION 9: PERFORMANCE & SCALABILITY

### 9.1 Large Diagrams
- **Virtual scrolling:** Yes (for 1000+ node diagrams)
- **Lazy loading:** No
- **Compression:** No

### 9.2 Editor Performance
- **Max code size:** 100K+ lines supported
- **Debouncing:** No keystroke debouncing
- **Render trigger:** Explicit render button click only

---

## SECTION 10: ACCESSIBILITY & UX

### 10.1 Keyboard Shortcuts
- **Ctrl+S:** Submit prompt (or Save in edit mode)
- **Ctrl+Enter:** Submit/Execute action
- **Ctrl+/:** Help/Documentation toggle
- **Tab navigation:** No (not between columns)

### 10.2 Responsive Behavior
- **Minimum screen width:** 1400px
- **Smaller screens:** Fail gracefully with message

### 10.3 Error Messages
- **Both technical and user-friendly:** Yes (shown together)
- **No toggle between formats**

---

## SECTION 11: THEME INTEGRATION

### 11.1 Theme System
- **Source:** Theme colors defined in .env file
- **Application:** All components (tabs, buttons, Monaco editor) auto-follow theme
- **No hardcoded colors**
- **Monaco editor:** Auto-switch based on page theme (no user override)

---

## SECTION 12: DATA TYPES & API

### 12.1 AgentOption JSON Structure

```json
{
  "id": "string",
  "agentId": "string",
  "name": "string",
  "description": "string",
  "template": "string",
  "validationRules": "string[]",
  "outputFormat": "string",
  "enabled": "boolean"
}
```

- **Storage:** `/prompts/SubAgent/*.json` (one file per agent option)
- **Retrieved by:** Backend API call at startup

### 12.2 Message Metadata Extension

When storing diagram generation in Message.metadata:

```json
{
  "provider": "string",
  "providerConfig": "object",
  "generationParameters": {
    "model": "string",
    "temperature": "number"
  }
}
```

- **Version info:** Not needed
- **No full provider config serialization**

### 12.3 Diagram Response Format

API endpoint: `/diagrams/v2/render` returns:

```json
{
  "svg": "string (SVG markup)",
  "provider": "string (e.g., 'kroki')",
  "code": "string (diagram code)",
  "metadata": {
    "provider": "string",
    "generationParameters": "object"
  },
  "status": "string (e.g., 'success', 'error')",
  "timestamp": "string (ISO 8601 format)"
}
```

---

## SECTION 13: TESTING & VALIDATION

### 13.1 Unit Tests
- **Scope:** All components + critical path
- **Coverage goal:** Comprehensive

### 13.2 E2E Tests
- **Status:** Not required for MVP

### 13.3 Validation Testing
- **Mock invalid diagrams:** Yes
- **Test auto-fix behavior:** Yes

---

## SECTION 14: SECURITY

### 14.1 Code Injection (XSS)
- **SVG rendering:** Safe (no XSS risk from rendering backend SVG)
- **Code sanitization:** Not needed for diagram code display

### 14.2 API Security
- **Per-user restrictions:** Not required
- **Role-based access:** Not required

---

## SECTION 15: CROSS-CUTTING CONCERNS

### 15.1 Loading States
- **Submit button:** Show disabled state (30-60 seconds)
- **Validate button:** Show loading state (30 seconds)
- **Render button:** Show disabled state (~10 seconds)
- **Tab switching:** Show loading if re-render needed

### 15.2 Error Recovery
- **LLM API failure:** Show error panel + toast notification
- **Diagram provider failure:** Show error panel + toast notification
- **SSE connection drop:** Show error panel + toast notification
- **No automatic retry**

### 15.3 Success Messages
- **Display type:** Status bar update only
- **No toast notifications for success**

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Core Architecture
- [ ] Set up 3-column layout with resizable dividers
- [ ] Implement header with agent selector
- [ ] Create footer status bar with SSE message area
- [ ] Set up state management (props-based)

### Phase 2: Left Column (Prompts)
- [ ] SubAgent list component (simple list)
- [ ] Monaco prompt editor with character limit
- [ ] Submit button with loading state
- [ ] LocalStorage persistence for agent selection and prompt

### Phase 3: Center Column (Diagram)
- [ ] Diagram tabs component
- [ ] SVG rendering area
- [ ] Zoom controls (20%-300%, 20% steps, keyboard shortcuts)
- [ ] Export/download (SVG, PDF, code)
- [ ] Minimize button with header toggle

### Phase 4: Right Column (Code Editor)
- [ ] Monaco editor with language auto-detection
- [ ] Validate button with backend integration
- [ ] Render button with validation requirement
- [ ] Error display panel
- [ ] Search/replace functionality

### Phase 5: Integration
- [ ] Backend API integration for agents
- [ ] SSE streaming implementation
- [ ] Theme integration from .env
- [ ] Keyboard shortcuts (Ctrl+S, Ctrl+Enter, Ctrl+/)

### Phase 6: Polish & Testing
- [ ] Unit tests for all components
- [ ] Error state testing
- [ ] Performance testing (large diagrams, 100K+ lines)
- [ ] Accessibility review
- [ ] Cross-browser testing

---

## KEY DECISIONS

| Decision | Rationale |
|----------|-----------|
| Standalone route (not modal/tab) | Clear separation from chat experience |
| Single-select agents | Simpler UX, prevents context confusion |
| Props-based state (no Context) | Manageable with 5 main components |
| SVG only from backend | Simplifies rendering, leverages existing providers |
| Explicit render button | Prevents accidental API calls on every keystroke |
| localStorage persistence | Quick recovery of last used agent/prompt |
| No diagram sharing to chat | Keep features separate, simpler implementation |
| Auto-fix visible in SSE | Transparency into system operation |
| Theme from .env | Single source of truth for all colors |

---

## MIGRATION NOTES

- **Monaco editor language modes:** Must align with providers (D2, Mermaid, etc.)
- **Backend agents endpoint:** Ensure returns proper AgentOption schema
- **SSE implementation:** Exponential backoff and 100-message queue limit
- **Zoom state:** NOT persisted (reset per diagram type)
- **Column widths:** Persisted to localStorage

---

**Document Status:** ✅ READY FOR IMPLEMENTATION
**Last Updated:** 2025-11-03
**All 81 clarification questions resolved**
