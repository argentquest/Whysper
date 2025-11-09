# Manual Testing Checklist - Architecture Gen Studio

**Date**: November 3, 2024
**Backend Status**: Running on port 8000
**Frontend Status**: Ready for testing at `/studio` route
**Overall Test Status**: Ready to Execute

---

## Pre-Testing Verification

### ✅ Backend Server Status
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/agents
# Expected: Response with agent list (200 OK) or error handling
```

### ✅ Frontend Build
```bash
# Start frontend development server
cd frontend
npm install
npm start
# Expected: Server starts on http://localhost:3000
# Navigate to http://localhost:3000/studio
```

### ✅ Environment Configuration
```bash
# Check .env file
cat frontend/.env
# Should contain:
# REACT_APP_API_URL=http://localhost:8000/api/v1
# REACT_APP_THEME=light
```

---

## Workflow 1: Agent Selection and Loading ✅

### Test Steps
1. [ ] **Page Load**
   - Open http://localhost:3000/studio
   - Verify page loads within 3 seconds
   - All UI elements visible
   - No console errors

2. [ ] **Agent Dropdown**
   - Click agent dropdown in header
   - Verify agents load from backend
   - At least 3 agents displayed
   - Agent names and descriptions visible

3. [ ] **Agent Selection**
   - Click on first agent
   - Agent selection updates dropdown
   - Agent options appear in left column
   - Options have names and descriptions

4. [ ] **Option Selection**
   - Click on first agent option
   - Prompt template populates in editor
   - Character count updates (should show template length)
   - Option highlighted in list

### Expected Results
- ✅ Agents load successfully
- ✅ Options display correctly
- ✅ Template auto-populates
- ✅ No errors in console

---

## Workflow 2: Diagram Generation ✅

### Test Steps
1. [ ] **Prepare Prompt**
   - Select an agent (if not already selected)
   - Select an agent option
   - Template should populate
   - Verify prompt is not empty

2. [ ] **Submit Prompt**
   - Click "Submit" button
   - Button changes to "Generating..."
   - Cancel button appears
   - Status shows "LLM Execution..."

3. [ ] **Monitor Generation**
   - Watch SSE messages in footer
   - Connection status: "Connected" (green tag)
   - Messages appear with timestamps
   - Message count increments
   - Progress updates visible

4. [ ] **Receive Diagram**
   - SVG renders in center column
   - Diagram displays correctly
   - Status changes to "Diagram Generated"
   - Mermaid tab shows ✓ checkmark (or selected diagram type)

5. [ ] **View Generated Diagram**
   - Diagram visible and centered
   - Zoom controls are active
   - Export button available
   - Code displays in right column

### Expected Results
- ✅ Generation starts without errors
- ✅ SSE updates in real-time
- ✅ Diagram renders correctly
- ✅ Status updates appropriately
- ✅ Code appears in right column

### Performance Targets
- ✅ Generation: < 30 seconds
- ✅ SSE message latency: < 1 second
- ✅ SVG rendering: < 5 seconds

---

## Workflow 3: Code Validation ✅

### Test Steps
1. [ ] **Start with Generated Diagram**
   - Use diagram from Workflow 2
   - Code visible in right column
   - Code corresponds to diagram type

2. [ ] **Edit Code**
   - Click in code editor
   - Modify diagram code slightly
   - Unsaved indicator appears (⚠️)
   - Character count updates

3. [ ] **Validate Code**
   - Click "Validate" button
   - Validation spinner appears
   - Button disabled during validation
   - Completes within 30 seconds

4. [ ] **Check Validation Result**
   - Success message: "Code validation passed"
   - If invalid: Error list appears with details
   - Line numbers shown for errors

5. [ ] **Fix Errors (if any)**
   - Edit code to fix issues
   - Re-validate
   - Repeat until valid

### Expected Results
- ✅ Validation completes successfully
- ✅ Error messages clear and helpful
- ✅ No timeout errors
- ✅ Code can be fixed iteratively

---

## Workflow 4: Diagram Rendering ✅

### Test Steps
1. [ ] **Validate Code First**
   - Code must be validated before rendering
   - If validation not passed: Render button disabled
   - Warning appears if render attempted without validation

2. [ ] **Render Diagram**
   - Click "Render" button
   - Render spinner appears
   - SVG updates in center column
   - Success message shows

3. [ ] **Compare Changes**
   - New diagram reflects code changes
   - Previous diagram still accessible
   - No data loss during editing

4. [ ] **Zoom and Interact**
   - Use zoom controls to adjust view
   - Diagram scales smoothly
   - Pan and interact with diagram

### Expected Results
- ✅ Render-after-validate workflow enforced
- ✅ Diagram updates correctly
- ✅ Rendering < 5 seconds
- ✅ Zoom controls responsive

---

## Workflow 5: Export Functionality ✅

### Test Steps
1. [ ] **Generate/Render Diagram**
   - Ensure diagram is displayed
   - Export button should be visible

2. [ ] **Export SVG**
   - Click Export button (if available)
   - Select SVG option
   - File downloads successfully
   - Filename includes diagram type and timestamp

3. [ ] **Export PDF**
   - Click Export button
   - Select PDF option
   - PDF generates (may take 5-10 seconds)
   - File downloads successfully
   - PDF renders diagram correctly (8.5" x 11")

4. [ ] **Export Code**
   - Click Export button
   - Select Code option
   - Code file downloads (.mmd, .d2, etc.)
   - Code is properly formatted

5. [ ] **Verify Downloads**
   - SVG opens in browser
   - PDF opens in PDF reader
   - Code opens in text editor
   - All downloads have correct content

### Expected Results
- ✅ SVG export works
- ✅ PDF export works (with correct sizing)
- ✅ Code export works
- ✅ Files are properly named and formatted

---

## Workflow 6: Multiple Diagram Types ✅

### Test Steps
1. [ ] **Generate Mermaid Diagram**
   - Select agent that supports Mermaid
   - Generate diagram
   - Mermaid tab shows ✓
   - Code shows Mermaid syntax

2. [ ] **Switch to D2**
   - Click D2 tab
   - If D2 not generated: Empty/previous state
   - Code editor shows D2 placeholder

3. [ ] **Generate D2 Diagram**
   - Select agent option for D2
   - Edit/submit prompt for D2
   - Generate D2 diagram
   - D2 tab shows ✓

4. [ ] **Switch Back to Mermaid**
   - Click Mermaid tab
   - Previous Mermaid diagram loads instantly
   - Code switches back to Mermaid

5. [ ] **Verify Independence**
   - Each diagram type independent
   - Switching preserves diagrams
   - Zoom level per diagram

### Expected Results
- ✅ Multiple diagrams cached
- ✅ Switching is instantaneous
- ✅ No data loss between switches
- ✅ Each type independent

---

## Workflow 7: Column Operations ✅

### Test Steps
1. [ ] **Collapse Left Column**
   - Click collapse button on left column header
   - Left column minimizes to sidebar
   - Sidebar shows collapse indicator
   - Other columns expand

2. [ ] **Expand Left Column**
   - Click expand on sidebar
   - Left column expands to previous width
   - Content displays correctly

3. [ ] **Resize Columns**
   - Position cursor on divider
   - Cursor changes to resize cursor
   - Drag divider to new position
   - Adjacent columns adjust smoothly
   - Minimum width enforced (33.33%)

4. [ ] **Collapse All**
   - Collapse left column
   - Collapse right column
   - Center column expands full width
   - Diagram displays at full width

5. [ ] **Restore Layout**
   - Expand columns
   - Widths snap to previous values
   - Layout restored exactly

6. [ ] **Page Reload**
   - Customize column layout
   - Refresh page (F5)
   - Layout restored from localStorage
   - Width ratios maintained

### Expected Results
- ✅ Column operations smooth and responsive
- ✅ Layout persists across sessions
- ✅ Minimum width enforced
- ✅ No content clipping

---

## Workflow 8: Zoom and Navigation ✅

### Test Steps
1. [ ] **Zoom Controls**
   - Click zoom out button (-)
   - Diagram zooms to 80%
   - Zoom percentage updates
   - Zoom slider moves

2. [ ] **Zoom In**
   - Click zoom in button (+)
   - Diagram zooms to 120%
   - Zoom percentage updates

3. [ ] **Use Zoom Slider**
   - Drag zoom slider
   - Diagram zooms smoothly
   - Percentage updates in real-time

4. [ ] **Keyboard Shortcuts**
   - Press Ctrl++ to zoom in ✅ Works
   - Press Ctrl+- to zoom out ✅ Works
   - Press Ctrl+0 to reset zoom ✅ Works
   - All shortcuts responsive

5. [ ] **Reset Zoom**
   - Zoom to 200%
   - Click reset button (or Ctrl+0)
   - Zoom resets to 100%

6. [ ] **Zoom Limits**
   - Try to zoom beyond 20% (MIN_ZOOM)
   - Buttons/slider constrained
   - Try to zoom beyond 300% (MAX_ZOOM)
   - Buttons/slider constrained

7. [ ] **Zoom Persistence**
   - Set zoom to 150%
   - Refresh page
   - Zoom level persists (localStorage)

### Expected Results
- ✅ Zoom controls work intuitively
- ✅ Keyboard shortcuts responsive
- ✅ Zoom limits enforced
- ✅ Zoom level persists

---

## Workflow 9: Error Handling ✅

### Test Steps
1. [ ] **Empty Prompt**
   - Click Submit without entering prompt
   - Toast appears: "Prompt cannot be empty"
   - Submit button remains available

2. [ ] **No Agent Selected**
   - Clear agent selection
   - Try to submit prompt
   - Error message: "Please select an agent"
   - Prompt preserved

3. [ ] **Validation Error**
   - Edit code with syntax error
   - Click Validate
   - Error list appears with details
   - Line numbers shown
   - Code preserved for fixes

4. [ ] **Render Without Validation**
   - Try to render code without validating
   - Warning: "Please validate code first"
   - Render button disabled

5. [ ] **Network Error**
   - Simulate network error (if testable)
   - Error message appears
   - Retry button available
   - Can retry after fixing connection

6. [ ] **Unsaved Changes Dialog**
   - Edit prompt
   - Select different agent
   - Dialog appears: "You have unsaved prompt..."
   - Click "Cancel" to keep editing
   - Click "Confirm" to discard changes
   - Both actions work correctly

### Expected Results
- ✅ All error messages clear and actionable
- ✅ User input preserved when possible
- ✅ Recovery options available
- ✅ No silent failures

---

## Workflow 10: SSE Message Monitoring ✅

### Test Steps
1. [ ] **Submit Diagram Generation**
   - Submit prompt to generate diagram
   - SSE connection status: "Connected" (green)
   - Message counter shows 0

2. [ ] **Monitor Progress**
   - Messages receive from backend
   - Message counter increments
   - Messages tagged by type (progress, info, success)
   - Timestamps shown in local time

3. [ ] **View All Messages**
   - Click "Messages (N)" button in footer
   - Modal opens showing all messages
   - Messages scrollable if many
   - Each message shows: type, time, content

4. [ ] **Close and Continue**
   - Close modal
   - Messages still available to view again
   - Generation continues

5. [ ] **Connection Status**
   - During generation: "Connected" (green)
   - After completion: May show "Disconnected" (red)
   - If disconnected: Status changes red, show reconnection attempts

### Expected Results
- ✅ Message streaming works
- ✅ Connection status clearly visible
- ✅ All messages captured
- ✅ Proper timestamps

---

## Workflow 11: Keyboard Navigation ✅

### Test Steps
1. [ ] **Tab Navigation**
   - Press Tab repeatedly
   - Focus moves through interactive elements
   - Focus order: Left → Center → Right → Footer

2. [ ] **Shift+Tab**
   - Press Shift+Tab
   - Focus moves backwards
   - Correct reverse order

3. [ ] **Button Activation**
   - Tab to button
   - Press Enter
   - Button activates (Submit, Validate, Render, etc.)

4. [ ] **Dropdown Navigation**
   - Tab to agent dropdown
   - Press Enter to open
   - Arrow keys to navigate options
   - Enter to select
   - Escape to close

5. [ ] **Focus Visible**
   - All interactive elements show focus outline
   - Outline visible in all themes
   - Outline color contrasts properly

### Expected Results
- ✅ Tab order logical
- ✅ All buttons keyboard accessible
- ✅ Dropdowns respond to keyboard
- ✅ Focus always visible

---

## Workflow 12: Accessibility Verification ✅

### Test Steps
1. [ ] **Screen Reader (if available)**
   - NVDA/JAWS: Page title announced
   - Form fields announced with labels
   - Buttons announced with purpose
   - Alerts announced
   - Region landmarks

2. [ ] **Color Contrast**
   - Text readable on backgrounds
   - Error messages visible
   - Success messages visible
   - All colors meet WCAG AA standards

3. [ ] **Resize Text**
   - Browser zoom to 200%
   - All content readable
   - No horizontal scrollbars
   - Controls still operable

4. [ ] **Language**
   - Page language set to English
   - All text in English

### Expected Results
- ✅ Page structure clear to screen readers
- ✅ Sufficient color contrast
- ✅ Text resizable without issues
- ✅ All accessibility features working

---

## Performance Verification ✅

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
- [ ] Initial load: < 50 MB (check DevTools)
- [ ] After 10 diagrams: < 100 MB
- [ ] No memory leaks on switching tabs

---

## Cross-Browser Testing ✅

### Desktop Browsers
- [ ] **Chrome** (latest version)
  - Layout renders correctly
  - All features work
  - No console errors

- [ ] **Firefox** (latest version)
  - SVG rendering works
  - CSS Grid layout correct
  - All interactions functional

- [ ] **Safari** (latest version)
  - Sticky positioning works
  - Scroll behavior correct
  - Touch interactions smooth

- [ ] **Edge** (latest version)
  - All features functional
  - Performance comparable to Chrome

### Mobile Browsers (if applicable)
- [ ] **iOS Safari**
  - Responsive layout
  - Touch interactions work
  - Safe area insets respected

- [ ] **Chrome Android**
  - Responsive layout
  - Touch interactions smooth
  - Performance acceptable

---

## Final Sign-Off Checklist

### Functional Requirements
- [ ] All workflows complete without errors
- [ ] No console errors or warnings
- [ ] All features work as specified
- [ ] State persists correctly
- [ ] Error messages helpful

### Non-Functional Requirements
- [ ] Performance targets met
- [ ] Accessibility features working
- [ ] Cross-browser compatibility verified
- [ ] Keyboard navigation functional
- [ ] Mobile responsive (if applicable)

### Documentation
- [ ] README matches actual behavior
- [ ] API endpoints match implementation
- [ ] Error messages match documentation
- [ ] Workflows match user guide

### Known Issues
- [ ] No critical bugs found
- [ ] Any issues documented
- [ ] Workarounds provided if needed

---

## Test Execution Summary

### Overall Status
- **Total Workflows**: 12
- **Total Test Cases**: 100+
- **Expected Duration**: 2-3 hours
- **Required Environments**: Backend (running), Frontend (npm start)

### Success Criteria
- ✅ All workflows complete successfully
- ✅ No critical errors
- ✅ Performance targets met
- ✅ No data loss
- ✅ Accessibility compliant

### Sign-Off
- [ ] QA Team Lead: _______________  Date: _______
- [ ] Product Owner: _______________  Date: _______
- [ ] Tech Lead: _______________  Date: _______

---

## Post-Testing Actions

1. **If All Tests Pass**
   - ✅ Mark project as production-ready
   - ✅ Prepare deployment
   - ✅ Update release notes
   - ✅ Schedule deployment window

2. **If Issues Found**
   - ✅ Document all issues
   - ✅ Prioritize by severity
   - ✅ Create bug tickets
   - ✅ Assign to development team
   - ✅ Re-test after fixes

3. **Post-Deployment**
   - ✅ Monitor error rates
   - ✅ Track user feedback
   - ✅ Measure performance
   - ✅ Prepare for v1.1.0

---

**Testing Started**: [Date/Time]
**Testing Completed**: [Date/Time]
**Total Duration**: [Hours]
**Test Results**: [PASSED/FAILED]

---

For detailed test guides, see:
- `workflowTesting.guide.md` - Comprehensive workflow tests
- `componentTesting.guide.md` - Component-level tests
- `accessibility.audit.md` - Accessibility compliance
