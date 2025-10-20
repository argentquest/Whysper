# D2 Diagram Tester - Feature Guide

## Overview

The **D2 Diagram Tester** is a professional testing tool integrated into Whysper that allows you to validate and render D2 diagrams in real-time. It features a Monaco code editor, pre-loaded test cases, and live SVG preview.

---

## Table of Contents

1. [How to Access](#how-to-access)
2. [User Interface](#user-interface)
3. [Features](#features)
4. [Test Cases](#test-cases)
5. [Validation](#validation)
6. [Rendering](#rendering)
7. [Common D2 Syntax](#common-d2-syntax)
8. [Troubleshooting](#troubleshooting)
9. [API Integration](#api-integration)

---

## How to Access

There are two ways to open the D2 Diagram Tester:

### Method 1: Header Dropdown Menu
1. Click the **More Options (⋮)** button in the top-right corner of the header
2. Select **"D2 Tester"** from the dropdown menu

### Method 2: Keyboard Shortcut (Future Enhancement)
- Currently not implemented
- Can be added if needed

---

## User Interface

The D2 Tester modal is divided into two main panels:

```
┌─────────────────────────────────────────────────────────────┐
│  D2 Diagram Tester                      [Server Status] [X] │
├──────────────────────────┬──────────────────────────────────┤
│  LEFT PANEL              │  RIGHT PANEL                     │
│                          │                                  │
│  ┌────────────────────┐  │  ┌────────────────────────────┐ │
│  │  D2 Code Editor    │  │  │  Test Cases                │ │
│  │  (Monaco Editor)   │  │  │  ┌──────────────────────┐  │ │
│  │                    │  │  │  │ ✅ Valid Simple      │  │ │
│  │                    │  │  │  │ ✅ Valid Architecture│  │ │
│  │                    │  │  │  │ ✅ Valid Network     │  │ │
│  │                    │  │  │  │ ❌ Unclosed String   │  │ │
│  │                    │  │  │  │ ❌ Invalid Shape     │  │ │
│  └────────────────────┘  │  │  │ ✅ Complex Diagram   │  │ │
│                          │  │  └──────────────────────┘  │ │
│  [Validate Only]         │  │                            │ │
│  [Validate & Render]     │  │  Rendered Diagram          │ │
│                          │  │  ┌──────────────────────┐  │ │
│  ┌────────────────────┐  │  │  │                      │  │ │
│  │  Validation Result │  │  │  │  [SVG Preview]       │  │ │
│  │  ✅ Valid / ❌ Error│  │  │  │                      │  │ │
│  └────────────────────┘  │  │  └──────────────────────┘  │ │
│                          │  │  Render time: 0.42s         │ │
└──────────────────────────┴──────────────────────────────────┘
```

---

## Features

### 1. Monaco Code Editor

**Professional code editing experience:**
- Syntax highlighting for D2 code
- Line numbers and code folding
- Multi-cursor support
- Find and replace
- Automatic indentation
- Theme support (light/dark based on app theme)

**How to use:**
- Type or paste D2 code directly into the editor
- Use keyboard shortcuts (Ctrl+F for find, Ctrl+Z for undo, etc.)
- Code is automatically saved while you type

### 2. Pre-loaded Test Cases

**6 ready-to-use examples:**
- ✅ **3 valid diagrams** - Working examples to learn from
- ❌ **2 invalid diagrams** - Common errors to understand
- ✅ **1 complex diagram** - Advanced microservices architecture

**How to use:**
- Click any test case card to load it into the editor
- The code will replace the current editor content
- Validation and render results will be cleared

### 3. Real-time Validation

**Instant syntax checking:**
- Click **"Validate Only"** to check syntax without rendering
- Results appear immediately below the buttons
- Shows error messages with details

### 4. Live SVG Preview

**Render diagrams on the fly:**
- Click **"Validate & Render"** to generate SVG
- Preview appears in the right panel
- Displays render time and validation status

### 5. Server Status Indicator

**Monitor backend connectivity:**
- Green dot = Server online and D2 CLI available
- Red dot = Server offline or D2 CLI not found
- Click **"Refresh"** to check status again

---

## Test Cases

### Valid Test Cases

#### 1. Valid Simple Diagram
```d2
# Simple flowchart
User: {
  shape: person
}

API: {
  shape: rectangle
}

Database: {
  shape: cylinder
}

User -> API: Request
API -> Database: Query
Database -> API: Results
API -> User: Response
```

**Description:** Basic flowchart with different shapes (person, rectangle, cylinder)

**Use case:** Learn basic D2 syntax and shape definitions

---

#### 2. Valid Architecture Diagram
```d2
# System Architecture
direction: right

Frontend: {
  UI: User Interface
  Router: React Router
}

Backend: {
  API: FastAPI Server
  Auth: Authentication
  DB: PostgreSQL {
    shape: cylinder
  }
}

Frontend.UI -> Frontend.Router
Frontend.Router -> Backend.API
Backend.API -> Backend.Auth
Backend.API -> Backend.DB
Backend.Auth -> Backend.DB
```

**Description:** Multi-tier system architecture with nested containers

**Use case:** Learn how to create complex hierarchies and connections

---

#### 3. Valid Network Diagram
```d2
# Network Topology
Internet: {
  shape: cloud
  label: "Internet"
}

Firewall: {
  shape: rectangle
}

LoadBalancer: {
  shape: rectangle
}

Server1: {
  shape: rectangle
}

Server2: {
  shape: rectangle
}

Internet -> Firewall
Firewall -> LoadBalancer
LoadBalancer -> Server1
LoadBalancer -> Server2
```

**Description:** Network infrastructure diagram with cloud and rectangles

**Use case:** Learn how to model network topologies

---

### Invalid Test Cases

#### 4. Unclosed String Error
```d2
# Invalid - unclosed quote
User: {
  label: "This is unclosed
}

API: {
  label: "API Server"
}

User -> API
```

**Error:** String not properly closed (missing closing quote)

**Expected error message:** Parse error or syntax error about unclosed string

**How to fix:** Add closing quote: `label: "This is unclosed"`

---

#### 5. Invalid Shape Error
```d2
# Invalid - unknown shape
User: {
  shape: human
}

API: {
  shape: rectangle
}

User -> API
```

**Error:** Using "human" instead of "person" for human shape

**Expected error message:** Unknown shape "human"

**How to fix:** Change to valid shape: `shape: person`

---

### Complex Test Cases

#### 6. Complex Microservices Architecture
```d2
# Microservices Architecture
direction: down

users: Users {
  shape: person
}

gateway: API Gateway {
  shape: rectangle
}

auth: Auth Service {
  shape: rectangle
}

user_service: User Service {
  shape: rectangle
}

order_service: Order Service {
  shape: rectangle
}

payment_service: Payment Service {
  shape: rectangle
}

user_db: User DB {
  shape: cylinder
}

order_db: Order DB {
  shape: cylinder
}

payment_db: Payment DB {
  shape: cylinder
}

cache: Redis Cache {
  shape: stored_data
}

queue: Message Queue {
  shape: queue
}

users -> gateway: HTTP Requests

gateway -> auth: Authenticate
gateway -> user_service: User Operations
gateway -> order_service: Order Operations
gateway -> payment_service: Payment Operations

auth -> cache: Session Cache

user_service -> user_db: CRUD
order_service -> order_db: CRUD
payment_service -> payment_db: CRUD

order_service -> queue: Order Events
payment_service -> queue: Payment Events
```

**Description:** Complete microservices architecture with multiple services, databases, cache, and message queue

**Use case:** Learn how to create complex production-grade diagrams

---

## Validation

### How Validation Works

1. **User clicks "Validate Only"**
2. **Frontend sends POST request** to `/api/v1/d2/validate`
3. **Backend validates** using D2 CLI
4. **Result returned** with validation status and errors (if any)
5. **UI updates** with validation result

### Validation Response

**Success:**
```json
{
  "is_valid": true,
  "error": null,
  "code_length": 234
}
```

**Failure:**
```json
{
  "is_valid": false,
  "error": "d2/d2parser/parse.go:123:4: unclosed string...",
  "code_length": 234
}
```

### Validation UI States

**Valid Syntax:**
- Green background (#f6ffed)
- Green border (#b7eb8f)
- ✅ "Valid Syntax" header
- Shows code length

**Invalid Syntax:**
- Orange background (#fff2e8)
- Orange border (#ffbb96)
- ❌ "Invalid Syntax" header
- Shows error message in scrollable pre block

---

## Rendering

### How Rendering Works

1. **User clicks "Validate & Render"**
2. **Frontend sends POST request** to `/api/v1/d2/render`
3. **Backend validates and renders** using D2 CLI
4. **SVG content returned** along with metadata
5. **UI displays SVG** in preview panel

### Render Response

**Success:**
```json
{
  "success": true,
  "svg_content": "<svg>...</svg>",
  "validation": {
    "is_valid": true,
    "error": null
  },
  "metadata": {
    "render_time": 0.42,
    "timestamp": "2025-01-20T12:34:56.789Z"
  },
  "error": null
}
```

**Failure:**
```json
{
  "success": false,
  "svg_content": null,
  "validation": {
    "is_valid": false,
    "error": "Parse error..."
  },
  "metadata": {
    "render_time": 0.0,
    "timestamp": "2025-01-20T12:34:56.789Z"
  },
  "error": "Rendering failed: Parse error..."
}
```

### Render UI States

**Successful Render:**
- SVG displayed in preview panel
- Centered and scaled to fit
- Render time shown below
- Green checkmark for validation

**Failed Render:**
- Red ❌ "Rendering failed" message
- Error details in scrollable pre block
- No SVG preview

**No Render Yet:**
- Gray placeholder text
- "Click 'Validate & Render' to see the diagram here"

---

## Common D2 Syntax

### Basic Shapes

```d2
# Person/User
User: {
  shape: person
}

# Rectangle (default)
Service: {
  shape: rectangle
}

# Database/Cylinder
DB: {
  shape: cylinder
}

# Cloud
Internet: {
  shape: cloud
}

# Queue
MessageQueue: {
  shape: queue
}

# Stored Data
Cache: {
  shape: stored_data
}

# Document
File: {
  shape: document
}

# Circle
Node: {
  shape: circle
}

# Diamond/Decision
Decision: {
  shape: diamond
}
```

### Connections

```d2
# Simple arrow
A -> B

# Labeled arrow
A -> B: Request

# Bidirectional
A <-> B: Sync

# No arrow (just line)
A -- B
```

### Containers/Groups

```d2
# Container with nested items
Frontend: {
  UI: User Interface
  Router: React Router
}

Backend: {
  API: FastAPI
  DB: PostgreSQL
}

# Connect nested items
Frontend.UI -> Backend.API
```

### Styling

```d2
# Labels
Node: {
  label: "Custom Label"
}

# Colors
Node: {
  style.fill: "#ff0000"
  style.stroke: "#000000"
}

# Fonts
Node: {
  style.font-size: 20
  style.bold: true
}
```

### Direction

```d2
# Top to bottom (default)
direction: down

# Left to right
direction: right

# Bottom to top
direction: up

# Right to left
direction: left
```

---

## Troubleshooting

### Issue: Server Offline

**Symptom:** Red dot in server status, "Server Offline" message

**Diagnosis:**
```bash
# Check if backend is running
curl http://localhost:8003/api/v1/d2/health
```

**Solution:**
1. Start backend server: `cd backend && python main.py`
2. Click "Refresh" button to check status again

---

### Issue: D2 CLI Not Available

**Symptom:** Server online but validation/rendering fails, error mentions D2 CLI not found

**Diagnosis:**
```bash
# Check if D2 is installed
cd backend
d2 --version
```

**Solution:**
```bash
# Install D2 CLI
# Windows:
# Download from https://d2lang.com/ and add to PATH

# macOS:
brew install d2

# Linux:
curl -fsSL https://d2lang.com/install.sh | sh -s --
```

---

### Issue: Validation Always Fails

**Symptom:** All diagrams fail validation, even known-good examples

**Diagnosis:**
1. Check D2 version: `d2 --version` (should be 0.6.0+)
2. Check backend logs for D2 errors
3. Test D2 CLI manually:
   ```bash
   echo "A -> B" > test.d2
   d2 test.d2 test.svg
   ```

**Solution:**
- Update D2 to latest version
- Check D2 CLI permissions
- Verify D2 can write to temp directory

---

### Issue: Rendering Timeout

**Symptom:** Rendering takes too long and fails with timeout

**Diagnosis:**
- Check diagram complexity (very large diagrams may timeout)
- Check system resources (CPU, memory)

**Solution:**
- Simplify the diagram
- Increase timeout in backend configuration
- Split into multiple smaller diagrams

---

### Issue: Monaco Editor Not Loading

**Symptom:** Editor shows blank or doesn't load

**Diagnosis:**
1. Check browser console for errors
2. Check Monaco editor dependencies in package.json
3. Check network tab for failed CDN requests

**Solution:**
- Clear browser cache
- Restart frontend dev server: `npm run dev`
- Check Monaco editor package is installed: `npm list monaco-editor`

---

## API Integration

### Backend Endpoints

The D2 Tester uses these API endpoints:

#### 1. Health Check
```
GET /api/v1/d2/health
```

**Response:**
```json
{
  "status": "healthy",
  "d2_available": true,
  "executable": "d2",
  "version": "v0.7.1"
}
```

---

#### 2. Validate D2 Code
```
POST /api/v1/d2/validate
Content-Type: application/json

{
  "code": "A -> B"
}
```

**Response:**
```json
{
  "is_valid": true,
  "error": null,
  "code_length": 7
}
```

---

#### 3. Render D2 Diagram
```
POST /api/v1/d2/render
Content-Type: application/json

{
  "code": "A -> B",
  "return_svg": true,
  "save_to_file": false
}
```

**Response:**
```json
{
  "success": true,
  "svg_content": "<svg>...</svg>",
  "validation": {
    "is_valid": true,
    "error": null
  },
  "metadata": {
    "render_time": 0.42,
    "timestamp": "2025-01-20T12:34:56.789Z"
  },
  "error": null
}
```

---

### Frontend Implementation

**Location:** `frontend/src/components/modals/D2TesterModal.tsx`

**Key Functions:**

1. **checkServerStatus()** - Checks D2 service availability
2. **loadTestCase()** - Loads pre-defined test case
3. **validateD2()** - Validates D2 code
4. **renderD2()** - Renders D2 diagram to SVG

**State Management:**
- `d2Code` - Current D2 code in editor
- `validating` - Validation in progress flag
- `rendering` - Rendering in progress flag
- `validationResult` - Validation result data
- `renderResult` - Render result data
- `serverStatus` - Server health status

---

## Best Practices

### For Users

1. **Start with test cases** - Load a valid example to understand syntax
2. **Test incrementally** - Build diagrams step by step, validating often
3. **Use validation first** - Validate before rendering to catch errors early
4. **Check server status** - Ensure green dot before testing
5. **Study error messages** - D2 error messages are helpful for fixing issues

### For Developers

1. **Cache SVG results** - Avoid re-rendering same diagrams
2. **Debounce validation** - Don't validate on every keystroke
3. **Handle timeouts gracefully** - Show user-friendly messages
4. **Log validation attempts** - Track success/failure rates
5. **Monitor render performance** - Watch for slow diagrams

---

## Keyboard Shortcuts

**Monaco Editor Standard Shortcuts:**
- `Ctrl+F` / `Cmd+F` - Find
- `Ctrl+H` / `Cmd+H` - Find and replace
- `Ctrl+Z` / `Cmd+Z` - Undo
- `Ctrl+Y` / `Cmd+Y` - Redo
- `Ctrl+/` / `Cmd+/` - Toggle comment
- `Alt+Up/Down` - Move line up/down
- `Shift+Alt+Up/Down` - Copy line up/down

---

## Comparison: D2 Tester vs Mermaid Tester

| Feature | D2 Tester | Mermaid Tester |
|---------|-----------|----------------|
| **CLI Tool** | D2 CLI | mmdc (Mermaid CLI) |
| **Diagram Types** | Architecture, flowcharts, networks | Flowcharts, sequence, Gantt, etc. |
| **Auto-Fix** | No | Yes (3 attempts) |
| **Test Cases** | 6 (3 valid, 2 invalid, 1 complex) | 5 (2 valid, 2 invalid, 1 complex) |
| **Syntax** | Custom D2 syntax | Mermaid markdown syntax |
| **Shapes** | person, cloud, cylinder, queue, etc. | Predefined node types |
| **Containers** | Nested with dot notation | Subgraphs |
| **Validation Speed** | ~0.1-0.5s | ~0.1-0.5s |
| **Render Speed** | ~0.4-1.0s | ~0.4-1.0s |

---

## Future Enhancements

**Potential features to add:**

1. **Export Functionality**
   - Download SVG to file
   - Download PNG version
   - Copy SVG to clipboard

2. **Code Templates**
   - Save custom templates
   - Quick insert common patterns
   - Share templates between users

3. **Diff Viewer**
   - Compare versions
   - Show changes visually
   - Undo/redo history

4. **Collaboration**
   - Share diagrams via URL
   - Real-time co-editing
   - Comment on diagrams

5. **Advanced Validation**
   - Linting for style issues
   - Best practice suggestions
   - Performance warnings

6. **Theme Customization**
   - Custom color schemes
   - Font selection
   - Shape style presets

---

## Summary

The **D2 Diagram Tester** provides a professional, integrated environment for testing D2 diagrams directly in Whysper:

✅ **Monaco editor** for professional code editing
✅ **6 pre-loaded test cases** for learning and testing
✅ **Real-time validation** with detailed error messages
✅ **Live SVG preview** with render time tracking
✅ **Server status monitoring** to ensure backend availability
✅ **Easy access** from header dropdown menu
✅ **Theme support** matching app appearance

**Perfect for:**
- Learning D2 syntax
- Testing diagram code before using in chat
- Debugging validation errors
- Creating complex architecture diagrams
- Rapid prototyping of diagrams

---

## Related Documentation

- [D2 Official Documentation](https://d2lang.com/)
- [D2 Shape Reference](https://d2lang.com/tour/shapes)
- [D2 Styling Guide](https://d2lang.com/tour/style)
- Backend D2 Service: `backend/app/services/d2_render_service.py`
- Backend D2 API: `backend/app/api/v1/endpoints/d2_render.py`

---

**Enjoy creating beautiful D2 diagrams with the D2 Tester!** 🎨
