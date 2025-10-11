# D2 Diagram Support - Implementation Guide

## 🎯 Overview

Whysper now supports **D2 diagrams** in addition to Mermaid diagrams! D2 is a modern diagram scripting language that turns text into diagrams, perfect for software architecture and system diagrams.

## ✅ What's Implemented

### Dual Format Support
- ✅ **Markdown**: ` ```d2 ` code blocks
- ✅ **HTML**: `<pre><code>` blocks with D2 syntax detection
- ✅ **Client-side rendering**: Using `@terrastruct/d2` WASM library
- ✅ **Full feature parity** with Mermaid: copy, download SVG/PNG, expand

### Smart Detection
- ✅ Detects D2 syntax patterns automatically
- ✅ Distinguishes between Mermaid and D2 diagrams
- ✅ Handles duplicate blocks (shows code + rendered diagram)

---

## 📚 D2 Syntax Examples

### Basic Connection
```d2
user -> server: Makes request
server -> database: Queries data
database -> server: Returns data
server -> user: Sends response
```

### Shapes and Styles
```d2
cloud: Cloud Service {
  shape: cloud
  style.fill: lightblue
}

api: API Gateway {
  shape: hexagon
  style.fill: orange
}

database: Database {
  shape: cylinder
  style.fill: green
}

cloud -> api
api -> database
```

### Complex Architecture
```d2
users: Users {
  shape: person
}

lb: Load Balancer {
  shape: hexagon
}

users -> lb

services: Services {
  api1: API Server 1
  api2: API Server 2
  api3: API Server 3

  api1.shape: rectangle
  api2.shape: rectangle
  api3.shape: rectangle
}

lb -> services.api1
lb -> services.api2
lb -> services.api3

db: PostgreSQL {
  shape: cylinder
  style.fill: #336791
}

services.api1 -> db
services.api2 -> db
services.api3 -> db
```

### Bidirectional Connections
```d2
frontend <-> backend: REST API
backend <-> cache: Read/Write
backend -> queue: Publish
worker <- queue: Subscribe
```

---

## 🔧 Technical Implementation

### Files Created

1. **`frontend/src/components/chat/D2Diagram.tsx`**
   - React component for rendering D2 diagrams
   - Uses `@terrastruct/d2` library for compilation
   - Provides copy, download SVG/PNG, expand features
   - Same interface as MermaidDiagram component

2. **`frontend/src/utils/mermaidUtils.ts`** (Updated)
   - Added D2 detection functions:
     - `isD2Code(language, inline)` - Check language attribute
     - `isD2Syntax(code)` - Heuristic D2 pattern detection
     - `prepareD2Code(code)` - Decode HTML entities
     - `isValidD2Diagram(code)` - Validation

### Files Modified

1. **`frontend/src/components/chat/ChatView.tsx`**
   - Updated `CodeComponentRenderer` to handle D2
   - Renamed `processMermaidInHTML` → `processDiagramsInHTML`
   - Added D2 detection alongside Mermaid detection
   - Both HTML and Markdown views support D2

2. **`frontend/package.json`**
   - Added `@terrastruct/d2": "^0.1.33`

---

## 🎨 D2 Detection Patterns

The system detects D2 syntax using these patterns:

| Pattern | Example | Description |
|---------|---------|-------------|
| `->` | `a -> b` | Arrow connection |
| `<->` | `a <-> b` | Bidirectional arrow |
| `<-` | `a <- b` | Reverse arrow |
| `.shape:` | `x.shape: rectangle` | Shape definition |
| `.style.` | `x.style.fill: blue` | Style definition |
| `.label:` | `x.label: "text"` | Label definition |
| `.class:` | `x.class: server` | Class definition |
| `layers {` | `layers { ... }` | Layers block |
| `scenarios {` | `scenarios { ... }` | Scenarios block |
| `direction:` | `direction: right` | Direction spec |

---

## 📝 Usage Examples

### For Users

Simply ask the LLM to create a D2 diagram:

**Example Prompts:**
```
"Create a D2 diagram showing microservices architecture"
"Generate a D2 diagram of user authentication flow"
"Make a D2 diagram for our database schema"
```

The LLM will return D2 code, and it will automatically render!

### Markdown Format
```markdown
```d2
users -> api: HTTP Request
api -> database: Query
database -> api: Result
api -> users: Response
```
```

### HTML Format (LLM responses)
```html
<h3>D2 Code</h3>
<pre><code>users -> api: HTTP Request
api -> database: Query</code></pre>

<h3>Rendered Diagram</h3>
<pre><code>users -> api: HTTP Request
api -> database: Query</code></pre>
```

**Result:** Shows collapsible code block + rendered diagram

---

## 🔍 How It Works

### Detection Flow

```
┌─────────────────────────────────────────────────────────┐
│ LLM Returns Response with D2 Code                      │
│ <pre><code>users -> api: Request</code></pre>         │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ ChatView Component                                      │
│ - HTML View: processDiagramsInHTML()                   │
│ - Markdown View: CodeComponentRenderer                 │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Detection (Both Paths)                                  │
│ 1. Extract code from block                             │
│ 2. Decode HTML entities                                │
│ 3. Check patterns: isD2Syntax()                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ D2 Detected? → Pattern Match                           │
│ - Check for: ->, <->, .shape, .style, etc.            │
│ - At least one pattern must match                     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ Render D2Diagram Component                             │
│ - Compile D2 code using @terrastruct/d2               │
│ - Generate SVG output                                  │
│ - Display with interaction buttons                    │
└─────────────────────────────────────────────────────────┘
```

### Rendering Process

```typescript
// In D2Diagram.tsx
import * as d2 from '@terrastruct/d2';

// Compile D2 to SVG
const result = await d2.compile(code, {
  layout: 'dagre',  // Client-side layout engine
  sketch: false,    // Clean, non-sketch mode
});

// Get SVG
const svg = result.data;

// Insert into DOM
container.innerHTML = svg;
```

---

## 🎯 Detection Priority

When processing code blocks, the system checks in this order:

1. **Explicit language tag** (Markdown)
   - ` ```mermaid ` → Mermaid
   - ` ```d2 ` → D2
   - ` ```d2lang ` → D2

2. **Syntax heuristics** (HTML blocks)
   - Check Mermaid patterns first
   - If no match, check D2 patterns
   - First match wins

3. **Fallback**
   - No patterns match → Regular code block

---

## 💡 Features Comparison

| Feature | Mermaid | D2 |
|---------|---------|-----|
| **Client-side rendering** | ✅ | ✅ |
| **Copy code** | ✅ | ✅ |
| **Download SVG** | ✅ | ✅ |
| **Download PNG** | ✅ | ✅ |
| **Expand to new tab** | ✅ | ✅ |
| **Collapsible code view** | ✅ | ✅ |
| **HTML detection** | ✅ | ✅ |
| **Markdown detection** | ✅ | ✅ |
| **Duplicate handling** | ✅ | ✅ |

---

## 🎨 D2 vs Mermaid - When to Use

### Use D2 When:
- ✅ Software architecture diagrams
- ✅ Infrastructure/deployment diagrams
- ✅ Clean, simple connection-based diagrams
- ✅ Need custom shapes and styles
- ✅ Box-and-arrow style preferred

### Use Mermaid When:
- ✅ Flowcharts with decision trees
- ✅ Sequence diagrams (timeline-based)
- ✅ Gantt charts for projects
- ✅ State machines
- ✅ Git graphs
- ✅ Need specialized diagram types

---

## 🧪 Testing D2 Diagrams

### Test Case 1: Simple Connection
```d2
frontend -> backend
backend -> database
```

**Expected:** Two boxes connected with arrows

### Test Case 2: Styled Shapes
```d2
api: API Server {
  shape: hexagon
  style.fill: orange
}

db: Database {
  shape: cylinder
  style.fill: blue
}

api -> db: Queries
```

**Expected:** Hexagon and cylinder with colors, connected

### Test Case 3: Complex Architecture
```d2
direction: right

users: Users { shape: person }
lb: Load Balancer { shape: diamond }

users -> lb

services: {
  api1: API 1
  api2: API 2
  api3: API 3
}

lb -> services.api1
lb -> services.api2
lb -> services.api3

db: Database { shape: cylinder }

services.api1 -> db
services.api2 -> db
services.api3 -> db
```

**Expected:** Multi-tier architecture diagram flowing left-to-right

---

## 🐛 Troubleshooting

### Diagram Not Rendering?

**Check:**
1. ✅ Is the syntax valid D2?
2. ✅ Does it contain at least one arrow (`->`, `<->`, `<-`)?
3. ✅ Is the message in "HTML View" mode?
4. ✅ Check browser console for errors

**Debug:**
```javascript
// Test detection in browser console
import { isD2Syntax } from './utils/mermaidUtils';

const code = "user -> server";
console.log(isD2Syntax(code)); // Should be true
```

### Shows as Code Block Instead of Diagram?

**Solutions:**
1. Toggle to "HTML View" (🌐 icon in message header)
2. Check if LLM included `d2` or `d2lang` language tag
3. Verify D2 patterns exist in the code

### Error: "Failed to render D2 diagram"?

**Possible Causes:**
- Invalid D2 syntax
- WASM module not loaded
- Browser incompatibility

**Solutions:**
- Verify syntax at [https://play.d2lang.com](https://play.d2lang.com)
- Check browser console for specific error
- Try in different browser (Chrome/Edge recommended)

---

## 📊 Example Outputs

### Before (Without D2 Support)
```
User: "Create a D2 diagram of microservices"

LLM Response shows:
<pre><code>users -> api
api -> database</code></pre>

Result: Plain text code block ❌
```

### After (With D2 Support)
```
User: "Create a D2 diagram of microservices"

LLM Response shows:
1. 📝 D2 Code (collapsible)
2. Rendered D2 Diagram with interaction buttons ✅
```

---

## 🚀 Future Enhancements

Potential improvements:
- [ ] Support TALA layout engine (requires backend API)
- [ ] Custom D2 themes
- [ ] Syntax validation before rendering
- [ ] Live preview editor
- [ ] Export to additional formats
- [ ] D2 code highlighting in collapsible block

---

## 📚 D2 Resources

- **Official D2 Documentation:** [https://d2lang.com](https://d2lang.com)
- **D2 Playground:** [https://play.d2lang.com](https://play.d2lang.com)
- **D2 GitHub:** [https://github.com/terrastruct/d2](https://github.com/terrastruct/d2)
- **D2.js NPM Package:** [@terrastruct/d2](https://www.npmjs.com/package/@terrastruct/d2)

---

## ✅ Summary

**What We Built:**
- ✅ Full D2 diagram support (Markdown + HTML)
- ✅ Client-side rendering using @terrastruct/d2
- ✅ Automatic detection with 10+ syntax patterns
- ✅ Feature parity with Mermaid diagrams
- ✅ Smart duplicate handling
- ✅ Clean, collapsible code display

**How to Use:**
1. Ask LLM for D2 diagram
2. LLM returns D2 code
3. Whysper detects and renders automatically
4. User sees beautiful diagrams! 🎉

**Result:**
Your application now supports **two powerful diagram languages** with seamless client-side rendering!

---

**Status:** ✅ **Production Ready**
**Last Updated:** 2025-10-09
**Version:** 1.0 - D2 Support
