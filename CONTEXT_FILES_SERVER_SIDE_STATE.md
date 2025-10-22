# Context Files - Server-Side State Implementation

## Summary

Implemented **Option 3: Server-side state for context files**. The backend conversation session is now the single source of truth for which files are in context.

## Changes Made

### 1. Backend API Endpoint

**File**: `backend/app/api/v1/endpoints/chat.py` (Lines 801-828)

Added new endpoint: `GET /chat/conversations/{conversation_id}/files`

Returns:
```json
{
  "success": true,
  "conversationId": "conv-1",
  "files": ["path/to/file1.py", "path/to/file2.py"],
  "count": 2
}
```

### 2. Frontend API Service

**File**: `frontend/src/services/api.ts` (Lines 240-253)

Added method: `ApiService.getConversationFiles(conversationId)`

### 3. Frontend State Management

**File**: `frontend/src/App.tsx`

#### Removed localStorage Persistence (Lines 150-152)
- **Before**: Context files saved to `localStorage.getItem('whysper_context_files')`
- **After**: Simple state `const [selectedFiles, setSelectedFiles] = useState<FileItem[]>([])`
- **Reason**: Backend session is the source of truth

#### Added loadConversationFiles Function (Lines 246-272)
```typescript
const loadConversationFiles = useCallback(async (conversationId: string) => {
  const response = await ApiService.getConversationFiles(conversationId);
  // Convert file paths to FileItem objects and update state
  setSelectedFiles(fileItems);
}, []);
```

#### Load Files on Tab Change (Lines 659-667)
```typescript
const handleTabChange = (tabId: string) => {
  setActiveTabId(tabId);

  // Load context files from backend session
  const tab = tabs.find(t => t.id === tabId);
  if (tab && tab.type === 'chat' && tab.conversationId) {
    loadConversationFiles(tab.conversationId);
  }
};
```

#### Load Files on App Initialization (Line 331)
```typescript
const initializeApp = async () => {
  await loadSettings();
  await loadAgentPrompts();
  await loadSubagentCommands();
  await loadConversationFiles(initialConversation.id); // NEW
};
```

## How It Works Now

### 1. User Selects Files
1. User clicks "Set Context" → Opens ContextModal
2. User selects files → Clicks "Apply"
3. Frontend state `selectedFiles` is updated
4. Footer shows file count immediately

### 2. User Sends First Message
1. Frontend sends selected file paths in request: `contextFiles: selectedFiles.map(f => f.path)`
2. Backend receives file paths
3. Backend adds files to conversation session: `session.add_file(file_path)`
4. Backend session persists files in `session.selected_files`
5. Backend reads actual file content from disk
6. AI receives file content in context

### 3. User Sends Second Message
1. Frontend still has files in state
2. Files sent again (backend ignores duplicates)
3. OR backend already has them in session memory

### 4. User Refreshes Page (F5)
1. Frontend state cleared: `selectedFiles = []`
2. App initializes with conversation `conv-1`
3. **NEW**: Frontend calls `loadConversationFiles('conv-1')`
4. Backend returns files from session: `session.selected_files`
5. Frontend state restored from backend
6. Footer shows correct file count again! ✅

### 5. User Switches Tabs
1. User clicks different chat tab
2. `handleTabChange()` called
3. **NEW**: Frontend calls `loadConversationFiles(newConversationId)`
4. Files loaded from that conversation's session
5. Footer updates to show files for active conversation

## Benefits

1. **Single Source of Truth**: Backend session is authoritative
2. **Survives Page Refresh**: Files not lost on F5
3. **Per-Conversation Context**: Each conversation has its own file context
4. **No localStorage Pollution**: Cleaner, more predictable state
5. **Server-Side Validation**: Backend controls what files are accessible

## Testing

1. ✅ Select files in ContextModal
2. ✅ Footer shows count immediately
3. ✅ Send message - files sent to backend
4. ✅ Backend logs show files received
5. ✅ Press F5 to refresh page
6. ✅ Footer still shows correct count (loaded from backend)
7. ✅ Create new tab - footer shows 0 (different conversation)
8. ✅ Switch back to first tab - footer shows count again

## Migration Notes

- Old localStorage data is no longer used
- Existing sessions will have empty file context until files are re-selected
- No breaking changes to API contracts
