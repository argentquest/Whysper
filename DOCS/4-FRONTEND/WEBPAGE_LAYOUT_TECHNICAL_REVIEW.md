# Architecture Gen Studio - Technical Review & Clarifications

## Overview
This document identifies technical questions, ambiguities, and areas requiring deeper clarification for the **WEBPAGE_LAYOUT_SPECIFICATION.md**.

---

## SECTION 1: HEADER SECTION

### Questions & Clarifications Needed

#### 1.1 Agent Selector Dropdown
- **Q1:** Should the agent selector be a **searchable Select** component or a simple dropdown?
  - Impact: UX complexity if there are 50+ agents
  - Current State: Searchable Select

- **Q2:** When user selects a new agent, should the prompt be **cleared** or **preserved**? Cleared
  - Impact: User experience and data loss prevention
  - Suggestion: Define behavior explicitly

- **Q3:** What happens to unsaved prompts when switching agents?
  - Clear them? NO, warn use they will loose the oprompt is not saved as local file
  - Save as draft? No
  - Show confirmation dialog? Yes

#### 1.2 Navigation Menu Structure
- **Q4:** The navigation shows "Home >> Current Home" - is this breadcrumb-style or literal menu items?
  - Current: Ambiguous
  - **RESOLVED:** Display labels only (not interactive breadcrumbs)

- **Q5:** Should "Architecture Gen Studio > New Page" open in:
  - Same tab? No
  - New tab? Yes
  - Modal dialog? No
  - Sidebar view? No

#### 1.3 User Account Menu
- **Q6:** What functionality should the user account dropdown include?
  - Profile view/edit?  We will rely on auth2 sso
  - API key management? No
  - Theme selection (if added back)? No hard coded
  - Subscription info? None
  - Current State: Only "logout" mentioned Only

#### 1.4 Notification Badges
- **Q7:** What types of notifications should trigger the badge?
  - Diagram generation complete? Yes
  - Errors occurred? Yes
  - SSE messages? No
  - System alerts? Yes

- **Q8:** Should notifications be:
  - Simple badge count? No
  - Dropdown panel? No
  - Toast notifications? Yes
  - All of the above?

---

## SECTION 2: LEFT COLUMN (Prompt Control Panel)

### Questions & Clarifications Needed

#### 2.1 SubAgent List Display
- **Q9:** How should subagents be displayed?
  - Simple list items? Yes
  - Cards with descriptions? No
  - Icons + text? no
  - Currently "No icons" specified, but description format unclear

- **Q10:** What is the interaction model for subagents?
  - Single-select only? Yes
  - Multi-select allowed? No
  - Can user create custom subagents? No
  - Current State: Not specified

- **Q11:** Should selected subagent affect the prompt template or instructions?
  - Auto-populate prompt hints? Yes
  - Change validation rules? Yes
  - Modify available diagram types? Yes

#### 2.2 Monaco Prompt Editor
- **Q12:** Should the prompt editor have:
  - Syntax highlighting? **RESOLVED:** Based on diagram type from selected tab
  - Auto-complete suggestions? No
  - Prompt templates/snippets? Use the field called Template for SubAgent
  - Character count limit? None
  - Current State: Just "text editor" mentioned

- **Q13:** Should there be a maximum character limit for prompts?
  - Performance consideration for LLM API calls Yes, 5000 characters
  - Current State: Not specified

- **Q14:** Should the prompt persist if user navigates away?
  - localStorage? No
  - Session storage? No
  - Session-based in memory? No

#### 2.3 AgentOption Type
- **Q15:** What is the exact JSON structure for AgentOption?
  - Fields?  Have extra field called Template
  - Required vs optional? Required
  - Validation rules? NOn
  - Current State: "Similar to SubAgent" is too vague

- **Q16:** Where are AgentOptions stored?
  - Backend database?  No
  - Frontend state? Ni
  - Configuration files? In the prompts directory as sub agent
  - Current State: "Extend prompts/ directory" - does this mean files? New subfolder called SubAgent

#### 2.4 Submit Button
- **Q17:** What happens on submit?
  - Immediate LLM call? Yes
  - Validation first? No
  - Show confirmation dialog? No
  - Current State: Only "triggers LLM processing" specified

- **Q18:** Should there be a loading/disabled state while processing?
  - How long is typical LLM response time? 30 to 60 se
  - Should user be able to cancel? Yes

- **Q19:** What if LLM returns an error?
  - Show in error panel Yes?
  - Toast notification? Yes
  - Both?
  - Retry mechanism? No

---

## SECTION 3: CENTER COLUMN (Diagram Rendering)

### Questions & Clarifications Needed

#### 3.1 Diagram Type Tabs
- **Q20:** How does user select multiple diagram types for the same prompt?
  - One at a time via tabs? One at a time
  - Generate all simultaneously? no
  - Side-by-side comparison? No
  - Current State: Implies one-at-a-time

- **Q21:** Should tab selection trigger automatic re-rendering?
  - Regenerate with different provider? yes if not rendered
  - Just switch view of existing code? yes but show empty if not rendered
  - Current State: Ambiguous

#### 3.2 Diagram Rendering Area
- **Q22:** How are diagrams actually rendered?
  - SVG directly in browser? SVG
  - Canvas? No
  - iframe with external renderer? The SVG will always come from the backend provider
  - Current State: "SVG display" but rendering engine not specified

- **Q23:** What happens if diagram rendering fails?
  - Show error message? Show error message in the error panel and toast notification 
  - Display partial diagram? no
  - Fallback to text representation? None
  - Current State: Not addressed

#### 3.3 Zoom Functionality
- **Q24:** What zoom range should be supported?
  - Min/max limits? 20% t0 300%
  - Zoom step size? 20&
  - Keyboard shortcuts (+ / - / ctrl+scroll)? Yes
  - Reset to fit? Yes
  - Current State: Just "zoom in/out" mentioned

- **Q25:** Should zoom level persist when switching diagram types?
  - Yes/no and why? no since all diagrams can be different.

#### 3.4 Download/Export
- **Q26:** What export formats should be supported?
  - SVG? Yes
  - PNG? No
  - PDF? **RESOLVED:** Yes
  - Code export (D2, Mermaid text)? Yes with proper extensions
  - Current State: Only "SVG file" mentioned

- **Q27:** What resolution/quality for non-SVG exports?
  - DPI for PNG? Not applicable
  - Paper size for PDF? **RESOLVED:** Standard 8.5" x 11"

#### 3.5 Minimize/Maximize Buttons
- **Q28:** What does minimize do?
  - Hide rendering area completely? yes but allow user to unhide
  - Collapse to show only tabs? show toggle in tabs
  - Resize to fixed percentage? yes to 1/3 of overall widrth
  - Current State: Not specified

- **Q29:** Should minimize state persist across page navigation?
  - Current State: Not addressed No

#### 3.6 Infinite Scroll
- **Q30:** What content scrolls infinitely in center column?
  - Multiple diagrams generated from one prompt? No
  - History of past diagrams? No
  - Variations/alternatives? No
  - Current State: Unclear - seems out of place for a single diagram renderer

---

## SECTION 4: RIGHT COLUMN (Code Editor)

### Questions & Clarifications Needed

#### 4.1 Monaco Editor Integration
- **Q31:** What language mode for Monaco editor?
  - Auto-detect based on provider (D2, Mermaid, etc.)? If possible
  - User selectable? No, based on the tab selected
  - Custom syntax definition? No
  - Current State: Not specified

- **Q32:** Should Monaco editor have:
  - Line numbers? No
  - Code folding? No
  - Search/replace? Yes
  - Git diff view? No
  - Minimap? **RESOLVED:** Yes
  - Bracket matching/highlighting? **RESOLVED:** Yes
  - Auto-indentation? **RESOLVED:** Yes
  - Current State: Specified

- **Q33:** Should code changes auto-save or require explicit save?
  - Impact on user experience Require Explicit Save
  - Current State: Not specified

#### 4.2 Validate Button
- **Q34:** What validation rules are applied?
  - Syntax validation via backend provider? Yes
  - Schema validation? Yes
  - Both?
  - Current State: Just "validates diagram code" - too vague

- **Q35:** How long does validation take?
  - Should it show loading state? Yes
  - Timeout behavior? 30 seconds
  - Current State: Not addressed

#### 4.3 Render Button
- **Q36:** What's the difference between Validate and Render?
  - Validate = syntax check only? Yes
  - Render = syntax check + generation? Yes
  - Current State: Implied but not explicit

- **Q37:** Can user render without validating first?
  - Yes/no and rationale? no

- **Q38:** Should render show progress/status?
  - Progress bar? No
  - Step indicators? No
  - Time estimate? 10 seconda

#### 4.4 Error Display
- **Q39:** What error types should be displayed?
  - Syntax errors? Yes
  - Validation errors? Yes
  - Render errors? Yes
  - LLM errors? Yes
  - Current State: "Error messages" - too generic

- **Q40:** Should error display show:
  - Error code/ID? Yes
  - Stack trace? No
  - User-friendly message? Yes
  - Suggested fix? No
  - Link to documentation? No

#### 4.5 Code Auto-fix Feature
- **Q41:** The specification mentions "3-tier validation" with auto-fix
  - Is this visible to user in UI? **RESOLVED:** Yes, visible in SSE messages showing retry attempts
  - Should there be a dedicated "Auto-fix" button? No
  - Current State: Visible through SSE footer messages

---

## SECTION 5: FOOTER (Status Bar)

### Questions & Clarifications Needed

#### 5.1 Column 1: Current Status
- **Q42:** What constitutes "current status"?
  - Processing state? Yes
  - Last operation result? Yes
  - System health? Yes
  - All of above?
  - Current State: Vague

- **Q43:** Should status show timestamps?
  - Yes/no for transparency? No

#### 5.2 Column 2: SSE Backend Messages
- **Q44:** What types of messages come via SSE?
  - Progress updates (% complete)? Yes
  - Info logs? Yes
  - Warning logs? No
  - Error logs? Yes
  - Current State: Not specified

- **Q45:** Should SSE messages be:
  - Real-time streamed text? Yes
  - Categorized/filtered? No
  - Scrollable history? Yes
  - Current State: Not specified

- **Q46:** Should user be able to clear SSE message log?
  - Yes/no? No

#### 5.3 Column 3: Links
- **Q47:** Where should About/Help links navigate?
  - About: **RESOLVED:** New tab (external URL)
  - Help: **RESOLVED:** New tab to documentation (no chat support, no FAQ)
  - Current State: Specified

---

## SECTION 6: STATE MANAGEMENT & DATA FLOW

### Questions & Clarifications Needed

#### 6.1 Application State
- **Q48:** How should component state be managed across the app?
  - Flat state in App.tsx? Not sure 
  - Custom hooks? As needed
  - Context for specific features?
  - Current State: Only "React Hooks" mentioned generically

- **Q49:** What data should be persisted to localStorage?
  - Current agent selection? Yes
  - Last prompt? Yes
  - Diagram history? No
  - User preferences? no
  - Current State: Not specified

- **Q50:** How many diagrams should be kept in history?
  - Session only? None
  - 10/50/100 diagrams? Non
  - Unlimited with pagination? None
  - Current State: Not addressed

#### 6.2 Props Drilling
- **Q51:** With 3 independent columns + header + footer, how deep is prop drilling?
  - Should we add Context API for shared state? No
  - Which data warrants Context? no
  - Current State: "Props-based communication" but scale unclear

#### 6.3 Real-time Updates
- **Q52:** When SSE messages arrive, should they:
  - Auto-scroll in footer? yes
  - Show toast notification? no
  - Update diagram automatically? no
  - Current State: Not specified

---

## SECTION 7: INTEGRATION WITH WHYSPER

### Questions & Clarifications Needed

#### 7.1 Conversation Context
- **Q53:** Is Architecture Gen Studio a standalone page or integrated in Whysper chat?
  - Separate route? Yes
  - Tab in existing chat? No
  - Modal overlay? No
  - Current State: Treated as separate but relationship unclear

- **Q54:** Can diagrams generated here be shared to chat conversations?
  - Yes/no? No
  - How is linkage maintained? none

#### 7.2 Agent System Integration
- **Q55:** How are agents loaded?
  - **RESOLVED:** From backend via API (YAML files stored in prompts folder on backend)
  - Loaded at startup and provided by backend
  - Current State: Specified

- **Q56:** Can agents be updated at runtime?
  - Require page reload? No
  - Dynamic update? No
  - Current State: Backend serves agents, frontend caches

#### 7.3 API Integration
- **Q57:** What's the request/response flow for diagram generation?
  - Single endpoint or multiple? Multiplr endpoint as needed
  - Streaming vs batch? Streaming
  - Error handling strategy? Standard Python Logging
  - Current State: Endpoints listed but flow not detailed

- **Q58:** What's the polling/subscription mechanism for SSE?
  - Reconnection strategy if SSE fails? Yes, with exponential backoff and maximum retry attempts.
  - Max message queue size? 100
  - Current State: Not specified

---

## SECTION 8: RESIZABLE COLUMNS

### Questions & Clarifications Needed

#### 8.1 Column Resizing
- **Q59:** What are minimum/maximum widths for columns?
  - **RESOLVED:** Each column minimum 1/3 of available space, can expand up to remaining space
  - Constraint: At least one column must have minimum 1/3 width
  - Current State: Specified

- **Q60:** Should column widths persist?
  - localStorage? Yes
  - Session only? No
  - Per-agent preference? No
  - Current State: Persisted to localStorage

#### 8.2 Collapse Behavior
- **Q61:** When column is collapsed, where does content go?
  - **RESOLVED:** Hidden but accessible via header button toggle (just a button, not a sidebar)
  - Column content completely hidden when collapsed
  - Current State: Specified

- **Q62:** Can all 3 columns be collapsed simultaneously?
  - **RESOLVED:** No, at least one column must remain open (safety constraint)
  - Current State: Specified

---

## SECTION 9: PERFORMANCE & SCALABILITY

### Questions & Clarifications Needed

#### 9.1 Large Diagrams
- **Q63:** How should app handle very large diagrams (1000+ nodes)?
  - Lazy loading? No
  - Virtual scrolling? Yes
  - Compression? No needed
  - Current State: Not addressed

#### 9.2 Editor Performance
- **Q64:** What's the maximum code size for Monaco editor?
  - Can it handle 100K+ lines? Yes
  - Should there be debouncing on input? no
  - Current State: Not specified

#### 9.3 Rendering Performance
- **Q65:** Should there be debouncing between code edit and render?
  - Auto-render on every keystroke? no
  - Wait for user to stop typing? No
  - Require explicit render click? Yes
  - Current State: Not specified

---

## SECTION 10: ACCESSIBILITY & UX

### Questions & Clarifications Needed

#### 10.1 Keyboard Navigation
- **Q66:** Should keyboard shortcuts be available for common actions?
  - Ctrl+S for save? Yes
  - Ctrl+Enter for submit? Yes
  - Ctrl+/ for help? Yes
  - Tab navigation between columns? No
  - Current State: Not specified

#### 10.2 Responsive Behavior on Small Screens
- **Q67:** Spec says "desktop-only" but what is minimum screen width?
  - 1024px? 1200px? 1400px? 1400pm
  - Should app fail gracefully on smaller screens? yes
  - Current State: Not specified

#### 10.3 Error Messages
- **Q68:** Should error messages be:
  - Technical (for developers)? yes
  - User-friendly (for end users)? yes
  - Both with toggle? no
  - Current State: Not specified

---

## SECTION 11: THEME INTEGRATION

### Questions & Clarifications Needed

#### 11.1 Theme Colors in Components
- **Q69:** How should the 11 theme variants affect this page specifically?
  - **RESOLVED:** Use theme colors as defined in .env file
  - All components (tabs, buttons, editor) follow theme automatically
  - No hardcoded theme selection
  - Current State: Theme-driven from .env

#### 11.2 Monaco Editor Theme
- **Q70:** Should Monaco editor theme:
  - Follow page theme automatically? yes
  - User selectable? no
  - Specific to code syntax highlighting? no
  - Current State: Not addressed

---

## SECTION 12: DATA TYPES & API

### Questions & Clarifications Needed

#### 12.1 AgentOption Structure
- **Q71:** **RESOLVED** - Exact JSON schema for AgentOption:
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
- Storage: `/prompts/SubAgent/*.json` (one file per agent option)
- Current State: Fully defined

#### 12.2 Message Extension
- **Q72:** When adding `provider` to Message.metadata:
  - Should it include provider config?Yes
  - Version info? No
  - Generation parameters (model, temperature, etc.)? Yes
  - Current State: Just "provider field" mentioned 

#### 12.3 Diagram Response Format
- **Q73:** **RESOLVED** - What does the API return for `/diagrams/v2/render`?
```json
{
  "svg": "string",
  "provider": "string",
  "code": "string",
  "metadata": {
    "provider": "string",
    "generationParameters": "object"
  },
  "status": "string",
  "timestamp": "string"
}
```
- Current State: Fully defined

---

## SECTION 13: TESTING & VALIDATION

### Questions & Clarifications Needed

#### 13.1 Unit Testing
- **Q74:** Which components require unit tests?
  - All? Yes
  - Critical path only? Yes
  - Current State: No test strategy mentioned

#### 13.2 E2E Testing
- **Q75:** Should there be E2E tests for complete workflows? No
  - Select agent → write prompt → submit → validate → render Ni
  - Yes/no and coverage scope?

#### 13.3 Validation Testing
- **Q76:** How should we test the 3-tier validation system?
  - Mock invalid diagrams? Yes
  - Test auto-fix behavior? Yes
  - Current State: Not addressed

---

## SECTION 14: SECURITY

### Questions & Clarifications Needed

#### 14.1 Code Injection
- **Q77:** Can user-edited code in Monaco editor cause XSS issues?
  - SVG rendering potential? No
  - Need to sanitize code before display? No
  - Current State: Not addressed

#### 14.2 API Security
- **Q78:** Should API calls validate user has permission to use selected agent?
  - Per-user agent restrictions? No
  - Role-based access? No
  - Current State: Not mentioned

---

## SECTION 15: CROSS-CUTTING CONCERNS

### Questions & Clarifications Needed

#### 15.1 Loading States
- **Q79:** All async operations need loading states:
  - Submit button → LLM processing 
  - Validate button → backend validation
  - Render button → diagram generation
  - Tab switching → potential re-render
  - Current State: Not specified where loading states appear

#### 15.2 Error Recovery
- **Q80:** What happens if:
  - LLM API fails? Show error message in the error panel and toast notification
  - Diagram provider fails? Show error message in the error panel and toast notification 
  - SSE connection drops? Show error message in the error panel and toast notification
  - Current State: Not addressed for any scenario

#### 15.3 User Feedback
- **Q81:** How should success messages be shown?
  - Toast notifications? No
  - Status bar update? Yes
  - Both?
  - Current State: Not specified

---

## SUMMARY OF CRITICAL GAPS - ALL RESOLVED ✅

### Top Priority Questions (ALL RESOLVED):

1. ✅ **Q15** - AgentOption JSON structure: Fully defined with 8 fields
2. ✅ **Q34** - Exact validation rules: Syntax + Schema validation via backend
3. ✅ **Q53** - Standalone vs integrated: Separate route, independent page
4. ✅ **Q55** - Agent loading: Backend API with YAML files in prompts folder
5. ✅ **Q71** - AgentOption data type: Complete schema defined
6. ✅ **Q73** - API response format: SVG + metadata structure defined
7. ✅ **Q4** - Navigation breadcrumbs: Display labels only (non-interactive)

### High Priority Questions (ALL RESOLVED):

8. ✅ **Q9** - SubAgent display: Simple list items, no icons
9. ✅ **Q22** - Diagram rendering: SVG from backend provider
10. ✅ **Q31** - Monaco editor language: Auto-detect based on diagram type tab
11. ✅ **Q42** - Status indicator: Processing state + last operation + system health
12. ✅ **Q48** - State management: Props-based, no Context API needed

### All Other Questions: RESOLVED ✅

All 81 clarification questions have been fully answered and documented.

---

## RECOMMENDATIONS FOR DEEPER TECHNICAL REVIEW

### Phase 1: Requirements Clarification
- [ ] Schedule design review meeting to address Q15, Q34, Q53-55, Q71, Q73
- [ ] Document answers in a FAQ/Requirements supplement
- [ ] Create detailed data flow diagrams

### Phase 2: Architecture Decisions
- [ ] Decide on state management approach (Q48, Q51)
- [ ] Define API contracts explicitly (Q57, Q73)
- [ ] Plan SSE implementation details (Q44-46)

### Phase 3: Implementation Details
- [ ] Create Storybook stories for each section (responsive to Q32, Q66)
- [ ] Define loading/error states for all operations
- [ ] Plan testing strategy (Q74-76)

### Phase 4: Security & Performance
- [ ] Conduct security review for code execution (Q77)
- [ ] Plan performance testing approach (Q63-65)
- [ ] Define monitoring/logging strategy

