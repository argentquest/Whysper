/**
 * DiagramWizard Component (Refactored)
 *
 * Main component for the diagram generation wizard interface.
 * Orchestrates three distinct screens:
 * 1. ModelSelectionScreen - User picks AI model
 * 2. SystemDescriptionScreen - User enters description + clarification
 * 3. GenerationScreen - Code generation, validation, rendering
 */

import React, { useState, useEffect, useCallback } from 'react';
import { message, Modal } from 'antd';
import { useDiagramSession } from './hooks/useDiagramSession';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { ModelSelectionScreen, type ModelId } from './screens/ModelSelectionScreen';
import { SystemDescriptionScreen } from './screens/SystemDescriptionScreen';
import { GenerationScreen } from './screens/GenerationScreen';
import type { DiagramWizardPersistedState, SavedSession } from './types/persistence';
import { getInitialPersistedState } from './types/persistence';

interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
  onClose?: () => void;
}

type DiagramType = 'Mermaid' | 'D2' | 'PlantUML';

const phases = [
  { title: 'Analysis', description: 'Understanding your system', icon: '🔍' },
  { title: 'Clarification', description: 'Asking detailed questions', icon: '💬' },
  { title: 'Generation', description: 'Creating diagram code', icon: '✏️' },
  { title: 'Rendering', description: 'Visualizing the diagram', icon: '🎨' },
];

export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
  onClose,
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
  const [diagramType] = useState<DiagramType>('Mermaid');

  // Session state
  const [isInitializing, setIsInitializing] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [isInAnalysisPhase, setIsInAnalysisPhase] = useState(false);
  const [score, setScore] = useState(0);

  // UI state
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [errorModalVisible, setErrorModalVisible] = useState(false);
  const [errorDetails, setErrorDetails] = useState({ title: '', message: '' });

  // ============ Diagram Session Hook ============

  const {
    sessionId,
    status,
    error,
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
              sessionId: sessionId,
              timestamp: Date.now(),
              initialPrompt: userInput,
              diagramType: diagramType,
              diagramCode,
              svgOutput,
              conversationHistory: chatHistory,
              score: score,
            });
            onDiagramGenerated?.(diagramCode, svgOutput);
          }
          break;
        case 'error':
          message.error(`Error: ${update.message || 'Unknown error occurred'}`);
          break;
        case 'failed':
          // Show error modal popup
          setErrorDetails({
            title: 'Diagram Generation Failed',
            message: update.error || update.message || 'An unexpected error occurred during diagram generation. Please check your configuration and try again.',
          });
          setErrorModalVisible(true);
          break;
      }
    },
    onError: (err) => {
      console.error('Session error:', err);
      message.error(`Session error: ${err.message}`);
    },
  });

  // Extract data from status
  // Convert history from tuples [role, content] to message objects
  const rawHistory = status?.history ?? [];
  const chatHistory = rawHistory.map((item, index) => {
    const [role, content] = Array.isArray(item) ? item : [item.role, item.content];

    // Add score and JSON data for the latest assistant message
    const messageObj: any = {
      role: role as 'user' | 'assistant',
      content: content || '',
    };

    // Only show score/JSON on the latest assistant message
    const isLatestAssistantMessage = role === 'assistant' &&
      index === rawHistory.length - 1;

    if (isLatestAssistantMessage) {
      // Include score if available in status
      if (typeof status?.clarity_score === 'number') {
        messageObj.score = status.clarity_score;
      }

      // Include JSON representation if available
      if (status?.jsonRepresentation && Object.keys(status.jsonRepresentation).length > 0) {
        messageObj.jsonData = status.jsonRepresentation;
      }
    }

    return messageObj;
  });
  const diagramCode = status?.diagramCode ?? '';
  const svgOutput = status?.svgOutput ?? '';
  const clarifications = (status?.clarifications ?? []).map(q =>
    typeof q === 'string' ? { question: q } : q
  );

  // ============ Helper Functions ============

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
      setScore(0); // Clear score when starting new diagram
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
      await submitClarification(clarification);
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
      await confirmReady();
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
    setCurrentPhase(0);
    setIsInAnalysisPhase(false);
    setScore(0);
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
    if (!sessionId) {
      setScore(0);
    }
  }, [sessionId]);

  // ============ Render ============

  // Handler for error modal OK button - close the Whysper tab
  const handleErrorModalOk = () => {
    setErrorModalVisible(false);
    // Close the Whysper tab if callback provided
    if (onClose) {
      onClose();
    } else {
      // Fallback: close browser tab
      window.close();
      setTimeout(() => {
        window.location.href = 'about:blank';
      }, 100);
    }
  };

  // Render the appropriate screen
  let screenContent;

  // Screen 1: Model Selection
  if (!selectedModel || currentScreen === 'model') {
    screenContent = (
      <ModelSelectionScreen
        onSelect={handleModelSelect}
        loading={loading || isInitializing}
      />
    );
  }
  // Screen 2: System Description + Analysis + Clarification
  else if (currentScreen === 'description' || (!sessionId && selectedModel)) {
    screenContent = (
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
        error={error ? { message: error.message } : undefined}
      />
    );
  }
  // Screen 3: Generation + Rendering
  else {
    screenContent = (
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
        error={error ? { message: error.message } : undefined}
      />
    );
  }

  return (
    <>
      {screenContent}

      {/* Error Modal - Shows when diagram generation fails */}
      <Modal
        title={errorDetails.title}
        open={errorModalVisible}
        onOk={handleErrorModalOk}
        onCancel={handleErrorModalOk}
        closable={false}
        maskClosable={false}
        okText="OK"
        cancelButtonProps={{ style: { display: 'none' } }}
        centered
      >
        <div style={{ padding: '20px 0' }}>
          <p style={{ fontSize: '14px', marginBottom: '16px' }}>
            {errorDetails.message}
          </p>
          <p style={{ fontSize: '12px', color: '#999' }}>
            Click OK to close this tab.
          </p>
        </div>
      </Modal>
    </>
  );
};

export default DiagramWizard;
