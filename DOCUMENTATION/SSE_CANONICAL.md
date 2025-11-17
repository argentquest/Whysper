# SSE (Server-Sent Events) - Canonical Reference

**Last Updated:** 2025-11-17
**Status:** ✅ Production Ready
**Canonical Document:** This is the single source of truth for SSE implementation

---

## Overview

DiagramWizard uses **Server-Sent Events (SSE)** for real-time streaming of diagram generation progress from backend to frontend.

---

## Frontend Implementation

### useSSE Hook

**Location:** `frontend/src/hooks/useSSE.ts`

**Features:**
- ✅ Automatic reconnection with exponential backoff
- ✅ Keep-alive timeout monitoring (30s)
- ✅ Connection status tracking
- ✅ Message queuing and history
- ✅ Auto-close on unmount
- ✅ Configurable retry limits

**Usage:**

```typescript
import { useSSE } from '../../hooks/useSSE';

const {
  isConnected,
  error,
  messages,
  clearMessages
} = useSSE<DiagramUpdate>({
  url: `${API_BASE}/diagram/stream/${sessionId}`,
  enabled: !!sessionId,
  onMessage: (message) => {
    console.log('SSE update:', message.data);
  },
  onError: (err) => {
    console.error('SSE error:', err);
  },
  maxReconnectAttempts: 5,
  reconnectInterval: 2000,
  keepAliveTimeout: 30000
});
```

### Configuration

```typescript
interface UseSSEOptions {
  url: string;                    // SSE endpoint URL
  enabled?: boolean;              // Enable/disable connection
  onMessage?: (msg) => void;      // Message handler
  onError?: (err) => void;        // Error handler
  onConnect?: () => void;         // Connection handler
  onDisconnect?: () => void;      // Disconnection handler
  maxReconnectAttempts?: number;  // Max retries (default: 5)
  reconnectInterval?: number;     // Initial delay ms (default: 2000)
  keepAliveTimeout?: number;      // Keep-alive timeout (default: 30000)
  autoClose?: boolean;            // Auto-close on completion (default: true)
}
```

### Reconnection Logic

**Exponential Backoff:**
```
Attempt 1: 2s
Attempt 2: 4s
Attempt 3: 8s
Attempt 4: 16s
Attempt 5: 32s (then give up)
```

**Max delay:** 32 seconds

---

## Backend Implementation

### Endpoint

**Location:** `backend/app/api/v1/endpoints/diagram.py`

**Endpoint:** `GET /api/v1/diagram/stream/{session_id}`

**Response Type:** `text/event-stream`

**Implementation:**

```python
@router.get("/stream/{session_id}")
async def stream_diagram_updates(session_id: str):
    async def event_generator():
        while True:
            # Get updates from session
            update = await get_session_update(session_id)

            if update:
                yield {
                    "event": "message",
                    "data": json.dumps(update)
                }

            # Keep-alive ping every 30s
            yield {
                "event": "ping",
                "data": json.dumps({"type": "keep-alive"})
            }

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
```

### SSE Message Format

```typescript
interface SSEMessage {
  id: string;           // Unique message ID
  type: string;         // Message type
  data: any;            // Message payload
  timestamp: number;    // Unix timestamp
  isRead: boolean;      // Read status
}
```

### Common Message Types

```typescript
type MessageType =
  | "started"              // Session started
  | "analyzing"            // Analysis in progress
  | "clarifying"           // Clarification needed
  | "can_proceed"          // Ready to proceed
  | "generating"           // Code generation
  | "code_generated"       // Code complete
  | "validating"           // Validation in progress
  | "refining"             // Auto-fix in progress
  | "rendering"            // SVG rendering
  | "completed"            // All done ✅
  | "error"                // Error occurred ❌
  | "failed";              // Fatal failure ❌
```

---

## Error Handling

### Frontend Error Handling

```typescript
onError: (err) => {
  // Log error
  console.error('SSE error:', err);

  // Update UI
  setError(err);

  // Attempt reconnection (automatic via useSSE)
  // If max attempts reached, show error to user
}
```

### Backend Error Handling

```python
try:
    # Generate update
    update = generate_diagram_update()
    yield {"data": json.dumps(update)}
except Exception as e:
    # Send error event
    yield {
        "data": json.dumps({
            "status": "error",
            "message": str(e)
        })
    }
    # Close stream
    break
```

---

## Keep-Alive Strategy

### Why Keep-Alive?

**Problem:** Network proxies/firewalls close idle connections

**Solution:** Send periodic "ping" messages

**Frontend:**
```typescript
// Reset keep-alive timer on each message
keepAliveTimerRef.current = setTimeout(() => {
  console.warn('Keep-alive timeout - reconnecting');
  reconnect();
}, keepAliveTimeout);
```

**Backend:**
```python
# Send keep-alive every 25 seconds
if time.time() - last_message_time > 25:
    yield {"data": json.dumps({"type": "keep-alive"})}
    last_message_time = time.time()
```

---

## Connection Lifecycle

```
1. User action triggers session creation
   ↓
2. Frontend calls useSSE with session_id
   ↓
3. EventSource connects to /stream/{session_id}
   ↓
4. Backend starts streaming updates
   ↓
5. Frontend receives messages via onMessage
   ↓
6. Keep-alive pings maintain connection
   ↓
7. On completion/error, connection closes
   ↓
8. Frontend cleanup on unmount
```

---

## Best Practices

### ✅ Do's

1. **Always include session_id in URL** for filtering
2. **Set keepAliveTimeout** to prevent idle disconnections
3. **Limit reconnection attempts** to avoid infinite loops
4. **Clear messages** when starting new session
5. **Handle errors gracefully** with user feedback

### ❌ Don'ts

1. **Don't skip error handling** - always provide onError
2. **Don't use polling** - SSE is more efficient
3. **Don't forget cleanup** - close connections on unmount
4. **Don't ignore connection status** - show to user
5. **Don't send large payloads** - SSE has size limits

---

## Debugging

### Frontend Debugging

```typescript
const logEvent = useCallback((label: string, payload?: unknown) => {
  console.log(`[DiagramSession] ${label}`, payload ?? '');
}, []);

// Use throughout useSSE
logEvent('SSE connected');
logEvent('SSE update', update);
logEvent('SSE error', error);
logEvent('SSE disconnected');
```

### Backend Debugging

```python
import logging

logger = logging.getLogger(__name__)

# Log SSE events
logger.info(f"SSE: Client connected - session_id={session_id}")
logger.info(f"SSE: Sending update - type={update['type']}")
logger.error(f"SSE: Error occurred - {str(e)}")
logger.info(f"SSE: Client disconnected - session_id={session_id}")
```

### Browser DevTools

**Network Tab:**
- Filter: "stream"
- Type: "eventsource"
- Check: Status 200, connection open

**Console:**
- Look for `[DiagramSession]` logs
- Check for reconnection attempts

---

## Performance Considerations

### Message Frequency

**Recommendation:** 1-5 messages per second max

**Reason:** Too many messages cause UI lag

**Implementation:**
```python
# Batch updates
updates = []
while True:
    update = get_next_update()
    updates.append(update)

    if len(updates) >= 5 or time_since_last_send > 1.0:
        yield {"data": json.dumps({"updates": updates})}
        updates = []
```

### Message Size

**Recommendation:** < 1KB per message

**Reason:** SSE has practical size limits (~64KB)

**Implementation:**
```python
# Send large data separately via HTTP
if len(diagram_code) > 10000:
    # Store in session
    store_in_session(session_id, "diagram_code", diagram_code)

    # Send reference via SSE
    yield {"data": json.dumps({
        "type": "code_ready",
        "code_url": f"/api/v1/diagram/{session_id}/code"
    })}
```

---

## Security Considerations

### 1. Session Validation

**Always validate session_id:**
```python
@router.get("/stream/{session_id}")
async def stream_updates(session_id: str):
    # Validate session exists and belongs to user
    if not is_valid_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
```

### 2. Rate Limiting

**Prevent abuse:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.get("/stream/{session_id}")
@limiter.limit("5/minute")  # Max 5 connections per minute
async def stream_updates(session_id: str):
    ...
```

### 3. CORS Configuration

**Allow SSE from frontend:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

---

## Related Documents

- **Architecture:** [ARCHITECTURE_CANONICAL.md](./ARCHITECTURE_CANONICAL.md)
- **Testing:** [TESTING_CANONICAL.md](./TESTING_CANONICAL.md)
- **API Reference:** [DIAGRAMWIZARD_COMPLETE.md](./DIAGRAMWIZARD_COMPLETE.md) - API section
- **Implementation:** [DIAGRAMWIZARD_ENHANCEMENT_PLAN.md](./DIAGRAMWIZARD_ENHANCEMENT_PLAN.md) - Phase 1

---

**Note:** This is a canonical reference. When SSE implementation changes, update THIS document first, then update references in other documents.
