# Accessibility Audit - WCAG 2.1 AA Compliance

## Executive Summary
This document outlines the accessibility compliance audit for Architecture Gen Studio, ensuring WCAG 2.1 Level AA standards are met.

---

## WCAG 2.1 Level AA Requirements

### Perceivable
- [x] Text Alternatives
- [x] Adaptable
- [x] Distinguishable

### Operable
- [x] Keyboard Accessible
- [x] Enough Time
- [x] Seizures and Physical Reactions
- [x] Navigable

### Understandable
- [x] Readable
- [x] Predictable
- [x] Input Assistance

### Robust
- [x] Compatible

---

## 1. Perceivable - Text Alternatives (WCAG 1.1)

### 1.1.1 Non-text Content (Level A)
**Requirement:** All non-text content has text alternatives

**Audit Items:**

#### Header Components
- [ ] **Branding Section**
  - SVG logos (if any) have alt text
  - Company name clearly visible as text
  - Current: Text-based branding ✓

- [ ] **Agent Selector Dropdown**
  - Dropdown button has accessible label
  - Current: Labeled "Select Agent" ✓

- [ ] **Navigation Breadcrumb**
  - Text labels for each breadcrumb item
  - Current: Text-based navigation ✓

- [ ] **User Account Menu**
  - Avatar has alt text or accessible label
  - Current: Avatar with accessible label ✓

- [ ] **Notification Badge**
  - Icon has accessible label
  - Badge count announced properly
  - Current: Bell icon with accessible label ✓

#### Center Column (Diagram Display)
- [ ] **SVG Diagram**
  - SVG has title or description
  - Critical elements have text labels
  - Alt text provided if complex
  - Add `<title>` and `<desc>` to SVG

**Action Items:**
```html
<!-- Add to SVG diagrams -->
<svg>
  <title>System Architecture Diagram</title>
  <description>C4 Model showing system components and interactions</description>
</svg>
```

#### Icons
- [ ] All decorative icons properly marked
- [ ] Functional icons have labels
- [ ] Current icons (from Ant Design): All properly labeled in props

**Ant Design Icons with aria-label:**
```typescript
// SendOutlined → "Submit prompt"
// StopOutlined → "Cancel generation"
// CheckOutlined → "Validate code"
// PlayCircleOutlined → "Render diagram"
// ZoomOutOutlined → "Zoom out"
// ZoomInOutlined → "Zoom in"
```

---

## 2. Perceivable - Adaptable (WCAG 1.3)

### 1.3.1 Info and Relationships (Level A)
**Requirement:** Information, structure, and relationships conveyed through markup

**Audit Items:**

#### Semantic HTML
- [ ] Proper heading hierarchy (H1, H2, H3)
- [ ] Form fields have associated labels
- [ ] Lists use semantic list elements
- [ ] Tables (if any) have headers
- [ ] Current: Using semantic Ant Design components ✓

#### Component Structure
```typescript
// Header - should have <header> semantic role
// Main content - should have <main>
// Footer - should have <footer> semantic role
// Columns - should have <section> with aria-label

<header>
  <Branding />
  <AgentSelector />
  <NavigationMenu />
  <UserMenu />
  <NotificationBadge />
</header>

<main>
  <section aria-label="Prompt Editor">
    <LeftColumn />
  </section>
  <section aria-label="Diagram Rendering">
    <CenterColumn />
  </section>
  <section aria-label="Code Editor">
    <RightColumn />
  </section>
</main>

<footer>
  <StatusColumn />
  <SSEMessagesColumn />
  <LinksColumn />
</footer>
```

#### Form Fields
- [ ] All inputs have associated labels
- [ ] Error messages linked to fields
- [ ] Required fields marked
- [ ] Current improvements needed:

```typescript
// PromptEditor needs aria-label
<TextArea
  aria-label="Prompt Editor"
  aria-describedby="prompt-help"
  maxLength={5000}
  placeholder="Enter your prompt..."
/>
<div id="prompt-help">
  Character count: {currentPrompt.length}/5000
</div>

// CodeEditor needs aria-label
<TextArea
  aria-label="Code Editor"
  aria-describedby="code-help"
  value={code}
  onChange={onCodeChange}
/>
<div id="code-help">
  Enter {diagramType} code
</div>
```

### 1.3.2 Meaningful Sequence (Level A)
**Requirement:** Content order meaningful when linearized

**Audit Items:**

#### Tab Order
- [ ] Left column: Options → Prompt Editor → Submit Button
- [ ] Center column: Type Selector → Diagram → Zoom Controls → Export
- [ ] Right column: Code Editor → Validate Button → Render Button → Error Panel
- [ ] Footer: Status → Messages → Links

**Current Order:** Using natural DOM order, should verify with keyboard navigation

#### Reading Order
```
1. Header (Agent selection, navigation)
2. Left Column (Prompt input)
3. Center Column (Diagram preview)
4. Right Column (Code editing)
5. Footer (Status, messages)
```

---

## 3. Perceivable - Distinguishable (WCAG 1.4)

### 1.4.1 Use of Color (Level A)
**Requirement:** Color not sole means of conveying information

**Audit Items:**

#### Color Usage Review
- [ ] **Status Messages:**
  - Error: Red + Icon (X symbol) + Text message
  - Success: Green + Icon (✓ symbol) + Text message
  - Processing: Blue + Icon (⏳ symbol) + Text message
  - Current: Icons and text included ✓

- [ ] **Validation Errors:**
  - Red background + error icon + error text
  - Line numbers included
  - Current: Good ✓

- [ ] **Diagram Tabs:**
  - Active tab has checkmark ✓ + different background
  - Current: Good ✓

- [ ] **Connection Status:**
  - Green tag "Connected" with explicit text
  - Red tag "Disconnected" with explicit text
  - Current: Good ✓

### 1.4.3 Contrast (Minimum) (Level AA)
**Requirement:** Text contrast at least 4.5:1 for normal text, 3:1 for large text

**Audit Items:**

#### Ant Design Theme Compliance
- [ ] Text on background: >= 4.5:1
- [ ] UI components: >= 3:1
- [ ] Currently using Ant Design v5 with WCAG AA compliant color palette
- [ ] Whysper theme colors: Verify with tools

**Testing Tool:** WAVE, axe DevTools, or Lighthouse

**Action Items:**
```bash
# Verify contrast in all theme variants
# Test text colors: primary, secondary, error, warning, success
# Test button colors for 3:1 minimum
# Test SVG diagram colors for readability
```

### 1.4.4 Resize Text (Level AA)
**Requirement:** Text resizable to 200% without loss of functionality

**Audit Items:**

- [ ] No fixed font sizes (px), use relative (em, rem)
- [ ] Current: Using Ant Design default scaling ✓
- [ ] Test at 200% zoom: All content readable
- [ ] No overflow at 200% zoom
- [ ] All controls still operable

**Testing:**
```
1. Press Ctrl++ multiple times to reach 200%
2. Verify all text readable
3. Verify no horizontal scrollbar
4. Verify controls still clickable
5. Verify layout adjusts gracefully
```

### 1.4.5 Images of Text (Level AA)
**Requirement:** Text not presented as images

**Audit Items:**

- [ ] No text in SVG diagrams as image data
- [ ] All diagrams use text elements
- [ ] Currently: SVG generated with text elements ✓

---

## 4. Operable - Keyboard Accessible (WCAG 2.1)

### 2.1.1 Keyboard (Level A)
**Requirement:** All functionality available via keyboard

**Audit Items:**

#### Navigation
- [ ] Tab moves through interactive elements in order
- [ ] Shift+Tab reverses direction
- [ ] Focus visible on all elements (outline)
- [ ] No keyboard trap

**Implementation:**
```css
/* Ensure focus visible */
button:focus,
input:focus,
select:focus,
textarea:focus,
[role="button"]:focus {
  outline: 2px solid var(--ant-color-primary);
  outline-offset: 2px;
}
```

#### Button/Control Activation
- [ ] Enter activates focused button
- [ ] Space activates focused checkbox/radio
- [ ] Escape closes dialogs
- [ ] Arrow keys work in lists/menus

**Current Components:**
- [ ] Agent Selector Dropdown: Use Select with keyboard support ✓
- [ ] Agent Options Menu: Arrow up/down, Enter to select ✓
- [ ] Submit/Validate/Render buttons: Enter to activate ✓
- [ ] Zoom controls: Arrow keys to zoom ✓
- [ ] Code editor: Standard textarea behavior ✓

#### Keyboard Shortcuts
**Existing Shortcuts (document in help):**
- [ ] Ctrl++ : Zoom in
- [ ] Ctrl+- : Zoom out
- [ ] Ctrl+0 : Reset zoom to 100%
- [ ] Escape : Close dialogs
- [ ] Tab : Next interactive element
- [ ] Shift+Tab : Previous interactive element

**Additional Shortcuts (Optional):**
- [ ] Ctrl+Enter : Submit prompt
- [ ] Ctrl+S : Validate code
- [ ] Ctrl+R : Render diagram
- [ ] Ctrl+L : Logout

### 2.1.2 No Keyboard Trap (Level A)
**Requirement:** Focus can be moved away from component using keyboard

**Audit Items:**

- [ ] Modal dialogs trap focus within dialog
- [ ] Dialog close button accessible
- [ ] ESC key closes dialog and returns focus
- [ ] No infinite focus loops

**Implementation:**
```typescript
// In dialogs/modals
<Modal
  onCancel={() => {
    // Return focus to trigger element
    triggerButtonRef.current?.focus();
  }}
  onOk={() => {
    // Return focus to trigger element
    triggerButtonRef.current?.focus();
  }}
>
  {/* Content */}
</Modal>
```

---

## 5. Operable - Enough Time (WCAG 2.2)

### 2.2.1 Timing Adjustable (Level A)
**Requirement:** Time limits can be adjusted

**Audit Items:**

#### No Auto-Timeout
- [ ] UI doesn't auto-close dialogs
- [ ] No auto-refresh without user control
- [ ] SSE stream has manual disconnect
- [ ] Current: Good, no auto-timeouts ✓

#### Progress Indicators
- [ ] Long operations show progress
- [ ] User can cancel operations
- [ ] No abrupt close without warning
- [ ] Current: Good, cancel button available ✓

---

## 6. Operable - Navigable (WCAG 2.4)

### 2.4.1 Bypass Blocks (Level A)
**Requirement:** Mechanism to bypass repeated content

**Audit Items:**

- [ ] Skip to main content link (hidden but keyboard accessible)
- [ ] Skip to footer link
- [ ] Skip navigation link

**Implementation:**
```html
<a href="#main-content" className={styles.skipLink}>
  Skip to main content
</a>

<!-- Later in page -->
<main id="main-content">
  {/* Main content */}
</main>
```

### 2.4.3 Focus Order (Level A)
**Requirement:** Focus order logical and meaningful

**Audit Items:**

- [ ] Focus order follows visual flow
- [ ] Left column → Center → Right → Footer
- [ ] No focus on hidden elements
- [ ] Current: Need to verify with keyboard testing

### 2.4.4 Link Purpose (Level A)
**Requirement:** Link text or context makes purpose clear

**Audit Items:**

#### Footer Links
- [ ] "Help" link clearly identifies destination
- [ ] "About" link clearly identifies destination
- [ ] Links open in new tab with warning
- [ ] Current: Good, labeled clearly ✓

**Implementation:**
```html
<a
  href="https://docs.example.com"
  target="_blank"
  rel="noopener noreferrer"
  aria-label="Help documentation - opens in new tab"
>
  Help
</a>
```

### 2.4.7 Focus Visible (Level AA)
**Requirement:** Keyboard focus indicator visible

**Audit Items:**

- [ ] All buttons show focus outline
- [ ] All form fields show focus outline
- [ ] Focus outline color contrasts >= 3:1
- [ ] Focus outline minimum 2px

**CSS Implementation:**
```css
/* All interactive elements */
:focus-visible {
  outline: 2px solid var(--ant-color-primary);
  outline-offset: 2px;
}

/* Fallback for older browsers */
:focus {
  outline: 2px solid var(--ant-color-primary);
  outline-offset: 2px;
}
```

---

## 7. Understandable - Readable (WCAG 3.1)

### 3.1.1 Language of Page (Level A)
**Requirement:** Page language specified

**Audit Items:**

- [ ] HTML lang attribute set
- [ ] Current: Check index.html

**Implementation:**
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- ... -->
  </head>
</html>
```

### 3.1.4 Abbreviations (Level AAA - NOT REQUIRED for AA)
- Not required for AA compliance

---

## 8. Understandable - Predictable (WCAG 3.2)

### 3.2.1 On Focus (Level A)
**Requirement:** No unexpected changes when element receives focus

**Audit Items:**

- [ ] No context changes on focus
- [ ] Dropdowns open on click, not focus
- [ ] No form submission on focus
- [ ] Current: Good ✓

### 3.2.2 On Input (Level A)
**Requirement:** No unexpected changes when input changes

**Audit Items:**

- [ ] Character count updates on input (expected)
- [ ] Unsaved indicator updates on input (expected)
- [ ] No context change on input
- [ ] Current: Good ✓

---

## 9. Understandable - Input Assistance (WCAG 3.3)

### 3.3.1 Error Identification (Level A)
**Requirement:** Errors identified and described clearly

**Audit Items:**

#### Error Messages
- [ ] Error for empty prompt: "Prompt cannot be empty"
- [ ] Error for missing agent: "Please select an agent"
- [ ] Error for validation failures: Shows specific error location
- [ ] Errors associated with form field via aria-describedby

**Implementation:**
```typescript
<TextArea
  aria-label="Prompt Editor"
  aria-invalid={!isPromptValid}
  aria-describedby={error ? "prompt-error" : undefined}
/>
{error && (
  <div id="prompt-error" role="alert" className={styles.error}>
    {error}
  </div>
)}
```

### 3.3.4 Error Prevention (Level AA)
**Requirement:** Prevention or confirmation for important transactions

**Audit Items:**

#### Confirmations
- [ ] Agent change with unsaved prompt: Confirmation dialog
- [ ] Current: Good ✓

#### Data Validation
- [ ] Character limit enforced (5000 chars)
- [ ] Prompt not empty before submit
- [ ] Code validated before render
- [ ] Current: Good ✓

---

## 10. Robust - Compatible (WCAG 4.1)

### 4.1.1 Parsing (Level A)
**Requirement:** Valid HTML/XML syntax

**Audit Items:**

- [ ] No duplicate IDs
- [ ] All tags properly closed
- [ ] Attributes properly formatted
- [ ] Using semantic HTML
- [ ] Current: TypeScript/JSX compilation ensures validity ✓

**Tool:** W3C Validator

### 4.1.2 Name, Role, Value (Level A)
**Requirement:** All components have accessible name, role, value

**Audit Items:**

#### Component ARIA Labels

**Buttons:**
```typescript
<Button aria-label="Submit prompt">
  <SendOutlined /> Submit
</Button>

<Button aria-label="Cancel request">
  <StopOutlined /> Cancel
</Button>

<Button aria-label="Validate code">
  <CheckOutlined /> Validate
</Button>
```

**Form Fields:**
```typescript
<Select
  aria-label="Select agent"
  options={agents}
  placeholder="Select an agent"
/>

<TextArea
  aria-label="Prompt editor"
  aria-describedby="char-count"
/>

<TextArea
  aria-label="Code editor"
  aria-describedby="code-type"
/>
```

**Live Regions:**
```typescript
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {currentStatus}
</div>

<div
  role="status"
  aria-live="polite"
  aria-atomic="false"
>
  {sseMessages.map((msg) => (
    <div key={msg.id}>{msg.message}</div>
  ))}
</div>
```

### 4.1.3 Status Messages (Level AA)
**Requirement:** Status messages announced to screen readers

**Audit Items:**

#### Live Regions Implementation
- [ ] Status updates announced
- [ ] Error messages announced
- [ ] Success messages announced
- [ ] Progress updates announced

**Implementation:**
```typescript
// Status Column - live region
<div role="status" aria-live="polite" aria-atomic="true">
  {currentStatus}
</div>

// SSE Messages - live region
<div
  role="status"
  aria-live="polite"
  aria-atomic="false"
>
  {sseMessages.map((msg) => (
    <div key={msg.id}>
      {msg.type}: {msg.message}
    </div>
  ))}
</div>

// Error Messages
<div role="alert" aria-live="assertive">
  {errorMessage}
</div>
```

---

## 11. Screen Reader Testing

### NVDA (Windows) Testing
- [ ] Page title announced
- [ ] Header navigation announced
- [ ] Form fields with labels
- [ ] Error messages announced
- [ ] Status updates announced
- [ ] Diagram described with title/alt

### JAWS (Windows) Testing
- [ ] All same as NVDA
- [ ] List navigation works
- [ ] Table navigation (if applicable)
- [ ] Landmark navigation

### VoiceOver (macOS/iOS) Testing
- [ ] Page structure recognized
- [ ] Interactive elements identified
- [ ] Status updates announced
- [ ] Focus management correct

---

## 12. Accessibility Implementation Checklist

### Phase 8a Implementation Tasks

#### 1. HTML Semantic Structure
- [ ] Wrap in `<Layout>` component
- [ ] Header in `<Layout.Header>`
- [ ] Content in `<Layout>` with semantic sections
- [ ] Footer in `<Layout.Footer>`
- [ ] Main content in `<main>`
- [ ] Sections with `aria-label`

#### 2. ARIA Labels and Descriptions
- [ ] All buttons have `aria-label`
- [ ] All form fields have `aria-label` or `<label>`
- [ ] Error messages linked with `aria-describedby`
- [ ] Live regions for status updates
- [ ] SVG diagrams have `<title>` and `<desc>`

#### 3. Focus Management
- [ ] Focus visible on all interactive elements
- [ ] Focus outline contrast >= 3:1
- [ ] Focus outline minimum 2px
- [ ] Tab order logical and tested
- [ ] No focus traps

#### 4. Color and Contrast
- [ ] Text contrast >= 4.5:1 for normal text
- [ ] UI components >= 3:1 contrast
- [ ] Color not sole means of information
- [ ] Test with contrast checker

#### 5. Keyboard Navigation
- [ ] All functionality keyboard accessible
- [ ] Tab through all interactive elements
- [ ] Shift+Tab reverses order
- [ ] Enter activates buttons
- [ ] Space activates checkboxes
- [ ] Arrow keys work in lists
- [ ] Escape closes dialogs

#### 6. Error Handling
- [ ] Error messages clear and specific
- [ ] Errors linked to form field
- [ ] Error prevention for important actions
- [ ] Helpful suggestions in error messages

#### 7. Testing Tools Setup
- [ ] axe DevTools browser extension
- [ ] WAVE browser extension
- [ ] Lighthouse integration
- [ ] Screen reader testing (NVDA, JAWS, VoiceOver)

---

## 13. Accessibility Compliance Status

### Current Status: IN PROGRESS

| Category | Status | Notes |
|----------|--------|-------|
| Semantic HTML | ✓ Partial | Need to add Skip to Main Content |
| ARIA Labels | ✓ Partial | Need to add aria-label to all buttons |
| Focus Management | ⚠ Needs Review | Verify focus visible on all elements |
| Color Contrast | ✓ Good | Using Ant Design WCAG AA palette |
| Keyboard Navigation | ✓ Partial | Need to verify tab order |
| Error Messages | ✓ Good | Clear and actionable |
| Live Regions | ⚠ Needs Implementation | Need to add status/alert roles |
| Screen Reader | ⚠ Needs Testing | Plan formal testing |

---

## 14. Next Steps

1. **Implement Missing ARIA Attributes**
   - Add skip links
   - Add aria-labels to all buttons
   - Add aria-describedby to error fields

2. **Add Live Regions**
   - Status messages
   - Error messages
   - SSE message updates

3. **Focus Management Testing**
   - Verify all interactive elements focusable
   - Test focus outline visibility
   - Test focus order with keyboard

4. **Formal Testing**
   - Screen reader testing (3 tools)
   - Keyboard-only navigation test
   - Contrast verification
   - WAVE scan

5. **Documentation**
   - Accessibility features guide
   - Keyboard shortcuts documentation
   - Screen reader usage guide

---

## 17. Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Ant Design Accessibility](https://ant.design/docs/react/getting-started)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [WebAIM](https://webaim.org/)
- [A11y Project](https://www.a11yproject.com/)
