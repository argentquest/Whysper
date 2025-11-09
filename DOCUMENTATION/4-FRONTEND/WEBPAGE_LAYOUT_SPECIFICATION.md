# Architecture Gen Studio - Web Page Layout Specification

## Overview
A specialized three-column web application for generating and editing architectural diagrams using AI-powered agents.

---

## HEADER SECTION

### Branding (Left-Aligned)

- **Line 1:** Well Fargo
- **Line 2:** Architecture Gen Studio

### Agent Selector

- **Dropdown/List:** Agent selection dropdown
- **Position:** In the header (center or right area)
- **Purpose:** Allows user to select which agent to work with

### Navigation Menu

- **Home** >> Current Home
- **Architecture Gen Studio** > New Page
- **Settings** \ Help

### Features

- **User Account Options:** Profile/Logout menu
- **Notification Icons/Badges:** Yes
- **Sticky:** Yes (stays visible while scrolling)
- **Search Bar:** Not included

---

## MAIN CONTENT AREA (Three Columns)

### Main Area Features

- **Collapsible Columns:** Each column (left, center, right) can be collapsed independently
- **Resizable Widths:** Column widths can be adjusted by dragging column dividers
- **Independent Scrollbars:** Each column has its own scrollbar and scrolls independently
- **Responsive Layout:** Columns maintain independent scroll positions

### LEFT COLUMN - Prompt Control Panel

**Purpose:** Prompt input and subagent/agent option display

**Structure:**

- **Row 1:** List of AgentOptions (tied to agent selected in header)
- **Row 2:** Text editor for writing prompts
- **Button:** Submit button (below text editor - triggers LLM processing)

**Features:**

- **AgentOption Display:** Vertical list of clickable items (menu/list component style)
- **Selection Model:** Single selection only - only one AgentOption can be active at a time
- **Auto-Population:** When a user selects an AgentOption, the `template` field is automatically populated into the Monaco prompt editor as the initial/default prompt value
- **Collapsible:** Yes (users can collapse to see more content)
- **Icons:** No, text labels only
- **Active/Highlighted States:** Yes (shows currently selected AgentOption with visual highlighting)
- **Scroll Behavior:** Independent scrollbar within column
- **Resizable:** Yes, column width is adjustable

**Monaco Editor Configuration (Left Column - Prompt Editor):**

- **Height:** Expands to fill available space (flexible height with scrolling)
- **Line Numbers:** No
- **Word Wrap:** Yes
- **Syntax Highlighting:** No (plain text)
- **Code Completion/IntelliSense:** No
- **Mini-map:** No
- **Character Limit:** None (unlimited)
- **Placeholder Text:** Yes - "Enter your prompt here or select an Agent Option template above"
- **Read-only:** No (fully editable)

**Submit Button Behavior:**

- **Button State While Processing:**
  - Submit button is **disabled** during LLM processing
  - Button shows **loading spinner/indicator**
  - Button text changes to **"Generating..."**
  - A secondary **Cancel button** appears next to Submit button to allow user to stop the LLM call

- **User Interactions During Processing:**
  - Monaco prompt editor becomes **read-only** during processing
  - User **cannot edit** the prompt while diagram is generating
  - User **must click Cancel** to enable editing again

- **Cancelation Support:**
  - **Cancel button** is supported and visible during processing
  - Clicking Cancel stops the LLM call and re-enables the editor
  - Cancellation does NOT save any partial results

- **Multiple Submissions:**
  - User **cannot** click Submit again while processing is in progress
  - Button is disabled, so additional clicks are impossible
  - User must either wait for completion or click Cancel and resubmit
  - **No queuing** - only one request can be active at a time

- **Success Indication:**
  - When diagram is successfully generated:
    - Diagram appears in **Center Column**
    - **Toast notification** displays confirming "Diagram Generated Successfully" (or similar)
    - Button returns to normal "Submit" state and is enabled again
    - Editor returns to editable state

**Components:**

1. AgentOption list (vertical menu/list of clickable items, directly under selected agent header)
2. Prompt text editor area (Monaco Editor - auto-populated with selected AgentOption's template, expands to fill available space)
3. Submit button (positioned below editor, with Cancel button appearing during processing)

---

### CENTER COLUMN - Diagram Rendering & Visualization

**Purpose:** Display and manage generated diagrams

**Upper Section - Diagram Type Tabs:**

- Tab selection for diagram types:
  - Mermaid
  - D2
  - Structurizr
  - PlantUML

**Diagram Type Tab Behavior:**

- **Initial Tab Selection:** Shows both the originally requested/generated diagram type AND the first available tab (Mermaid) as default options
- **Tab Switching Behavior:** When user clicks a different diagram type tab:
  - If diagram has NOT been generated for that type: Shows empty state/loading state
  - System prepares to regenerate the original prompt for the selected diagram type
  - User can request re-rendering of the prompt for the new diagram type
  - Tabs that haven't been requested show as empty until explicitly rendered
- **Multi-Tab Generation:** Only one diagram type is generated at a time (no upfront generation of all types)
- **Automatic Format Conversion:** NOT supported - user must request new render for different diagram type
- **Right Column Synchronization:** When user switches to a different diagram type tab:
  - Right column code editor automatically updates to show code for the selected diagram type
  - Right column is locked to the currently selected center column tab (no independent viewing)
  - If user edited the original code: changes are lost when switching tabs (unless user clicks Render first)
  - If user edits code in right column and wants to switch tabs: must click Render first to apply changes, or switch will discard edits

**Middle Section - Diagram Rendering Area:**

- Render area for selected diagram type
- **Zoom Functionality:** Allow zoom in/out
- **Download:** Save diagram as SVG file
- **Minimize/Maximize Buttons:** Controls to minimize/maximize the rendered area
- **Infinite Scroll:** Content loads as user scrolls down
- **Action Buttons:** Yes, for content interactions

**Features:**

- **Responsive Design:** Not required (desktop-only)
- **Pagination/Infinite Scroll:** Infinite scroll enabled
- **Filtering/Sorting:** Not needed
- **Breadcrumbs:** Not needed
- **Content Types:** Diagram rendering (SVG)
- **Scroll Behavior:** Independent scrollbar within column
- **Collapsible:** Yes (can be collapsed to show more space for other columns)

**Lower Row - SVG Display Area:**

- Large area for displaying the rendered SVG
- Minimize/maximize controls

---

### RIGHT COLUMN - Code Editor & Validation

**Purpose:** Manual diagram code editing and validation

**Structure:**

1. **Monaco Text Editor Area:**
   - Display diagram code (editable)
   - Allow manual modification of rendered code
   - Independent scrollbar within column

2. **Action Buttons (Below Editor):**
   - **Validate Button:** Validates diagram code
   - **Render Button:** Renders the diagram in center column

3. **Error Display Area (Collapsible):**
   - Shows validation errors or error messages
   - Collapsible to save space

**Monaco Editor Configuration (Right Column - Code Editor):**

- **Height:** Expands to fill available space (flexible height with scrolling)
- **Line Numbers:** No
- **Word Wrap:** No
- **Syntax Highlighting:** No (plain text - no language-specific highlighting)
- **Code Completion/IntelliSense:** No
- **Mini-map:** No
- **Character Limit:** None (unlimited)
- **Placeholder Text:** Auto-populated with diagram code from selected diagram type tab in center column
- **Read-only:** No (fully editable)
- **Bracket Matching/Highlighting:** Yes (enabled for code editing convenience)
- **Language Detection:** No manual selector needed - editor displays code for whatever diagram type tab is currently active in center column

**Features:**

- **Content Type:** Editable code + interactive buttons
- **Scroll Behavior:** Independent scrollbar within column
- **Collapsible Sections:** Yes, error area is collapsible; column itself can be collapsed
- **Resizable:** Yes, column width is adjustable
- **Call-to-Action:** Buttons only (Validate and Render), no forms
- **Contextual Updates:** When "Render" button is pressed, center column displays the newly rendered diagram

---

## FOOTER SECTION - Status Bar

### Overall Footer Behavior

- **Sticky Position:** Footer is **sticky** and always visible at the bottom of the screen while scrolling
- **Cannot scroll out of view:** Footer remains fixed at bottom at all times

### Three-Column Status Bar Layout

**Column 1 - Current Status:**

- **Default State:** "Idle"
- **Status Types:**
  - "Idle" - Default/ready state
  - "LLM Execution..." - During prompt processing
  - "Rendering..." - During diagram rendering
  - "Diagram Generated" - After successful generation
  - "Error: [message]" - When validation or rendering fails
- **Auto-Update:** Yes, updates automatically as state changes
- **Message History:** Shows last 50 status messages (currently implemented pattern)
- **Clear Behavior:** Old messages are kept (accumulate with scroll)
- **Error Display:** Validation/rendering errors show as toast notifications (separate from column 1)

**Column 2 - Backend SSE Messages:**

- **Real-time Streaming:** Messages appear as they stream in from backend (via SSE)
- **Auto-scroll:** Yes, automatically scrolls to show latest message
- **Message History:** Full history available via scroll/history
- **Timestamps:** Yes, each message has a timestamp
- **Height:** Has **max height** with scrolling enabled (not infinite expansion)
- **Clear Button:** No clear/reset button - messages persist for session
- **Message Format:** Each message appears on its own line with timestamp prefix

**Column 3 - Links:**

- **About** link - Opens in new tab
- **Help** link - Opens in new tab
- **Disclaimer:** "Information was AI Generated" (displayed in footer)
- **Static Links Only:** No other interactive elements

### Footer Content Structure

- Left-aligned: Column 1 (Current Status)
- Center-aligned: Column 2 (SSE Backend Messages)
- Right-aligned: Column 3 (About/Help Links + Disclaimer)
- **Dividers:** Vertical dividers separate the three columns

---

## DESIGN SYSTEM & THEMING

### Design Framework

- **UI Component Library:** Ant Design (antd)
- **Design Principles:** Follow Ant Design best practices and patterns
- **Accessibility:** WCAG 2.1 AA compliance

### Theming Engine

- **Theme Provider:** Existing `ThemeProvider` wrapper (`frontend/src/themes/ThemeProvider.tsx`)
- **Theme Context:** `ThemeContext` for global theme state management
- **Custom Hook:** `useTheme()` hook for accessing theme context in components
- **Ant Design ConfigProvider:** Centralized theme configuration via `getThemeConfig()`
- **Color System:** 11 Ant Design theme variants from `antd-themes.ts`
- **Persistence:** localStorage for theme preference persistence
- **Default Theme:** `modernGradient` (can be changed to any of the 11 variants)

### Ant Design Components Usage

#### Header

- **Layout.Header:** Primary layout component
- **Menu:** Navigation menu with responsive behavior
- **Select:** Agent selector dropdown
- **Badge:** Notification badges
- **Avatar/Dropdown:** User account menu

#### Main Content Area

- **Layout.Sider:** Left column (collapsible sidebar)
- **Layout.Content:** Center and content areas
- **Tabs:** Diagram type tabs
- **Button:** Action buttons (Validate, Render, Submit)
- **Editor (Monaco integrated with antd styling):** Code editor

#### Resizable Columns

- **react-resizable-panels or similar:** Column resizing functionality
- **Styled to match antd design language**

#### ScrollBar & Scrolling

- **antd Scrollbar:** Custom scrollbars matching design system
- **Independent scroll containers:** Each column uses scroll containers

#### Error Handling

- **Alert:** Error display in right column
- **Collapse:** Collapsible error section
- **Message/Notification:** Real-time error notifications

#### Footer

- **Layout.Footer:** Footer container
- **Divider:** Column separators in status bar
- **Text/Typography:** Status messages

### Theme Customization Points

- **Primary Colors:** Configurable via theme tokens
- **Typography:** Font sizes, weights, line heights
- **Spacing:** Consistent padding/margins per antd grid system
- **Border Radius:** Rounded corners following design system
- **Shadows:** Elevation system for depth

### CSS-in-JS & Styling

- **Solution:** Ant Design's built-in CSS-in-JS (emotion/styled-components)
- **Token System:** Use antd token system for consistent styling
- **Theme Definitions:** All theme tokens defined in `frontend/src/themes/antd-themes.ts`
- **Component Styling:** Use Ant Design token system for component overrides
- **Data Attribute:** Document root uses `data-theme` attribute for CSS-based theme switching

### Responsive Behavior

- **Breakpoints:** Follow Ant Design breakpoints
- **Sticky Header:** Use antd positioning utilities
- **Collapsible Sidebars:** antd Sider component with collapse trigger

---

## APPLICATION WORKFLOW

### Typical User Flow:

1. **User selects agent** from header agent selector dropdown
2. **User views available subagents** for that agent in Left Column
3. **User writes prompt** in Left Column Monaco text editor
4. **User clicks Submit** button in Left Column
5. **LLM processes** the request (SSE messages appear in Footer Column 2)
6. **Diagram is generated** in Center Column
7. **User selects diagram type** (Mermaid, D2, Structurizr, PlantUML) via tabs
8. **Diagram code appears** in Right Column Monaco editor
9. **User can optionally:**
   - Manually edit code in Right Column
   - Click **Validate** to check code validity (calls backend validation)
   - Click **Render** to regenerate diagram in Center Column
10. **User can zoom, download** SVG from Center Column
11. **Footer displays** real-time status and SSE backend messages

---

## REUSING EXISTING WHYSPER CODEBASE

### Frontend Integration

#### Existing Components to Reuse

- **ThemeProvider** - Existing ConfigProvider wrapper with 11 Ant Design theme variants (`frontend/src/themes/ThemeProvider.tsx`)
- **useTheme Hook** - Custom hook for accessing theme context in components (`frontend/src/themes/useTheme.ts`)
- **Theme Context** - Global theme state management (`frontend/src/themes/ThemeContext.ts`)
- **Theme Config** - 11 predefined Ant Design theme variants (`frontend/src/themes/antd-themes.ts`)
- Layout components from `layout/` folder
- Monaco Editor integration from `editor/` folder
- Diagram renderers: `MermaidRenderer`, `D2Renderer` from `chat/` folder
- API client from `services/api.ts` (Axios with interceptors)
- SSE client from `services/sseClient.ts` (real-time message streaming)
- Type definitions from `types/index.ts`

#### Existing Services to Leverage

- `APIService` - For backend communication
- `DiagramProviderService` - Provider selection and rendering
- Conversation session management patterns

### Backend Integration

#### Existing Diagram System (`backend/diagrams/`)

- 7 pluggable providers:
  - `mermaidv1` - Mermaid CLI
  - `d2v1` - D2 CLI
  - `krokid2`, `krokimermaid`, `krokic4`, `krokiplantuml`, `krokistructurizr` - Kroki API
- `BaseDiagramProvider` - Abstract base class
- `validate_code()`, `render()`, `auto_fix_pattern_based()` - Core methods
- Provider registry system for plugin discovery

#### Existing Endpoints to Leverage

- `/api/v1/diagrams/v2/validate` - Code validation
- `/api/v1/diagrams/v2/render` - Diagram rendering
- `/api/v1/diagrams/v2/fix` - Auto-fix with LLM
- `/api/v1/logs/stream` - SSE real-time streaming
- `/api/v1/chat` - Message processing

#### Existing Agent System

- Agent prompts in `prompts/` directory (YAML format)
- Agent selection dropdown pattern
- System message integration with selected agent

### State Management

#### Reuse Patterns

- React Hooks (useState/useEffect) - no Redux
- Context API for theming (existing `ThemeProvider`)
- Props-based component communication
- localStorage for persistence

#### Message Structure (reuse from existing)

```typescript
Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  metadata: {
    codeBlocks,
    diagrams,
    tokens,
    model,
    provider // NEW: diagram provider used
  }
}
```

### New Component Structure

#### Left Column

- Agent selector (moved from left to header)
- SubAgent list component (reuse from existing UI patterns)
- Monaco Editor from existing `editor/` folder
- Submit button

#### Center Column

- Provider tabs (reuse tab pattern from existing)
- Diagram renderer (reuse from chat renderers)
- Zoom/pan controls (existing implementations)
- SVG export (existing functionality)

#### Right Column

- Monaco Editor (existing integration)
- Validate button → calls `/api/v1/diagrams/v2/validate`
- Render button → calls `/api/v1/diagrams/v2/render`
- Error display (reuse Alert/Collapse from existing)

#### Header Section

- Agent selector (new placement, leverage existing dropdown)
- Notification badges (existing Badge component)
- User account (existing Avatar/Dropdown)

#### Footer Section

- Status bar with 3 columns (new layout)
- SSE integration (reuse from existing sseClient.ts)
- Divider components from Ant Design

---

## DATA TYPES

### New Type: AgentOption

- **Purpose:** Represents options/settings for an agent, including help content and default prompt templates
- **Association:** Tied directly to Agent (one-to-many relationship)
- **Storage:** Extend existing `prompts/` directory structure
- **Usage Pattern:** When a user selects an AgentOption from the left column, the template field is used as the default value in the Monaco prompt editor

**AgentOption JSON Structure:**

```typescript
interface AgentOption {
  id: string;                  // Unique identifier for this option
  name: string;                // Display name of the option
  description?: string;         // Short description
  helpContent: string;          // Help/documentation text for this option
  template: string;             // Default prompt template (becomes initial editor value)
  tags?: string[];              // Optional tags for categorization
}
```

**Example AgentOption:**

```json
{
  "id": "c4-microservices",
  "name": "C4 Microservices Architecture",
  "description": "Generate C4 diagrams for microservices systems",
  "helpContent": "This option is optimized for creating C4 context, container, component, and code diagrams of microservices architectures. Supports multiple languages and frameworks.",
  "template": "Create a C4 diagram showing a microservices architecture with the following components:\n1. API Gateway\n2. User Service\n3. Order Service\n4. Inventory Service\n5. Payment Service\n\nInclude interactions between components.",
  "tags": ["c4", "microservices", "architecture"]
}
```

### Extend Existing Types

- `Message` - Add `provider` field to metadata
- `ConversationSession` - Add `selectedAgent` field
- `AppSettings` - Add `diagramProvider` preference

---

## TECHNICAL NOTES

### Frontend Stack (Reuse)

- **Framework:** React 18.3.1 + TypeScript 5.8.3
- **Build:** Vite 7.1.7
- **UI Components:** Ant Design 5.27.4
- **Editor:** Monaco Editor 0.53.0
- **API:** Axios 1.12.2
- **Diagram Rendering:** Mermaid 11.12.0

### Backend Stack (Reuse)

- **Framework:** FastAPI (async)
- **Python Version:** 3.x
- **Diagram Providers:** Mermaid CLI, D2 CLI, Kroki API
- **Validation:** 3-tier (pattern-based, LLM-based, manual)
- **Real-time:** SSE for progress streaming

### SVG Display & Export

- Uses existing diagram render system
- SVG format output from all providers
- Download functionality via existing patterns

### Column Management

- Resizable dividers using `react-resizable-panels` pattern
- Independent scroll containers with custom scrollbars
- Collapse/expand via existing collapse button patterns

### Diagram Validation Flow

1. User edits code in Right Column Monaco editor
2. Click **Validate** → POST `/api/v1/diagrams/v2/validate`
3. Backend validates using selected provider
4. Error display in Right Column (Alert component)
5. Click **Render** → POST `/api/v1/diagrams/v2/render`
6. Center Column updates with new SVG
7. SSE messages stream to Footer

---

## RESPONSIVE CONSIDERATIONS
- **Desktop-only application** (no responsive design required for smaller screens)
- All three columns visible simultaneously

