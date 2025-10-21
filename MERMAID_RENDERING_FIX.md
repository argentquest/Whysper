# Mermaid Diagram Rendering Investigation

## Issue
Mermaid diagrams returned by the AI in HTML format (`<pre><code>`) are not rendering.

## Analysis

### What the AI Returns
```html
<pre><code>graph TD
    A[Start] --&gt; B[End]
</code></pre>
```

**Problems:**
- ❌ No language marker (`class="language-mermaid"`)
- ❌ HTML entities encoded (`--&gt;` instead of `-->`)
- ❌ Generic `<pre><code>` without type info

### Expected Flow (Based on Code Analysis)

1. **Detection** ([ChatView.tsx:615](frontend/src/components/chat/ChatView.tsx#L615))
   - `detectHtmlContent()` checks if message contains HTML
   - Looks for `<pre>` tags (line 589) → ✅ MATCH
   - Looks for HTML entities (line 606) → ✅ MATCH
   - Sets `viewMode = 'html'`

2. **Processing** ([ChatView.tsx:1276](frontend/src/components/chat/ChatView.tsx#L1276))
   - Calls `processDiagramsInHTML(displayContent)`

3. **Enhanced Detection** ([ChatView.tsx:263](frontend/src/components/chat/ChatView.tsx#L263))
   - Calls `processMixedHtmlContent()` from [mermaidUtils.ts](frontend/src/utils/mermaidUtils.ts)
   - Extracts diagram candidates from HTML

4. **Fallback Detection** ([ChatView.tsx:369-373](frontend/src/components/chat/ChatView.tsx#L369-L373))
   - Regex: `/<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi`
   - Extracts raw code → `graph TD\n    A --&gt; B...`
   - Calls `prepareMermaidCode(rawCode)` → Decodes HTML entities
   - Calls `isMermaidSyntax(decodedMermaid)` → Looks for "graph" keyword
   - **Should** detect and render!

### Why It Should Work

The code has **comprehensive detection**:
- ✅ Extracts from `<pre><code>` blocks
- ✅ Decodes HTML entities (`prepareMermaidCode()`)
- ✅ Detects Mermaid keywords ("graph", "flowchart", etc.)
- ✅ Renders MermaidDiagram component

### Debugging Steps

1. **Open Whysper app in browser**
2. **Open DevTools (F12) → Console**
3. **Look for these log messages:**
   - `🎨 [DIAGRAM DETECTION]` - Detection events
   - `🎨 [MERMAID DIAGRAM]` - Rendering events
   - `❌` - Errors

4. **Check if diagram is being detected:**
   ```javascript
   // Should see logs like:
   🎨 [DIAGRAM DETECTION] Mermaid syntax detected by keyword
   🎨 [MERMAID DIAGRAM] Starting Mermaid diagram render
   ```

5. **If no logs appear:**
   - View mode might not be 'html'
   - Detection regex might not be matching
   - displayContent might be truncated

### Test Files Created

1. **[test_mermaid_rendering.html](test_mermaid_rendering.html)**
   - Comprehensive test with 3 test cases
   - Shows which tests pass/fail

2. **[test_mermaid_simple.html](test_mermaid_simple.html)**
   - Simple test to verify Mermaid library works

3. **[test_actual_llm_response.html](test_actual_llm_response.html)**
   - Tests the exact format the AI returned
   - Shows HTML entity decoding

4. **[test_diagram_logging.html](test_diagram_logging.html)**
   - Replicates exact detection logic from Whysper
   - Shows detailed logs of detection process
   - **Open this first to verify detection works!**

### Fixes Applied

1. **Show More/Show Less** ([ChatView.tsx:620-624](frontend/src/components/chat/ChatView.tsx#L620-L624))
   - ✅ Changed threshold from 5000 to 500 characters
   - Now appears for almost all messages

### Next Steps

**Please run the test file:**
```bash
start "c:\Code2025\Whysper\test_diagram_logging.html"
```

This will show you:
- ✅ If diagram detection logic works
- ✅ If HTML decoding works
- ✅ If Mermaid rendering works
- ❌ Any errors in the process

**Then check Whysper app console:**
- Look for 🎨 emojis in console logs
- Tell me what view mode it's using (HTML or Markdown)
- Check if `processDiagramsInHTML()` is being called

## Potential Issues (To Investigate)

1. **displayContent might be truncated** - If `showFullContent = false`, only first 500 chars shown
2. **viewMode might be 'markdown'** - Check which view mode is active
3. **MermaidDiagram component might be failing silently** - Returns `null` if `isValid === false`

## How to Force Markdown View

If HTML view is causing issues, you can toggle to Markdown view:
- Look for the view toggle buttons in the message header
- Click the "Markdown View" button (FileTextOutlined icon)

