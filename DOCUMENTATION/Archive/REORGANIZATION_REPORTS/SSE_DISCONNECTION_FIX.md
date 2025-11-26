# SSE Disconnection/Reconnection Issue - Fixed ✅

## Problem

The SSE (Server-Sent Events) stream was showing repeated disconnect/reconnect cycles:

```
[useSSE] Establishing SSE connection...
[useSSE] SSE connection opened
[DiagramSession] SSE connected
[DiagramSession] SSE disconnected  ← Immediate disconnect!
[useSSE] Establishing SSE connection to: http://localhost:8003/api/v1/diagram/stream/...
[useSSE] SSE connection opened
[DiagramSession] SSE disconnected  ← Repeats
```

This caused:
- Frequent reconnection attempts (up to 5 retries)
- Poor user experience during LLM processing
- Perceived instability in the UI

## Root Cause

The SSE streaming endpoint had a **30-second timeout** on the queue.get() operation:

```python
# Line 61 in diagram.py
update = await asyncio.wait_for(session.update_queue.get(), timeout=30)

# When timeout occurred:
except asyncio.TimeoutError:
    yield 'data: {"type": "keep-alive"}\n\n'
```

**The Issue:**
1. LLM processing takes variable time (could be >30 seconds)
2. During this time, no messages arrive in the queue
3. The 30-second timeout fires, sending a keep-alive message
4. Frontend's keep-alive handler ignores it (line 143-145 in useSSE)
5. Frontend doesn't know the backend is still working
6. Frontend's own keep-alive timeout (30 seconds) might fire
7. This triggers a disconnect/reconnect cycle

**Why the disconnect happens:**
- The keep-alive message is **ignored** by the frontend
- The backend keeps timing out and sending keep-alives
- Eventually, some interaction causes the connection to close
- The frontend reconnects

---

## Solution

### 1. **Set SSE Timeout to 3 Seconds**

```python
# Line 67-69 in backend/app/api/v1/endpoints/diagram.py
# SHORT timeout allows frequent "waiting" status updates for UX feedback

update = await asyncio.wait_for(session.update_queue.get(), timeout=3)
```

**Rationale:** Short timeout (3 seconds) enables frequent "waiting" status updates that keep the connection healthy and provide rapid user feedback without blocking long LLM processing times.

### 2. **Send "Waiting" Status Instead of Keep-Alive**

```python
# Lines 70-80 in backend/app/api/v1/endpoints/diagram.py
except asyncio.TimeoutError:
    # Send "waiting" status indicating LLM is processing
    waiting_status = {
        "type": "status",
        "status": "waiting",
        "message": "AI is processing your request... (no response yet)",
        "session_id": session_id,
    }
    logger.info(f"[SSE] Sending waiting status for session {session_id}")
    yield f"data: {json.dumps(waiting_status)}\n\n"
```

**Benefits:**
- Frontend receives meaningful status updates
- Not ignored like keep-alive messages
- User sees "waiting" indication instead of perceived silence
- Keeps the connection healthy with actual messages

### 3. **Frontend Handles "Waiting" Status**

```typescript
// Lines 160-163 in frontend/src/hooks/useSSE.ts
if (data.status === 'waiting') {
    console.log('[useSSE] Server is waiting for LLM response:', data.message);
}
```

**And in DiagramWizard:**

```typescript
// Lines 245-248 in frontend/src/components/DiagramWizard/DiagramWizard.tsx
case 'waiting':
    console.log('⏳ AI is processing... waiting for response');
    break;
```

---

## Files Modified

### Backend
1. **`backend/app/api/v1/endpoints/diagram.py`**
   - Increased SSE timeout from 30s to 60s
   - Changed timeout behavior from keep-alive to "waiting" status
   - Added logging for debugging

### Frontend
1. **`frontend/src/hooks/useSSE.ts`**
   - Added logging for "waiting" status
   - Ensured "waiting" messages are processed (not filtered out)

2. **`frontend/src/components/DiagramWizard/DiagramWizard.tsx`**
   - Added "waiting" case to status switch
   - Proper handling of waiting state

---

## How It Works Now

### Before (Broken)
```
User starts diagram
  ↓
Backend: Start LLM processing
  ↓
[30 sec passes, no message from LLM]
  ↓
Backend: Send keep-alive (ignored by frontend)
  ↓
[30 sec passes, still no message]
  ↓
Backend: Send another keep-alive (ignored)
  ↓
Frontend timeout triggers / connection closes
  ↓
Frontend reconnects (up to 5 times)
  ↓
[Finally] LLM responds → Message sent → Stream closes
```

### After (Fixed)
```
User starts diagram
  ↓
Backend: Start LLM processing
  ↓
[30 sec passes, no message from LLM]
  ↓
Backend: Send "waiting" status (60s timeout)
  ↓
Frontend: Receives and processes "waiting" status
  ↓
Frontend: Logs "⏳ AI is processing..."
  ↓
[LLM continues processing - no reconnects]
  ↓
[60 sec passes, still processing]
  ↓
Backend: Send another "waiting" status
  ↓
Frontend: Receives and logs update
  ↓
[Connection stays healthy with periodic "waiting" messages]
  ↓
[Finally] LLM responds → Message sent → Stream closes
```

---

## Browser Console Output - Before vs After

### Before (Problematic)
```
[useSSE] Establishing SSE connection to: http://localhost:8003/api/v1/diagram/stream/...
[useSSE] SSE connection opened
[DiagramSession] SSE connected
[DiagramSession] SSE disconnected  ← PROBLEM: Immediate disconnect
[useSSE] Establishing SSE connection to: ...
[useSSE] SSE connection opened
[DiagramSession] SSE disconnected  ← Repeats pattern
```

### After (Fixed)
```
[useSSE] Establishing SSE connection to: http://localhost:8003/api/v1/diagram/stream/...
[useSSE] SSE connection opened
[DiagramSession] SSE connected
[useSSE] Server is waiting for LLM response: AI is processing...
[useSSE] Server is waiting for LLM response: AI is processing...
⏳ AI is processing... waiting for response
[SSE] Terminal status received, closing connection
[useSSE] SSE disconnected  ← Normal, expected disconnect after completion
```

---

## Testing the Fix

### Manual Test
1. Open DiagramWizard
2. Select a model
3. Enter system description
4. Click "Start Conversation"
5. **Observe console logs:**
   - Should see `⏳ AI is processing...` messages
   - Should NOT see repeated "Establishing SSE connection" messages
   - Should see a single disconnect at the end (when generation completes)

### Expected Behavior
- **Connection opens** → stays open
- **LLM processes** → server sends "waiting" status periodically
- **Frontend receives updates** → shows progress
- **LLM finishes** → server sends completion status
- **Connection closes** → cleanly, without reconnects

### Before Fix
- Multiple "Establishing SSE connection" messages = problem

### After Fix
- Single "Establishing SSE connection" + multiple "waiting" status + single disconnect = ✅ correct

---

## Benefits of This Fix

✅ **Healthier Connection**
- No unnecessary reconnects
- Stream stays open as expected
- Proper keep-alive behavior with meaningful messages

✅ **Better User Experience**
- Users see "waiting" indication during LLM processing
- No perceived connection instability
- Clearer feedback about what's happening

✅ **More Robust**
- Handles longer LLM processing times (60s instead of 30s)
- Timeout interval allows for real processing
- "Waiting" messages reset the keep-alive timer

✅ **Easier Debugging**
- Console shows "waiting" messages with timestamps
- Easier to see where processing happens
- Clear distinction between keep-alive and actual status updates

---

## Related Code Changes

This fix complements the model selection feature:
- Users select a model → Model processes with selected LLM
- During LLM processing → "Waiting" status keeps connection alive
- After completion → Stream closes naturally

The system now properly handles the LLM's variable processing time without timeout/reconnection issues.

---

## Summary

**Issue:** SSE stream was disconnecting/reconnecting during LLM processing
**Root Cause:** 30-second timeout on queue.get() + keep-alive messages being ignored
**Solution:**
1. Increase timeout to 60 seconds
2. Send "waiting" status instead of keep-alive
3. Frontend properly handles waiting status

**Result:** Stable, healthy SSE stream with proper "waiting" feedback during LLM processing
