# Toast Command System

The toast command system allows the backend to trigger frontend toast notifications by including special keywords in SSE messages.

## Available Commands

| Command | Type | Description | Example |
|---------|------|-------------|---------|
| `TOASTINFO:` | Info | Blue info toast | `TOASTINFO: Analyzing diagram...` |
| `TOASTSUCCESS:` | Success | Green success toast | `TOASTSUCCESS: Code corrected!` |
| `TOASTERROR:` | Error | Red error toast | `TOASTERROR: Validation failed` |
| `TOASTWARNING:` | Warning | Orange warning toast | `TOASTWARNING: Attempting fallback fix` |
| `TOASTLOADING:` | Loading | Loading spinner toast | `TOASTLOADING: Processing request...` |

## Frontend Implementation

The toast parser is automatically active in:
- **DiagramWizard**: All SSE updates are parsed for toast commands
- **System-Wide**: Can be used anywhere by calling `parseAndShowToast(message)`

Located in: `frontend/src/utils/toastHelper.ts`

## Backend Usage

### Option 1: Direct Message Field

```python
await update_callback({
    "status": "rendering",
    "message": "TOASTINFO: Starting diagram validation...",
})
```

### Option 2: Progress Callback in Provider

```python
await self._send_progress(progress_callback, {
    "status": "llm_correcting",
    "message": "TOASTWARNING: AI correction attempt 1/8...",
    "step": "3/4",
})
```

### Option 3: Custom Status + Toast

```python
await update_callback({
    "status": "custom_phase",
    "message": "TOASTSUCCESS: ✅ Diagram validated successfully!",
    "diagram_code": code,
})
```

## Real-World Examples

### Example 1: D2 Provider LLM Correction

```python
# In base_diagram.py - _attempt_llm_correction()
await self._send_progress(progress_callback, {
    "status": "llm_correcting",
    "message": f"TOASTINFO: AI correction attempt {attempt}/{max_retries}...",
    "step": "3/4",
    "attempt": attempt,
})
```

**Result**: Frontend shows blue info toast: "AI correction attempt 2/8..."

### Example 2: Rendering Success

```python
# In rendering_nodes.py
await update_callback({
    "status": "rendered",
    "message": "TOASTSUCCESS: ✅ Diagram rendered successfully!",
})
```

**Result**: Frontend shows green success toast: "✅ Diagram rendered successfully!"

### Example 3: Validation Error

```python
# In d2_renderer.py
await update_callback({
    "status": "error",
    "message": f"TOASTERROR: D2 validation failed: {error_details}",
    "error": error_details,
})
```

**Result**: Frontend shows red error toast: "D2 validation failed: missing semicolon"

### Example 4: Warning Before Fallback

```python
# In base_diagram.py
await self._send_progress(progress_callback, {
    "status": "llm_correcting",
    "message": "TOASTWARNING: ⚠️  Validation failed after all attempts. Rendering best attempt...",
})
```

**Result**: Frontend shows orange warning toast: "⚠️  Validation failed after all attempts. Rendering best attempt..."

## Benefits

### 1. **No Frontend Changes Needed**
Backend developers can add new toast notifications without modifying frontend code.

### 2. **Consistent UX**
All SSE messages use the same toast system for unified user experience.

### 3. **Flexible**
- Combine with status updates
- Include emojis for visual clarity
- Works with all SSE event types

### 4. **Global**
Works across the entire application, not just DiagramWizard.

## Backward Compatibility

The system is **fully backward compatible**:
- Messages without toast keywords are displayed normally
- Existing switch/case status handling still works
- Toast commands are **additive**, not replacements

## Testing

### Frontend Test
```typescript
import { parseAndShowToast } from '@/utils/toastHelper';

// Should show info toast
parseAndShowToast("TOASTINFO: Test message");

// Should return false (no toast shown)
parseAndShowToast("Regular message");
```

### Backend Test
```python
# Send SSE update with toast command
await update_callback({
    "status": "test",
    "message": "TOASTERROR: This is a test error toast",
})
```

## Best Practices

### DO ✅
- Use descriptive messages: `TOASTINFO: Analyzing 150 diagram nodes...`
- Include context: `TOASTERROR: Validation failed on line 42`
- Use appropriate types: Success for completions, Error for failures
- Add emojis for clarity: `TOASTSUCCESS: ✅ Code corrected!`

### DON'T ❌
- Don't spam toasts: Use sparingly for important events only
- Don't use TOASTLOADING for quick operations (< 1 second)
- Don't duplicate: If you show a toast, don't also trigger a switch/case toast
- Don't include toast keywords in regular log messages

## Architecture

```
Backend Provider
    ↓ (sends SSE with "TOASTINFO: message")
DiagramWizard onUpdate
    ↓ (calls parseAndShowToast)
Toast Helper
    ↓ (extracts keyword + message)
Ant Design Toast System
    ↓ (displays)
User sees notification! 🎉
```

## Future Enhancements

Possible future additions:
- `TOASTDURATION: 5000` - Custom toast display duration
- `TOASTKEY: unique-key` - Prevent duplicate toasts
- `TOASTLINK: /path` - Clickable toast with navigation
- `TOASTACTION: button-text` - Action button in toast
