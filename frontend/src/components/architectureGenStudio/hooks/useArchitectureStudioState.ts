/**
 * Main state management hook for Architecture Gen Studio
 * Manages all state and provides action handlers
 */

import { useState, useCallback, useEffect } from 'react';
import {
  ArchitectureStudioState,
  Agent,
  AgentOption,
  DiagramType,
  GeneratedDiagram,
  ValidationResult,
  SSEMessage,
  DEFAULT_STATE,
  STORAGE_KEYS,
  DiagramResponse,
} from '../types/architectureStudio';

export interface UseArchitectureStudioStateReturn {
  state: ArchitectureStudioState;
  // Agent handlers
  setCurrentAgent: (agent: Agent | null) => void;
  setAgents: (agents: Agent[]) => void;
  setAgentsLoading: (loading: boolean) => void;
  setAgentsError: (error: string | null) => void;
  // Agent options handlers
  setCurrentAgentOptions: (options: AgentOption[]) => void;
  setSelectedAgentOption: (option: AgentOption | null) => void;
  setOptionsLoading: (loading: boolean) => void;
  setOptionsError: (error: string | null) => void;
  // Prompt handlers
  setCurrentPrompt: (prompt: string) => void;
  setPromptHasUnsavedChanges: (hasChanges: boolean) => void;
  clearPrompt: () => void;
  // Diagram handlers
  setSelectedDiagramType: (type: DiagramType) => void;
  addGeneratedDiagram: (type: DiagramType, response: DiagramResponse) => void;
  getGeneratedDiagram: (type: DiagramType) => GeneratedDiagram | undefined;
  setIsProcessing: (processing: boolean) => void;
  setProcessingError: (error: string | null) => void;
  setProcessingRequestId: (id: string | null) => void;
  // Code editor handlers
  setCodeEditorContent: (content: string) => void;
  setCodeEditorHasUnsavedChanges: (hasChanges: boolean) => void;
  setValidationResult: (result: ValidationResult | null) => void;
  setIsValidating: (validating: boolean) => void;
  setIsRendering: (rendering: boolean) => void;
  // UI state handlers
  setColumnWidths: (widths: { left: number; center: number; right: number }) => void;
  setCollapsedColumn: (column: 'left' | 'center' | 'right', collapsed: boolean) => void;
  addSSEMessage: (message: SSEMessage) => void;
  clearSSEMessages: () => void;
  setCurrentStatus: (status: string, type?: 'idle' | 'processing' | 'success' | 'error') => void;
  setZoomLevel: (level: number) => void;
  // Persistence
  loadFromLocalStorage: () => void;
  saveToLocalStorage: () => void;
}

export function useArchitectureStudioState(): UseArchitectureStudioStateReturn {
  const [state, setState] = useState<ArchitectureStudioState>(DEFAULT_STATE);

  // ============================================================================
  // Agent Handlers
  // ============================================================================

  const setCurrentAgent = useCallback((agent: Agent | null) => {
    setState((prev) => ({ ...prev, currentAgent: agent }));
  }, []);

  const setAgents = useCallback((agents: Agent[]) => {
    setState((prev) => ({ ...prev, agents }));
  }, []);

  const setAgentsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, agentsLoading: loading }));
  }, []);

  const setAgentsError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, agentsError: error }));
  }, []);

  // ============================================================================
  // Agent Options Handlers
  // ============================================================================

  const setCurrentAgentOptions = useCallback((options: AgentOption[]) => {
    setState((prev) => ({ ...prev, currentAgentOptions: options }));
  }, []);

  const setSelectedAgentOption = useCallback((option: AgentOption | null) => {
    setState((prev) => ({
      ...prev,
      selectedAgentOption: option,
      // Auto-populate prompt with template
      currentPrompt: option?.template || '',
      promptHasUnsavedChanges: !!option?.template,
    }));
  }, []);

  const setOptionsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, optionsLoading: loading }));
  }, []);

  const setOptionsError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, optionsError: error }));
  }, []);

  // ============================================================================
  // Prompt Handlers
  // ============================================================================

  const setCurrentPrompt = useCallback((prompt: string) => {
    setState((prev) => ({
      ...prev,
      currentPrompt: prompt,
      promptHasUnsavedChanges: true,
    }));
  }, []);

  const setPromptHasUnsavedChanges = useCallback((hasChanges: boolean) => {
    setState((prev) => ({ ...prev, promptHasUnsavedChanges: hasChanges }));
  }, []);

  const clearPrompt = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentPrompt: '',
      promptHasUnsavedChanges: false,
    }));
  }, []);

  // ============================================================================
  // Diagram Handlers
  // ============================================================================

  const setSelectedDiagramType = useCallback((type: DiagramType) => {
    setState((prev) => ({
      ...prev,
      selectedDiagramType: type,
      // Don't persist zoom across diagram types
      zoomLevel: 100,
    }));
  }, []);

  const addGeneratedDiagram = useCallback((type: DiagramType, response: DiagramResponse) => {
    setState((prev) => {
      const newDiagrams = new Map(prev.generatedDiagrams);
      newDiagrams.set(type, {
        type,
        response,
        generatedAt: new Date().toISOString(),
      });
      return {
        ...prev,
        generatedDiagrams: newDiagrams,
        codeEditorContent: response.code,
        codeEditorHasUnsavedChanges: false,
      };
    });
  }, []);

  const getGeneratedDiagram = useCallback(
    (type: DiagramType) => {
      return state.generatedDiagrams.get(type);
    },
    [state.generatedDiagrams]
  );

  const setIsProcessing = useCallback((processing: boolean) => {
    setState((prev) => ({ ...prev, isProcessing: processing }));
  }, []);

  const setProcessingError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, processingError: error }));
  }, []);

  const setProcessingRequestId = useCallback((id: string | null) => {
    setState((prev) => ({ ...prev, processingRequestId: id }));
  }, []);

  // ============================================================================
  // Code Editor Handlers
  // ============================================================================

  const setCodeEditorContent = useCallback((content: string) => {
    setState((prev) => ({
      ...prev,
      codeEditorContent: content,
      codeEditorHasUnsavedChanges: true,
    }));
  }, []);

  const setCodeEditorHasUnsavedChanges = useCallback((hasChanges: boolean) => {
    setState((prev) => ({ ...prev, codeEditorHasUnsavedChanges: hasChanges }));
  }, []);

  const setValidationResult = useCallback((result: ValidationResult | null) => {
    setState((prev) => ({ ...prev, validationResult: result }));
  }, []);

  const setIsValidating = useCallback((validating: boolean) => {
    setState((prev) => ({ ...prev, isValidating: validating }));
  }, []);

  const setIsRendering = useCallback((rendering: boolean) => {
    setState((prev) => ({ ...prev, isRendering: rendering }));
  }, []);

  // ============================================================================
  // UI State Handlers
  // ============================================================================

  const setColumnWidths = useCallback(
    (widths: { left: number; center: number; right: number }) => {
      setState((prev) => ({ ...prev, columnWidths: widths }));
    },
    []
  );

  const setCollapsedColumn = useCallback(
    (column: 'left' | 'center' | 'right', collapsed: boolean) => {
      setState((prev) => ({
        ...prev,
        collapsedColumns: {
          ...prev.collapsedColumns,
          [column]: collapsed,
        },
      }));
    },
    []
  );

  const addSSEMessage = useCallback((message: SSEMessage) => {
    setState((prev) => ({
      ...prev,
      sseMessages: [...prev.sseMessages, message].slice(-100), // Max 100 messages
    }));
  }, []);

  const clearSSEMessages = useCallback(() => {
    setState((prev) => ({
      ...prev,
      sseMessages: [],
    }));
  }, []);

  const setCurrentStatus = useCallback(
    (status: string, type: 'idle' | 'processing' | 'success' | 'error' = 'idle') => {
      setState((prev) => ({
        ...prev,
        currentStatus: status,
        statusHistory: [
          ...prev.statusHistory,
          {
            message: status,
            timestamp: new Date().toISOString(),
            type,
          },
        ].slice(-50), // Max 50 status messages
      }));
    },
    []
  );

  const setZoomLevel = useCallback((level: number) => {
    setState((prev) => ({ ...prev, zoomLevel: level }));
  }, []);

  // ============================================================================
  // LocalStorage Persistence
  // ============================================================================

  const loadFromLocalStorage = useCallback(() => {
    try {
      const agent = localStorage.getItem(STORAGE_KEYS.CURRENT_AGENT);
      const prompt = localStorage.getItem(STORAGE_KEYS.LAST_PROMPT);
      const option = localStorage.getItem(STORAGE_KEYS.SELECTED_AGENT_OPTION);
      const widths = localStorage.getItem(STORAGE_KEYS.COLUMN_WIDTHS);
      const collapsed = localStorage.getItem(STORAGE_KEYS.COLLAPSED_COLUMNS);

      setState((prev) => ({
        ...prev,
        currentAgent: agent ? JSON.parse(agent) : null,
        currentPrompt: prompt || '',
        selectedAgentOption: option ? JSON.parse(option) : null,
        columnWidths: widths ? JSON.parse(widths) : prev.columnWidths,
        collapsedColumns: collapsed ? JSON.parse(collapsed) : prev.collapsedColumns,
      }));
    } catch (error) {
      console.error('Failed to load from localStorage:', error);
    }
  }, []);

  const saveToLocalStorage = useCallback(() => {
    try {
      if (state.currentAgent) {
        localStorage.setItem(STORAGE_KEYS.CURRENT_AGENT, JSON.stringify(state.currentAgent));
      }
      if (state.currentPrompt) {
        localStorage.setItem(STORAGE_KEYS.LAST_PROMPT, state.currentPrompt);
      }
      if (state.selectedAgentOption) {
        localStorage.setItem(
          STORAGE_KEYS.SELECTED_AGENT_OPTION,
          JSON.stringify(state.selectedAgentOption)
        );
      }
      localStorage.setItem(STORAGE_KEYS.COLUMN_WIDTHS, JSON.stringify(state.columnWidths));
      localStorage.setItem(
        STORAGE_KEYS.COLLAPSED_COLUMNS,
        JSON.stringify(state.collapsedColumns)
      );
    } catch (error) {
      console.error('Failed to save to localStorage:', error);
    }
  }, [state]);

  // Load from localStorage on mount
  useEffect(() => {
    loadFromLocalStorage();
  }, [loadFromLocalStorage]);

  // Save to localStorage whenever state changes (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      saveToLocalStorage();
    }, 1000); // Debounce at 1 second

    return () => clearTimeout(timer);
  }, [state, saveToLocalStorage]);

  return {
    state,
    setCurrentAgent,
    setAgents,
    setAgentsLoading,
    setAgentsError,
    setCurrentAgentOptions,
    setSelectedAgentOption,
    setOptionsLoading,
    setOptionsError,
    setCurrentPrompt,
    setPromptHasUnsavedChanges,
    clearPrompt,
    setSelectedDiagramType,
    addGeneratedDiagram,
    getGeneratedDiagram,
    setIsProcessing,
    setProcessingError,
    setProcessingRequestId,
    setCodeEditorContent,
    setCodeEditorHasUnsavedChanges,
    setValidationResult,
    setIsValidating,
    setIsRendering,
    setColumnWidths,
    setCollapsedColumn,
    addSSEMessage,
    clearSSEMessages,
    setCurrentStatus,
    setZoomLevel,
    loadFromLocalStorage,
    saveToLocalStorage,
  };
}
