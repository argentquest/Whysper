/**
 * DiagramWizard Component (Refactored)
 *
 * Main component for the diagram generation wizard interface.
 * Orchestrates three distinct screens:
 * 1. ModelSelectionScreen - User picks AI model
 * 2. SystemDescriptionScreen - User enters description + clarification
 * 3. GenerationScreen - Code generation, validation, rendering
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { message } from 'antd';
import { useDiagramSession } from './hooks/useDiagramSession';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { ModelSelectionScreen, type ModelId } from './screens/ModelSelectionScreen';
import { SystemDescriptionScreen } from './screens/SystemDescriptionScreen';
import { GenerationScreen } from './screens/GenerationScreen';
import styles from './diagram-wizard.module.css';
import type { ScoreInfo, DiagramUpdate } from '../../services/diagram/diagramApi';
import type { DiagramWizardPersistedState, SavedSession } from './types/persistence';
import { getInitialPersistedState } from './types/persistence';

interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
}

type DiagramType = 'Mermaid' | 'D2' | 'PlantUML';

interface AssistantResponseDetail {
  id: string;
  messageIndex: number;
  message?: string;
  score?: number;
  scoreInfo?: ScoreInfo;
  clarityScore?: number;
  jsonRepresentation?: Record<string, unknown> | null;
  rawUpdate?: Record<string, unknown>;
}

type DiagramUpdateWithVariants = DiagramUpdate & {
  json_representation?: unknown;
  score_info?: ScoreInfo;
  scoreInfo?: ScoreInfo;
};

const phases = [
  { title: 'Analysis', description: 'Understanding your system', icon: '🔍' },
  { title: 'Clarification', description: 'Asking detailed questions', icon: '💬' },
  { title: 'Generation', description: 'Creating diagram code', icon: '✏️' },
  { title: 'Rendering', description: 'Visualizing the diagram', icon: '🎨' },
];

export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
}) => {
  // ============ State Management ============

  // localStorage persistence
  const [persistedState, setPersistedState] = useLocalStorage<DiagramWizardPersistedState>(
    'diagramWizard.v2',
    getInitialPersistedState()
  );

  // Screen navigation
  const [currentScreen, setCurrentScreen] = useState<'model' | 'description' | 'generation'>('model');
  const [selectedModel, setSelectedModel] = useState<ModelId | null>(() => {
    try {
      const saved = localStorage.getItem('diagramWizard.selectedModel');
      return (saved as ModelId) || null;
    } catch {
      return null;
    }
  });

  // User input
  const [userInput, setUserInput] = useState('');
  const [clarificationInput, setClarificationInput] = useState('');
  const [diagramType] = useState<DiagramType>('Mermaid');

  // Session state
  const [isInitializing, setIsInitializing] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [isInAnalysisPhase, setIsInAnalysisPhase] = useState(false);
  const [score, setScore] = useState(0);
  const [assistantResponses, setAssistantResponses] = useState<Record<number, AssistantResponseDetail>>({});
  const [selectedResponse, setSelectedResponse] = useState<AssistantResponseDetail | null>(null);

  // UI state
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const previewContainerRef = useRef<HTMLDivElement>(null);

  // ============ Diagram Session Hook ============

  const {
    sessionId,
    status,
    error,
    chatHistory,
    diagramCode,
    svgOutput,
    clarifications,
    loading,
    sseConnected,
    startSession,
    submitClarification,
    confirmReady,
  } = useDiagramSession({
    onUpdate: (update) => {
      const statusValue = update.status;

      // Track score
      const latestScore = typeof update.score === 'number'
        ? update.score
        : typeof update.assessment_score === 'number'
        ? update.assessment_score
        : undefined;
      if (typeof latestScore === 'number') {
        setScore(latestScore);
      }

      // Track assistant responses
      trackAssistantResponse(update);

      // Handle status changes
      switch (statusValue) {
        case 'waiting':
          console.log('⏳ AI is processing... waiting for response');
          break;
        case 'started':
          setCurrentPhase(1);
          setIsInAnalysisPhase(true);
          message.info('AI received your request and is starting the analysis...');
          break;
        case 'analyzing':
          setCurrentPhase(1);
          message.info('Analyzing your system description...');
          break;
        case 'analysis_complete':
          message.success('Analysis complete!');
          break;
        case 'clarifying':
          setCurrentPhase(2);
          message.info('AI is asking clarifying questions...');
          break;
        case 'clarification_ready':
          message.success('Clarification received. Processing...');
          break;
        case 'can_proceed':
          message.success('Ready to proceed with diagram generation!');
          break;
        case 'diagram_type_determined':
          message.success('Diagram type selected');
          break;
        case 'generating_json':
          setCurrentPhase(2);
          message.loading('Preparing structured data...');
          break;
        case 'generating':
          setCurrentPhase(3);
          message.loading('Generating diagram code...');
          break;
        case 'code_generated':
          message.success('Code generated!');
          break;
        case 'refining':
          message.warning('Refining code...');
          break;
        case 'fallback_fix':
          message.warning('Attempting fallback fix...');
          break;
        case 'code_refined':
          message.success('Code fixed!');
          break;
        case 'rendering':
          message.loading('Rendering SVG...');
          break;
        case 'rendered':
          message.success('Preview ready!');
          break;
        case 'completed':
          setCurrentPhase(4);
          message.success('Complete! ✅');
          // Move to generation screen if still in analysis
          if (currentScreen === 'description') {
            setCurrentScreen('generation');
          }
          // Save session
          if (sessionId && diagramCode && svgOutput) {
            saveSessionToHistory({
              id: sessionId,
              timestamp: Date.now(),
              model: selectedModel || 'default',
              prompt: userInput,
              diagramCode,
              svgOutput,
            } as SavedSession);
            onDiagramGenerated?.(diagramCode, svgOutput);
          }
          break;
        case 'error':
          message.error(`Error: ${update.message || 'Unknown error occurred'}`);
          break;
      }
    },
    onError: (err) => {
      console.error('Session error:', err);
      message.error(`Session error: ${err.message}`);
    },
  });

  // ============ Helper Functions ============

  const normalizeJsonRepresentation = (jsonData: unknown): Record<string, unknown> | null => {
    if (!jsonData) return null;
    if (typeof jsonData === 'string') {
      try {
        return JSON.parse(jsonData);
      } catch (err) {
        console.warn('Failed to parse JSON representation', err);
        return null;
      }
    }
    if (typeof jsonData === 'object') {
      return jsonData as Record<string, unknown>;
    }
    return null;
  };

  const getScoreInfo = (payload?: DiagramUpdateWithVariants): ScoreInfo | undefined => {
    if (!payload) return undefined;
    if (payload.score_info) return payload.score_info;
    if (payload.scoreInfo) return payload.scoreInfo;
    return undefined;
  };

  const trackAssistantResponse = (update: DiagramUpdateWithVariants) => {
    const historyLength = update.history?.length ?? 0;
    if (!historyLength) return;

    const latestIndex = historyLength - 1;
    const latestEntry = update.history?.[latestIndex];
    if (!latestEntry) return;

    const [role, entryContent] = latestEntry;
    if (role !== 'assistant') return;

    const normalizedJson = normalizeJsonRepresentation(
      update.jsonRepresentation ?? update.json_representation ?? null
    ) ?? null;

    setAssistantResponses((prev) => {
      const existing = prev[latestIndex];
      const detail: AssistantResponseDetail = {
        id: existing?.id ?? `${update.session_id}-${latestIndex}`,
        messageIndex: latestIndex,
        message: update.message ?? entryContent ?? existing?.message,
        score:
          typeof update.score === 'number'
            ? update.score
            : typeof update.assessment_score === 'number'
            ? update.assessment_score
            : existing?.score,
        scoreInfo: getScoreInfo(update) ?? existing?.scoreInfo,
        clarityScore:
          typeof update.clarity_score === 'number' ? update.clarity_score : existing?.clarityScore,
        jsonRepresentation: normalizedJson ?? existing?.jsonRepresentation ?? null,
        rawUpdate: update as unknown as Record<string, unknown>,
      };

      if (
        existing &&
        existing.message === detail.message &&
        existing.score === detail.score &&
        existing.clarityScore === detail.clarityScore &&
        existing.scoreInfo === detail.scoreInfo &&
        existing.jsonRepresentation === detail.jsonRepresentation
      ) {
        return prev;
      }

      return {
        ...prev,
        [latestIndex]: detail,
      };
    });
  };

  const saveSessionToHistory = useCallback(
    (session: SavedSession) => {
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
    },
    [persistedState.preferences, setPersistedState]
  );

  // ============ Event Handlers ============

  const handleModelSelect = (modelId: ModelId) => {
    setSelectedModel(modelId);
    try {
      localStorage.setItem('diagramWizard.selectedModel', modelId);
    } catch (err) {
      console.warn('Failed to save model preference to localStorage:', err);
    }
    setCurrentScreen('description');
    message.success(`Selected ${modelId} - ready to start!`);
  };

  const handleChangeModel = () => {
    setCurrentScreen('model');
    setSelectedModel(null);
    setUserInput('');
    setClarificationInput('');
    setCurrentPhase(0);
    setIsInAnalysisPhase(false);
    localStorage.removeItem('diagramWizard.selectedModel');
  };

  const handleStartDiagram = async (prompt: string) => {
    if (!prompt.trim()) {
      message.warning('Please enter a system description');
      return;
    }
    if (!selectedModel) {
      message.warning('Please select an AI model first');
      return;
    }
    if (sessionId || isInitializing || loading) {
      message.warning('Session already in progress');
      return;
    }

    try {
      setIsInitializing(true);
      setCurrentPhase(0);
      console.log('🚀 Starting new diagram session with model:', selectedModel);
      await startSession(prompt, diagramType, selectedModel);
      console.log('✅ Session started, waiting for AI analysis...');
    } catch (err) {
      console.error('❌ Failed to start session:', err);
      message.error(`Failed to start AI analysis: ${err}`);
      setCurrentPhase(0);
    } finally {
      setIsInitializing(false);
      setUserInput('');
    }
  };

  const handleSubmitClarification = async (clarification: string) => {
    if (!clarification.trim()) {
      message.warning('Please provide clarification details');
      return;
    }
    if (!sessionId) {
      message.error('No active session');
      return;
    }

    try {
      await submitClarification(sessionId, clarification);
      setClarificationInput('');
    } catch (err) {
      console.error('Clarification submission failed:', err);
      message.error('Failed to submit clarification');
    }
  };

  const handleConfirmReady = async () => {
    if (!sessionId) {
      message.error('No active session');
      return;
    }

    try {
      await confirmReady(sessionId);
      setCurrentScreen('generation');
    } catch (err) {
      console.error('Confirm ready failed:', err);
      message.error('Failed to confirm ready');
    }
  };

  const handleExportClick = () => {
    setExportModalVisible(true);
  };

  const handleExportModalClose = () => {
    setExportModalVisible(false);
  };

  const handleNewDiagram = () => {
    setCurrentScreen('model');
    setSelectedModel(null);
    setUserInput('');
    setClarificationInput('');
    setCurrentPhase(0);
    setIsInAnalysisPhase(false);
    setScore(0);
    setAssistantResponses({});
    localStorage.removeItem('diagramWizard.selectedModel');
  };

  // ============ Effects ============

  useEffect(() => {
    if (initialPrompt && !sessionId && !isInitializing) {
      setUserInput(initialPrompt);
      console.log('📝 Initial prompt set, waiting for user to start manually');
    }
  }, [initialPrompt, sessionId, isInitializing]);

  useEffect(() => {
    setAssistantResponses({});
    setSelectedResponse(null);
    if (!sessionId) {
      setScore(0);
    }
  }, [sessionId]);

  // ============ Render ============

  // Screen 1: Model Selection
  if (!selectedModel || currentScreen === 'model') {
    return (
      <ModelSelectionScreen
        onSelect={handleModelSelect}
        loading={loading || isInitializing}
      />
    );
  }

  // Screen 2: System Description + Analysis + Clarification
  if (currentScreen === 'description' || (!sessionId && selectedModel)) {
    return (
      <SystemDescriptionScreen
        selectedModel={selectedModel}
        currentPhase={currentPhase}
        phases={phases}
        userInput={userInput}
        loading={loading}
        isInAnalysisPhase={isInAnalysisPhase}
        sessionId={sessionId}
        status={status}
        score={score}
        clarifications={clarifications}
        chatHistory={chatHistory}
        sseConnected={sseConnected}
        onChangeModel={handleChangeModel}
        onStartDiagram={handleStartDiagram}
        onClearInput={() => setUserInput('')}
        onInputChange={setUserInput}
        onSubmitClarification={handleSubmitClarification}
        onConfirmReady={handleConfirmReady}
        error={error}
      />
    );
  }

  // Screen 3: Generation + Rendering
  return (
    <GenerationScreen
      selectedModel={selectedModel}
      currentPhase={currentPhase}
      phases={phases}
      loading={loading}
      sessionId={sessionId}
      status={status}
      score={score}
      diagramCode={diagramCode}
      svgOutput={svgOutput}
      chatHistory={chatHistory}
      clarifications={clarifications}
      sseConnected={sseConnected}
      exportModalOpen={exportModalVisible}
      onChangeModel={handleChangeModel}
      onNewDiagram={handleNewDiagram}
      onExportClick={handleExportClick}
      onExportModalClose={handleExportModalClose}
      onExportSubmit={async (filename, format) => {
        // TODO: Implement export logic
        console.log('Export:', { filename, format, diagramCode, svgOutput });
      }}
      error={error}
    />
  );
};

export default DiagramWizard;
