# Working Spinner Guide for Backend Developers

## Overview

The frontend has a generic "Working" spinner modal that can be controlled via SSE messages from the backend. This provides a blocking UI spinner for long-running operations where the user should wait without interacting.

## How to Use

### Show the Spinner

Send an SSE message with:
```python
send_sse({
    "message": "Working"
})
```

Or with a custom message:
```python
send_sse({
    "message": "Working: Computing diagram scores..."
})
```

The custom message will be displayed to the user in the spinner modal.

### Hide the Spinner

Send an SSE message with:
```python
send_sse({
    "message": "Working Done"
})
```

Or simply:
```python
send_sse({
    "message": "Done"
})
```

## Recommended Usage Points

Based on the diagram wizard workflow, here are the recommended places to use the working spinner:

### 1. Computing Diagram Type Scores
**Status:** `awaiting_diagram_type_selection`

```python
# When user clicks "I'm Ready" and backend starts computing scores
send_sse({"message": "Working: Computing diagram scores..."})

# ... compute keyword_scores for each diagram type ...

send_sse({
    "status": "awaiting_diagram_type_selection",
    "keyword_scores": {...},
    "recommended_diagram_type": "Mermaid",
    "message": "Working Done"
})
```

### 2. Generating Architecture Model
**Status:** `generating_json`

```python
send_sse({"message": "Working: Generating architecture model..."})

# ... generate JSON representation ...

send_sse({
    "status": "json_generated",
    "json_generation_output": {...},
    "message": "Working Done"
})
```

### 3. Generating Diagram Code
**Status:** `generating`

```python
send_sse({"message": "Working: Generating diagram code..."})

# ... generate diagram code from JSON ...

send_sse({
    "status": "code_generated",
    "diagram_code": "...",
    "message": "Working Done"
})
```

### 4. Fixing Validation Errors
**Status:** `refining` or `llm_correcting`

```python
send_sse({"message": "Working: Fixing validation errors..."})

# ... attempt to fix code ...

send_sse({
    "status": "code_refined",
    "diagram_code": "...",
    "message": "Working Done"
})
```

### 5. Rendering Diagram
**Status:** `rendering`

```python
send_sse({"message": "Working: Rendering diagram..."})

# ... render diagram code to SVG ...

send_sse({
    "status": "rendered",
    "svg_output": "...",
    "message": "Working Done"
})
```

## Message Format

The spinner detection is case-insensitive and looks for these patterns:

- **Show:** Message contains "working" (e.g., "Working", "WORKING", "Working: Please wait...")
- **Hide:** Message contains "working done" or equals "done" (case-insensitive)

### Custom Messages

You can provide context-specific messages by using the format:
```
"Working: Your custom message here..."
```

The text after "Working:" will be displayed in the spinner modal.

## Best Practices

1. **Always hide the spinner** - Make sure every "Working" message has a corresponding "Working Done"
2. **Use descriptive messages** - Help users understand what's happening (e.g., "Computing scores..." not just "Working")
3. **Combine with status updates** - You can send "Working Done" in the same message that updates the status
4. **Don't overuse** - Only use for operations that take >1 second and block user interaction
5. **Handle errors** - If an error occurs, send "Working Done" before sending the error status

## Example Flow

```python
# User clicks "I'm Ready"
send_sse({"message": "Working: Computing diagram scores..."})

try:
    # Long-running computation
    scores = compute_keyword_scores(system_description)

    # Send results and hide spinner in one message
    send_sse({
        "status": "awaiting_diagram_type_selection",
        "keyword_scores": scores,
        "recommended_diagram_type": "Mermaid",
        "message": "Working Done"
    })
except Exception as e:
    # Make sure to hide spinner even on error
    send_sse({
        "status": "error",
        "message": "Working Done"
    })
    send_sse({
        "status": "error",
        "message": f"Error: {str(e)}"
    })
```

## UI Behavior

When the spinner is shown:
- A centered modal appears with a large spinning indicator
- The custom message is displayed in blue
- The modal cannot be closed by clicking outside or pressing ESC
- All other UI interactions are blocked
- The modal disappears when "Working Done" is received

## Testing

To test the spinner in development:
1. Send a "Working" message via SSE
2. Wait a few seconds
3. Send "Working Done" to dismiss

The spinner should appear and disappear smoothly without blocking the SSE connection.
