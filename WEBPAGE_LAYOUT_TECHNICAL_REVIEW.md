# Architecture Gen Studio - Technical Review & Clarifications

## Overview
This document identifies technical questions, ambiguities, and areas requiring deeper clarification for the **WEBPAGE_LAYOUT_SPECIFICATION.md**.

---

## SECTION 1: HEADER SECTION

### Questions & Clarifications Needed

#### 1.1 Agent Selector Dropdown
- **Q1:** Should the agent selector be a **searchable Select** component or a simple dropdown?
  - Impact: UX complexity if there are 50+ agents
  - Current State: Not specified

- **Q2:** When user selects a new agent, should the prompt be **cleared** or **preserved**?
  - Impact: User experience and data loss prevention
  - Suggestion: Define behavior explicitly

- **Q3:** What happens to unsaved prompts when switching agents?
  - Clear them?
  - Save as draft?
  - Show confirmation dialog?

#### 1.2 Navigation Menu Structure
- **Q4:** The navigation shows "Home >> Current Home" - is this breadcrumb-style or literal menu items?
  - Current: Ambiguous
  - Clarification needed: Is this a true breadcrumb navigation or just menu labels?

- **Q5:** Should "Architecture Gen Studio > New Page" open in:
  - Same tab?
  - New tab?
  - Modal dialog?
  - Sidebar view?

#### 1.3 User Account Menu
- **Q6:** What functionality should the user account dropdown include?
  - Profile view/edit?
  - API key management?
  - Theme selection (if added back)?
  - Subscription info?
  - Current State: Only "logout" mentioned

#### 1.4 Notification Badges
- **Q7:** What types of notifications should trigger the badge?
  - Diagram generation complete?
  - Errors occurred?
  - SSE messages?
  - System alerts?

- **Q8:** Should notifications be:
  - Simple badge count?
  - Dropdown panel?
  - Toast notifications?
  - All of the above?

---

## SECTION 2: LEFT COLUMN (Prompt Control Panel)

### Questions & Clarifications Needed

#### 2.1 SubAgent List Display
- **Q9:** How should subagents be displayed?
  - Simple list items?
  - Cards with descriptions?
  - Icons + text?
  - Currently "No icons" specified, but description format unclear

- **Q10:** What is the interaction model for subagents?
  - Single-select only?
  - Multi-select allowed?
  - Can user create custom subagents?
  - Current State: Not specified

- **Q11:** Should selected subagent affect the prompt template or instructions?
  - Auto-populate prompt hints?
  - Change validation rules?
  - Modify available diagram types?

#### 2.2 Monaco Prompt Editor
- **Q12:** Should the prompt editor have:
  - Syntax highlighting?
  - Auto-complete suggestions?
  - Prompt templates/snippets?
  - Character count limit?
  - Current State: Just "text editor" mentioned

- **Q13:** Should there be a maximum character limit for prompts?
  - Performance consideration for LLM API calls
  - Current State: Not specified

- **Q14:** Should the prompt persist if user navigates away?
  - localStorage?
  - Session storage?
  - Session-based in memory?

#### 2.3 AgentOption Type
- **Q15:** What is the exact JSON structure for AgentOption?
  - Fields?
  - Required vs optional?
  - Validation rules?
  - Current State: "Similar to SubAgent" is too vague

- **Q16:** Where are AgentOptions stored?
  - Backend database?
  - Frontend state?
  - Configuration files?
  - Current State: "Extend prompts/ directory" - does this mean files?

#### 2.4 Submit Button
- **Q17:** What happens on submit?
  - Immediate LLM call?
  - Validation first?
  - Show confirmation dialog?
  - Current State: Only "triggers LLM processing" specified

- **Q18:** Should there be a loading/disabled state while processing?
  - How long is typical LLM response time?
  - Should user be able to cancel?

- **Q19:** What if LLM returns an error?
  - Show in error panel?
  - Toast notification?
  - Both?
  - Retry mechanism?

---

## SECTION 3: CENTER COLUMN (Diagram Rendering)

### Questions & Clarifications Needed

#### 3.1 Diagram Type Tabs
- **Q20:** How does user select multiple diagram types for the same prompt?
  - One at a time via tabs?
  - Generate all simultaneously?
  - Side-by-side comparison?
  - Current State: Implies one-at-a-time

- **Q21:** Should tab selection trigger automatic re-rendering?
  - Regenerate with different provider?
  - Just switch view of existing code?
  - Current State: Ambiguous

#### 3.2 Diagram Rendering Area
- **Q22:** How are diagrams actually rendered?
  - SVG directly in browser?
  - Canvas?
  - iframe with external renderer?
  - Current State: "SVG display" but rendering engine not specified

- **Q23:** What happens if diagram rendering fails?
  - Show error message?
  - Display partial diagram?
  - Fallback to text representation?
  - Current State: Not addressed

#### 3.3 Zoom Functionality
- **Q24:** What zoom range should be supported?
  - Min/max limits?
  - Zoom step size?
  - Keyboard shortcuts (+ / - / ctrl+scroll)?
  - Reset to fit?
  - Current State: Just "zoom in/out" mentioned

- **Q25:** Should zoom level persist when switching diagram types?
  - Yes/no and why?

#### 3.4 Download/Export
- **Q26:** What export formats should be supported?
  - Just SVG?
  - PNG, PDF?
  - Code export (D2, Mermaid text)?
  - Current State: Only "SVG file" mentioned

- **Q27:** What resolution/quality for non-SVG exports?
  - DPI for PNG?
  - Paper size for PDF?

#### 3.5 Minimize/Maximize Buttons
- **Q28:** What does minimize do?
  - Hide rendering area completely?
  - Collapse to show only tabs?
  - Resize to fixed percentage?
  - Current State: Not specified

- **Q29:** Should minimize state persist across page navigation?
  - Current State: Not addressed

#### 3.6 Infinite Scroll
- **Q30:** What content scrolls infinitely in center column?
  - Multiple diagrams generated from one prompt?
  - History of past diagrams?
  - Variations/alternatives?
  - Current State: Unclear - seems out of place for a single diagram renderer

---

## SECTION 4: RIGHT COLUMN (Code Editor)

### Questions & Clarifications Needed

#### 4.1 Monaco Editor Integration
- **Q31:** What language mode for Monaco editor?
  - Auto-detect based on provider (D2, Mermaid, etc.)?
  - User selectable?
  - Custom syntax definition?
  - Current State: Not specified

- **Q32:** Should Monaco editor have:
  - Line numbers?
  - Code folding?
  - Search/replace?
  - Git diff view?
  - Current State: Not specified

- **Q33:** Should code changes auto-save or require explicit save?
  - Impact on user experience
  - Current State: Not specified

#### 4.2 Validate Button
- **Q34:** What validation rules are applied?
  - Syntax validation via backend provider?
  - Schema validation?
  - Both?
  - Current State: Just "validates diagram code" - too vague

- **Q35:** How long does validation take?
  - Should it show loading state?
  - Timeout behavior?
  - Current State: Not addressed

#### 4.3 Render Button
- **Q36:** What's the difference between Validate and Render?
  - Validate = syntax check only?
  - Render = syntax check + generation?
  - Current State: Implied but not explicit

- **Q37:** Can user render without validating first?
  - Yes/no and rationale?

- **Q38:** Should render show progress/status?
  - Progress bar?
  - Step indicators?
  - Time estimate?

#### 4.4 Error Display
- **Q39:** What error types should be displayed?
  - Syntax errors?
  - Validation errors?
  - Render errors?
  - LLM errors?
  - Current State: "Error messages" - too generic

- **Q40:** Should error display show:
  - Error code/ID?
  - Stack trace?
  - User-friendly message?
  - Suggested fix?
  - Link to documentation?

#### 4.5 Code Auto-fix Feature
- **Q41:** The specification mentions "3-tier validation" with auto-fix
  - Is this visible to user in UI?
  - Should there be a dedicated "Auto-fix" button?
  - Current State: Mentioned in backend but not in UI spec

---

## SECTION 5: FOOTER (Status Bar)

### Questions & Clarifications Needed

#### 5.1 Column 1: Current Status
- **Q42:** What constitutes "current status"?
  - Processing state?
  - Last operation result?
  - System health?
  - All of above?
  - Current State: Vague

- **Q43:** Should status show timestamps?
  - Yes/no for transparency?

#### 5.2 Column 2: SSE Backend Messages
- **Q44:** What types of messages come via SSE?
  - Progress updates (% complete)?
  - Info logs?
  - Warning logs?
  - Error logs?
  - Current State: Not specified

- **Q45:** Should SSE messages be:
  - Real-time streamed text?
  - Categorized/filtered?
  - Scrollable history?
  - Current State: Not specified

- **Q46:** Should user be able to clear SSE message log?
  - Yes/no?

#### 5.3 Column 3: Links
- **Q47:** Where should About/Help links navigate?
  - About: Modal dialog? New page? External URL?
  - Help: Documentation? Chat support? FAQ?
  - Current State: Not specified

---

## SECTION 6: STATE MANAGEMENT & DATA FLOW

### Questions & Clarifications Needed

#### 6.1 Application State
- **Q48:** How should component state be managed across the app?
  - Flat state in App.tsx?
  - Custom hooks?
  - Context for specific features?
  - Current State: Only "React Hooks" mentioned generically

- **Q49:** What data should be persisted to localStorage?
  - Current agent selection?
  - Last prompt?
  - Diagram history?
  - User preferences?
  - Current State: Not specified

- **Q50:** How many diagrams should be kept in history?
  - Session only?
  - 10/50/100 diagrams?
  - Unlimited with pagination?
  - Current State: Not addressed

#### 6.2 Props Drilling
- **Q51:** With 3 independent columns + header + footer, how deep is prop drilling?
  - Should we add Context API for shared state?
  - Which data warrants Context?
  - Current State: "Props-based communication" but scale unclear

#### 6.3 Real-time Updates
- **Q52:** When SSE messages arrive, should they:
  - Auto-scroll in footer?
  - Show toast notification?
  - Update diagram automatically?
  - Current State: Not specified

---

## SECTION 7: INTEGRATION WITH WHYSPER

### Questions & Clarifications Needed

#### 7.1 Conversation Context
- **Q53:** Is Architecture Gen Studio a standalone page or integrated in Whysper chat?
  - Separate route?
  - Tab in existing chat?
  - Modal overlay?
  - Current State: Treated as separate but relationship unclear

- **Q54:** Can diagrams generated here be shared to chat conversations?
  - Yes/no?
  - How is linkage maintained?

#### 7.2 Agent System Integration
- **Q55:** How are agents loaded?
  - From YAML files at startup?
  - From API endpoint?
  - Cached with refresh mechanism?
  - Current State: Not specified

- **Q56:** Can agents be updated at runtime?
  - Require page reload?
  - Dynamic update?
  - Current State: Not addressed

#### 7.3 API Integration
- **Q57:** What's the request/response flow for diagram generation?
  - Single endpoint or multiple?
  - Streaming vs batch?
  - Error handling strategy?
  - Current State: Endpoints listed but flow not detailed

- **Q58:** What's the polling/subscription mechanism for SSE?
  - Reconnection strategy if SSE fails?
  - Max message queue size?
  - Current State: Not specified

---

## SECTION 8: RESIZABLE COLUMNS

### Questions & Clarifications Needed

#### 8.1 Column Resizing
- **Q59:** What are minimum/maximum widths for columns?
  - Absolute pixels?
  - Percentages?
  - Should there be smart defaults?
  - Current State: Not specified

- **Q60:** Should column widths persist?
  - localStorage?
  - Session only?
  - Per-agent preference?
  - Current State: Not addressed

#### 8.2 Collapse Behavior
- **Q61:** When column is collapsed, where does content go?
  - Completely hidden?
  - Hidden but accessible via toggle?
  - Moved to sidebar?
  - Current State: "Collapsible" but implementation unclear

- **Q62:** Can all 3 columns be collapsed simultaneously?
  - No? Yes? Restrict at least 1 must be open?
  - Current State: Not specified

---

## SECTION 9: PERFORMANCE & SCALABILITY

### Questions & Clarifications Needed

#### 9.1 Large Diagrams
- **Q63:** How should app handle very large diagrams (1000+ nodes)?
  - Lazy loading?
  - Virtual scrolling?
  - Compression?
  - Current State: Not addressed

#### 9.2 Editor Performance
- **Q64:** What's the maximum code size for Monaco editor?
  - Can it handle 100K+ lines?
  - Should there be debouncing on input?
  - Current State: Not specified

#### 9.3 Rendering Performance
- **Q65:** Should there be debouncing between code edit and render?
  - Auto-render on every keystroke?
  - Wait for user to stop typing?
  - Require explicit render click?
  - Current State: Not specified

---

## SECTION 10: ACCESSIBILITY & UX

### Questions & Clarifications Needed

#### 10.1 Keyboard Navigation
- **Q66:** Should keyboard shortcuts be available for common actions?
  - Ctrl+S for save?
  - Ctrl+Enter for submit?
  - Ctrl+/ for help?
  - Tab navigation between columns?
  - Current State: Not specified

#### 10.2 Responsive Behavior on Small Screens
- **Q67:** Spec says "desktop-only" but what is minimum screen width?
  - 1024px? 1200px? 1400px?
  - Should app fail gracefully on smaller screens?
  - Current State: Not specified

#### 10.3 Error Messages
- **Q68:** Should error messages be:
  - Technical (for developers)?
  - User-friendly (for end users)?
  - Both with toggle?
  - Current State: Not specified

---

## SECTION 11: THEME INTEGRATION

### Questions & Clarifications Needed

#### 11.1 Theme Colors in Components
- **Q69:** How should the 11 theme variants affect this page specifically?
  - Tab colors?
  - Button colors?
  - Editor theme (dark/light)?
  - Monaco editor theme auto-switch?
  - Current State: Not specified

#### 11.2 Monaco Editor Theme
- **Q70:** Should Monaco editor theme:
  - Follow page theme automatically?
  - User selectable?
  - Specific to code syntax highlighting?
  - Current State: Not addressed

---

## SECTION 12: DATA TYPES & API

### Questions & Clarifications Needed

#### 12.1 AgentOption Structure
- **Q71:** Exact JSON schema for AgentOption:
```json
{
  id: string,
  agentId: string,
  name: string,
  description: string,
  inputTemplate?: string,
  validationRules?: string[],
  outputFormat?: string,
  // Other fields?
}
```
- Current State: Not defined

#### 12.2 Message Extension
- **Q72:** When adding `provider` to Message.metadata:
  - Should it include provider config?
  - Version info?
  - Generation parameters (model, temperature, etc.)?
  - Current State: Just "provider field" mentioned

#### 12.3 Diagram Response Format
- **Q73:** What does the API return for `/diagrams/v2/render`?
```json
{
  svg: string,
  provider: string,
  code: string,
  metadata: { ... },
  // Other fields?
}
```
- Current State: Not specified

---

## SECTION 13: TESTING & VALIDATION

### Questions & Clarifications Needed

#### 13.1 Unit Testing
- **Q74:** Which components require unit tests?
  - All?
  - Critical path only?
  - Current State: No test strategy mentioned

#### 13.2 E2E Testing
- **Q75:** Should there be E2E tests for complete workflows?
  - Select agent → write prompt → submit → validate → render
  - Yes/no and coverage scope?

#### 13.3 Validation Testing
- **Q76:** How should we test the 3-tier validation system?
  - Mock invalid diagrams?
  - Test auto-fix behavior?
  - Current State: Not addressed

---

## SECTION 14: SECURITY

### Questions & Clarifications Needed

#### 14.1 Code Injection
- **Q77:** Can user-edited code in Monaco editor cause XSS issues?
  - SVG rendering potential?
  - Need to sanitize code before display?
  - Current State: Not addressed

#### 14.2 API Security
- **Q78:** Should API calls validate user has permission to use selected agent?
  - Per-user agent restrictions?
  - Role-based access?
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
  - LLM API fails?
  - Diagram provider fails?
  - SSE connection drops?
  - Current State: Not addressed for any scenario

#### 15.3 User Feedback
- **Q81:** How should success messages be shown?
  - Toast notifications?
  - Status bar update?
  - Both?
  - Current State: Not specified

---

## SUMMARY OF CRITICAL GAPS

### Top Priority Questions (Must Clarify Before Development):

1. **Q15** - AgentOption JSON structure (blocks backend work)
2. **Q34** - Exact validation rules (blocks validation logic)
3. **Q54** - Is this standalone or integrated with chat? (blocks architecture)
4. **Q55** - How agents are loaded at runtime (blocks agent system)
5. **Q71** - Exact data types for all API responses
6. **Q73** - API response format for diagram render endpoint
7. **Q53** - UI hierarchy and page structure clarity

### High Priority Questions (Should Clarify):

8. **Q9** - SubAgent display format
9. **Q22** - Diagram rendering engine details
10. **Q31** - Monaco editor language detection
11. **Q42** - Status indicator definition
12. **Q48** - State management architecture

### Medium Priority Questions (Nice to Have):

- Q1-Q8: UX refinements
- Q24-Q29: Feature specifics
- Q59-Q62: Resizing behavior details

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

