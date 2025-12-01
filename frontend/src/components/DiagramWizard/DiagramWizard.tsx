/**
 * DiagramWizard Component
 *
 * A comprehensive wizard interface for generating system architecture diagrams using AI.
 * This component orchestrates the entire diagram generation workflow across multiple screens.
 *
 * ## Workflow Phases
 * 1. **Model Selection**: User selects an AI model (gpt5, grok, claude, gemini)
 * 2. **System Description**: User describes their system and engages in clarification Q&A
 * 3. **Generation**: AI generates diagram code (Mermaid/D2/PlantUML)
 * 4. **Rendering**: Diagram is rendered and displayed for preview/export
 *
 * ## Key Features
 * - Multi-tab support: Each tab maintains independent session
 * - Real-time SSE updates: Server-sent events for live processing updates
 * - Clarification loop: AI asks targeted questions to refine understanding
 * - Multiple diagram types: Mermaid, D2, PlantUML support
 * - Session persistence: Completed diagrams saved to local history
 * - Export functionality: Save diagrams as code, SVG, PNG, etc.
 *
 * ## Props
 * @property {Function} onDiagramGenerated - Callback when diagram generation succeeds
 * @property {string} initialPrompt - Pre-filled system description (optional)
 * @property {Function} onClose - Callback when wizard is closed
 * @property {string} tabId - UI tab identifier for session tracking
 * @property {string} sessionId - Pre-assigned backend session ID from tab
 *
 * ## State Management
 * - **Screen Navigation**: Tracks which screen is currently displayed (model/description/generation)
 * - **Session State**: Manages AI model selection, user input, and processing state
 * - **Score Tracking**: Stores clarity scores from AI assessment
 * - **UI State**: Controls modal visibility and error display
 * - **Persistence**: Uses localStorage for session history and preferences
 *
 * ## Session Lifecycle
 * 1. Component mounts with optional pre-assigned sessionId from tab
 * 2. Session created on backend when user clicks "Start Conversation"
 * 3. SSE connection established for real-time updates
 * 4. User clarifies system details through Q&A loop
 * 5. AI generates and refines diagram code
 * 6. User reviews and exports diagram
 * 7. Session cleaned up on component unmount (tab close)
 *
 * ## Integration Points
 * - useDiagramSession: Custom hook managing session lifecycle and API communication
 * - useLocalStorage: Persistence for user preferences and session history
 * - Server-Sent Events: Real-time updates from backend processing
 * - App context: Tab management and session binding
 */

import React, { useState, useEffect, useCallback } from 'react';
import { message, Modal } from 'antd';
import { useDiagramSession } from './hooks/useDiagramSession';
import { useLocalStorage } from '../../hooks/useLocalStorage';
import { ModelSelectionScreen, type ModelId } from './screens/ModelSelectionScreen';
import { SystemDescriptionScreen } from './screens/SystemDescriptionScreen';
import { DiagramTypeSelectionScreen } from './screens/DiagramTypeSelectionScreen';
import { GenerationScreen } from './screens/GenerationScreen';
import type { DiagramWizardPersistedState, SavedSession } from './types/persistence';
import { getInitialPersistedState } from './types/persistence';
import { DiagramApi } from '../../services/diagram/diagramApi';
import { parseAndShowToast } from '../../utils/toastHelper';

/**
 * Props for the DiagramWizard component
 *
 * @interface DiagramWizardProps
 * @property {Function} [onDiagramGenerated] - Callback invoked when diagram generation completes successfully.
 *                                            Receives generated diagram code and SVG rendering.
 * @property {string} [initialPrompt] - Pre-filled system description to initialize user input
 * @property {Function} [onClose] - Callback invoked when user closes the wizard (via tab close or error modal)
 * @property {string} [tabId] - Unique identifier for the UI tab containing this wizard instance.
 *                              Used for session tracking and multi-tab support.
 * @property {string} [sessionId] - Pre-assigned backend session ID from the parent tab.
 *                                  Allows session lifecycle to be bound to tab lifecycle.
 */
/**
 * DiagramWizardProps type definition
 * 
 * Describes the structure and properties of DiagramWizardProps
 */
interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
  onClose?: () => void;
  tabId?: string;
  sessionId?: string;
}

type DiagramType = 'Mermaid' | 'D2' | 'PlantUML';

const phases = [
  { title: 'Analysis', description: 'Understanding your system', icon: '🔍' },
  { title: 'Clarification', description: 'Asking detailed questions', icon: '💬' },
  { title: 'Generation', description: 'Creating diagram code', icon: '✏️' },
  { title: 'Rendering', description: 'Visualizing the diagram', icon: '🎨' },
];

/**
 * DiagramWizard component
 */
export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
  onClose,
  tabId: _tabId, // eslint-disable-next-line @typescript-eslint/no-unused-vars
  sessionId: initialSessionId,
}) => {
  // ============ State Management ============

  // localStorage persistence - stores user preferences, session history, and stats
  // Uses versioned key 'diagramWizard.v2' to allow schema migrations
  const [persistedState, setPersistedState] = useLocalStorage<DiagramWizardPersistedState>(
    'diagramWizard.v2',
    getInitialPersistedState()
  );

  // Screen navigation - controls which UI screen is visible to user
  // Possible values: 'model' (AI selection), 'description' (input/clarification), 'diagramTypeSelection' (choose diagram type), 'generation' (result display)
  const [currentScreen, setCurrentScreen] = useState<'model' | 'description' | 'diagramTypeSelection' | 'generation'>('model');

  // Selected AI model - initialized from localStorage to remember user's last choice
  const [selectedModel, setSelectedModel] = useState<ModelId | null>(() => {
    try {
      // Attempt to restore previously selected model from localStorage
      const saved = localStorage.getItem('diagramWizard.selectedModel');
      return (saved as ModelId) || null;
    } catch {
      // If localStorage read fails, start with no selection
      return null;
    }
  });

  // User input - stores the system description text before session starts
  const [userInput, setUserInput] = useState('');

  // Diagram type - currently hardcoded to Mermaid (future: user selectable)
  const [diagramType] = useState<DiagramType>('Mermaid');

  // Session state - tracks initialization and processing phases
  const [isInitializing, setIsInitializing] = useState(false); // True while startSession API call is pending
  const [currentPhase, setCurrentPhase] = useState(0); // 0-4 index into phases array (Analysis -> Clarification -> Generation -> Rendering)
  const [isInAnalysisPhase, setIsInAnalysisPhase] = useState(false); // True when AI is analyzing initial description
  const [score, setScore] = useState(0); // Clarity score (0-100) from AI assessment
  const [scoreTarget, setScoreTarget] = useState(80); // Target score from backend .env (default: 80)

  // Diagram type selection state
  const [recommendedDiagramType, setRecommendedDiagramType] = useState<string>('Mermaid'); // AI-recommended diagram type
  const [keywordScores, setKeywordScores] = useState<{ [key: string]: number }>({
    Mermaid: 25,
    D2: 25,
    PlantUML: 25,
    Structurizr: 25,
  }); // Suitability scores for each diagram type
  const [diagramAnalysisText, setDiagramAnalysisText] = useState<string>(''); // Text shown on diagram type selection screen
  const [diagramTypeSelected, setDiagramTypeSelected] = useState<boolean>(false); // Whether user picked a type yet
  const [jsonGenerationOutput, setJsonGenerationOutput] = useState<string>(''); // Raw AI output from JSON generation

  // UI state - controls modal visibility and error display
  const [exportModalVisible, setExportModalVisible] = useState(false); // Export options modal
  const [errorModalVisible, setErrorModalVisible] = useState(false); // Critical error modal (closes tab)
  const [errorDetails, setErrorDetails] = useState({ title: '', message: '' }); // Error content for modal

  // ============ Diagram Session Hook ============

  // Custom hook that manages the entire diagram session lifecycle
  // Provides: session state, API methods, SSE connection status, error handling
  const {
    sessionId,          // Backend session UUID (null until session starts)
    status,            // Current session status object with history, clarifications, diagram code, etc.
    error,             // Error object if session fails
    loading,           // True when API request is in flight
    sseConnected,      // True when Server-Sent Events connection is active
    startSession,      // Function to initiate new diagram session with user's prompt
    submitClarification, // Function to send clarification responses back to AI
    confirmReady,      // Function to signal readiness to proceed with diagram generation
    endSession,        // Function to cleanup session on backend (called on unmount)
  } = useDiagramSession({
    initialSessionId,  // Pre-assigned session ID from tab (enables session-tab binding)
    onUpdate: (update) => {
      // Callback triggered whenever SSE sends status update from backend
      const statusValue = update.status;

      // ============ Toast Command Processing ============
      // Check if the message contains a toast command (TOASTINFO, TOASTERROR, etc.)
      // This allows backend to explicitly trigger toasts by including keywords in messages
      if (update.message && typeof update.message === 'string') {
        parseAndShowToast(update.message);
      }

      // Extract and update clarity score from multiple possible fields
      // Backend may send 'score' or 'assessment_score' depending on processing stage
      const latestScore = typeof update.score === 'number'
        ? update.score
        : typeof update.assessment_score === 'number'
        ? update.assessment_score
        : undefined;
      if (typeof latestScore === 'number') {
        // Update UI score display (0-100 scale)
        setScore(latestScore);
      }

      // Extract and update score target from backend if provided
      if (typeof update.score_target === 'number') {
        setScoreTarget(update.score_target);
      }
      if (update.json_generation_output) {
        setJsonGenerationOutput(update.json_generation_output);
      }

      // Handle different session status values and update UI accordingly
      // Status transitions: started -> analyzing -> clarifying -> generating -> rendering -> completed
      switch (statusValue) {
        case 'waiting':
          // AI is processing the request - no UI update needed, just log
          console.log('⏳ AI is processing... waiting for response');
          break;
        case 'started':
          // Session has been created, AI beginning analysis of user's description
          setCurrentPhase(1); // Move to "Analysis" phase in UI
          setIsInAnalysisPhase(true); // Enable analysis UI indicators
          message.info('AI received your request and is starting the analysis...');
          break;
        case 'analyzing':
          // AI actively analyzing system description for clarity and completeness
          setCurrentPhase(1); // Stay in "Analysis" phase
          message.info('Analyzing your system description...');
          break;
        case 'analysis_complete':
          // AI has finished initial analysis, may proceed to clarification or generation
          message.success('Analysis complete!');
          break;
        case 'clarifying':
          // AI is formulating clarification questions based on gaps in description
          setCurrentPhase(2); // Move to "Clarification" phase in UI
          message.info('AI is asking clarifying questions...');
          break;
        case 'clarification_ready':
          // User submitted clarification response, AI processing it
          message.success('Clarification received. Processing...');
          break;
        case 'can_proceed':
          // AI determined it has sufficient information to generate diagram
          message.success('Ready to proceed with diagram generation!');
          break;
      case 'json_generated':
        // JSON representations produced
        message.success('Architecture JSON generated!');
        setIsInAnalysisPhase(false);
        break;
      case 'awaiting_diagram_type_selection':
        // AI has analyzed diagram options and is waiting for user to select preferred type
        message.info('Analyzing content to recommend the best diagram type...');
        setIsInAnalysisPhase(false);
        // Extract diagram type options and scores from update
        if (update.recommended_diagram_type) {
          setRecommendedDiagramType(update.recommended_diagram_type);
        }
        if (update.keyword_scores) {
        setKeywordScores(update.keyword_scores);
      }
      if (update.analysis_text) {
        setDiagramAnalysisText(update.analysis_text);
      }
      setDiagramTypeSelected(false);
      // Navigate to diagram type selection screen
      setCurrentScreen('diagramTypeSelection');
      break;
      case 'diagram_type_selected':
        // User selected diagram type, AI proceeding to code generation
        message.success('Diagram type selected');
        setDiagramTypeSelected(true);
        setIsInAnalysisPhase(false);
        // Navigate to generation screen
        setCurrentScreen('generation');
        break;
      case 'generating_json':
        // AI creating structured JSON representation of system architecture
        setCurrentPhase(2); // Stay in preparation phase
        message.loading('Preparing structured data...');
        setIsInAnalysisPhase(false);
        break;
      case 'generating':
        // AI actively generating diagram code from structured data
        setCurrentPhase(3); // Move to "Generation" phase in UI
        message.loading('Generating diagram code...');
        setIsInAnalysisPhase(false);
        break;
      case 'code_generated':
        // Diagram code has been successfully generated
        message.success('Code generated!');
        setIsInAnalysisPhase(false);
        break;
      case 'refining':
        // Diagram code had validation errors, AI attempting to fix them
        message.warning('Refining code...');
        setIsInAnalysisPhase(false);
        break;
      case 'fallback_fix':
        // Primary refinement failed, attempting fallback fix strategy
        message.warning('Attempting fallback fix...');
        setIsInAnalysisPhase(false);
        break;
      case 'code_refined':
        // Validation errors resolved, code is now valid
        message.success('Code fixed!');
        setIsInAnalysisPhase(false);
        break;
      case 'rendering':
        // Backend rendering diagram code to SVG using appropriate renderer
        message.loading('Rendering SVG...');
        setIsInAnalysisPhase(false);
        break;
      case 'rendered':
        // SVG successfully generated and ready for display
        message.success('Preview ready!');
        setIsInAnalysisPhase(false);
        if (!diagramTypeSelected) {
          // If user hasn't picked a type yet, stay on selection screen
          setCurrentScreen('diagramTypeSelection');
          break;
        }
        break;
      case 'completed':
        // Entire workflow complete: analysis -> clarification -> generation -> rendering
        setCurrentPhase(4); // Move to final "Rendering" phase
        message.success('Complete! ✅');
        setIsInAnalysisPhase(false);

        // Navigate to generation screen if user is still on description screen
        if (currentScreen === 'description' && diagramTypeSelected) {
          setCurrentScreen('generation');
          }

          // Persist completed session to localStorage for history/replay
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

            // Notify parent component (if provided) that diagram is ready
            onDiagramGenerated?.(diagramCode, svgOutput);
          }
          break;
        case 'error':
          // Recoverable error occurred during processing
          message.error(`Error: ${update.message || 'Unknown error occurred'}`);
          break;
        case 'failed':
          // Critical failure - show error modal and allow user to close tab
          setErrorDetails({
            title: 'Diagram Generation Failed',
            message: update.error || update.message || 'An unexpected error occurred during diagram generation. Please check your configuration and try again.',
          });
          setErrorModalVisible(true);
          break;
      }
    },
    onError: (err) => {
      // Handle session-level errors (network failures, SSE disconnections, etc.)
      console.error('Session error:', err);
      message.error(`Session error: ${err.message}`);
    },
  });

  // ============ Data Extraction from Session Status ============

  // Extract conversation history from session status
  // Backend sends history as array of [role, content] tuples
  const rawHistory = status?.history ?? [];

  // Find the index of the last assistant message to attach metadata to
  const lastAssistantMessageIndex = rawHistory.reduce((lastIndex, item, index) => {
    const role = Array.isArray(item) ? item[0] : (item as any).role;
    return role === 'assistant' ? index : lastIndex;
  }, -1);

  // Transform tuples into properly typed message objects for UI display
  const chatHistory = rawHistory.map((item, index) => {
    // Handle both tuple format [role, content] and object format {role, content}
    const [role, content] = Array.isArray(item) ? item : [(item as any).role, (item as any).content];

    // Create base message object with role and content
    const messageObj: any = {
      role: role as 'user' | 'assistant',
      content: content || '',
    };

    // Determine if this is the most recent AI response
    const isLatestAssistantMessage = role === 'assistant' &&
      index === lastAssistantMessageIndex;

    // Attach additional metadata only to the latest AI message
    if (isLatestAssistantMessage) {
      // Include clarity score if AI provided assessment
      if (typeof status?.clarity_score === 'number') {
        messageObj.score = status.clarity_score;
      }

      // Include structured JSON representation if AI extracted system architecture
      if (status?.jsonRepresentation && Object.keys(status.jsonRepresentation).length > 0) {
        messageObj.jsonData = status.jsonRepresentation;
      }

      // Include full AI response for debugging (if available)
      if (status?.full_ai_response) {
        messageObj.fullAiResponse = status.full_ai_response;
      }

      // Include analysis summary and question for table display
      if (status?.analysis_summary) {
        messageObj.analysisSummary = status.analysis_summary;
      }
      if (status?.question) {
        messageObj.question = status.question;
      }
    }

    return messageObj;
  });

  // Extract generated diagram code (Mermaid/D2/PlantUML syntax)
  const diagramCode = status?.diagramCode ?? '';

  // Extract rendered SVG output (ready for display/export)
  const svgOutput = status?.svgOutput ?? '';

  // Debug: Log SVG output length when it changes
  React.useEffect(() => {
    if (svgOutput) {
      console.log('[DiagramWizard] SVG Output received:', svgOutput.substring(0, 100) + '... (length: ' + svgOutput.length + ')');
    }
  }, [svgOutput]);

  const structurizrWorkspace = (status as any)?.structurizr_workspace || '';
  const cleanStructurizr = (status as any)?.clean_structurizr || '';
  const jsonRepresentation = status?.jsonRepresentation ?? null;

  // Extract clarification questions from AI, normalizing to object format
  const clarifications = (status?.clarifications ?? []).map(q =>
    typeof q === 'string' ? { question: q } : q
  );

  // ============ Helper Functions ============

  // Persist completed session to localStorage for history/replay functionality
  const saveSessionToHistory = useCallback(
    (session: SavedSession) => {
      // Respect user's privacy preference - don't save if disabled
      if (!persistedState.preferences.keepSessionHistory) return;

      setPersistedState((prev) => {
        // Add new session to front of history array, limit to max items
        const newHistory = [session, ...prev.sessionHistory].slice(
          0,
          prev.preferences.maxHistoryItems
        );

        // Update persisted state with new history and updated stats
        return {
          ...prev,
          sessionHistory: newHistory, // Updated history array
          lastSession: session,        // Quick access to most recent session
          stats: {
            ...prev.stats,
            totalSessions: prev.stats.totalSessions + 1,                   // Increment total counter
            successfulGenerations: prev.stats.successfulGenerations + 1,   // Increment success counter
            lastUsed: Date.now(),                                          // Update timestamp
          },
        };
      });
    },
    [persistedState.preferences, setPersistedState]
  );

  // ============ Event Handlers ============

  // Handle AI model selection from ModelSelectionScreen
  const handleModelSelect = (modelId: ModelId) => {
    // Store selected model in component state
    setSelectedModel(modelId);

    // Persist model choice to localStorage for next session
    try {
      localStorage.setItem('diagramWizard.selectedModel', modelId);
    } catch (err) {
      console.warn('Failed to save model preference to localStorage:', err);
    }

    // Navigate to system description screen
    setCurrentScreen('description');

    // Show success feedback to user
    message.success(`Selected ${modelId} - ready to start!`);
  };

  // Handle user requesting to change AI model (reset workflow)
  const handleChangeModel = () => {
    // Navigate back to model selection screen
    setCurrentScreen('model');

    // Clear all session state to start fresh
    setSelectedModel(null);
    setUserInput('');
    setCurrentPhase(0);
    setIsInAnalysisPhase(false);

    // Remove persisted model preference
    localStorage.removeItem('diagramWizard.selectedModel');
  };

  // Handle user clicking "Start Conversation" to begin diagram generation
  const handleStartDiagram = async (prompt: string) => {
    // Validate user input is not empty
    if (!prompt.trim()) {
      message.warning('Please enter a system description');
      return;
    }

    // Ensure model was selected
    if (!selectedModel) {
      message.warning('Please select an AI model first');
      return;
    }

    // Prevent multiple concurrent sessions
    if (sessionId || isInitializing || loading) {
      message.warning('Session already in progress');
      return;
    }

    try {
      // Set loading state to show spinner
      setIsInitializing(true);

      // Reset phase and score for new session
      setCurrentPhase(0);
      setScore(0);

      console.log('🚀 Starting new diagram session with model:', selectedModel);

      // Call API to create session and begin AI analysis
      await startSession(prompt, diagramType, selectedModel);

      console.log('✅ Session started, waiting for AI analysis...');
    } catch (err) {
      // Handle session creation failure
      console.error('❌ Failed to start session:', err);
      message.error(`Failed to start AI analysis: ${err}`);
      setCurrentPhase(0);
    } finally {
      // Clear loading state and input field
      setIsInitializing(false);
      setUserInput('');
    }
  };

  // Handle user submitting clarification response to AI's questions
  const handleSubmitClarification = async (clarification: string) => {
    // Validate clarification is not empty
    if (!clarification.trim()) {
      message.warning('Please provide clarification details');
      return;
    }

    // Ensure session is active
    if (!sessionId) {
      message.error('No active session');
      return;
    }

    try {
      // Send clarification to backend, which triggers AI processing
      await submitClarification(clarification);
    } catch (err) {
      console.error('Clarification submission failed:', err);
      message.error('Failed to submit clarification');
    }
  };

  // Handle user clicking "Ready to Generate" to skip further clarifications
  const handleConfirmReady = async () => {
    // Ensure session is active
    if (!sessionId) {
      message.error('No active session');
      return;
    }

    try {
      // Signal backend that user is satisfied with clarification
      await confirmReady();

      // Wait for backend to send 'awaiting_diagram_type_selection' before navigating
    } catch (err) {
      console.error('Confirm ready failed:', err);
      message.error('Failed to confirm ready');
    }
  };

  // Handle user selecting diagram type
  const handleSelectDiagramType = async (diagramType: string) => {
    // Ensure session is active
    if (!sessionId) {
      message.error('No active session');
      return;
    }

    try {
      // Send diagram type selection to backend
      await DiagramApi.selectDiagramType(sessionId, diagramType);
      message.success(`${diagramType} diagram selected`);
      setDiagramTypeSelected(true);

      // Immediately move to generation screen while backend continues workflow
      setCurrentScreen('generation');
      setCurrentPhase(3); // Generation phase indicator

      // Note: Navigation to generation screen happens via SSE update
      // Backend sends 'diagram_type_selected' status which triggers navigation
    } catch (err) {
      console.error('Select diagram type failed:', err);
      message.error('Failed to select diagram type');
    }
  };

  // Handle user clicking export button
  const handleExportClick = () => {
    // Show export modal with format options
    setExportModalVisible(true);
  };

  // Handle closing export modal
  const handleExportModalClose = () => {
    // Hide export modal
    setExportModalVisible(false);
  };

  // Handle user clicking "New Diagram" to start completely fresh
  const handleNewDiagram = () => {
    // Navigate back to model selection
    setCurrentScreen('model');

    // Reset all state to initial values
    setSelectedModel(null);
    setUserInput('');
    setCurrentPhase(0);
    setIsInAnalysisPhase(false);
    setScore(0);
    setDiagramAnalysisText('');

    // Clear persisted model preference
    localStorage.removeItem('diagramWizard.selectedModel');
  };

  // ============ Effects ============

  // Effect: Populate input field with initialPrompt prop if provided
  useEffect(() => {
    if (initialPrompt && !sessionId && !isInitializing) {
      // Set user input to pre-filled prompt (doesn't auto-start session)
      setUserInput(initialPrompt);
      console.log('📝 Initial prompt set, waiting for user to start manually');
    }
  }, [initialPrompt, sessionId, isInitializing]);

  // Effect: Reset score and scoreTarget when session ends
  useEffect(() => {
    if (!sessionId) {
      // No active session means no valid score - reset to defaults
      setScore(0);
      setScoreTarget(80);
      setDiagramAnalysisText('');
      setDiagramTypeSelected(false);
      setJsonGenerationOutput('');
    }
  }, [sessionId]);

  // Effect: Cleanup backend session when component unmounts (tab closed)
  useEffect(() => {
    return () => {
      // Cleanup function runs when component is destroyed
      if (sessionId) {
        // Tell backend to cleanup session resources (memory, SSE connection, etc.)
        endSession().catch(err => {
          console.error('Error cleaning up diagram session:', err);
        });
      }
    };
  }, [sessionId, endSession]);

  // ============ Render ============

  // Handle error modal OK button - close the Whysper tab on critical failure
  const handleErrorModalOk = () => {
    // Hide error modal
    setErrorModalVisible(false);

    // Attempt to close the Whysper tab using onClose callback
    if (onClose) {
      onClose();
    } else {
      // Fallback: try to close browser tab programmatically
      window.close();

      // If close() fails (can only close tabs opened by script), redirect
      setTimeout(() => {
        window.location.href = 'about:blank';
      }, 100);
    }
  };

  // Determine which screen to render based on current state
  let screenContent;

  // Screen 1: Model Selection
  // Show if no model selected OR user explicitly navigated back
  if (!selectedModel || currentScreen === 'model') {
    screenContent = (
      <ModelSelectionScreen
        onSelect={handleModelSelect}
        loading={loading || isInitializing}
      />
    );
  }
  // Screen 2: System Description + Analysis + Clarification
  // Show if model selected but no session started OR explicit description screen navigation
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
        scoreTarget={scoreTarget}
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
  // Screen 3: Diagram Type Selection
  // Show after clarification phase when user confirms ready
  else if (currentScreen === 'diagramTypeSelection') {
    screenContent = (
      <DiagramTypeSelectionScreen
        selectedModel={selectedModel}
        currentPhase={currentPhase}
        phases={phases}
        sessionId={sessionId}
        score={score}
        scoreTarget={scoreTarget}
        sseConnected={sseConnected}
        loading={loading}
        recommendedDiagramType={recommendedDiagramType}
        keywordScores={keywordScores}
        analysisText={diagramAnalysisText}
        onSelectDiagramType={handleSelectDiagramType}
      />
    );
  }
  // Screen 4: Generation + Rendering
  // Show once session is active and user has moved to generation phase
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
        scoreTarget={scoreTarget}
        diagramCode={diagramCode}
        svgOutput={svgOutput}
        chatHistory={chatHistory}
        clarifications={clarifications}
        sseConnected={sseConnected}
        exportModalOpen={exportModalVisible}
        structurizrWorkspace={structurizrWorkspace}
        cleanStructurizr={cleanStructurizr}
        jsonRepresentation={jsonRepresentation}
        onChangeModel={handleChangeModel}
        onNewDiagram={handleNewDiagram}
        onExportClick={handleExportClick}
        onExportModalClose={handleExportModalClose}
        onExportSubmit={async (filename, format) => {
          // TODO: Implement export logic (download diagram as file)
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
