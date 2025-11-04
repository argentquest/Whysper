# Architecture Gen Studio - Implementation Tasks Plan

**Status:** 📋 Planning Phase
**Last Updated:** 2025-11-03
**Total Tasks:** 85+

---

## MASTER TASK BREAKDOWN

### Phase 1: Project Setup & Architecture (Estimated: 2-3 days)
- [ ] Initialize project structure
- [ ] Set up routing
- [ ] Create component folder structure
- [ ] Configure state management
- [ ] Setup API client integration

### Phase 2: Header Section (Estimated: 2-3 days)
- [ ] Implement branding/logo section
- [ ] Create agent selector dropdown
- [ ] Build navigation menu
- [ ] Add user account menu
- [ ] Implement notification system

### Phase 3: Left Column - Prompt Control (Estimated: 3-4 days)
- [ ] Create AgentOption list component
- [ ] Integrate Monaco editor for prompts
- [ ] Implement submit button with states
- [ ] Add cancel functionality
- [ ] Setup localStorage persistence

### Phase 4: Center Column - Diagram Rendering (Estimated: 4-5 days)
- [ ] Create diagram type tabs component
- [ ] Implement SVG rendering area
- [ ] Add zoom controls
- [ ] Create export functionality
- [ ] Implement minimize/maximize

### Phase 5: Right Column - Code Editor (Estimated: 3-4 days)
- [ ] Setup Monaco editor for code
- [ ] Implement validate button
- [ ] Implement render button
- [ ] Create error display panel
- [ ] Add syntax highlighting per diagram type

### Phase 6: Footer Section (Estimated: 2-3 days)
- [ ] Create status bar layout (3 columns)
- [ ] Implement SSE message streaming
- [ ] Add about/help links
- [ ] Setup disclaimer text

### Phase 7: Integration & Testing (Estimated: 3-5 days)
- [ ] API integration testing
- [ ] State management testing
- [ ] E2E workflow testing
- [ ] Performance optimization
- [ ] Bug fixes

### Phase 8: Polish & Deployment (Estimated: 2-3 days)
- [ ] Accessibility review
- [ ] Theme testing
- [ ] Cross-browser testing
- [ ] Documentation
- [ ] Deployment preparation

---

## DETAILED TASK LIST

## PHASE 1: PROJECT SETUP & ARCHITECTURE

### 1.1 Initialize Project Structure
**Priority:** 🔴 CRITICAL
**Status:** ✅ Complete
**Depends on:** None
**Estimated Hours:** 4 (actual: 2.5)

- [x] Create `/frontend/src/components/architectureGenStudio/` directory
- [x] Create subdirectories:
  - [x] `/components/` (for all UI components)
  - [x] `/hooks/` (custom React hooks)
  - [x] `/types/` (TypeScript interfaces)
  - [x] `/styles/` (component-specific styles)
- [x] Create `index.tsx` as main component entry point
- [x] Create component folder structure:
  - [x] Header component folder
  - [x] LeftColumn component folder
  - [x] CenterColumn component folder
  - [x] RightColumn component folder
  - [x] Footer component folder

**Completed:**
- [x] Folder structure created
- [x] Entry point configured
- [x] Import paths verified

**Files Created:**
- `index.tsx` - Main component with state management integration
- `types/architectureStudio.ts` - Complete type definitions (350+ lines)
- `types/index.ts` - Type exports
- `hooks/useArchitectureStudioState.ts` - State management hook
- `hooks/useLocalStorage.ts` - localStorage utility hook
- `hooks/useAPIClient.ts` - API integration hook
- `hooks/index.ts` - Hook exports
- `styles/architectureStudio.module.css` - Base CSS styles

---

### 1.2 Setup Routing
**Priority:** 🔴 CRITICAL
**Status:** ✅ Complete
**Depends on:** 1.1
**Estimated Hours:** 2 (actual: 0.5)

- [x] Create route path `/studio`
- [x] Add route to main router configuration
- [x] Import ArchitectureGenStudio page component
- [x] Test route navigation path
- [x] Ensure proper layout hierarchy with existing theme provider

**Completed:**
- [x] Route added to router config (`frontend/src/main.tsx`)
- [x] ArchitectureGenStudio component imported
- [x] Theme provider wraps component (inherited from app)
- [x] React Router properly configured

**Files Modified:**
- `frontend/src/main.tsx` - Added route for `/studio` path

**Route Details:**
- Path: `/studio`
- Component: `ArchitectureGenStudio`
- Theme Provider: Inherited from parent `<ThemeProvider>`
- Accessible at: `http://localhost:5173/studio`

---

### 1.3 Configure State Management
**Priority:** 🔴 CRITICAL
**Status:** ✅ Complete
**Depends on:** 1.1
**Estimated Hours:** 3 (actual: included in 1.1)

**Global State Requirements:**
- [x] Created state interface for:
  - [x] `currentAgent` (selected agent from dropdown)
  - [x] `currentPrompt` (text in prompt editor)
  - [x] `selectedDiagramType` (currently selected tab)
  - [x] `generatedDiagrams` (map of diagram type → SVG + code)
  - [x] `selectedAgentOption` (selected subagent template)
  - [x] `isProcessing` (boolean for submit/cancel states)
  - [x] `columnWidths` (persisted column width percentages)
  - [x] `collapsedColumns` (which columns are collapsed)

- [x] Created custom hooks:
  - [x] `useArchitectureStudioState()` - main state hook (500+ lines)
  - [x] `useLocalStorage()` - for persistence
  - [x] `useAPIClient()` - for API calls

- [x] Setup localStorage keys:
  - [x] `studio_currentAgent`
  - [x] `studio_lastPrompt`
  - [x] `studio_selectedAgentOption`
  - [x] `studio_columnWidths`
  - [x] `studio_collapsedColumns`
  - [x] `studio_zoomLevel`

**Completed:**
- [x] State types fully defined in `types/architectureStudio.ts`
- [x] Custom hooks created and exported
- [x] localStorage auto-initialization and debounced persistence
- [x] State update handlers with proper types

**Key Features:**
- Auto-population of prompt template when AgentOption selected
- Debounced localStorage saves (1 second)
- Max 100 SSE messages, max 50 status history
- Zoom not persisted across diagram types
- All state updates are immutable

---

### 1.4 Setup API Client Integration
**Priority:** 🔴 CRITICAL
**Status:** ✅ Complete
**Depends on:** 1.3
**Estimated Hours:** 3 (actual: included in 1.1)

- [x] Created `hooks/useAPIClient.ts` hook:
  - [x] Function: `fetchAgents()` - GET /api/v1/agents
  - [x] Function: `fetchAgentOptions(agentId)` - GET /api/v1/agents/{agentId}/options
  - [x] Function: `submitPrompt(request)` - POST /api/v1/diagrams/v2/generate
  - [x] Function: `validateCode(request)` - POST /api/v1/diagrams/v2/validate (30s timeout)
  - [x] Function: `renderDiagram(request)` - POST /api/v1/diagrams/v2/render
  - [x] Function: `cancelRequest(requestId)` - POST /api/v1/diagrams/v2/cancel

- [x] API Features:
  - [x] All functions return typed responses
  - [x] Error handling with try/catch
  - [x] 30 second timeout for validation
  - [x] Proper request/response types
  - [x] SSE integration ready (via existing sseClient pattern)

- [x] Error handling:
  - [x] Network errors logged and thrown
  - [x] API response status checked
  - [x] Timeout handling (30 seconds for validate)
  - [x] User-friendly error messages

**Completed:**
- [x] API hook created with all endpoints
- [x] TypeScript request/response types defined
- [x] Error handling with proper feedback
- [x] Ready for SSE integration in Phase 6

**API Endpoints Implemented:**
- `GET /api/v1/agents` - Fetch all agents
- `GET /api/v1/agents/{agentId}/options` - Fetch agent options
- `POST /api/v1/diagrams/v2/generate` - Generate diagram
- `POST /api/v1/diagrams/v2/validate` - Validate code (30s timeout)
- `POST /api/v1/diagrams/v2/render` - Render diagram
- `POST /api/v1/diagrams/v2/cancel` - Cancel request

---

### 1.5 Type Definitions
**Priority:** 🔴 CRITICAL
**Status:** ✅ Complete
**Depends on:** 1.3
**Estimated Hours:** 2 (actual: included in 1.1)

Created `/types/architectureStudio.ts` (350+ lines):

- [x] Agent interface
- [x] AgentOption interface (8 fields)
- [x] DiagramType union type
- [x] DiagramResponse interface
- [x] GeneratedDiagram interface
- [x] ValidationResult interface
- [x] SSEMessage types
- [x] ArchitectureStudioState interface
- [x] Component Props interfaces (Header, Left, Center, Right, Footer)
- [x] API Request/Response types
- [x] Storage keys constants
- [x] Diagram type constants (mermaid, d2, structurizr, plantuml)
- [x] Default state constant

**Completed:**
- [x] All interfaces fully defined and documented
- [x] Types properly exported from single file
- [x] Used throughout state management and hooks
- [x] Component prop types for all 5 main components
- [x] Constants for validation (5000 char limit, zoom ranges, etc.)

**Key Types:**
- 8 diagram-related interfaces
- 12 state/component interfaces
- 6 API request/response types
- Full TypeScript coverage with no `any` types

---

## PHASE 2: HEADER SECTION

### 2.1 Create Header Component
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.1, 1.5
**Estimated Hours:** 2

File: `/components/Header/Header.tsx`

- [ ] Create Layout.Header component
- [ ] Set height to match design (typically 64px for Ant Design)
- [ ] Make sticky with z-index layering
- [ ] Configure padding and spacing
- [ ] Import sub-components (to be built in following tasks)
- [ ] Apply theme colors from `useTheme()` hook

**Props:**
```typescript
interface HeaderProps {
  onAgentChange: (agent: Agent) => void;
  currentAgent: Agent | null;
  notificationCount: number;
}
```

**Checklist:**
- [ ] Header component renders
- [ ] Sticky positioning works
- [ ] Theme colors applied
- [ ] Sub-components imported (placeholders ok)

---

### 2.2 Create Branding Section (Left Side)
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 2.1
**Estimated Hours:** 1

File: `/components/Header/BrandingSection.tsx`

- [ ] Display "Well Fargo" (Line 1)
- [ ] Display "Architecture Gen Studio" (Line 2)
- [ ] Use Typography.Title and Typography.Text from Ant Design
- [ ] Left-aligned in header
- [ ] Apply theme primary color

**Checklist:**
- [ ] Text displays correctly
- [ ] Layout is left-aligned
- [ ] Theme colors applied

---

### 2.3 Create Agent Selector Dropdown
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 2.1, 1.5
**Estimated Hours:** 3

File: `/components/Header/AgentSelector.tsx`

- [ ] Fetch agents list from API on mount
- [ ] Create searchable Select component (Ant Design)
- [ ] Show agent name and description
- [ ] Handle agent selection change
- [ ] Show confirmation dialog if unsaved prompt exists
  - [ ] Dialog message: "You have unsaved prompt. Switching agents will discard it. Continue?"
  - [ ] OK: clear prompt and switch agent
  - [ ] Cancel: stay on current agent
- [ ] Show loading state while fetching
- [ ] Handle errors gracefully

**Props:**
```typescript
interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentSelect: (agent: Agent) => void;
  hasUnsavedPrompt: boolean;
}
```

**Checklist:**
- [ ] Agents fetched and displayed
- [ ] Searchable/filterable
- [ ] Confirmation dialog shows
- [ ] Selection handler works
- [ ] Error handling in place

---

### 2.4 Create Navigation Menu
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 2.1
**Estimated Hours:** 2

File: `/components/Header/NavigationMenu.tsx`

- [ ] Create Menu component (Ant Design)
- [ ] Menu items (display labels only, not clickable):
  - [ ] "Home >> Architecture Gen Studio"
  - [ ] "Architecture Gen Studio > New Page"
  - [ ] "Settings"
  - [ ] "Help"
- [ ] Center-aligned in header
- [ ] Use theme colors

**Checklist:**
- [ ] Menu renders with all items
- [ ] Items are properly labeled
- [ ] Styling matches theme

---

### 2.5 Create User Account Menu
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 2.1, 1.5
**Estimated Hours:** 2

File: `/components/Header/UserAccountMenu.tsx`

- [ ] Create Avatar + Dropdown menu (Ant Design)
- [ ] Menu items:
  - [ ] "Logout" (click handler)
- [ ] Right-aligned in header
- [ ] Get user info from auth context
- [ ] Handle logout action

**Props:**
```typescript
interface UserAccountMenuProps {
  onLogout: () => void;
}
```

**Checklist:**
- [ ] Avatar displays user icon
- [ ] Dropdown menu opens
- [ ] Logout action works
- [ ] Right-aligned

---

### 2.6 Create Notification Badge
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 2.1, 1.5
**Estimated Hours:** 2

File: `/components/Header/NotificationBadge.tsx`

- [ ] Create Badge component (Ant Design)
- [ ] Show count of unread notifications
- [ ] Trigger notifications for:
  - [ ] Diagram generation complete
  - [ ] Errors occurred
  - [ ] System alerts
- [ ] Display as toast notification (not dropdown or badge count)
- [ ] Right side of header, next to user menu

**Props:**
```typescript
interface NotificationBadgeProps {
  count: number;
}
```

**Checklist:**
- [ ] Badge renders
- [ ] Count updates
- [ ] Toast notifications work

---

### 2.7 Integrate Header Components
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 2.2, 2.3, 2.4, 2.5, 2.6
**Estimated Hours:** 2

Update `/components/Header/Header.tsx`:

- [ ] Import all sub-components
- [ ] Layout in proper order:
  - [ ] Left: BrandingSection
  - [ ] Center: NavigationMenu
  - [ ] Right: NotificationBadge + UserAccountMenu
- [ ] Use Ant Design Row/Col for alignment
- [ ] Test responsive layout
- [ ] Ensure theme consistency

**Checklist:**
- [ ] All components integrated
- [ ] Layout matches spec
- [ ] Styling consistent
- [ ] No import errors

---

## PHASE 3: LEFT COLUMN - PROMPT CONTROL

### 3.1 Create Left Column Container
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.1, 1.5
**Estimated Hours:** 2

File: `/components/LeftColumn/LeftColumn.tsx`

- [ ] Create Layout.Sider component (Ant Design)
- [ ] Set min-width to 33% of screen
- [ ] Make collapsible with header toggle button
- [ ] Add collapse/expand animation
- [ ] Independent scrollbar
- [ ] Import sub-components

**Props:**
```typescript
interface LeftColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
}
```

**Checklist:**
- [ ] Container renders
- [ ] Collapsible works
- [ ] Width can be adjusted
- [ ] Scrollbar present

---

### 3.2 Create AgentOption List Component
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 3.1, 1.5
**Estimated Hours:** 3

File: `/components/LeftColumn/AgentOptionList.tsx`

- [ ] Fetch AgentOptions for selected agent
- [ ] Display as vertical list (Menu component from Ant Design)
- [ ] Single selection model (only one can be active)
- [ ] Show active/highlighted state for selected option
- [ ] On selection:
  - [ ] Auto-populate template into prompt editor
  - [ ] Update validation rules
  - [ ] Update available diagram types
- [ ] Handle loading state
- [ ] Handle errors

**Props:**
```typescript
interface AgentOptionListProps {
  agentId: string;
  options: AgentOption[];
  selectedOptionId: string | null;
  onOptionSelect: (option: AgentOption) => void;
  isLoading: boolean;
  error: string | null;
}
```

**Checklist:**
- [ ] Options fetched for current agent
- [ ] List displays correctly
- [ ] Single selection works
- [ ] Template auto-populates
- [ ] Active state shows

---

### 3.3 Create Monaco Prompt Editor
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 3.1, 1.5
**Estimated Hours:** 3

File: `/components/LeftColumn/PromptEditor.tsx`

- [ ] Integrate Monaco Editor from existing `/editor/` folder
- [ ] Configuration:
  - [ ] Line numbers: No
  - [ ] Word wrap: Yes
  - [ ] Syntax highlighting: No (plain text)
  - [ ] Code completion: No
  - [ ] Mini-map: No
  - [ ] Height: Expands to fill available space
  - [ ] Scrollbar: Yes (independent)
- [ ] Placeholder text: "Enter your prompt here or select an Agent Option template above"
- [ ] Character limit enforcement: 5000 characters
- [ ] Show character count: "XX/5000"
- [ ] Read-only during processing
- [ ] Handle paste/input events

**Props:**
```typescript
interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  isReadOnly: boolean;
  maxCharacters: number;
  placeholder?: string;
}
```

**Checklist:**
- [ ] Monaco renders
- [ ] Character limit enforced
- [ ] Character count displayed
- [ ] Read-only state works
- [ ] Content updates on template select

---

### 3.4 Create Submit Button with States
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 3.1, 3.3
**Estimated Hours:** 4

File: `/components/LeftColumn/SubmitButton.tsx`

**Button States to Implement:**

1. **Idle State:**
   - [ ] Text: "Submit"
   - [ ] Enabled: true
   - [ ] Color: Primary (theme color)

2. **Processing State:**
   - [ ] Text: "Generating..."
   - [ ] Enabled: false (disabled)
   - [ ] Show spinner icon
   - [ ] Show Cancel button next to Submit
   - [ ] Color: Changed to loading color

3. **Error State:**
   - [ ] Text: "Submit" (back to normal)
   - [ ] Enabled: true
   - [ ] Show error message below button
   - [ ] Color: Warning/error color

4. **Success State:**
   - [ ] Show brief success notification
   - [ ] Return to Idle state after 2 seconds

**Implementation:**

- [ ] Create button component with state machine
- [ ] Implement `onSubmit` handler:
  - [ ] Validate prompt not empty
  - [ ] Call `submitPrompt()` API
  - [ ] Set processing state
  - [ ] Show toast notification on completion
  - [ ] Update state with generated diagrams
- [ ] Implement `onCancel` handler:
  - [ ] Call `cancelRequest()` API
  - [ ] Re-enable editor
  - [ ] Reset button state
  - [ ] Clear processing state
- [ ] Handle API errors:
  - [ ] Show error message
  - [ ] Show in error panel (right column)
  - [ ] Show toast notification
  - [ ] Keep button enabled for retry

**Props:**
```typescript
interface SubmitButtonProps {
  isProcessing: boolean;
  hasError: boolean;
  errorMessage?: string;
  onSubmit: (prompt: string) => Promise<void>;
  onCancel: () => Promise<void>;
  prompt: string;
  disabled?: boolean;
}
```

**Checklist:**
- [ ] All states render correctly
- [ ] Loading spinner shows during processing
- [ ] Cancel button appears when processing
- [ ] Cancel works properly
- [ ] Error message displays
- [ ] Success notification shows
- [ ] Editor becomes read-only during processing

---

### 3.5 Setup localStorage Persistence
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 1.3, 3.3, 3.2
**Estimated Hours:** 2

In main ArchitectureGenStudio page component:

- [ ] Load on mount:
  - [ ] `studio_currentAgent` → set currentAgent
  - [ ] `studio_lastPrompt` → set currentPrompt
  - [ ] `studio_selectedAgentOption` → set selectedAgentOption

- [ ] Save on change:
  - [ ] currentAgent changed → save to localStorage
  - [ ] currentPrompt changed → save to localStorage (debounced at 1 second)
  - [ ] selectedAgentOption changed → save to localStorage

- [ ] Handle localStorage quota errors gracefully

**Checklist:**
- [ ] Data persists on page reload
- [ ] No console errors on load
- [ ] Correct values restored

---

### 3.6 Test Left Column Flow
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 3.1-3.5
**Estimated Hours:** 2

- [ ] Test agent selection
- [ ] Test AgentOption list loading
- [ ] Test template auto-population
- [ ] Test prompt editing
- [ ] Test character limit
- [ ] Test submit button flow
- [ ] Test cancel functionality
- [ ] Test localStorage persistence
- [ ] Test error handling

**Checklist:**
- [ ] All user interactions work
- [ ] No console errors
- [ ] State updates correctly

---

## PHASE 4: CENTER COLUMN - DIAGRAM RENDERING

### 4.1 Create Center Column Container
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.1
**Estimated Hours:** 2

File: `/components/CenterColumn/CenterColumn.tsx`

- [ ] Create Layout.Content component
- [ ] Set min-width to 33% of screen
- [ ] Make collapsible with header toggle button
- [ ] Independent scrollbar
- [ ] Flex layout for tabs + rendering area

**Props:**
```typescript
interface CenterColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
  selectedDiagramType: string;
  onDiagramTypeChange: (type: string) => void;
}
```

**Checklist:**
- [ ] Container renders
- [ ] Collapsible works
- [ ] Width adjustable

---

### 4.2 Create Diagram Type Tabs
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 4.1, 1.5
**Estimated Hours:** 3

File: `/components/CenterColumn/DiagramTabs.tsx`

- [ ] Create Tabs component (Ant Design)
- [ ] Tab items:
  - [ ] Mermaid
  - [ ] D2
  - [ ] Structurizr
  - [ ] PlantUML
- [ ] Behavior on tab change:
  - [ ] If diagram NOT generated for type: show empty state
  - [ ] If diagram already generated: show existing SVG
  - [ ] Update right column code editor to show code for selected type
  - [ ] Set selectedDiagramType in state
- [ ] Visual indicator for:
  - [ ] Generated tabs (bold/highlighted)
  - [ ] Empty tabs (grayed out)
- [ ] Handle tab switching with pending edits:
  - [ ] Warn if user has unsaved code edits
  - [ ] Option to Render first or discard changes

**Props:**
```typescript
interface DiagramTabsProps {
  activeTab: string;
  onTabChange: (type: string) => void;
  generatedDiagrams: Map<string, DiagramResponse>;
  hasUnsavedCodeEdits: boolean;
}
```

**Checklist:**
- [ ] All 4 tabs render
- [ ] Tab switching works
- [ ] Empty state shows
- [ ] Warning on unsaved edits works
- [ ] Right column syncs

---

### 4.3 Create SVG Rendering Area
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 4.1, 1.5
**Estimated Hours:** 3

File: `/components/CenterColumn/DiagramRenderingArea.tsx`

- [ ] Render SVG from selected diagram's response
- [ ] SVG container:
  - [ ] Background color from theme
  - [ ] Border for visual separation
  - [ ] Padding around SVG
- [ ] Empty state:
  - [ ] Show message: "Select a diagram type and click Render to generate diagram"
  - [ ] Or: "No diagram generated yet for this type"
- [ ] Error state:
  - [ ] Display error message
  - [ ] Show in error panel (right column)
  - [ ] Show toast notification
- [ ] Loading state:
  - [ ] Show spinner while rendering
- [ ] Scrollable:
  - [ ] For large diagrams (virtual scrolling for 1000+ nodes)

**Props:**
```typescript
interface DiagramRenderingAreaProps {
  diagram: DiagramResponse | null;
  isLoading: boolean;
  error: string | null;
  diagramType: string;
}
```

**Checklist:**
- [ ] SVG renders correctly
- [ ] Empty state shows
- [ ] Error state shows
- [ ] Loading state shows
- [ ] Large diagrams scroll properly

---

### 4.4 Create Zoom Controls
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 4.3
**Estimated Hours:** 3

File: `/components/CenterColumn/ZoomControls.tsx`

**Zoom Features:**
- [ ] Range: 20% to 300%
- [ ] Step size: 20%
- [ ] Initial zoom: 100%
- [ ] Do NOT persist zoom across diagram type switches

**UI Components:**
- [ ] Zoom In button (+ icon)
- [ ] Zoom Out button (- icon)
- [ ] Zoom level display (e.g., "100%")
- [ ] Reset button (reset to 100%)
- [ ] Zoom slider for quick adjustment

**Keyboard Shortcuts:**
- [ ] Ctrl+Plus: Zoom in
- [ ] Ctrl+Minus: Zoom out
- [ ] Ctrl+0: Reset zoom
- [ ] Ctrl+Scroll: Zoom (scroll wheel)

**SVG Transformation:**
- [ ] Apply CSS transform: `scale(zoomLevel)`
- [ ] Or use SVG viewBox manipulation
- [ ] Center zoom around middle of diagram

**Props:**
```typescript
interface ZoomControlsProps {
  zoomLevel: number;
  onZoomChange: (level: number) => void;
  onReset: () => void;
  minZoom: number;
  maxZoom: number;
  step: number;
}
```

**Checklist:**
- [ ] Zoom buttons work
- [ ] Slider works
- [ ] Keyboard shortcuts work
- [ ] Reset works
- [ ] Zoom not persisted
- [ ] SVG scales correctly

---

### 4.5 Create Export/Download Functionality
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 4.3
**Estimated Hours:** 3

File: `/components/CenterColumn/ExportButton.tsx`

**Export Formats Supported:**
- [ ] SVG (native download)
- [ ] PDF (8.5" x 11" paper size)
- [ ] Code export (D2, Mermaid, etc. with proper extensions)

**Implementation:**

For SVG:
- [ ] Get SVG element
- [ ] Create blob with SVG content
- [ ] Generate download link
- [ ] Trigger download with filename: `diagram-{timestamp}.svg`

For PDF:
- [ ] Use `jsPDF` or similar library
- [ ] Set paper size to 8.5" x 11"
- [ ] Convert SVG to image
- [ ] Embed in PDF
- [ ] Generate download with filename: `diagram-{timestamp}.pdf`

For Code:
- [ ] Get code from diagram response
- [ ] Determine file extension from provider:
  - [ ] `.mmd` for Mermaid
  - [ ] `.d2` for D2
  - [ ] `.puml` for PlantUML
  - [ ] `.c4` for Structurizr
- [ ] Create text file
- [ ] Trigger download with appropriate extension

**UI:**
- [ ] Dropdown menu with export options
- [ ] Or separate buttons for each format
- [ ] Show success message after download
- [ ] Handle errors gracefully

**Props:**
```typescript
interface ExportButtonProps {
  diagram: DiagramResponse | null;
  diagramType: string;
  disabled?: boolean;
}
```

**Checklist:**
- [ ] SVG download works
- [ ] PDF download works
- [ ] Code export works
- [ ] Filenames correct
- [ ] No errors

---

### 4.6 Create Minimize/Maximize Button
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 4.1
**Estimated Hours:** 2

File: `/components/CenterColumn/MinimizeButton.tsx`

- [ ] Create toggle button in column header
- [ ] States:
  - [ ] Normal: "Maximize" or chevron-down icon
  - [ ] Minimized: "Minimize" or chevron-up icon
- [ ] On click:
  - [ ] Minimize: Hide rendering area, show only tabs
  - [ ] Column width becomes ~1/3 of screen
  - [ ] Content completely hidden
  - [ ] Button shows in header to restore
- [ ] Animation on minimize/maximize
- [ ] Do NOT persist minimize state

**Props:**
```typescript
interface MinimizeButtonProps {
  isMinimized: boolean;
  onToggle: () => void;
}
```

**Checklist:**
- [ ] Toggle works
- [ ] Content hides/shows
- [ ] Animation smooth
- [ ] State not persisted

---

### 4.7 Test Center Column Flow
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 4.1-4.6
**Estimated Hours:** 2

- [ ] Test diagram generation and display
- [ ] Test tab switching
- [ ] Test zoom controls (all methods)
- [ ] Test export functionality
- [ ] Test minimize/maximize
- [ ] Test error handling
- [ ] Test large diagram rendering

**Checklist:**
- [ ] All features work
- [ ] No console errors
- [ ] Performance acceptable

---

## PHASE 5: RIGHT COLUMN - CODE EDITOR

### 5.1 Create Right Column Container
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.1
**Estimated Hours:** 2

File: `/components/RightColumn/RightColumn.tsx`

- [ ] Create Layout.Sider component
- [ ] Set min-width to 33% of screen
- [ ] Make collapsible with header toggle button
- [ ] Flex layout for editor + buttons + error panel
- [ ] Independent scrollbar

**Props:**
```typescript
interface RightColumnProps {
  isCollapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
  width: number;
  onWidthChange: (width: number) => void;
}
```

**Checklist:**
- [ ] Container renders
- [ ] Collapsible works
- [ ] Layout correct

---

### 5.2 Create Monaco Code Editor
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 5.1, 1.5
**Estimated Hours:** 3

File: `/components/RightColumn/CodeEditor.tsx`

- [ ] Integrate Monaco Editor
- [ ] Configuration:
  - [ ] Line numbers: No
  - [ ] Word wrap: No
  - [ ] Syntax highlighting: Based on diagram type (auto-detect)
  - [ ] Code completion: No
  - [ ] Mini-map: Yes
  - [ ] Height: Expands to fill available space
  - [ ] Bracket matching: Yes
  - [ ] Auto-indentation: Yes
- [ ] Content: Auto-populated with diagram code from selected tab
- [ ] Read-only: No (fully editable)
- [ ] Placeholder: "No diagram code available. Generate a diagram first."
- [ ] Language modes:
  - [ ] Mermaid: `mermaid`
  - [ ] D2: `d2` (or plain text if not available)
  - [ ] PlantUML: `plantuml` (or plain text)
  - [ ] Structurizr: `c4` (or plain text)

**Props:**
```typescript
interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  diagramType: string;
  isReadOnly: boolean;
  hasUnsavedChanges: boolean;
}
```

**Checklist:**
- [ ] Monaco renders
- [ ] Code displays
- [ ] Editing works
- [ ] Language highlighting works
- [ ] Minimap shows
- [ ] Bracket matching works

---

### 5.3 Create Validate Button
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 5.1, 5.2
**Estimated Hours:** 3

File: `/components/RightColumn/ValidateButton.tsx`

- [ ] Button text: "Validate"
- [ ] On click:
  - [ ] Disable button, show loading state
  - [ ] Call `validateCode()` API with code and provider
  - [ ] Timeout: 30 seconds
  - [ ] Set loading state for user feedback
- [ ] Success response:
  - [ ] Show success message in error panel
  - [ ] Return to enabled state
  - [ ] Clear any previous errors
- [ ] Error response:
  - [ ] Display error in error panel (show all error details)
  - [ ] Show toast notification with error summary
  - [ ] Return to enabled state
  - [ ] Keep code editor editable

**Props:**
```typescript
interface ValidateButtonProps {
  code: string;
  diagramType: string;
  onValidationComplete: (result: ValidationResult) => void;
  onValidationError: (error: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
}
```

**Checklist:**
- [ ] Button click works
- [ ] Loading state shows
- [ ] API call succeeds
- [ ] Validation errors display
- [ ] Success feedback shows

---

### 5.4 Create Render Button
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 5.1, 5.2, 5.3
**Estimated Hours:** 3

File: `/components/RightColumn/RenderButton.tsx`

- [ ] Button text: "Render"
- [ ] Requirement: Must validate first (disallow render without validation)
  - [ ] Only enable after successful validation
  - [ ] Or require validation before each render
- [ ] On click:
  - [ ] Disable button, show loading state
  - [ ] Call `renderDiagram()` API
  - [ ] Time estimate: ~10 seconds
  - [ ] Show disabled state during processing
- [ ] Success response:
  - [ ] Update center column with new SVG
  - [ ] Return to enabled state
  - [ ] Show success message in status bar
  - [ ] Mark code as saved (no unsaved indicator)
- [ ] Error response:
  - [ ] Display error in error panel
  - [ ] Show toast notification
  - [ ] Return to enabled state
  - [ ] Keep code editable for retry

**Props:**
```typescript
interface RenderButtonProps {
  code: string;
  diagramType: string;
  onRenderComplete: (diagram: DiagramResponse) => void;
  onRenderError: (error: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  canRender: boolean; // Whether validation passed
}
```

**Checklist:**
- [ ] Button click works
- [ ] Validation check enforced
- [ ] Loading state shows
- [ ] API call succeeds
- [ ] Diagram updates
- [ ] Error handling works

---

### 5.5 Create Error Display Panel
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 5.1
**Estimated Hours:** 3

File: `/components/RightColumn/ErrorPanel.tsx`

- [ ] Collapsible Alert/Collapse component (Ant Design)
- [ ] Display error information:
  - [ ] Error type (syntax, validation, render, LLM)
  - [ ] Error message (user-friendly)
  - [ ] Error code/ID (for developers)
  - [ ] Additional details if available
  - [ ] No stack trace
- [ ] Multiple errors:
  - [ ] Show all errors in list
  - [ ] Numbered for reference
- [ ] Styling:
  - [ ] Error color from theme (red/orange)
  - [ ] Icon indicator (warning, error)
  - [ ] Clear visual hierarchy
- [ ] Interactions:
  - [ ] Click to expand/collapse
  - [ ] Copy error details to clipboard
- [ ] Auto-show on new error
- [ ] Can be dismissed (hides but doesn't clear)

**Props:**
```typescript
interface ErrorPanelProps {
  errors: ErrorInfo[];
  isVisible: boolean;
  onDismiss: () => void;
  type: 'syntax' | 'validation' | 'render' | 'llm';
}

interface ErrorInfo {
  id: string;
  message: string;
  code?: string;
  details?: string;
  timestamp: string;
}
```

**Checklist:**
- [ ] Error panel renders
- [ ] Errors display with all details
- [ ] Collapsible works
- [ ] Copy works
- [ ] Auto-shows on error
- [ ] Dismissable

---

### 5.6 Test Right Column Flow
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 5.1-5.5
**Estimated Hours:** 2

- [ ] Test code display from diagram
- [ ] Test code editing
- [ ] Test validate button
- [ ] Test render button
- [ ] Test validation requirement
- [ ] Test error panel display
- [ ] Test language syntax highlighting
- [ ] Test Monaco features (minimap, bracket matching)

**Checklist:**
- [ ] All features work
- [ ] No console errors
- [ ] Proper state management

---

## PHASE 6: FOOTER SECTION

### 6.1 Create Footer Container
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.1, 1.5
**Estimated Hours:** 2

File: `/components/Footer/Footer.tsx`

- [ ] Create Layout.Footer component
- [ ] Make sticky at bottom (fixed positioning)
- [ ] Z-index: ensure above main content
- [ ] Three-column layout:
  - [ ] Left: Status
  - [ ] Center: SSE Messages
  - [ ] Right: Links
- [ ] Use Row/Col from Ant Design for alignment
- [ ] Add vertical dividers between columns
- [ ] Apply theme background color

**Props:**
```typescript
interface FooterProps {
  currentStatus: string;
  sseMessages: SSEMessage[];
  unreadMessageCount: number;
}
```

**Checklist:**
- [ ] Footer renders
- [ ] Sticky positioning works
- [ ] Three columns visible
- [ ] Dividers show

---

### 6.2 Create Status Column (Column 1)
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 6.1
**Estimated Hours:** 2

File: `/components/Footer/StatusColumn.tsx`

- [ ] Display current status message
- [ ] Status types:
  - [ ] "Idle" (default)
  - [ ] "LLM Execution..." (during prompt processing)
  - [ ] "Rendering..." (during diagram rendering)
  - [ ] "Diagram Generated" (after success)
  - [ ] "Error: [message]" (on failure)
- [ ] Auto-update as state changes
- [ ] Keep last 50 messages (visible on scroll back)
- [ ] Old messages accumulate with scroll
- [ ] No clear button
- [ ] Text styling based on status type:
  - [ ] Idle: Normal
  - [ ] Processing: Highlight color
  - [ ] Success: Success color
  - [ ] Error: Error color

**Props:**
```typescript
interface StatusColumnProps {
  currentStatus: string;
  statusHistory: StatusMessage[];
  statusType: 'idle' | 'processing' | 'success' | 'error';
}

interface StatusMessage {
  message: string;
  timestamp: string;
  type: string;
}
```

**Checklist:**
- [ ] Status displays
- [ ] Status updates on state change
- [ ] History accessible via scroll
- [ ] Colors correct

---

### 6.3 Create SSE Messages Column (Column 2)
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 6.1, 1.5
**Estimated Hours:** 3

File: `/components/Footer/SSEMessagesColumn.tsx`

- [ ] Receive SSE messages from backend
- [ ] Display real-time streaming messages
- [ ] Message format: `[timestamp] message text`
- [ ] Timestamps: Yes, for each message
- [ ] Auto-scroll: Yes, always show latest message
- [ ] Max height with scrolling enabled (not infinite)
- [ ] Message history: Full available via scroll
- [ ] Message types:
  - [ ] Progress updates (e.g., "50% complete")
  - [ ] Info logs
  - [ ] Error logs
  - [ ] Validation retry info (for 3-tier validation visibility)
- [ ] No clear button
- [ ] Message styling:
  - [ ] Info: Normal text
  - [ ] Error: Red text
  - [ ] Progress: Highlight color
  - [ ] Retry: Warning color

**Props:**
```typescript
interface SSEMessagesColumnProps {
  messages: SSEMessage[];
  isConnected: boolean;
  unreadCount: number;
}

interface SSEMessage {
  id: string;
  timestamp: string;
  type: 'info' | 'error' | 'progress' | 'retry';
  message: string;
}
```

**Checklist:**
- [ ] Messages display in real-time
- [ ] Auto-scroll works
- [ ] Timestamp formatting correct
- [ ] Message colors correct
- [ ] No clear button
- [ ] Connection status shown

---

### 6.4 Create Links Column (Column 3)
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 6.1
**Estimated Hours:** 1

File: `/components/Footer/LinksColumn.tsx`

- [ ] "About" link → opens in new tab (external URL)
- [ ] "Help" link → opens in new tab (documentation)
- [ ] Disclaimer text: "Information was AI Generated"
- [ ] Right-aligned in footer
- [ ] Links styled as theme primary color
- [ ] Hover effects

**Checklist:**
- [ ] Links display
- [ ] Clicking opens new tab
- [ ] Disclaimer visible
- [ ] Right-aligned
- [ ] Styling correct

---

### 6.5 Integrate SSE Client
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.4, 6.3
**Estimated Hours:** 3

In Footer component or higher (App level):

- [ ] Initialize SSE connection to `/api/v1/logs/stream`
- [ ] Handle connection states:
  - [ ] Connecting: Show connecting indicator
  - [ ] Connected: Normal operation
  - [ ] Disconnected: Show disconnection notice
  - [ ] Error: Show error message
- [ ] Implement reconnection logic:
  - [ ] Exponential backoff
  - [ ] Max retry attempts (e.g., 5)
  - [ ] Max wait time (e.g., 30 seconds)
- [ ] Message queue:
  - [ ] Max 100 messages in memory
  - [ ] Remove oldest when limit reached
- [ ] Message filtering:
  - [ ] Filter by type if needed
  - [ ] Parse timestamp from message
- [ ] Handle connection drops:
  - [ ] Show "SSE disconnected" message
  - [ ] Attempt automatic reconnection
  - [ ] Show retry status

**Checklist:**
- [ ] Connection established
- [ ] Messages received and displayed
- [ ] Reconnection works
- [ ] Error handling works
- [ ] Message queue limited

---

### 6.6 Test Footer
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 6.1-6.5
**Estimated Hours:** 2

- [ ] Test status updates
- [ ] Test SSE message streaming
- [ ] Test auto-scroll
- [ ] Test link navigation
- [ ] Test sticky positioning
- [ ] Test message history scroll
- [ ] Test disconnection/reconnection

**Checklist:**
- [ ] All features work
- [ ] No console errors
- [ ] Performance good with many messages

---

## PHASE 7: INTEGRATION & TESTING

### 7.1 Integrate Main Page Component
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 3.1-6.6
**Estimated Hours:** 2

File: `/pages/ArchitectureGenStudio/index.tsx`

- [ ] Import all main components:
  - [ ] Header
  - [ ] LeftColumn
  - [ ] CenterColumn
  - [ ] RightColumn
  - [ ] Footer
- [ ] Create main layout using Layout component
- [ ] Setup state management at page level
- [ ] Setup resize handlers for columns
- [ ] Setup collapse handlers for columns
- [ ] Test component imports

**Checklist:**
- [ ] All components render
- [ ] No import errors
- [ ] Layout looks correct

---

### 7.2 Complete State Management
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 7.1, 1.3
**Estimated Hours:** 3

- [ ] Implement all state update handlers:
  - [ ] onAgentChange
  - [ ] onPromptChange
  - [ ] onDiagramTypeChange
  - [ ] onAgentOptionSelect
  - [ ] onSubmitPrompt
  - [ ] onValidateCode
  - [ ] onRenderDiagram
  - [ ] onCancelRequest
  - [ ] onColumnWidthChange
  - [ ] onColumnCollapsedChange
- [ ] State mutations:
  - [ ] Test state updates flow correctly
  - [ ] Test derived state calculations
- [ ] localStorage integration:
  - [ ] Load on mount
  - [ ] Save on change
  - [ ] Handle missing data gracefully

**Checklist:**
- [ ] All handlers implemented
- [ ] State updates work
- [ ] localStorage persists correctly

---

### 7.3 Resizable Columns Implementation
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 7.1
**Estimated Hours:** 3

- [ ] Install `react-resizable-panels` or similar library
- [ ] Implement column dividers:
  - [ ] Between left and center
  - [ ] Between center and right
- [ ] Resize handlers:
  - [ ] Min width: 1/3 of available space
  - [ ] Max width: remaining space
  - [ ] Constraints: at least one column 1/3 width
- [ ] Persist widths to localStorage
  - [ ] Load on mount
  - [ ] Save on resize
- [ ] Visual feedback:
  - [ ] Cursor changes on divider hover
  - [ ] Highlight divider on hover
  - [ ] Smooth resize animation

**Checklist:**
- [ ] Columns resizable
- [ ] Min/max constraints work
- [ ] Widths persist
- [ ] No layout breaks

---

### 7.4 Column Collapse Implementation
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 7.1
**Estimated Hours:** 2

- [ ] Add collapse toggle button to each column header
- [ ] Collapse behavior:
  - [ ] Hide column content
  - [ ] Show button in header to restore
  - [ ] Constraint: at least one column must be open
  - [ ] Prevent collapsing if only one column
- [ ] Persist collapse state to localStorage
- [ ] Animation on collapse/expand
- [ ] Space redistribution:
  - [ ] When a column collapses, redistribute space to others
  - [ ] Maintain minimum width constraints

**Checklist:**
- [ ] Toggle buttons work
- [ ] Collapse/expand works
- [ ] Constraint enforced
- [ ] Space redistributes

---

### 7.5 API Integration Testing
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 1.4, 7.2
**Estimated Hours:** 3

Test each API endpoint:

- [ ] Fetch agents: `/api/v1/agents`
  - [ ] Verify response format
  - [ ] Test error handling
  - [ ] Test loading state
- [ ] Fetch agent options: `/api/v1/agents/{agentId}/options`
  - [ ] Verify response format
  - [ ] Test for selected agent
  - [ ] Test error handling
- [ ] Submit prompt: `/api/v1/diagrams/v2/generate`
  - [ ] Verify request format
  - [ ] Verify response format
  - [ ] Test SSE streaming
  - [ ] Test cancellation
  - [ ] Test error handling
- [ ] Validate code: `/api/v1/diagrams/v2/validate`
  - [ ] Verify request format
  - [ ] Verify response format
  - [ ] Test timeout (30 seconds)
  - [ ] Test error handling
- [ ] Render diagram: `/api/v1/diagrams/v2/render`
  - [ ] Verify request format
  - [ ] Verify SVG response
  - [ ] Test for each diagram type
  - [ ] Test error handling
- [ ] Cancel request: `/api/v1/diagrams/v2/cancel`
  - [ ] Verify cancellation works
  - [ ] Test cleanup

**Checklist:**
- [ ] All endpoints callable
- [ ] Request/response formats correct
- [ ] Error handling works
- [ ] No API errors in console

---

### 7.6 User Workflow Testing
**Priority:** 🔴 CRITICAL
**Status:** ⏳ Pending
**Depends on:** 7.1-7.5
**Estimated Hours:** 4

Test complete workflows:

1. **Basic Flow:**
   - [ ] Select agent
   - [ ] Select agent option (auto-populate template)
   - [ ] Edit prompt
   - [ ] Click submit
   - [ ] Wait for diagram generation
   - [ ] View diagram in center column
   - [ ] View code in right column
   - [ ] View SSE messages in footer

2. **Tab Switching:**
   - [ ] Generate diagram in Mermaid
   - [ ] Switch to D2 tab (shows empty)
   - [ ] Click render on generated code
   - [ ] D2 diagram appears
   - [ ] Switch back to Mermaid
   - [ ] Original Mermaid diagram still there

3. **Code Editing:**
   - [ ] Select different diagram type tab
   - [ ] Edit code in right column
   - [ ] Click validate (verify check works)
   - [ ] Click render
   - [ ] Center column updates with new diagram
   - [ ] Switch tabs (warn about unsaved edits)
   - [ ] Render first, then switch (no warning)

4. **Cancel Flow:**
   - [ ] Click submit
   - [ ] During processing, click cancel
   - [ ] Request cancels
   - [ ] Editor re-enables
   - [ ] Button returns to normal

5. **Error Handling:**
   - [ ] Submit with empty prompt (shows error)
   - [ ] Invalid code validation (shows errors)
   - [ ] Render fails (shows error)
   - [ ] API timeout (shows timeout error)
   - [ ] Network error (shows network error)

6. **Persistence:**
   - [ ] Make changes to prompt, agent, etc.
   - [ ] Reload page
   - [ ] Verify last state restored

7. **Column Management:**
   - [ ] Resize columns (min/max constraints)
   - [ ] Collapse left column
   - [ ] Collapse right column
   - [ ] Cannot collapse all
   - [ ] Widths persist on reload

8. **Zoom & Export:**
   - [ ] Zoom in/out with buttons
   - [ ] Zoom with keyboard shortcuts
   - [ ] Zoom with slider
   - [ ] Reset zoom
   - [ ] Export SVG
   - [ ] Export PDF
   - [ ] Export code

**Checklist:**
- [ ] All workflows complete successfully
- [ ] No errors or unexpected behavior
- [ ] State persists correctly
- [ ] Performance acceptable

---

### 7.7 Error State Testing
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1-7.6
**Estimated Hours:** 2

Test error scenarios:

- [ ] Network unavailable
- [ ] API timeout
- [ ] Invalid response format
- [ ] LLM API error
- [ ] Diagram provider error
- [ ] Validation error
- [ ] Render error
- [ ] SSE connection drop
- [ ] SSE reconnection

**Checklist:**
- [ ] All errors handled gracefully
- [ ] User-friendly messages shown
- [ ] No app crashes

---

### 7.8 Performance Testing
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1-7.7
**Estimated Hours:** 2

- [ ] Load with large prompt (5000 characters)
- [ ] Load with large diagram (1000+ nodes)
- [ ] Render large SVG without lag
- [ ] Virtual scrolling works for large diagrams
- [ ] Zoom performance with large diagram
- [ ] Edit large code file (100K+ lines)
- [ ] Monitor memory usage
- [ ] Check bundle size

**Checklist:**
- [ ] No performance bottlenecks
- [ ] Smooth interactions
- [ ] Memory usage acceptable

---

## PHASE 8: POLISH & DEPLOYMENT

### 8.1 Accessibility Review
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1-7.8
**Estimated Hours:** 2

- [ ] Keyboard navigation:
  - [ ] Tab through all interactive elements
  - [ ] Shift+Tab to reverse
  - [ ] Enter to activate buttons
  - [ ] Esc to cancel dialogs
- [ ] ARIA labels:
  - [ ] Buttons have aria-label
  - [ ] Icons have title/aria-label
  - [ ] Input fields have labels
- [ ] Color contrast:
  - [ ] All text meets WCAG AA standards
  - [ ] No color-only indicators
- [ ] Focus indicators:
  - [ ] Focus rings visible
  - [ ] Focus order logical
- [ ] Screen reader testing:
  - [ ] Test with popular screen readers

**Checklist:**
- [ ] WCAG 2.1 AA compliant
- [ ] Keyboard navigation works
- [ ] Screen reader friendly

---

### 8.2 Theme Testing
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1, 2.1
**Estimated Hours:** 2

- [ ] Test all 11 theme variants:
  - [ ] Colors applied correctly
  - [ ] Buttons themed
  - [ ] Editor themed
  - [ ] Status bar themed
- [ ] Test dark/light mode toggle
- [ ] Verify Monaco editor respects theme
- [ ] Test on different screen backgrounds

**Checklist:**
- [ ] All themes look correct
- [ ] Theme switching smooth
- [ ] No hardcoded colors

---

### 8.3 Cross-browser Testing
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1-8.2
**Estimated Hours:** 2

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (if applicable)

Test on each:
- [ ] Layout renders correctly
- [ ] All features work
- [ ] Performance acceptable
- [ ] No console errors

**Checklist:**
- [ ] All browsers supported
- [ ] Layout responsive
- [ ] No browser-specific issues

---

### 8.4 Documentation
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** All previous phases
**Estimated Hours:** 2

- [ ] Create component documentation:
  - [ ] Props interfaces
  - [ ] Usage examples
  - [ ] State management guide
- [ ] API integration guide:
  - [ ] Endpoint descriptions
  - [ ] Request/response examples
  - [ ] Error handling
- [ ] User guide:
  - [ ] How to use the studio
  - [ ] Supported diagram types
  - [ ] Tips and tricks
- [ ] Developer guide:
  - [ ] Architecture overview
  - [ ] Component hierarchy
  - [ ] State flow diagram
  - [ ] Adding new diagram types

**Checklist:**
- [ ] All documentation complete
- [ ] Examples working
- [ ] Diagrams clear

---

### 8.5 Bug Fixes & Polish
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 7.1-8.4
**Estimated Hours:** 3

- [ ] Fix reported bugs
- [ ] Improve UI/UX based on testing
- [ ] Optimize animations
- [ ] Fine-tune spacing/padding
- [ ] Fix console warnings
- [ ] Remove debug code

**Checklist:**
- [ ] No known bugs
- [ ] No console errors
- [ ] UI polished

---

### 8.6 Prepare for Deployment
**Priority:** 🟡 HIGH
**Status:** ⏳ Pending
**Depends on:** 8.1-8.5
**Estimated Hours:** 1

- [ ] Build optimizations:
  - [ ] Minification enabled
  - [ ] Code splitting configured
  - [ ] Assets optimized
- [ ] Environment variables:
  - [ ] API endpoints configured
  - [ ] Theme colors set
  - [ ] Feature flags set
- [ ] Deploy to staging:
  - [ ] Verify build succeeds
  - [ ] Test in staging environment
  - [ ] Performance check
- [ ] Release notes prepared:
  - [ ] Features listed
  - [ ] Known limitations noted
  - [ ] Setup instructions included

**Checklist:**
- [ ] Build succeeds
- [ ] No deployment errors
- [ ] Staging environment stable

---

## PROGRESS TRACKING

### Completion Metrics

| Phase | Target | Completed | % | Status |
|-------|--------|-----------|---|--------|
| 1. Setup | 5 tasks | 5 | 100% | ✅ |
| 2. Header | 7 tasks | 0 | 0% | ⏳ |
| 3. Left Column | 6 tasks | 0 | 0% | ⏳ |
| 4. Center Column | 7 tasks | 0 | 0% | ⏳ |
| 5. Right Column | 6 tasks | 0 | 0% | ⏳ |
| 6. Footer | 6 tasks | 0 | 0% | ⏳ |
| 7. Integration | 8 tasks | 0 | 0% | ⏳ |
| 8. Polish | 6 tasks | 0 | 0% | ⏳ |
| **TOTAL** | **51** | **5** | **10%** | ⚙️ |

### Phase 1 Summary
- ✅ **Status:** COMPLETE (5/5 tasks)
- **Time Spent:** ~2.5 hours (vs 2-3 days estimated)
- **Files Created:** 8
- **Lines of Code:** ~1,200 lines
- **Key Deliverables:**
  - Complete project structure with proper directory layout
  - Full TypeScript type system (350+ lines, 26 interfaces)
  - State management hooks with localStorage persistence
  - API client integration with all 6 endpoints
  - React Router integration at `/studio` path
  - Base CSS styles and component scaffolding
  - Main component with state/API initialization

---

## NOTES & CONVENTIONS

### Code Style
- Use TypeScript for all new code
- Follow existing Whysper codebase style
- Use Ant Design components consistently
- Follow React/Hook best practices
- Use descriptive variable names

### Component Structure
```
ComponentName/
  ├── ComponentName.tsx          # Main component
  ├── ComponentName.types.ts     # Type definitions
  ├── ComponentName.module.css   # Styles (optional)
  └── index.ts                   # Export
```

### State Management
- Use React hooks (useState, useEffect)
- Custom hooks for reusable logic
- Props-based component communication
- localStorage for persistence

### Testing
- Focus on critical paths first
- Test user workflows end-to-end
- Verify API integrations
- Check error handling

### Git Commits
Each major task completion should have a commit:
```
git commit -m "feat: implement [component/feature]

- Task: [Task ID]
- Description of changes
- Tests included
"
```

---

## TIMELINE ESTIMATE

- **Phase 1:** 2-3 days
- **Phase 2:** 2-3 days
- **Phase 3:** 3-4 days
- **Phase 4:** 4-5 days
- **Phase 5:** 3-4 days
- **Phase 6:** 2-3 days
- **Phase 7:** 3-5 days
- **Phase 8:** 2-3 days

**Total Estimated Timeline:** 22-30 days (roughly 4-6 weeks)

---

**Document Status:** 📋 READY FOR IMPLEMENTATION
**Last Updated:** 2025-11-03
