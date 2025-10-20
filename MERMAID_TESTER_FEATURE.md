# Mermaid Tester Feature

## Overview

I've successfully integrated a **Mermaid Diagram Tester** into your Whysper frontend application! This provides an interactive UI for testing and validating Mermaid diagrams using the backend validation API.

---

## What's New

### Frontend Component

**File Created:** [frontend/src/components/modals/MermaidTesterModal.tsx](frontend/src/components/modals/MermaidTesterModal.tsx)

A comprehensive modal component that provides:
- **Code Editor** - Write and edit Mermaid diagram code
- **Validation** - Test syntax without rendering
- **Auto-Fix** - Automatically fix common syntax errors
- **Rendering** - Render diagrams to SVG in real-time
- **Test Cases** - Pre-loaded examples for testing
- **Server Status** - Real-time connection monitoring

---

## How to Access

### In the Application:

1. **Click the "More Options" (⋮) button** in the top-right header
2. **Select "Mermaid Tester"** from the dropdown menu

The menu item appears between "Settings" and "About".

---

## Features

### 1. Code Editor
- **Large text area** for writing Mermaid code
- **Monospace font** for better code readability
- **Real-time editing** without page refresh

### 2. Action Buttons

**Validate Only**
- Quick syntax check without rendering
- Shows validation errors if any
- No diagram generation

**Validate & Auto-Fix**
- Validates syntax
- Attempts to fix common errors automatically
- Shows fixed code with "Apply" button
- Examples:
  - Missing diagram type → adds `flowchart TD`
  - Arrow spacing issues → fixes spacing
  - Reserved keywords → suggests alternatives

**Validate & Render**
- Full validation + rendering
- Auto-fixes if needed
- Displays SVG in preview pane
- Shows render time

### 3. Test Cases Panel

Pre-loaded examples (click to load):

✅ **Valid Flowchart**
- Basic flowchart with decision nodes
- Good for testing basic rendering

✅ **Valid Sequence Diagram**
- Participant interactions
- Message passing example

❌ **Missing Diagram Type**
- Tests auto-fix functionality
- Should add `flowchart TD` automatically

❌ **Reserved Keyword Error**
- Using `end` as node ID
- Shows proper error handling

✅ **Complex Architecture**
- Multi-tier system with subgraphs
- Tests advanced features

### 4. Live Preview
- **Rendered diagram** displayed in right panel
- **SVG output** - scalable and crisp
- **Auto-centered** in preview area
- **Scrollable** for large diagrams

### 5. Server Status
- **Green dot** = Backend online
- **Red dot** = Backend offline
- **Refresh button** to check connection
- Located in modal header

---

## Integration Details

### Files Modified

1. **[frontend/src/components/modals/index.ts](frontend/src/components/modals/index.ts)**
   - Exported `MermaidTesterModal`

2. **[frontend/src/App.tsx](frontend/src/App.tsx)**
   - Imported component
   - Added state: `mermaidTesterModalOpen`
   - Added modal render
   - Added handler: `() => setMermaidTesterModalOpen(true)`

3. **[frontend/src/components/layout/Header.tsx](frontend/src/components/layout/Header.tsx)**
   - Added prop: `onMermaidTester`
   - Added menu item in dropdown with PlayCircle icon

---

## Backend API Integration

The Mermaid Tester connects to these backend endpoints:

### Health Check
```
GET http://localhost:8003/api/v1/mermaid/health
```

### Validation
```
POST http://localhost:8003/api/v1/mermaid/validate
Body: { "code": "...", "auto_fix": true }
```

### Rendering
```
POST http://localhost:8003/api/v1/mermaid/render
Body: { "code": "...", "return_svg": true, "output_format": "svg" }
```

---

## Usage Examples

### Example 1: Quick Validation

1. Click **More Options** → **Mermaid Tester**
2. The default test case loads automatically
3. Click **"Validate Only"**
4. See ✅ or ❌ result

### Example 2: Auto-Fix Invalid Code

1. Click **"Missing Diagram Type"** test case
2. Click **"Validate & Auto-Fix"**
3. See the fixed code in the result panel
4. Click **"Apply Fixed Code"** to use it
5. Click **"Validate & Render"** to see the diagram

### Example 3: Render Custom Diagram

1. Type your Mermaid code in the editor
2. Click **"Validate & Render"**
3. View the rendered SVG in the preview pane
4. If errors occur, they're shown with details

---

## Error Handling

### Validation Errors
- **Clear error messages** from mmdc CLI
- **Parse error line numbers** when available
- **Suggestions** for common mistakes

### Auto-Fix Capability
- **Missing diagram types** → adds appropriate type
- **Arrow syntax** → fixes spacing
- **Node syntax** → adds quotes where needed
- **Subgraph issues** → adds missing `end` statements

### Render Errors
- **Invalid syntax** → shows validation error
- **Reserved keywords** → highlights the issue
- **Backend offline** → shows connection error

---

## Visual Design

### Layout
- **Two-column grid** (50/50 split)
- **Left:** Code editor + buttons + results
- **Right:** Test cases + preview

### Color Scheme
- **Success messages:** Green background
- **Error messages:** Red/Orange background
- **Info messages:** Blue background
- **Code blocks:** Light gray monospace

### Responsive
- **Large modal:** 1400px width
- **Scrollable areas** for long content
- **Fixed header** with status indicator

---

## Testing the Feature

1. **Open the app** at http://localhost:5174
2. **Click More Options** (⋮) in header
3. **Select "Mermaid Tester"**
4. **Try the test cases** by clicking them
5. **Validate and render** to see results

### What to Test
- ✅ Valid diagrams render correctly
- ✅ Invalid diagrams show errors
- ✅ Auto-fix works for common issues
- ✅ Server status updates correctly
- ✅ Apply fixed code button works
- ✅ Preview pane displays SVG

---

## Benefits

### For Developers
1. **Quick testing** of Mermaid syntax
2. **Immediate feedback** on errors
3. **Auto-fix suggestions** save time
4. **No need to switch contexts** - all in the app

### For Users
1. **Learn Mermaid syntax** through examples
2. **Debug diagrams** before using in chat
3. **Understand errors** with clear messages
4. **Preview before sending** to AI

### For AI Integration
1. **Validate AI-generated diagrams** before showing to users
2. **Get error details** to ask AI to regenerate
3. **Test fixes** before applying them
4. **Confidence in diagram quality**

---

## Next Steps

You can now:

1. ✅ **Test Mermaid diagrams** in a dedicated UI
2. ✅ **Validate syntax** before using in chat
3. ✅ **Auto-fix errors** with one click
4. ✅ **Preview renderings** instantly
5. ✅ **Learn from examples** with test cases

### Optional Enhancements

- Add **"Save Diagram"** button to store favorites
- Add **"Copy to Chat"** button to insert into conversation
- Add **"Export SVG"** button to download rendered diagrams
- Add **"Share Test Case"** to save custom examples
- Add **"Diagram History"** to see previous tests
- Add **"Diff View"** to compare original vs fixed code

---

## Screenshots

When you open the Mermaid Tester, you'll see:

```
┌─────────────────────────────────────────────────────────────────┐
│  Mermaid Diagram Tester               ● Server Online  [Refresh]│
├─────────────────────────┬───────────────────────────────────────┤
│ Mermaid Code Editor     │ Test Cases                            │
│ ┌─────────────────────┐ │ ┌────────────────────────────────────┐│
│ │ flowchart TD        │ │ │ ✅ Valid Flowchart                 ││
│ │   A[Start] --> B    │ │ │ Basic flowchart...                 ││
│ │   B --> C[End]      │ │ └────────────────────────────────────┘│
│ └─────────────────────┘ │ ┌────────────────────────────────────┐│
│                         │ │ ✅ Valid Sequence Diagram          ││
│ [Validate Only]         │ │ Simple sequence...                 ││
│ [Validate & Auto-Fix]   │ └────────────────────────────────────┘│
│ [Validate & Render]     │ ┌────────────────────────────────────┐│
│                         │ │ ❌ Missing Diagram Type            ││
│ ┌─────────────────────┐ │ │ Should be auto-fixed...            ││
│ │ ✅ Valid Syntax!    │ │ └────────────────────────────────────┘│
│ └─────────────────────┘ │                                        │
│                         │ Rendered Diagram                       │
│                         │ ┌────────────────────────────────────┐│
│                         │ │        ┌───────┐                   ││
│                         │ │        │ Start │                   ││
│                         │ │        └───┬───┘                   ││
│                         │ │            │                       ││
│                         │ │        ┌───▼───┐                   ││
│                         │ │        │  End  │                   ││
│                         │ │        └───────┘                   ││
│                         │ └────────────────────────────────────┘│
└─────────────────────────┴───────────────────────────────────────┘
```

---

## Enjoy Your New Mermaid Tester! 🎉

The feature is now fully integrated and ready to use. Just click the More Options menu and select "Mermaid Tester" to get started!
