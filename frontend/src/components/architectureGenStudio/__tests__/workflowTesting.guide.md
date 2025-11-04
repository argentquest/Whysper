# Workflow Testing Guide - Architecture Gen Studio

## Complete End-to-End Workflow Tests

---

## Workflow 1: Create Diagram from Scratch

### Steps
1. **Load Application**
   - [ ] Page loads within 3 seconds
   - [ ] Three-column layout visible
   - [ ] Header with agent dropdown visible
   - [ ] Footer with status visible

2. **Fetch Agents**
   - [ ] Click agent dropdown
   - [ ] Agent list loads within 1 second
   - [ ] All agents display with names and descriptions

3. **Select Agent**
   - [ ] Click on an agent
   - [ ] Agent selected in dropdown
   - [ ] Agent options load automatically

4. **View Options**
   - [ ] Agent options display in left column
   - [ ] Each option shows name and description
   - [ ] Options are clickable

5. **Select Option**
   - [ ] Click on agent option
   - [ ] Prompt template auto-populates in editor
   - [ ] Character count shows template length
   - [ ] Option highlighted in list

6. **Edit Prompt**
   - [ ] Click in prompt editor
   - [ ] Edit template text
   - [ ] Character count updates in real-time
   - [ ] Unsaved indicator appears (⚠️)

7. **Submit Prompt**
   - [ ] Click submit button
   - [ ] Status changes to "LLM Execution..."
   - [ ] Submit button disabled, shows "Generating..."
   - [ ] Cancel button appears

8. **Monitor Generation**
   - [ ] SSE connection establishes (green "Connected" tag)
   - [ ] Progress messages appear in footer
   - [ ] Message count increments
   - [ ] Status updates with progress

9. **Receive Diagram**
   - [ ] SVG renders in center column
   - [ ] Diagram displays correctly
   - [ ] Status changes to "Diagram Generated"
   - [ ] Mermaid tab shows ✓ checkmark

10. **View Result**
    - [ ] Diagram visible and centered
    - [ ] Zoom controls active
    - [ ] Export button available
    - [ ] Code displays in right column

### Expected Outcomes
- Diagram successfully generated and displayed
- All UI elements respond correctly
- No errors in console
- localStorage contains agent selection and prompt

---

## Workflow 2: Modify Code and Render

### Steps
1. **Start with Generated Diagram**
   - [ ] Use diagram from Workflow 1
   - [ ] Code visible in right column

2. **Edit Code**
   - [ ] Click in code editor
   - [ ] Modify diagram code
   - [ ] Character count updates
   - [ ] Unsaved indicator appears

3. **Validate Code**
   - [ ] Click validate button
   - [ ] Validation spinner appears
   - [ ] Validation completes within 30 seconds

4. **Check Validation Result**
   - [ ] If valid: Success message shows
   - [ ] If invalid: Error list appears with details
   - [ ] Line numbers shown for errors

5. **Fix Errors (if any)**
   - [ ] Edit code to fix validation errors
   - [ ] Re-validate
   - [ ] Repeat until valid

6. **Render Diagram**
   - [ ] Click render button (only if validation passed)
   - [ ] Render spinner appears
   - [ ] SVG updates in center column
   - [ ] Success message shows

7. **Compare Changes**
   - [ ] New diagram shows changes
   - [ ] Zoom level maintained
   - [ ] Previous diagram still accessible in history

### Expected Outcomes
- Code validation works correctly
- Render only enabled after validation
- Diagram updates reflect code changes
- No data loss during editing

---

## Workflow 3: Switch Between Diagram Types

### Steps
1. **Start with Mermaid Diagram**
   - [ ] Mermaid diagram generated and displayed
   - [ ] Mermaid code visible in editor
   - [ ] Mermaid tab shows ✓

2. **Click D2 Tab**
   - [ ] Center column switches to D2
   - [ ] Right column clears or shows previous D2 code
   - [ ] No diagram visible if D2 not yet generated

3. **Generate D2 Diagram**
   - [ ] Select agent option for D2
   - [ ] Edit prompt for D2 style
   - [ ] Submit and generate D2 diagram
   - [ ] D2 tab shows ✓

4. **Switch to Structurizr**
   - [ ] Click Structurizr tab
   - [ ] Center shows Structurizr (if available)
   - [ ] Code switches to Structurizr format

5. **Manage Multiple Diagrams**
   - [ ] Switch between Mermaid, D2, Structurizr tabs
   - [ ] Each tab preserves its diagram and code
   - [ ] Zoom level per diagram maintained

6. **Export Different Formats**
   - [ ] Generate diagram for each type
   - [ ] Export SVG for each type
   - [ ] Files download with correct names
   - [ ] SVG contents match displayed diagram

### Expected Outcomes
- Multiple diagrams cached and retrievable
- Switching tabs is instant
- No data loss between switches
- Each diagram type independent

---

## Workflow 4: Export and Save Diagrams

### Steps
1. **Generate Diagram** (from Workflow 1)
   - [ ] Diagram displayed and ready

2. **Download as SVG**
   - [ ] Click export button
   - [ ] Select "SVG" option
   - [ ] File downloads successfully
   - [ ] File named with diagram type and timestamp

3. **Download as PDF**
   - [ ] Click export button
   - [ ] Select "PDF" option
   - [ ] PDF generates (may take 5-10 seconds)
   - [ ] PDF downloads successfully
   - [ ] PDF contains SVG rendered properly (8.5" x 11")

4. **Download Code**
   - [ ] Click export button
   - [ ] Select "Code" option
   - [ ] Code file downloads (.mmd, .d2, etc.)
   - [ ] Code is properly formatted

5. **Verify Downloads**
   - [ ] SVG renders in browser
   - [ ] PDF opens in PDF reader
   - [ ] Code file opens in text editor
   - [ ] All downloads have correct content

6. **Share Diagram**
   - [ ] Copy diagram URL
   - [ ] Share URL with team
   - [ ] Open in different browser
   - [ ] Diagram loads correctly

### Expected Outcomes
- All export formats work correctly
- Downloads have correct names and content
- File sizes reasonable
- Files are usable in other tools

---

## Workflow 5: Error Recovery

### Steps
1. **Network Error During Generation**
   - [ ] Submit prompt
   - [ ] Disconnect network (or simulate timeout)
   - [ ] Error message appears
   - [ ] Prompt preserved in editor
   - [ ] Retry button available

2. **Attempt Retry**
   - [ ] Click retry button
   - [ ] Reconnect network
   - [ ] Generation restarts
   - [ ] Completes successfully

3. **Validation Error**
   - [ ] Edit code with syntax error
   - [ ] Click validate
   - [ ] Error shows with location
   - [ ] Dismiss error panel
   - [ ] Code preserved
   - [ ] Can fix and re-validate

4. **Timeout Error**
   - [ ] Submit very complex prompt (if available)
   - [ ] Wait for timeout (30+ seconds)
   - [ ] Timeout message appears
   - [ ] Cancel button works
   - [ ] Can try again

5. **Invalid User Action**
   - [ ] Try to submit empty prompt
   - [ ] Toast shows: "Prompt cannot be empty"
   - [ ] Prompt editor focused
   - [ ] Submit button remains disabled

6. **Unsaved Changes Dialog**
   - [ ] Edit prompt
   - [ ] Select different agent
   - [ ] Confirmation dialog appears
   - [ ] Click "Cancel" to keep editing
   - [ ] Click "Confirm" to discard changes
   - [ ] Either action works correctly

### Expected Outcomes
- All errors handled gracefully
- User input preserved when possible
- Clear error messages guide recovery
- Retry mechanisms work reliably

---

## Workflow 6: Column Operations

### Steps
1. **Collapse Left Column**
   - [ ] Click collapse button on left column header
   - [ ] Left column minimizes to 40px sidebar
   - [ ] Sidebar shows collapse indicator
   - [ ] Other columns expand

2. **Expand Left Column**
   - [ ] Click expand button on sidebar
   - [ ] Left column expands to previous width
   - [ ] Content displays correctly
   - [ ] Width preserved

3. **Resize Columns**
   - [ ] Position cursor on column divider
   - [ ] Cursor changes to resize cursor
   - [ ] Drag divider to resize
   - [ ] Adjacent columns adjust
   - [ ] Minimum width enforced (33.33%)

4. **Collapse All Columns**
   - [ ] Collapse left column
   - [ ] Collapse right column
   - [ ] Center column expands to fill space
   - [ ] Diagram displays at full width

5. **Restore Layout**
   - [ ] Expand left and right columns
   - [ ] Widths snap to previous values
   - [ ] Layout restored exactly

6. **Page Reload**
   - [ ] Collapse/resize columns to custom layout
   - [ ] Refresh page (F5)
   - [ ] Layout restored from localStorage
   - [ ] Width ratios maintained

### Expected Outcomes
- Column operations smooth and responsive
- Layout persists across sessions
- Minimum width enforced
- No content clipping

---

## Workflow 7: Zoom and Navigation

### Steps
1. **Zoom Controls**
   - [ ] Click zoom out button (-)
   - [ ] Diagram zooms to 80%
   - [ ] Zoom percentage updates
   - [ ] Zoom slider moves

2. **Zoom In**
   - [ ] Click zoom in button (+)
   - [ ] Diagram zooms to 120%
   - [ ] Zoom percentage updates

3. **Use Zoom Slider**
   - [ ] Drag zoom slider
   - [ ] Diagram zooms smoothly
   - [ ] Zoom percentage updates in real-time

4. **Keyboard Shortcuts**
   - [ ] Press Ctrl++ to zoom in
   - [ ] Press Ctrl+- to zoom out
   - [ ] Press Ctrl+0 to reset zoom
   - [ ] All shortcuts work

5. **Reset Zoom**
   - [ ] Zoom to 200%
   - [ ] Click reset button (or Ctrl+0)
   - [ ] Zoom resets to 100%

6. **Zoom Limits**
   - [ ] Try to zoom beyond 20% (MIN_ZOOM)
   - [ ] Zoom buttons/slider constrained
   - [ ] Try to zoom beyond 300% (MAX_ZOOM)
   - [ ] Zoom buttons/slider constrained

7. **Zoom Persistence**
   - [ ] Set zoom to 150%
   - [ ] Refresh page
   - [ ] Zoom level persists (from localStorage)
   - [ ] Diagram displays at correct zoom

### Expected Outcomes
- Zoom controls work intuitively
- Keyboard shortcuts responsive
- Zoom limits enforced
- Zoom level persists

---

## Workflow 8: Message Monitoring

### Steps
1. **Submit Diagram Generation**
   - [ ] Submit prompt to generate diagram
   - [ ] SSE connection status: "Connected"
   - [ ] Message counter shows 0

2. **Monitor Progress**
   - [ ] Messages receive from backend
   - [ ] Message counter increments
   - [ ] Message types: progress, success, etc.
   - [ ] Timestamps shown

3. **View All Messages**
   - [ ] Click "Messages" button in footer
   - [ ] Modal opens showing all messages
   - [ ] Messages scrollable if many
   - [ ] Each message shows type, time, content

4. **Message Details**
   - [ ] Messages tagged by type (info, error, progress)
   - [ ] Colors differentiate message types
   - [ ] Error messages highlighted in red
   - [ ] Timestamps in local time

5. **Close Modal**
   - [ ] Click close button
   - [ ] Modal disappears
   - [ ] Messages still available to view again

6. **SSE Disconnection**
   - [ ] Generate long-running diagram
   - [ ] Simulate SSE disconnect
   - [ ] Status changes to "Disconnected" (red tag)
   - [ ] System attempts reconnection
   - [ ] After 5 failed attempts, shows error

### Expected Outcomes
- Message streaming works reliably
- Connection status clearly visible
- All messages captured and viewable
- Reconnection automatic and transparent

---

## Performance Checklist

### Load Times
- [ ] Initial page load: < 3 seconds
- [ ] Agent fetch: < 1 second
- [ ] Options fetch: < 1 second
- [ ] Diagram generation: < 30 seconds
- [ ] Code validation: < 30 seconds
- [ ] Diagram rendering: < 5 seconds

### Responsiveness
- [ ] Column drag: < 100ms latency
- [ ] Zoom interaction: < 50ms latency
- [ ] Code editing: < 50ms per keystroke
- [ ] Tab switching: < 100ms
- [ ] Collapse/expand: < 200ms

### Memory Usage
- [ ] Initial load: < 50 MB
- [ ] After 10 diagrams: < 100 MB
- [ ] After 100 diagrams: < 200 MB (with cleanup)
- [ ] No memory leaks on tab switching

---

## Accessibility Checklist

### Keyboard Navigation
- [ ] Tab through all interactive elements
- [ ] Shift+Tab reverses focus
- [ ] Enter activates buttons
- [ ] Space activates checkboxes/radio buttons
- [ ] Escape closes dialogs
- [ ] Focus visible on all elements

### Screen Reader
- [ ] Page title descriptive
- [ ] Headings hierarchical
- [ ] Images have alt text
- [ ] Form labels associated
- [ ] Error messages announced
- [ ] Live regions for updates

### Color Contrast
- [ ] Text: 4.5:1 contrast ratio
- [ ] UI components: 3:1 contrast ratio
- [ ] No color-only information
- [ ] Links distinguishable from text

### Focus Management
- [ ] Focus on page load
- [ ] Focus on dialog open
- [ ] Focus trap in modal
- [ ] Focus restore on close

---

## Browser Compatibility

### Desktop
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

### Mobile
- [ ] iPad (Safari)
- [ ] Android (Chrome)
- [ ] Responsiveness at 1024px breakpoint
- [ ] Touch interactions functional

---

## Final Sign-Off Checklist

Before deployment:
- [ ] All workflows tested and passing
- [ ] No console errors
- [ ] No TypeScript errors
- [ ] Performance targets met
- [ ] Accessibility standards met
- [ ] Keyboard navigation works
- [ ] Error messages helpful
- [ ] Data persistence working
- [ ] SSE reconnection reliable
- [ ] Export functionality complete
- [ ] All themes working
- [ ] Documentation updated
- [ ] Team signoff obtained
