# DiagramWizard Enhancement Implementation Plan

**Version:** 1.0
**Date:** 2025-11-15
**Objective:** Enhance DiagramWizard with key features from ArchitectureGenStudio while maintaining its conversational workflow strength

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1: Foundation (Week 1-2)](#phase-1-foundation-week-1-2)
3. [Phase 2: User Experience (Week 3-4)](#phase-2-user-experience-week-3-4)
4. [Phase 3: Quality & Accessibility (Week 5-6)](#phase-3-quality--accessibility-week-5-6)
5. [Phase 4: Advanced Features (Optional)](#phase-4-advanced-features-optional)
6. [Testing Strategy](#testing-strategy)
7. [Rollback Plan](#rollback-plan)
8. [Success Metrics](#success-metrics)

---

## Executive Summary

### Goals
- Enhance DiagramWizard's robustness without compromising its conversational UX
- Integrate proven ArchitectureGenStudio infrastructure
- Improve user retention through state persistence
- Expand export capabilities and accessibility

### Key Principles
1. **Preserve Core Strength:** Keep LangGraph conversational workflow intact
2. **Incremental Migration:** Phase-based approach with rollback points
3. **Backward Compatibility:** Maintain existing API contracts
4. **Test Coverage:** Add comprehensive tests for each enhancement

### Timeline Overview
- **Phase 1:** 2 weeks (Foundation)
- **Phase 2:** 2 weeks (User Experience)
- **Phase 3:** 2 weeks (Quality & Accessibility)
- **Phase 4:** 4 weeks (Advanced Features - Optional)

**Total:** 6-10 weeks depending on scope

---

## Phase 1: Foundation (Week 1-2)

**Objective:** Establish infrastructure foundations for all future enhancements

### 1.1 Extract and Integrate Robust SSE Hook

**Priority:** CRITICAL
**Effort:** 3 days
**Risk:** MEDIUM

#### Current State Analysis

**DiagramWizard SSE Implementation:**
```typescript
// frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts:31-80
// Bespoke inline handling, no reconnection logic
useEffect(() => {
  if (!sessionId) return;

  const eventSource = new EventSource(`${API_URL}/diagram/stream/${sessionId}`);

  eventSource.onmessage = (event) => {
    const update = JSON.parse(event.data);
    handleUpdate(update);
  };

  eventSource.onerror = () => {
    eventSource.close();
  };

  return () => eventSource.close();
}, [sessionId]);
```

**ArchStudio SSE Implementation:**
```typescript
// frontend/src/components/architectureGenStudio/hooks/useSSE.ts:34-147
// Resilient with reconnection, backoff, keep-alive
export const useSSE = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);

  // Exponential backoff, max 30s
  // Keep-alive message handling
  // Auto-cleanup on unmount
};
```

#### Implementation Steps

**Step 1.1.1: Create Shared SSE Hook**

**File:** `frontend/src/hooks/useSSE.ts` (NEW)

```typescript
/**
 * Robust SSE Hook
 * Extracted from ArchitectureGenStudio with enhancements for DiagramWizard
 */

import { useState, useEffect, useRef, useCallback } from 'react';

export interface SSEMessage {
  id: string;
  type: string;
  data: any;
  timestamp: number;
  isRead: boolean;
}

export interface UseSSEOptions {
  url: string;
  enabled?: boolean;
  onMessage?: (message: SSEMessage) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  maxReconnectAttempts?: number;
  reconnectInterval?: number;
  keepAliveTimeout?: number;
}

export const useSSE = ({
  url,
  enabled = true,
  onMessage,
  onError,
  onConnect,
  onDisconnect,
  maxReconnectAttempts = 5,
  reconnectInterval = 1000,
  keepAliveTimeout = 30000,
}: UseSSEOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [error, setError] = useState<Error | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const keepAliveTimerRef = useRef<NodeJS.Timeout | null>(null);

  const clearKeepAliveTimer = useCallback(() => {
    if (keepAliveTimerRef.current) {
      clearTimeout(keepAliveTimerRef.current);
      keepAliveTimerRef.current = null;
    }
  }, []);

  const resetKeepAliveTimer = useCallback(() => {
    clearKeepAliveTimer();
    keepAliveTimerRef.current = setTimeout(() => {
      console.warn('SSE keep-alive timeout - no messages received');
      disconnect();
    }, keepAliveTimeout);
  }, [keepAliveTimeout]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    clearKeepAliveTimer();
    setIsConnected(false);
    onDisconnect?.();
  }, [onDisconnect, clearKeepAliveTimer]);

  const connect = useCallback(() => {
    if (!enabled || !url) return;

    // Close existing connection
    disconnect();

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection established:', url);
        setIsConnected(true);
        setError(null);
        reconnectAttempts.current = 0;
        resetKeepAliveTimer();
        onConnect?.();
      };

      eventSource.onmessage = (event) => {
        resetKeepAliveTimer();

        try {
          const data = JSON.parse(event.data);

          // Handle keep-alive messages
          if (data.type === 'keep-alive' || data.type === 'ping') {
            console.log('SSE keep-alive received');
            return;
          }

          const message: SSEMessage = {
            id: data.id || `msg-${Date.now()}`,
            type: data.type || 'message',
            data: data,
            timestamp: Date.now(),
            isRead: false,
          };

          setMessages((prev) => [...prev, message]);
          onMessage?.(message);
        } catch (err) {
          console.error('Error parsing SSE message:', err);
        }
      };

      eventSource.onerror = (event) => {
        console.error('SSE error:', event);

        const error = new Error('SSE connection error');
        setError(error);
        onError?.(error);

        eventSource.close();
        setIsConnected(false);
        clearKeepAliveTimer();

        // Attempt reconnection with exponential backoff
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = reconnectInterval * Math.pow(2, reconnectAttempts.current);
          console.log(`Attempting reconnect in ${delay}ms (attempt ${reconnectAttempts.current + 1}/${maxReconnectAttempts})`);

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        } else {
          console.error('Max reconnection attempts reached');
          onDisconnect?.();
        }
      };
    } catch (err) {
      console.error('Error creating SSE connection:', err);
      setError(err as Error);
      onError?.(err as Error);
    }
  }, [url, enabled, onMessage, onError, onConnect, onDisconnect, maxReconnectAttempts, reconnectInterval, resetKeepAliveTimer, disconnect]);

  useEffect(() => {
    if (enabled && url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url, enabled, connect, disconnect]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const markAsRead = useCallback((messageId: string) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, isRead: true } : msg
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setMessages((prev) => prev.map((msg) => ({ ...msg, isRead: true })));
  }, []);

  return {
    isConnected,
    messages,
    error,
    connect,
    disconnect,
    clearMessages,
    markAsRead,
    markAllAsRead,
  };
};
```

**Step 1.1.2: Update DiagramWizard to Use New SSE Hook**

**File:** `frontend/src/components/DiagramWizard/hooks/useDiagramSession.ts`

```typescript
import { useSSE } from '../../../hooks/useSSE';

export const useDiagramSession = ({ onUpdate, onError }: UseDiagramSessionProps) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<DiagramSessionStatus | null>(null);

  // Replace custom SSE logic with robust hook
  const {
    isConnected: sseConnected,
    messages: sseMessages,
    error: sseError,
    connect: connectSSE,
    disconnect: disconnectSSE,
    clearMessages: clearSSEMessages,
  } = useSSE({
    url: sessionId ? `${API_URL}/diagram/stream/${sessionId}` : '',
    enabled: !!sessionId,
    onMessage: (message) => {
      // Transform SSE message to DiagramUpdate
      const update = message.data as DiagramUpdate;
      onUpdate?.(update);

      // Update local status
      setStatus((prev) => ({
        ...prev,
        ...update,
      }));
    },
    onError: (error) => {
      console.error('SSE error in DiagramWizard:', error);
      onError?.(error);
    },
    onDisconnect: () => {
      console.log('SSE disconnected for session:', sessionId);
    },
    maxReconnectAttempts: 5,
    reconnectInterval: 2000,
    keepAliveTimeout: 30000,
  });

  // Rest of the hook implementation...
};
```

**Step 1.1.3: Add SSE Status Indicator to UI**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
// Add connection status to header
<Layout.Header className={styles.header}>
  <div className={styles.headerContent}>
    <h2 className={styles.title}>Diagram Wizard</h2>

    {sessionId && (
      <Space>
        <span className={styles.sessionId}>Session: {sessionId.substring(0, 8)}...</span>

        {/* SSE Connection Status */}
        <Badge
          status={sseConnected ? 'success' : 'error'}
          text={sseConnected ? 'Connected' : 'Disconnected'}
        />

        {status?.isRunning && <Spin size="small" />}
      </Space>
    )}
  </div>
</Layout.Header>
```

**Testing Checklist:**
- [ ] SSE reconnects after network interruption
- [ ] Exponential backoff works correctly
- [ ] Keep-alive messages prevent timeout
- [ ] Error messages display properly
- [ ] Connection status indicator updates
- [ ] Old sessions cleanup properly
- [ ] No memory leaks on repeated connect/disconnect

---

### 1.2 Add localStorage Persistence

**Priority:** HIGH
**Effort:** 4 days
**Risk:** LOW

#### Implementation Steps

**Step 1.2.1: Create localStorage Hook**

**File:** `frontend/src/hooks/useLocalStorage.ts` (NEW - adapted from ArchStudio)

```typescript
/**
 * localStorage Hook
 * Adapted from ArchitectureGenStudio
 */

import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  // State to store our value
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error loading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Return a wrapped version of useState's setter function that persists to localStorage
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        // Allow value to be a function (same API as useState)
        const valueToStore = value instanceof Function ? value(storedValue) : value;

        // Save state
        setStoredValue(valueToStore);

        // Save to localStorage
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.error(`Error saving localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Listen for changes in other tabs/windows
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.error(`Error parsing storage event for key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  const removeValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue] as const;
}
```

**Step 1.2.2: Define Persistence Schema**

**File:** `frontend/src/components/DiagramWizard/types/persistence.ts` (NEW)

```typescript
/**
 * DiagramWizard Persistence Types
 */

export interface DiagramWizardPreferences {
  defaultDiagramType: 'Mermaid' | 'D2' | 'PlantUML' | 'auto';
  autoSave: boolean;
  keepSessionHistory: boolean;
  maxHistoryItems: number;
  theme: 'light' | 'dark' | 'auto';
  showScoreInfo: boolean;
}

export interface SavedSession {
  sessionId: string;
  timestamp: number;
  initialPrompt: string;
  diagramType: string;
  diagramCode: string;
  svgOutput: string;
  conversationHistory: Array<[string, string]>;
  score: number;
  scoreInfo?: any;
}

export interface DiagramWizardPersistedState {
  preferences: DiagramWizardPreferences;
  sessionHistory: SavedSession[];
  lastSession?: SavedSession;
  stats: {
    totalSessions: number;
    successfulGenerations: number;
    lastUsed: number;
  };
}

export const DEFAULT_PREFERENCES: DiagramWizardPreferences = {
  defaultDiagramType: 'auto',
  autoSave: true,
  keepSessionHistory: true,
  maxHistoryItems: 10,
  theme: 'auto',
  showScoreInfo: true,
};
```

**Step 1.2.3: Integrate Persistence into DiagramWizard**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
import { useLocalStorage } from '../../hooks/useLocalStorage';
import {
  DiagramWizardPersistedState,
  DEFAULT_PREFERENCES,
  SavedSession
} from './types/persistence';

export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
}) => {
  // Persistent state
  const [persistedState, setPersistedState, clearPersistedState] = useLocalStorage<DiagramWizardPersistedState>(
    'diagramWizard.state',
    {
      preferences: DEFAULT_PREFERENCES,
      sessionHistory: [],
      stats: {
        totalSessions: 0,
        successfulGenerations: 0,
        lastUsed: Date.now(),
      },
    }
  );

  // Initialize with persisted preferences
  const [diagramType, setDiagramType] = useState<DiagramType>(
    persistedState.preferences.defaultDiagramType as DiagramType
  );

  // Save session to history when completed
  const saveSessionToHistory = useCallback((session: SavedSession) => {
    if (!persistedState.preferences.keepSessionHistory) return;

    setPersistedState((prev) => {
      const newHistory = [session, ...prev.sessionHistory].slice(
        0,
        prev.preferences.maxHistoryItems
      );

      return {
        ...prev,
        sessionHistory: newHistory,
        lastSession: session,
        stats: {
          ...prev.stats,
          totalSessions: prev.stats.totalSessions + 1,
          successfulGenerations: prev.stats.successfulGenerations + 1,
          lastUsed: Date.now(),
        },
      };
    });
  }, [persistedState.preferences, setPersistedState]);

  // Auto-save when diagram is completed
  useEffect(() => {
    if (status?.status === 'completed' && sessionId && persistedState.preferences.autoSave) {
      const savedSession: SavedSession = {
        sessionId,
        timestamp: Date.now(),
        initialPrompt: userInput,
        diagramType: diagramType,
        diagramCode: status.diagramCode || '',
        svgOutput: status.svgOutput || '',
        conversationHistory: status.history || [],
        score: score,
        scoreInfo: status.score_info,
      };

      saveSessionToHistory(savedSession);
      message.success('Session saved to history');
    }
  }, [status?.status, sessionId, persistedState.preferences.autoSave]);

  // Add "Load Previous Session" feature
  const handleLoadSession = (savedSession: SavedSession) => {
    setUserInput(savedSession.initialPrompt);
    setDiagramType(savedSession.diagramType as DiagramType);
    message.info('Previous session loaded');
  };

  // Render session history in UI (add to existing UI)
  const renderSessionHistory = () => {
    if (persistedState.sessionHistory.length === 0) return null;

    return (
      <div className={styles.sessionHistory}>
        <h4>Recent Sessions</h4>
        <List
          size="small"
          dataSource={persistedState.sessionHistory.slice(0, 5)}
          renderItem={(session) => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  size="small"
                  onClick={() => handleLoadSession(session)}
                >
                  Load
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={session.diagramType}
                description={`${session.initialPrompt.substring(0, 50)}... (${new Date(session.timestamp).toLocaleDateString()})`}
              />
            </List.Item>
          )}
        />
      </div>
    );
  };
};
```

**Step 1.2.4: Add Settings Panel**

**File:** `frontend/src/components/DiagramWizard/components/SettingsPanel.tsx` (NEW)

```typescript
import React from 'react';
import { Modal, Form, Switch, Select, InputNumber } from 'antd';
import { DiagramWizardPreferences } from '../types/persistence';

interface SettingsPanelProps {
  visible: boolean;
  preferences: DiagramWizardPreferences;
  onSave: (preferences: DiagramWizardPreferences) => void;
  onCancel: () => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  visible,
  preferences,
  onSave,
  onCancel,
}) => {
  const [form] = Form.useForm();

  const handleSave = () => {
    form.validateFields().then((values) => {
      onSave(values as DiagramWizardPreferences);
    });
  };

  return (
    <Modal
      title="DiagramWizard Settings"
      open={visible}
      onOk={handleSave}
      onCancel={onCancel}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={preferences}
      >
        <Form.Item
          name="defaultDiagramType"
          label="Default Diagram Type"
          tooltip="Diagram type to use by default"
        >
          <Select>
            <Select.Option value="auto">Auto (AI Decides)</Select.Option>
            <Select.Option value="Mermaid">Mermaid</Select.Option>
            <Select.Option value="D2">D2</Select.Option>
            <Select.Option value="PlantUML">PlantUML</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="autoSave"
          label="Auto-Save Sessions"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          name="keepSessionHistory"
          label="Keep Session History"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>

        <Form.Item
          name="maxHistoryItems"
          label="Max History Items"
          tooltip="Maximum number of sessions to keep in history"
        >
          <InputNumber min={1} max={50} />
        </Form.Item>

        <Form.Item
          name="showScoreInfo"
          label="Show Information Scoring"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  );
};
```

**Testing Checklist:**
- [ ] Preferences persist across page refreshes
- [ ] Session history saves correctly
- [ ] Load previous session works
- [ ] Settings panel updates preferences
- [ ] Auto-save triggers on completion
- [ ] localStorage quota not exceeded
- [ ] Cross-tab synchronization works
- [ ] Migration from no localStorage works

---

### 1.3 Wire to `/diagrams/v2/*` Provider System

**Priority:** CRITICAL
**Effort:** 5 days
**Risk:** HIGH

#### Current Backend Flow

```
DiagramWizard → /diagram/start → DiagramFactoryService
  → LangGraph workflow → Custom rendering logic
```

#### Target Backend Flow

```
DiagramWizard → /diagram/start → DiagramFactoryService
  → LangGraph workflow (clarification only)
  → /diagrams/v2/render (provider system)
```

#### Implementation Steps

**Step 1.3.1: Update Backend - DiagramFactoryService**

**File:** `backend/app/services/diagram_factory_service.py`

```python
from diagrams.provider_registry import ProviderRegistry
from app.api.v1.endpoints.diagram_provider import render_diagram_internal

class DiagramFactoryService:
    """
    Updated to use provider system for rendering
    Keep LangGraph for clarification workflow
    """

    def __init__(self):
        self.session_store = DiagramSessionStore()
        self.provider_registry = ProviderRegistry.get_instance()

    async def render_diagram(
        self,
        session_id: str,
        code: str,
        diagram_type: str
    ) -> RenderResult:
        """
        Use provider system instead of custom rendering
        """
        session = self.session_store.get_session(session_id)

        try:
            # Use the unified provider system
            result = await render_diagram_internal(
                code=code,
                diagram_type=diagram_type,
                auto_fix=True,  # Enable pattern-based fixes
                llm_correction=True,  # Enable LLM-based corrections
                save_to_file=True,  # Save to static directory
                output_format="svg",
                max_retries=3,
                session_id=session_id,  # For logging
            )

            # Update session state
            session.svg_output = result.svg
            session.diagram_code = result.code  # May be corrected

            # Push update via SSE
            await self._push_update(session_id, {
                "status": "completed",
                "svg_output": result.svg,
                "diagram_code": result.code,
                "provider_used": result.metadata.get("provider_id"),
                "corrections_applied": result.metadata.get("corrections_applied", []),
            })

            return result

        except Exception as e:
            logger.info(f"Rendering failed for session {session_id}: {e}")
            await self._push_update(session_id, {
                "status": "error",
                "message": f"Rendering failed: {str(e)}",
            })
            raise
```

**Step 1.3.2: Add Provider Metadata to SSE Updates**

**File:** `backend/app/utils/diagram_wizard/nodes.py`

Update the `render_diagram` node:

```python
async def render_diagram(state: GraphState) -> GraphState:
    """
    Render diagram using provider system
    Enhanced with metadata
    """
    session_id = state.get("session_id")
    diagram_code = state.get("diagram_code")
    diagram_type = state.get("diagram_type")

    logger.info(f"[{session_id}] Rendering diagram with provider system")

    try:
        # Use provider registry
        provider_registry = ProviderRegistry.get_instance()

        result = await provider_registry.render_with_validation(
            code=diagram_code,
            diagram_type=diagram_type.value,
            auto_fix=True,
            llm_correction=True,
            output_format="svg",
        )

        # Update state with provider metadata
        return {
            **state,
            "svg_output": result.svg,
            "diagram_code": result.code,  # May be corrected
            "is_valid": True,
            "current_state": SessionState.READY,
            "provider_metadata": {
                "provider_id": result.metadata.get("provider_id"),
                "corrections_applied": result.metadata.get("corrections_applied", []),
                "validation_passed": result.metadata.get("validation_passed", True),
            },
        }

    except Exception as e:
        logger.info(f"[{session_id}] Rendering failed: {e}")
        return {
            **state,
            "validation_error": str(e),
            "current_state": SessionState.ERROR,
        }
```

**Step 1.3.3: Update Frontend to Display Provider Info**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
// Show provider metadata when diagram is generated
{status?.provider_metadata && (
  <Alert
    type="info"
    message="Diagram Generated"
    description={
      <div>
        <p>Provider: {status.provider_metadata.provider_id}</p>
        {status.provider_metadata.corrections_applied.length > 0 && (
          <p>Auto-corrections applied: {status.provider_metadata.corrections_applied.join(', ')}</p>
        )}
      </div>
    }
    closable
  />
)}
```

**Step 1.3.4: Add Provider Health Check**

**File:** `frontend/src/services/diagram/diagramApi.ts`

```typescript
/**
 * Check provider system health
 */
export const checkProviderHealth = async (): Promise<ProviderHealthResponse> => {
  const response = await fetch(`${API_URL}/diagrams/v2/health`);

  if (!response.ok) {
    throw new Error('Provider health check failed');
  }

  return response.json();
};

// Call on component mount to verify provider availability
useEffect(() => {
  checkProviderHealth().then((health) => {
    console.log('Available providers:', health.providers);
  }).catch((error) => {
    message.warning('Some diagram providers are unavailable');
  });
}, []);
```

**Step 1.3.5: Backend API Endpoint Update**

**File:** `backend/app/api/v1/endpoints/diagram_provider.py`

Add internal helper for DiagramWizard:

```python
async def render_diagram_internal(
    code: str,
    diagram_type: str,
    auto_fix: bool = True,
    llm_correction: bool = True,
    save_to_file: bool = False,
    output_format: str = "svg",
    max_retries: int = 3,
    session_id: Optional[str] = None,
) -> RenderResult:
    """
    Internal rendering function for use by DiagramFactoryService
    Reuses provider system logic without HTTP overhead
    """
    provider_registry = ProviderRegistry.get_instance()

    # Get provider for diagram type
    provider = provider_registry.get_provider_for_type(diagram_type)

    if not provider:
        raise ValueError(f"No provider available for diagram type: {diagram_type}")

    # Render with validation and auto-correction
    result = await provider.render_with_validation(
        code=code,
        output_format=output_format,
        auto_fix=auto_fix,
        llm_correction=llm_correction,
        max_retries=max_retries,
    )

    # Optionally save to file
    if save_to_file and result.svg:
        file_path = await save_diagram_to_file(
            result.svg,
            diagram_type,
            session_id or "unknown",
        )
        result.metadata["file_path"] = str(file_path)

    # Add session_id to metadata for logging
    if session_id:
        result.metadata["session_id"] = session_id

    return result
```

**Testing Checklist:**
- [ ] DiagramWizard renders via provider system
- [ ] LangGraph clarification workflow unaffected
- [ ] Auto-fix corrections apply correctly
- [ ] LLM corrections work when needed
- [ ] Provider metadata displays in UI
- [ ] Fallback works if provider unavailable
- [ ] All existing diagram types still work
- [ ] Performance not degraded
- [ ] Error messages are clear

---

## Phase 1 Completion Criteria

**Before moving to Phase 2, verify:**

1. **SSE Resilience:**
   - [ ] Reconnection works after network drop
   - [ ] Keep-alive prevents timeouts
   - [ ] Connection status accurate

2. **Persistence:**
   - [ ] Sessions save automatically
   - [ ] Preferences persist
   - [ ] History loads correctly
   - [ ] Cross-tab sync works

3. **Provider Integration:**
   - [ ] All diagram types render via providers
   - [ ] Auto-fix applied when needed
   - [ ] Metadata visible in UI
   - [ ] No regressions in existing functionality

4. **Testing:**
   - [ ] Unit tests pass (90%+ coverage)
   - [ ] Integration tests pass
   - [ ] Manual QA completed
   - [ ] Performance benchmarks met

5. **Documentation:**
   - [ ] API changes documented
   - [ ] User guide updated
   - [ ] Migration guide created

**Phase 1 Deliverables:**
- ✅ Robust SSE implementation
- ✅ Full state persistence
- ✅ Provider system integration
- ✅ Test coverage > 90%
- ✅ Documentation complete

---

## Phase 2: User Experience (Week 3-4)

**Objective:** Enhance user-facing features for better usability and export capabilities

### 2.1 Zoom Controls for Preview Panel

**Priority:** HIGH
**Effort:** 3 days
**Risk:** LOW

#### Implementation Steps

**Step 2.1.1: Create ZoomControls Component**

**File:** `frontend/src/components/DiagramWizard/components/ZoomControls.tsx` (NEW)

```typescript
/**
 * Zoom Controls Component
 * Adapted from ArchitectureGenStudio
 */

import React from 'react';
import { Button, Space, Tooltip, Slider } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  ExpandOutlined,
  OneToOneOutlined,
} from '@ant-design/icons';
import styles from './ZoomControls.module.css';

interface ZoomControlsProps {
  zoomLevel: number;
  onZoomChange: (level: number) => void;
  onFitToScreen: () => void;
  onReset: () => void;
  min?: number;
  max?: number;
  step?: number;
}

export const ZoomControls: React.FC<ZoomControlsProps> = ({
  zoomLevel,
  onZoomChange,
  onFitToScreen,
  onReset,
  min = 25,
  max = 400,
  step = 25,
}) => {
  const handleZoomIn = () => {
    onZoomChange(Math.min(zoomLevel + step, max));
  };

  const handleZoomOut = () => {
    onZoomChange(Math.max(zoomLevel - step, min));
  };

  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case '+':
          case '=':
            e.preventDefault();
            handleZoomIn();
            break;
          case '-':
          case '_':
            e.preventDefault();
            handleZoomOut();
            break;
          case '0':
            e.preventDefault();
            onReset();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [zoomLevel, onReset]);

  return (
    <div className={styles.zoomControls}>
      <Space size="small">
        <Tooltip title="Zoom Out (Ctrl/Cmd + -)">
          <Button
            icon={<ZoomOutOutlined />}
            onClick={handleZoomOut}
            disabled={zoomLevel <= min}
            size="small"
          />
        </Tooltip>

        <Slider
          value={zoomLevel}
          onChange={onZoomChange}
          min={min}
          max={max}
          step={step}
          style={{ width: 100 }}
          tooltip={{ formatter: (val) => `${val}%` }}
        />

        <span className={styles.zoomLevel}>{zoomLevel}%</span>

        <Tooltip title="Zoom In (Ctrl/Cmd + +)">
          <Button
            icon={<ZoomInOutlined />}
            onClick={handleZoomIn}
            disabled={zoomLevel >= max}
            size="small"
          />
        </Tooltip>

        <Tooltip title="Fit to Screen">
          <Button
            icon={<ExpandOutlined />}
            onClick={onFitToScreen}
            size="small"
          />
        </Tooltip>

        <Tooltip title="Reset (100%) - Ctrl/Cmd + 0">
          <Button
            icon={<OneToOneOutlined />}
            onClick={onReset}
            size="small"
          />
        </Tooltip>
      </Space>
    </div>
  );
};
```

**Step 2.1.2: Update PreviewPanel with Zoom**

**File:** `frontend/src/components/DiagramWizard/panels/Panel2_Preview.tsx`

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { ZoomControls } from '../components/ZoomControls';

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  svgOutput,
  isLoading,
}) => {
  const [zoomLevel, setZoomLevel] = useState(100);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  // Fit to screen
  const handleFitToScreen = () => {
    if (!containerRef.current || !contentRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const contentRect = contentRef.current.getBoundingClientRect();

    const scaleX = containerRect.width / contentRect.width;
    const scaleY = containerRect.height / contentRect.height;
    const scale = Math.min(scaleX, scaleY, 1) * 100;

    setZoomLevel(Math.floor(scale));
    setPanOffset({ x: 0, y: 0 });
  };

  // Reset zoom
  const handleReset = () => {
    setZoomLevel(100);
    setPanOffset({ x: 0, y: 0 });
  };

  // Mouse wheel zoom
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleWheel = (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault();

        const delta = e.deltaY > 0 ? -10 : 10;
        setZoomLevel((prev) => Math.max(25, Math.min(400, prev + delta)));
      }
    };

    container.addEventListener('wheel', handleWheel, { passive: false });
    return () => container.removeEventListener('wheel', handleWheel);
  }, []);

  // Panning logic
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {  // Left click
      setIsPanning(true);
      e.preventDefault();
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPanOffset((prev) => ({
        x: prev.x + e.movementX,
        y: prev.y + e.movementY,
      }));
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  return (
    <div className={styles.previewPanel}>
      <div className={styles.toolbar}>
        <ZoomControls
          zoomLevel={zoomLevel}
          onZoomChange={setZoomLevel}
          onFitToScreen={handleFitToScreen}
          onReset={handleReset}
        />
      </div>

      <div
        ref={containerRef}
        className={styles.previewContainer}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
      >
        <div
          ref={contentRef}
          className={styles.previewContent}
          style={{
            transform: `scale(${zoomLevel / 100}) translate(${panOffset.x}px, ${panOffset.y}px)`,
            transformOrigin: 'center center',
            transition: isPanning ? 'none' : 'transform 0.2s ease',
          }}
          dangerouslySetInnerHTML={{ __html: svgOutput }}
        />
      </div>

      {isLoading && (
        <div className={styles.loadingOverlay}>
          <Spin size="large" tip="Rendering diagram..." />
        </div>
      )}
    </div>
  );
};
```

**Step 2.1.3: Add CSS**

**File:** `frontend/src/components/DiagramWizard/components/ZoomControls.module.css` (NEW)

```css
.zoomControls {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.zoomLevel {
  min-width: 50px;
  text-align: center;
  font-size: 12px;
  color: #666;
}
```

**Testing Checklist:**
- [ ] Zoom in/out buttons work
- [ ] Slider updates zoom level
- [ ] Keyboard shortcuts work (Ctrl/Cmd +/-)
- [ ] Mouse wheel zoom works
- [ ] Fit to screen calculates correctly
- [ ] Reset returns to 100%
- [ ] Pan with mouse drag works
- [ ] Touch gestures work on mobile

---

### 2.2 Enhanced Export Options

**Priority:** HIGH
**Effort:** 4 days
**Risk:** MEDIUM

#### Implementation Steps

**Step 2.2.1: Install Dependencies**

```bash
npm install jspdf html2canvas
npm install @types/jspdf --save-dev
```

**Step 2.2.2: Create Export Service**

**File:** `frontend/src/services/export/exportService.ts` (NEW)

```typescript
/**
 * Export Service
 * Handles SVG, PNG, and PDF exports
 */

import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export interface ExportOptions {
  filename?: string;
  format: 'svg' | 'png' | 'pdf';
  quality?: number;
  metadata?: {
    title?: string;
    author?: string;
    subject?: string;
    keywords?: string;
  };
}

export class ExportService {
  /**
   * Export SVG
   */
  static exportSVG(svgContent: string, filename: string = 'diagram.svg'): void {
    const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  }

  /**
   * Export PNG
   */
  static async exportPNG(
    svgElement: HTMLElement,
    filename: string = 'diagram.png',
    quality: number = 1.0
  ): Promise<void> {
    try {
      const canvas = await html2canvas(svgElement, {
        backgroundColor: '#ffffff',
        scale: 2, // Higher resolution
        logging: false,
      });

      canvas.toBlob(
        (blob) => {
          if (!blob) {
            throw new Error('Failed to create PNG blob');
          }

          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        },
        'image/png',
        quality
      );
    } catch (error) {
      console.error('PNG export failed:', error);
      throw new Error('Failed to export PNG');
    }
  }

  /**
   * Export PDF
   */
  static async exportPDF(
    svgContent: string,
    options: ExportOptions
  ): Promise<void> {
    try {
      // Create temporary container
      const container = document.createElement('div');
      container.style.position = 'absolute';
      container.style.left = '-9999px';
      container.innerHTML = svgContent;
      document.body.appendChild(container);

      // Get SVG dimensions
      const svgElement = container.querySelector('svg');
      if (!svgElement) {
        throw new Error('No SVG element found');
      }

      const svgWidth = svgElement.viewBox.baseVal.width || svgElement.clientWidth;
      const svgHeight = svgElement.viewBox.baseVal.height || svgElement.clientHeight;

      // Determine PDF orientation
      const orientation = svgWidth > svgHeight ? 'landscape' : 'portrait';

      // Create PDF
      const pdf = new jsPDF({
        orientation,
        unit: 'pt',
        format: [svgWidth + 40, svgHeight + 40], // Add margins
      });

      // Add metadata
      if (options.metadata) {
        pdf.setProperties({
          title: options.metadata.title || 'Diagram',
          author: options.metadata.author || 'DiagramWizard',
          subject: options.metadata.subject || 'Generated Diagram',
          keywords: options.metadata.keywords || 'diagram',
          creator: 'DiagramWizard',
        });
      }

      // Convert SVG to canvas
      const canvas = await html2canvas(container, {
        backgroundColor: '#ffffff',
        scale: 2,
        logging: false,
      });

      // Add image to PDF
      const imgData = canvas.toDataURL('image/png');
      pdf.addImage(imgData, 'PNG', 20, 20, svgWidth, svgHeight);

      // Add footer with metadata
      pdf.setFontSize(8);
      pdf.setTextColor(128, 128, 128);
      pdf.text(
        `Generated by DiagramWizard | ${new Date().toLocaleDateString()}`,
        20,
        svgHeight + 35
      );

      // Save PDF
      pdf.save(options.filename || 'diagram.pdf');

      // Cleanup
      document.body.removeChild(container);
    } catch (error) {
      console.error('PDF export failed:', error);
      throw new Error('Failed to export PDF');
    }
  }

  /**
   * Unified export function
   */
  static async export(
    svgContent: string,
    svgElement: HTMLElement,
    options: ExportOptions
  ): Promise<void> {
    const filename = options.filename || `diagram_${Date.now()}`;

    switch (options.format) {
      case 'svg':
        this.exportSVG(svgContent, `${filename}.svg`);
        break;

      case 'png':
        await this.exportPNG(svgElement, `${filename}.png`, options.quality || 1.0);
        break;

      case 'pdf':
        await this.exportPDF(svgContent, {
          ...options,
          filename: `${filename}.pdf`,
        });
        break;

      default:
        throw new Error(`Unsupported export format: ${options.format}`);
    }
  }
}
```

**Step 2.2.3: Create Export Modal Component**

**File:** `frontend/src/components/DiagramWizard/components/ExportModal.tsx` (NEW)

```typescript
import React, { useState } from 'react';
import { Modal, Form, Input, Select, Slider, Checkbox, message } from 'antd';
import { ExportService, ExportOptions } from '../../../services/export/exportService';

interface ExportModalProps {
  visible: boolean;
  svgContent: string;
  svgElement: HTMLElement | null;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  visible,
  svgContent,
  svgElement,
  onClose,
}) => {
  const [form] = Form.useForm();
  const [exporting, setExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<'svg' | 'png' | 'pdf'>('svg');

  const handleExport = async () => {
    try {
      const values = await form.validateFields();

      if (!svgElement) {
        message.error('No diagram to export');
        return;
      }

      setExporting(true);

      const options: ExportOptions = {
        filename: values.filename,
        format: selectedFormat,
        quality: values.quality / 100,
        metadata: values.includeMetadata ? {
          title: values.title,
          author: values.author,
          subject: values.subject,
          keywords: values.keywords,
        } : undefined,
      };

      await ExportService.export(svgContent, svgElement, options);

      message.success(`Exported as ${selectedFormat.toUpperCase()}`);
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
      message.error('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <Modal
      title="Export Diagram"
      open={visible}
      onOk={handleExport}
      onCancel={onClose}
      confirmLoading={exporting}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          filename: `diagram_${Date.now()}`,
          format: 'svg',
          quality: 100,
          includeMetadata: true,
          title: 'Architecture Diagram',
          author: 'DiagramWizard User',
        }}
      >
        <Form.Item
          name="filename"
          label="Filename"
          rules={[{ required: true, message: 'Please enter a filename' }]}
        >
          <Input placeholder="my-diagram" />
        </Form.Item>

        <Form.Item
          name="format"
          label="Export Format"
          rules={[{ required: true }]}
        >
          <Select onChange={(value) => setSelectedFormat(value as any)}>
            <Select.Option value="svg">SVG (Scalable Vector Graphics)</Select.Option>
            <Select.Option value="png">PNG (Raster Image)</Select.Option>
            <Select.Option value="pdf">PDF (Portable Document)</Select.Option>
          </Select>
        </Form.Item>

        {(selectedFormat === 'png' || selectedFormat === 'pdf') && (
          <Form.Item
            name="quality"
            label="Quality (%)"
            tooltip="Higher quality means larger file size"
          >
            <Slider min={50} max={100} marks={{ 50: '50%', 75: '75%', 100: '100%' }} />
          </Form.Item>
        )}

        {selectedFormat === 'pdf' && (
          <>
            <Form.Item name="includeMetadata" valuePropName="checked">
              <Checkbox>Include metadata in PDF</Checkbox>
            </Form.Item>

            <Form.Item
              noStyle
              shouldUpdate={(prevValues, currentValues) =>
                prevValues.includeMetadata !== currentValues.includeMetadata
              }
            >
              {({ getFieldValue }) =>
                getFieldValue('includeMetadata') ? (
                  <>
                    <Form.Item name="title" label="Title">
                      <Input />
                    </Form.Item>
                    <Form.Item name="author" label="Author">
                      <Input />
                    </Form.Item>
                    <Form.Item name="subject" label="Subject">
                      <Input />
                    </Form.Item>
                    <Form.Item name="keywords" label="Keywords">
                      <Input placeholder="architecture, diagram, system" />
                    </Form.Item>
                  </>
                ) : null
              }
            </Form.Item>
          </>
        )}
      </Form>
    </Modal>
  );
};
```

**Step 2.2.4: Integrate Export Modal into DiagramWizard**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
import { ExportModal } from './components/ExportModal';

export const DiagramWizard: React.FC<DiagramWizardProps> = ({...}) => {
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const svgPreviewRef = useRef<HTMLDivElement>(null);

  // Update action bar with new export button
  <div className={styles.actionBar}>
    <Space>
      {/* Replace simple download button with export modal */}
      <Button
        icon={<DownloadOutlined />}
        onClick={() => setExportModalVisible(true)}
        disabled={!status?.svgOutput}
      >
        Export Diagram
      </Button>

      <Button
        icon={<CopyOutlined />}
        onClick={handleCopyCode}
        disabled={!status?.diagramCode}
      >
        Copy Code
      </Button>

      {/* ... other buttons ... */}
    </Space>
  </div>

  {/* Export Modal */}
  <ExportModal
    visible={exportModalVisible}
    svgContent={status?.svgOutput || ''}
    svgElement={svgPreviewRef.current}
    onClose={() => setExportModalVisible(false)}
  />
};
```

**Testing Checklist:**
- [ ] SVG export works
- [ ] PNG export generates high-quality images
- [ ] PDF export includes diagrams correctly
- [ ] PDF metadata is embedded
- [ ] Filename validation works
- [ ] Quality slider affects output
- [ ] Large diagrams export without errors
- [ ] Mobile export works

---

### 2.3 Status Footer Component

**Priority:** MEDIUM
**Effort:** 2 days
**Risk:** LOW

#### Implementation Steps

**Step 2.3.1: Create Footer Component**

**File:** `frontend/src/components/DiagramWizard/components/Footer.tsx` (NEW)

```typescript
/**
 * Status Footer Component
 * Adapted from ArchitectureGenStudio
 */

import React, { useState } from 'react';
import { Layout, Badge, Collapse, Typography, Tag, Button } from 'antd';
import {
  CheckCircleOutlined,
  LoadingOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import { SSEMessage } from '../../../hooks/useSSE';
import styles from './Footer.module.css';

const { Footer: AntFooter } = Layout;
const { Panel } = Collapse;
const { Text } = Typography;

interface StatusFooterProps {
  currentStatus: {
    message: string;
    type: 'idle' | 'processing' | 'success' | 'error';
  };
  sseMessages: SSEMessage[];
  isSSEConnected: boolean;
  onClearMessages?: () => void;
}

export const StatusFooter: React.FC<StatusFooterProps> = ({
  currentStatus,
  sseMessages,
  isSSEConnected,
  onClearMessages,
}) => {
  const [expanded, setExpanded] = useState(false);

  const getStatusIcon = () => {
    switch (currentStatus.type) {
      case 'processing':
        return <LoadingOutlined spin />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const unreadCount = sseMessages.filter((m) => !m.isRead).length;

  return (
    <AntFooter className={styles.footer}>
      <div className={styles.footerContent}>
        <div className={styles.statusSection}>
          <Space size="middle">
            {getStatusIcon()}
            <Text>{currentStatus.message}</Text>

            <Badge
              status={isSSEConnected ? 'success' : 'error'}
              text={isSSEConnected ? 'Connected' : 'Disconnected'}
            />
          </Space>
        </div>

        <div className={styles.messagesSection}>
          <Button
            type="text"
            size="small"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Hide' : 'Show'} Messages
            {unreadCount > 0 && (
              <Badge count={unreadCount} style={{ marginLeft: 8 }} />
            )}
          </Button>
        </div>
      </div>

      {expanded && (
        <Collapse
          activeKey={expanded ? ['messages'] : []}
          className={styles.messagesCollapse}
        >
          <Panel
            header={
              <div className={styles.messagesPanelHeader}>
                <span>SSE Messages ({sseMessages.length})</span>
                {sseMessages.length > 0 && (
                  <Button
                    type="link"
                    size="small"
                    icon={<ClearOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      onClearMessages?.();
                    }}
                  >
                    Clear
                  </Button>
                )}
              </div>
            }
            key="messages"
          >
            <div className={styles.messagesList}>
              {sseMessages.length === 0 ? (
                <Text type="secondary">No messages</Text>
              ) : (
                sseMessages.map((msg) => (
                  <div key={msg.id} className={styles.messageItem}>
                    <div className={styles.messageHeader}>
                      <Tag color={getMessageColor(msg.type)}>{msg.type}</Tag>
                      <Text type="secondary" className={styles.messageTime}>
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </Text>
                    </div>
                    <pre className={styles.messageData}>
                      {JSON.stringify(msg.data, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </Panel>
        </Collapse>
      )}
    </AntFooter>
  );
};

function getMessageColor(type: string): string {
  switch (type) {
    case 'error':
      return 'red';
    case 'success':
    case 'completed':
      return 'green';
    case 'progress':
    case 'processing':
      return 'blue';
    case 'clarifying':
      return 'orange';
    default:
      return 'default';
  }
}
```

**Step 2.3.2: Add CSS**

**File:** `frontend/src/components/DiagramWizard/components/Footer.module.css` (NEW)

```css
.footer {
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  padding: 8px 24px;
}

.footerContent {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statusSection {
  flex: 1;
}

.messagesSection {
  display: flex;
  align-items: center;
}

.messagesCollapse {
  margin-top: 8px;
}

.messagesPanelHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.messagesList {
  max-height: 300px;
  overflow-y: auto;
}

.messageItem {
  border-bottom: 1px solid #f0f0f0;
  padding: 8px 0;
}

.messageItem:last-child {
  border-bottom: none;
}

.messageHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.messageTime {
  font-size: 11px;
}

.messageData {
  font-family: 'Courier New', monospace;
  font-size: 11px;
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  margin: 0;
  overflow-x: auto;
}
```

**Step 2.3.3: Integrate into DiagramWizard**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
import { StatusFooter } from './components/Footer';

export const DiagramWizard: React.FC<DiagramWizardProps> = ({...}) => {
  const [currentStatus, setCurrentStatus] = useState({
    message: 'Ready',
    type: 'idle' as 'idle' | 'processing' | 'success' | 'error',
  });

  // Update status based on SSE messages
  useEffect(() => {
    if (!status) return;

    switch (status.status) {
      case 'analyzing':
        setCurrentStatus({ message: 'Analyzing your request...', type: 'processing' });
        break;
      case 'clarifying':
        setCurrentStatus({ message: 'Waiting for clarification...', type: 'processing' });
        break;
      case 'generating':
        setCurrentStatus({ message: 'Generating diagram code...', type: 'processing' });
        break;
      case 'completed':
        setCurrentStatus({ message: 'Diagram generated successfully!', type: 'success' });
        break;
      case 'error':
        setCurrentStatus({ message: status.message || 'An error occurred', type: 'error' });
        break;
      default:
        setCurrentStatus({ message: 'Ready', type: 'idle' });
    }
  }, [status]);

  return (
    <Layout className={styles.diagramWizard}>
      {/* ... existing content ... */}

      {/* Add Footer */}
      <StatusFooter
        currentStatus={currentStatus}
        sseMessages={sseMessages}
        isSSEConnected={sseConnected}
        onClearMessages={clearSSEMessages}
      />
    </Layout>
  );
};
```

**Testing Checklist:**
- [ ] Status updates correctly
- [ ] SSE messages display
- [ ] Connection indicator accurate
- [ ] Expand/collapse works
- [ ] Clear messages works
- [ ] Unread count updates
- [ ] Message formatting correct
- [ ] Performance with many messages

---

## Phase 2 Completion Criteria

**Before moving to Phase 3, verify:**

1. **Zoom Controls:**
   - [ ] All zoom controls functional
   - [ ] Keyboard shortcuts work
   - [ ] Mouse wheel zoom works
   - [ ] Pan/drag works smoothly

2. **Export Options:**
   - [ ] SVG export works
   - [ ] PNG export high quality
   - [ ] PDF export with metadata
   - [ ] All formats tested

3. **Status Footer:**
   - [ ] Status updates in real-time
   - [ ] Messages display correctly
   - [ ] Connection status accurate

4. **Testing:**
   - [ ] Unit tests pass
   - [ ] Integration tests pass
   - [ ] Manual QA completed

**Phase 2 Deliverables:**
- ✅ Zoom controls implemented
- ✅ Multi-format export (SVG, PNG, PDF)
- ✅ Status footer with SSE messages
- ✅ Test coverage maintained
- ✅ Documentation updated

---

## Phase 3: Quality & Accessibility (Week 5-6)

**Objective:** Improve code quality, validation, and accessibility compliance

### 3.1 Code Validation & Error Panel

**Priority:** HIGH
**Effort:** 5 days
**Risk:** MEDIUM

#### Implementation Steps

**Step 3.1.1: Create Validation Service**

**File:** `frontend/src/services/validation/validationService.ts` (NEW)

```typescript
/**
 * Validation Service
 * Integrates with backend validation and LLM correction
 */

export interface ValidationError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
  suggestion?: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  correctedCode?: string;
  metadata?: {
    provider: string;
    validationTime: number;
    autoFixApplied: boolean;
  };
}

export class ValidationService {
  private static API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8003/api/v1';

  /**
   * Validate diagram code
   */
  static async validate(
    code: string,
    diagramType: string
  ): Promise<ValidationResult> {
    try {
      const response = await fetch(`${this.API_URL}/diagrams/v2/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          diagram_type: diagramType,
        }),
      });

      if (!response.ok) {
        throw new Error('Validation request failed');
      }

      const data = await response.json();
      return this.transformBackendResponse(data);
    } catch (error) {
      console.error('Validation failed:', error);
      throw error;
    }
  }

  /**
   * Validate and auto-fix
   */
  static async validateAndFix(
    code: string,
    diagramType: string
  ): Promise<ValidationResult> {
    try {
      const response = await fetch(`${this.API_URL}/diagrams/v2/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          diagram_type: diagramType,
          auto_fix: true,
          llm_correction: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Validation request failed');
      }

      const data = await response.json();
      return this.transformBackendResponse(data);
    } catch (error) {
      console.error('Validation and fix failed:', error);
      throw error;
    }
  }

  /**
   * Transform backend response to frontend format
   */
  private static transformBackendResponse(data: any): ValidationResult {
    return {
      isValid: data.is_valid || false,
      errors: (data.errors || []).map((err: any) => ({
        line: err.line || 0,
        column: err.column || 0,
        message: err.message || 'Unknown error',
        severity: err.severity || 'error',
        suggestion: err.suggestion,
      })),
      warnings: (data.warnings || []).map((warn: any) => ({
        line: warn.line || 0,
        column: warn.column || 0,
        message: warn.message || 'Unknown warning',
        severity: 'warning',
        suggestion: warn.suggestion,
      })),
      correctedCode: data.corrected_code,
      metadata: data.metadata,
    };
  }
}
```

**Step 3.1.2: Create Error Panel Component**

**File:** `frontend/src/components/DiagramWizard/components/ErrorPanel.tsx` (NEW)

```typescript
/**
 * Error Panel Component
 * Displays validation errors with line numbers and suggestions
 */

import React from 'react';
import { Alert, List, Button, Typography, Tag, Space } from 'antd';
import {
  CloseCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  BulbOutlined,
} from '@ant-design/icons';
import { ValidationError } from '../../../services/validation/validationService';
import styles from './ErrorPanel.module.css';

const { Text, Paragraph } = Typography;

interface ErrorPanelProps {
  errors: ValidationError[];
  warnings: ValidationError[];
  onFixError?: (error: ValidationError) => void;
  onDismiss?: () => void;
}

export const ErrorPanel: React.FC<ErrorPanelProps> = ({
  errors,
  warnings,
  onFixError,
  onDismiss,
}) => {
  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const allIssues = [...errors, ...warnings].sort((a, b) => a.line - b.line);

  return (
    <div className={styles.errorPanel}>
      <Alert
        type={errors.length > 0 ? 'error' : 'warning'}
        message={
          <div className={styles.alertHeader}>
            <span>
              {errors.length} error(s), {warnings.length} warning(s) found
            </span>
            {onDismiss && (
              <Button type="link" size="small" onClick={onDismiss}>
                Dismiss
              </Button>
            )}
          </div>
        }
        closable={false}
      />

      <List
        size="small"
        className={styles.errorList}
        dataSource={allIssues}
        renderItem={(issue) => (
          <List.Item className={styles.errorItem}>
            <div className={styles.errorContent}>
              <div className={styles.errorHeader}>
                <Space>
                  {getIcon(issue.severity)}
                  <Tag color={issue.severity === 'error' ? 'red' : 'orange'}>
                    Line {issue.line}:{issue.column}
                  </Tag>
                  <Text strong>{issue.message}</Text>
                </Space>
              </div>

              {issue.suggestion && (
                <div className={styles.suggestion}>
                  <BulbOutlined style={{ color: '#faad14', marginRight: 8 }} />
                  <Text type="secondary">{issue.suggestion}</Text>
                  {onFixError && (
                    <Button
                      type="link"
                      size="small"
                      onClick={() => onFixError(issue)}
                    >
                      Apply Fix
                    </Button>
                  )}
                </div>
              )}
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};
```

**Step 3.1.3: Add Real-Time Validation to Code Editor**

**File:** `frontend/src/components/DiagramWizard/panels/Panel3_CodeEditor.tsx`

```typescript
import React, { useState, useEffect, useCallback } from 'react';
import { Button, Space, Spin, message } from 'antd';
import { CheckCircleOutlined, ToolOutlined } from '@ant-design/icons';
import { ValidationService, ValidationResult } from '../../../services/validation/validationService';
import { ErrorPanel } from '../components/ErrorPanel';
import { debounce } from 'lodash';

export const CodeEditorPanel: React.FC<CodeEditorPanelProps> = ({
  code,
  diagramType,
  onChange,
  isLoading,
}) => {
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  // Debounced validation (wait 500ms after user stops typing)
  const debouncedValidate = useCallback(
    debounce(async (codeToValidate: string) => {
      if (!codeToValidate.trim()) {
        setValidationResult(null);
        return;
      }

      setIsValidating(true);
      try {
        const result = await ValidationService.validate(codeToValidate, diagramType);
        setValidationResult(result);
      } catch (error) {
        console.error('Validation error:', error);
      } finally {
        setIsValidating(false);
      }
    }, 500),
    [diagramType]
  );

  // Validate on code change
  useEffect(() => {
    debouncedValidate(code);
  }, [code, debouncedValidate]);

  // Manual validation with auto-fix
  const handleValidateAndFix = async () => {
    setIsValidating(true);
    try {
      const result = await ValidationService.validateAndFix(code, diagramType);
      setValidationResult(result);

      if (result.correctedCode && result.correctedCode !== code) {
        onChange?.(result.correctedCode);
        message.success('Code auto-corrected');
      } else if (result.isValid) {
        message.success('Code is valid');
      } else {
        message.warning('Could not auto-fix all errors');
      }
    } catch (error) {
      message.error('Validation failed');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className={styles.codeEditorPanel}>
      <div className={styles.toolbar}>
        <Space>
          <Button
            icon={<CheckCircleOutlined />}
            onClick={handleValidateAndFix}
            loading={isValidating}
            type={validationResult?.isValid ? 'primary' : 'default'}
          >
            Validate & Fix
          </Button>

          {isValidating && <Spin size="small" />}

          {validationResult && !isValidating && (
            <span>
              {validationResult.isValid ? (
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
              ) : (
                <span style={{ color: '#ff4d4f' }}>
                  {validationResult.errors.length} error(s)
                </span>
              )}
            </span>
          )}
        </Space>
      </div>

      {validationResult && !validationResult.isValid && (
        <ErrorPanel
          errors={validationResult.errors}
          warnings={validationResult.warnings}
          onDismiss={() => setValidationResult(null)}
        />
      )}

      <textarea
        className={styles.codeEditor}
        value={code}
        onChange={(e) => onChange?.(e.target.value)}
        spellCheck={false}
        disabled={isLoading}
      />
    </div>
  );
};
```

**Testing Checklist:**
- [ ] Real-time validation works
- [ ] Debouncing prevents excessive API calls
- [ ] Error panel displays correctly
- [ ] Line numbers accurate
- [ ] Auto-fix applies corrections
- [ ] Validation status updates
- [ ] Performance acceptable

---

### 3.2 Accessibility Improvements (WCAG 2.1 AA)

**Priority:** HIGH
**Effort:** 4 days
**Risk:** LOW

#### Implementation Steps

**Step 3.2.1: Add ARIA Labels and Roles**

**File:** `frontend/src/components/DiagramWizard/DiagramWizard.tsx`

```typescript
// Add semantic HTML and ARIA labels throughout

<Layout className={styles.diagramWizard} role="main">
  {/* Skip to main content link */}
  <a
    href="#diagram-content"
    className={styles.skipLink}
    onFocus={(e) => e.currentTarget.classList.add(styles.visible)}
    onBlur={(e) => e.currentTarget.classList.remove(styles.visible)}
  >
    Skip to main content
  </a>

  <Layout.Header className={styles.header} role="banner">
    <div className={styles.headerContent}>
      <h1 className={styles.title}>Diagram Wizard</h1>

      {sessionId && (
        <div role="status" aria-live="polite" aria-atomic="true">
          <Space>
            <span id="session-id-label">Session:</span>
            <span aria-labelledby="session-id-label">
              {sessionId.substring(0, 8)}...
            </span>

            <Badge
              status={sseConnected ? 'success' : 'error'}
              text={sseConnected ? 'Connected' : 'Disconnected'}
              aria-label={`Connection status: ${sseConnected ? 'Connected' : 'Disconnected'}`}
            />
          </Space>
        </div>
      )}
    </div>
  </Layout.Header>

  <Layout.Content className={styles.content} id="diagram-content">
    {/* Progress indicator with ARIA */}
    <nav aria-label="Progress">
      <Steps
        current={currentPhase}
        size="small"
        items={phases.map((phase, index) => ({
          title: phase.title,
          description: phase.description,
          icon: phase.icon,
          status: currentPhase > index ? 'finish' : currentPhase === index ? 'process' : 'wait',
        }))}
        aria-label="Diagram generation progress"
      />
    </nav>

    {/* Error messages with ARIA live region */}
    {error && (
      <div role="alert" aria-live="assertive">
        <Alert
          message="Error"
          description={error.message}
          type="error"
          closable
        />
      </div>
    )}

    {/* Main content based on phase */}
    {!sessionId ? (
      <section aria-labelledby="initial-prompt-heading">
        <h2 id="initial-prompt-heading" className={styles.visuallyHidden}>
          Describe Your System
        </h2>

        <Input.TextArea
          placeholder="Describe the system, process, or architecture you want to diagram..."
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          rows={6}
          disabled={loading}
          aria-label="System description input"
          aria-describedby="input-instructions"
        />

        <p id="input-instructions" className={styles.instructions}>
          Tell us about the system or process you want to visualize. We'll have a conversation to gather all the details needed.
        </p>

        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleStartDiagram}
          loading={loading || isInitializing}
          size="large"
          aria-label="Start diagram generation conversation"
        >
          Start Conversation
        </Button>
      </section>
    ) : isInAnalysisPhase ? (
      <section aria-labelledby="conversation-heading">
        <h2 id="conversation-heading" className={styles.visuallyHidden}>
          Conversation with AI Assistant
        </h2>

        {/* Chat history */}
        <div
          role="log"
          aria-live="polite"
          aria-label="Conversation history"
          className={styles.conversationHistory}
        >
          {status?.history?.map(([role, content], index) => (
            <div
              key={index}
              role={role === 'user' ? 'article' : 'article'}
              aria-label={`${role === 'user' ? 'Your message' : 'AI response'} ${index + 1}`}
            >
              {/* Message content */}
            </div>
          ))}
        </div>

        {/* Response input */}
        <div role="form" aria-labelledby="response-heading">
          <h3 id="response-heading" className={styles.visuallyHidden}>
            Your Response
          </h3>

          <Input.TextArea
            placeholder="Type your response here..."
            value={clarificationInput}
            onChange={(e) => setClarificationInput(e.target.value)}
            rows={6}
            disabled={loading}
            aria-label="Clarification response input"
          />

          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleClarificationSubmit}
            loading={loading || isInitializing}
            aria-label="Send response to AI assistant"
          >
            Send Response
          </Button>
        </div>
      </section>
    ) : (
      {/* Multi-panel view with proper ARIA */}
    )}
  </Layout.Content>
</Layout>
```

**Step 3.2.2: Add CSS for Accessibility**

**File:** `frontend/src/components/DiagramWizard/diagram-wizard.module.css`

```css
/* Skip link for keyboard navigation */
.skipLink {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--ant-primary-color, #1890ff);
  color: white;
  padding: 8px 16px;
  z-index: 100;
  text-decoration: none;
  border-radius: 4px;
}

.skipLink.visible,
.skipLink:focus {
  top: 10px;
  left: 10px;
}

/* Visually hidden but accessible to screen readers */
.visuallyHidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Focus indicators */
.diagramWizard button:focus,
.diagramWizard input:focus,
.diagramWizard textarea:focus {
  outline: 2px solid var(--ant-primary-color, #1890ff);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .diagramWizard {
    --border-color: #000;
    --text-color: #000;
    --background-color: #fff;
  }

  .diagramWizard button {
    border: 2px solid currentColor;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .diagramWizard * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Color blind friendly status indicators */
.diagramWizard [role="status"],
.diagramWizard [role="alert"] {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Ensure sufficient color contrast */
.diagramWizard .ant-tag {
  border: 1px solid currentColor;
}
```

**Step 3.2.3: Add Keyboard Navigation**

**File:** `frontend/src/components/DiagramWizard/hooks/useKeyboardNavigation.ts` (NEW)

```typescript
/**
 * Keyboard Navigation Hook
 * Provides keyboard shortcuts and focus management
 */

import { useEffect, useCallback } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  action: () => void;
  description: string;
}

export const useKeyboardNavigation = (shortcuts: KeyboardShortcut[]) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const ctrlMatch = shortcut.ctrl ? (event.ctrlKey || event.metaKey) : !event.ctrlKey && !event.metaKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;

        if (
          event.key === shortcut.key &&
          ctrlMatch &&
          shiftMatch &&
          altMatch
        ) {
          event.preventDefault();
          shortcut.action();
          break;
        }
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
};

// Usage in DiagramWizard
export const DiagramWizard: React.FC<DiagramWizardProps> = ({...}) => {
  useKeyboardNavigation([
    {
      key: 'Enter',
      ctrl: true,
      action: handleStartDiagram,
      description: 'Start diagram generation',
    },
    {
      key: 's',
      ctrl: true,
      action: () => setExportModalVisible(true),
      description: 'Save/Export diagram',
    },
    {
      key: 'Escape',
      action: () => {
        if (exportModalVisible) setExportModalVisible(false);
        if (selectedResponse) setSelectedResponse(null);
      },
      description: 'Close modal',
    },
    {
      key: '?',
      shift: true,
      action: () => setShowKeyboardHelp(true),
      description: 'Show keyboard shortcuts',
    },
  ]);
};
```

**Step 3.2.4: Add Screen Reader Announcements**

**File:** `frontend/src/components/DiagramWizard/components/LiveRegion.tsx` (NEW)

```typescript
/**
 * Live Region Component
 * Announces dynamic content to screen readers
 */

import React, { useEffect, useState } from 'react';
import styles from './LiveRegion.module.css';

interface LiveRegionProps {
  message: string;
  politeness?: 'polite' | 'assertive';
  clearDelay?: number;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({
  message,
  politeness = 'polite',
  clearDelay = 5000,
}) => {
  const [displayMessage, setDisplayMessage] = useState('');

  useEffect(() => {
    if (message) {
      setDisplayMessage(message);

      if (clearDelay > 0) {
        const timer = setTimeout(() => {
          setDisplayMessage('');
        }, clearDelay);

        return () => clearTimeout(timer);
      }
    }
  }, [message, clearDelay]);

  return (
    <div
      className={styles.liveRegion}
      role="status"
      aria-live={politeness}
      aria-atomic="true"
    >
      {displayMessage}
    </div>
  );
};
```

```css
/* LiveRegion.module.css */
.liveRegion {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

**Usage in DiagramWizard:**

```typescript
import { LiveRegion } from './components/LiveRegion';

export const DiagramWizard: React.FC<DiagramWizardProps> = ({...}) => {
  const [announcement, setAnnouncement] = useState('');

  // Announce phase changes
  useEffect(() => {
    const phaseNames = ['Describe', 'Analyze', 'Generate', 'Visualize'];
    setAnnouncement(`Phase ${currentPhase + 1}: ${phaseNames[currentPhase]}`);
  }, [currentPhase]);

  return (
    <>
      <LiveRegion message={announcement} />
      {/* Rest of component */}
    </>
  );
};
```

**Testing Checklist:**
- [ ] Screen reader navigation works
- [ ] All interactive elements have labels
- [ ] Focus visible on all elements
- [ ] Keyboard shortcuts functional
- [ ] Live regions announce updates
- [ ] High contrast mode works
- [ ] Color blind friendly
- [ ] WCAG 2.1 AA compliance verified

---

## Phase 3 Completion Criteria

**Before moving to Phase 4 (optional), verify:**

1. **Code Validation:**
   - [ ] Real-time validation works
   - [ ] Error panel displays correctly
   - [ ] Auto-fix functionality works
   - [ ] Performance acceptable

2. **Accessibility:**
   - [ ] WCAG 2.1 AA compliance
   - [ ] Screen reader compatible
   - [ ] Keyboard navigation complete
   - [ ] Color contrast sufficient
   - [ ] Focus indicators clear

3. **Testing:**
   - [ ] Accessibility audit passed
   - [ ] Screen reader testing completed
   - [ ] Keyboard navigation tested
   - [ ] Cross-browser compatibility verified

**Phase 3 Deliverables:**
- ✅ Code validation system
- ✅ Error panel with suggestions
- ✅ WCAG 2.1 AA compliance
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Accessibility documentation

---

## Phase 4: Advanced Features (Optional - Week 7-10)

**Note:** These are lower priority enhancements that can be implemented if time and resources allow.

### 4.1 Resizable Panels

**Priority:** LOW
**Effort:** 3 days
**Risk:** LOW

Use `react-resizable-panels` library:

```bash
npm install react-resizable-panels
```

```typescript
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';

<PanelGroup direction="horizontal">
  <Panel defaultSize={30} minSize={20}>
    <ChatPanel />
  </Panel>

  <PanelResizeHandle />

  <Panel defaultSize={40} minSize={30}>
    <PreviewPanel />
  </Panel>

  <PanelResizeHandle />

  <Panel defaultSize={30} minSize={20}>
    <CodeEditorPanel />
  </Panel>
</PanelGroup>
```

### 4.2 Multi-Diagram Support

**Priority:** LOW
**Effort:** 5 days
**Risk:** MEDIUM

Allow generating multiple diagram types from one session:

- Update backend to support multiple diagram outputs per session
- Add tabbed interface for switching between diagrams
- Persist all generated diagrams in session history

### 4.3 Template System

**Priority:** LOW
**Effort:** 4 days
**Risk:** LOW

Add pre-built templates:

```typescript
interface DiagramTemplate {
  id: string;
  name: string;
  description: string;
  diagramType: string;
  initialPrompt: string;
  tags: string[];
}

const templates: DiagramTemplate[] = [
  {
    id: 'microservices',
    name: 'Microservices Architecture',
    description: 'Template for microservices system architecture',
    diagramType: 'D2',
    initialPrompt: 'Design a microservices architecture with...',
    tags: ['architecture', 'backend'],
  },
  // More templates...
];
```

---

## Testing Strategy

### Unit Testing

**Framework:** Jest + React Testing Library

**Coverage Goals:**
- Components: 90%+
- Hooks: 95%+
- Services: 95%+
- Utils: 100%

**Example Test:**

```typescript
// frontend/src/hooks/__tests__/useSSE.test.ts

import { renderHook, waitFor } from '@testing-library/react';
import { useSSE } from '../useSSE';

describe('useSSE', () => {
  it('should connect and receive messages', async () => {
    const mockUrl = 'http://localhost:8003/stream';
    const { result } = renderHook(() =>
      useSSE({
        url: mockUrl,
        enabled: true,
      })
    );

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    // Simulate SSE message
    // ...assertions
  });

  it('should reconnect after error', async () => {
    // Test reconnection logic
  });

  it('should handle keep-alive messages', async () => {
    // Test keep-alive
  });
});
```

### Integration Testing

**Framework:** Playwright or Cypress

**Test Scenarios:**
1. Complete diagram generation flow
2. Session persistence across refresh
3. Export in all formats
4. Validation and auto-fix
5. Accessibility compliance
6. Keyboard navigation

**Example E2E Test:**

```typescript
// e2e/diagram-wizard.spec.ts

describe('DiagramWizard E2E', () => {
  it('should generate a diagram end-to-end', async ({ page }) => {
    await page.goto('/diagram-wizard');

    // Enter initial prompt
    await page.fill('[aria-label="System description input"]',
      'A user authentication system with login, signup, and password reset'
    );

    // Start conversation
    await page.click('text=Start Conversation');

    // Wait for AI response
    await page.waitForSelector('[role="article"]');

    // Respond to clarification
    await page.fill('[aria-label="Clarification response input"]',
      'The system should use JWT tokens for authentication'
    );

    // Send response
    await page.click('text=Send Response');

    // Continue until diagram is generated
    await page.waitForSelector('text=Diagram generated successfully', {
      timeout: 60000,
    });

    // Verify diagram is displayed
    await expect(page.locator('.previewContent')).toBeVisible();

    // Export as PDF
    await page.click('text=Export Diagram');
    await page.selectOption('select[name="format"]', 'pdf');
    await page.click('text=OK');

    // Verify download
    const download = await page.waitForEvent('download');
    expect(download.suggestedFilename()).toContain('.pdf');
  });
});
```

### Accessibility Testing

**Tools:**
- axe-core (automated)
- WAVE (manual)
- Screen readers (NVDA, JAWS, VoiceOver)

**Checklist:**
- [ ] All images have alt text
- [ ] All form inputs have labels
- [ ] Color contrast meets WCAG AA
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] No keyboard traps
- [ ] Screen reader announcements work
- [ ] ARIA attributes correct

### Performance Testing

**Metrics to Track:**
- Time to first diagram (< 10s)
- SSE message latency (< 500ms)
- UI responsiveness (60fps)
- Memory usage (< 100MB)
- Bundle size (< 500KB gzipped)

**Tools:**
- Lighthouse
- Chrome DevTools Performance
- webpack-bundle-analyzer

---

## Rollback Plan

### Rollback Triggers

Rollback to previous version if:
1. Critical bugs in production (P0/P1)
2. Performance degradation > 30%
3. User complaints > threshold
4. Data loss or corruption
5. Security vulnerability introduced

### Rollback Procedure

**Phase 1 Rollback:**
1. Revert SSE hook changes
2. Remove localStorage persistence
3. Restore original provider integration
4. Deploy previous backend version
5. Clear localStorage for all users

**Phase 2 Rollback:**
1. Remove zoom controls
2. Restore simple export
3. Remove status footer
4. Revert UI changes

**Phase 3 Rollback:**
1. Disable validation service
2. Remove error panel
3. Revert accessibility changes

**Git Strategy:**
```bash
# Tag each phase completion
git tag -a phase-1-complete -m "Phase 1 completed"
git tag -a phase-2-complete -m "Phase 2 completed"
git tag -a phase-3-complete -m "Phase 3 completed"

# Rollback to phase
git revert <commit-range>
# or
git reset --hard phase-X-complete
```

### Communication Plan

**Rollback Communication:**
1. Notify users via in-app banner
2. Send email to active users
3. Update status page
4. Post mortem within 48 hours

---

## Success Metrics

### User Experience Metrics

**Target Improvements:**
- Session completion rate: +20%
- User retention (7-day): +30%
- Average session duration: +15%
- Export usage: +50%
- Accessibility score: 100/100

### Technical Metrics

**Performance:**
- Lighthouse score: > 90
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- SSE reconnection success: > 95%

**Quality:**
- Test coverage: > 90%
- Bug density: < 1 bug/KLOC
- Zero critical security vulnerabilities
- WCAG 2.1 AA compliance: 100%

**Reliability:**
- Uptime: > 99.9%
- Error rate: < 0.1%
- Successful renders: > 98%

### Business Metrics

**Engagement:**
- Daily active users: +25%
- Diagrams generated per user: +40%
- Feature adoption (export): > 60%
- User satisfaction (NPS): > 50

---

## Risk Management

### High-Risk Areas

**1. Backend Provider Integration**
- **Risk:** Breaking existing diagram generation
- **Mitigation:**
  - Feature flag for provider system
  - Extensive integration testing
  - Gradual rollout (10% → 50% → 100%)
  - Fallback to legacy system

**2. SSE Reconnection Logic**
- **Risk:** Memory leaks or infinite loops
- **Mitigation:**
  - Max reconnection attempts
  - Memory profiling during testing
  - Circuit breaker pattern
  - Monitoring and alerts

**3. localStorage Quota**
- **Risk:** Exceeding storage limits
- **Mitigation:**
  - Implement quota management
  - LRU eviction policy
  - Compression for large data
  - User notification before eviction

**4. Accessibility Regression**
- **Risk:** Breaking existing accessibility
- **Mitigation:**
  - Automated a11y tests in CI
  - Manual screen reader testing
  - User testing with disabled users
  - Continuous monitoring

### Dependency Risks

**New Dependencies:**
- `jspdf`: PDF export (well-maintained, 15k+ stars)
- `html2canvas`: Canvas rendering (well-maintained, 28k+ stars)
- `react-resizable-panels`: Panel resizing (optional, 1k+ stars)

**Risk Mitigation:**
- Pin exact versions
- Regular security audits (npm audit)
- License compatibility check
- Bundlephobia size check
- Alternative libraries identified

---

## Timeline & Milestones

### Detailed Schedule

**Week 1-2: Phase 1 - Foundation**
- Days 1-3: SSE hook extraction and integration
- Days 4-6: localStorage persistence
- Days 7-10: Provider system integration
- Test and deploy

**Week 3-4: Phase 2 - User Experience**
- Days 1-3: Zoom controls
- Days 4-7: Export options (SVG, PNG, PDF)
- Days 8-10: Status footer
- Test and deploy

**Week 5-6: Phase 3 - Quality & Accessibility**
- Days 1-5: Code validation system
- Days 6-10: Accessibility compliance
- Test and deploy

**Week 7-10: Phase 4 - Advanced (Optional)**
- Week 7: Resizable panels
- Week 8-9: Multi-diagram support
- Week 10: Template system
- Test and deploy

### Milestones

| Milestone | Date | Deliverables |
|-----------|------|-------------|
| M1: Phase 1 Complete | End Week 2 | SSE, Persistence, Providers |
| M2: Phase 2 Complete | End Week 4 | Zoom, Export, Footer |
| M3: Phase 3 Complete | End Week 6 | Validation, Accessibility |
| M4: Phase 4 Complete | End Week 10 | Resizable, Multi-diagram, Templates |
| M5: Production Release | Week 11 | Full deployment |

---

## Conclusion

This implementation plan provides a structured approach to enhancing DiagramWizard with proven features from ArchitectureGenStudio. The phased approach allows for:

1. **Incremental Value Delivery:** Each phase adds user value independently
2. **Risk Mitigation:** Early phases establish foundation for later work
3. **Flexibility:** Phases can be adjusted based on user feedback
4. **Quality Assurance:** Comprehensive testing at each phase

**Key Success Factors:**
- Maintain DiagramWizard's conversational strength
- Prioritize user experience and accessibility
- Ensure backward compatibility
- Comprehensive testing coverage
- Clear rollback procedures

**Next Steps:**
1. Review and approve this plan
2. Set up project tracking (Jira/Linear)
3. Allocate development resources
4. Begin Phase 1 implementation
5. Schedule weekly progress reviews

---

**Document Control:**
- **Author:** AI Assistant
- **Date Created:** 2025-11-15
- **Status:** DRAFT
- **Approvers:** Product Owner, Tech Lead, UX Designer
- **Next Review:** After Phase 1 completion
