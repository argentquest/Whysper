/**
 * SystemDescriptionScreen Component
 *
 * Second screen of DiagramWizard workflow: Handles system description input,
 * analysis initiation, and interactive clarification phase.
 *
 * ## Screen Phases
 * 1. **Input Phase**: User enters system description and clicks "Start Conversation"
 * 2. **Analysis Phase**: AI analyzes description, provides initial score and questions
 * 3. **Clarification Phase**: Interactive Q&A loop where AI asks targeted questions
 * 4. **Ready Phase**: User confirms they're done, AI generates diagram code
 *
 * ## Key Features
 * - **Real-time Scoring**: Shows clarity_score (1-10) with color coding
 * - **JSON Representation**: Displays structured architecture data as diagram progresses
 * - **Live Chat Panel**: Shows conversation history with both user and AI messages
 * - **Score Tracking**: Color-coded badges (green ≥8, blue 6-7, orange <6)
 * - **Session Status**: Displays connected/disconnected state for SSE connection
 * - **Progress Indicator**: Shows current phase in multi-step wizard
 * - **Confirmation Button**: Appears when AI determines system is understood
 *
 * ## Layout
 * ```
 * Header (Model, Session ID, Connection Status)
 *   ↓
 * Progress Steps (Analysis → Clarification → Generation → Rendering)
 *   ↓
 * Conditional Content:
 *   If Input Phase:
 *     - Text area for system description
 *     - "Start Conversation" button
 *     - "Clear" button
 *   If Analysis/Clarification Phase:
 *     - Score display with badge
 *     - JSON Representation (collapsible)
 *     - Chat Panel with message history
 *     - Input field for responses
 * ```
 *
 * ## Data Flow
 * User Input → onStartDiagram() → Backend Analysis → SSE Updates → Score Display
 * AI Question → Chat Panel Display → User Response → onSubmitClarification() → AI Evaluation
 *
 * ## Props Integration
 * - `userInput`, `onInputChange`: Control textarea value
 * - `status`: Contains latest analysis results (score, json_representation)
 * - `chatHistory`: Displays conversation between user and AI
 * - `score`: Clarity score from AI assessment (0-10)
 * - `clarifications`: List of AI questions asked
 *
 * ## Session Management
 * - Session starts when user clicks "Start Conversation"
 * - sessionId provided by parent component (tied to tab)
 * - SSE connection shows real-time status updates
 * - Cleanup happens automatically when tab closes
 */

import React, { useRef } from 'react';
import { Layout, Button, Alert, message, Space, Tag, Modal } from 'antd';
import { SendOutlined, ClearOutlined, LeftOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import styles from '../diagram-wizard.module.css';
import ChatPanel from '../panels/Panel1_Chat';
import DiagramWizardHeader from '../components/DiagramWizardHeader';
import type { ModelId } from './ModelSelectionScreen';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';

/**
 * Props for SystemDescriptionScreen component
 *
 * @interface SystemDescriptionScreenProps
 * @property {ModelId} selectedModel - Currently selected AI model (gpt5, grok, claude, gemini)
 * @property {number} currentPhase - Current phase index (0-3) for progress indicator
 * @property {Array} phases - Array of phase objects with title, description, and icon
 * @property {string} userInput - Current value of system description textarea
 * @property {boolean} loading - Whether a request is being processed
 * @property {boolean} isInAnalysisPhase - Whether currently in analysis/clarification phase
 * @property {string | null} sessionId - Unique session ID from backend (null if not started)
 * @property {DiagramUpdate | null} status - Latest status update from backend (includes scores, json_representation)
 * @property {number} score - Current clarity_score (0-10) from AI assessment
 * @property {number} scoreTarget - Target clarity_score (usually 80)
 * @property {Array} clarifications - List of clarification questions asked by AI
 * @property {Array} chatHistory - Array of message objects with role, content, and optional score/jsonData
 * @property {boolean} sseConnected - Whether SSE connection to backend is active
 * @property {Function} onChangeModel - Callback to return to model selection screen
 * @property {Function} onStartDiagram - Callback when user clicks "Start Conversation" with system description
 * @property {Function} onClearInput - Callback to clear textarea content
 * @property {Function} onInputChange - Callback when textarea content changes (value parameter)
 * @property {Function} onSubmitClarification - Callback when user submits response to clarification question
 * @property {Function} onConfirmReady - Callback when user confirms they're done with clarifications
 * @property {Object} [error] - Optional error object with message property for displaying errors
 */
/**
 * SystemDescriptionScreenProps type definition
 * 
 * Describes the structure and properties of SystemDescriptionScreenProps
 */
interface SystemDescriptionScreenProps {
  selectedModel: ModelId;
  currentPhase: number;
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>;
  userInput: string;
  loading: boolean;
  isInAnalysisPhase: boolean;
  sessionId: string | null;
  status: DiagramUpdate | null;
  score: number;
  scoreTarget: number;
  clarifications: Array<{ question: string; answer?: string }>;
  chatHistory: any[];
  sseConnected: boolean;
  onChangeModel: () => void;
  onStartDiagram: (prompt: string) => void;
  onClearInput: () => void;
  onInputChange: (value: string) => void;
  onSubmitClarification: (clarification: string) => void;
  onConfirmReady: () => void;
  error?: { message: string };
}

/**
 * SystemDescriptionScreen component
 */
export const SystemDescriptionScreen: React.FC<SystemDescriptionScreenProps> = ({
  selectedModel,
  currentPhase,
  phases,
  userInput,
  loading,
  isInAnalysisPhase,
  sessionId,
  status,
  score,
  scoreTarget,
  clarifications,
  chatHistory,
  sseConnected,
  onChangeModel,
  onStartDiagram,
  onClearInput,
  onInputChange,
  onSubmitClarification,
  onConfirmReady,
  error,
}) => {
  const promptEditorRef = useRef<any>(null);
  // Show input field during clarification phase (includes initial analysis and follow-up questions)
  // Keep input visible as long as we're in analysis phase (hasn't moved to generation yet)
  const isClarifying = !!(isInAnalysisPhase && sessionId && (
    status?.status === 'clarifying' ||
    status?.status === 'analysis_complete' ||
    status?.status === 'waiting' ||
    status?.status === 'analyzing'
  ));
  // Loosen visibility: allow confirm button anytime we're in an active analysis/clarification session
  // Hide only after we leave the analysis phase (e.g., generating/rendering/completed/failed)
  const canConfirmReady = !!(sessionId && isInAnalysisPhase);

  // Debug logging
  console.log('[SystemDescriptionScreen] Debug:', {
    statusValue: status?.status,
    isClarifying,
    canConfirmReady,
    sessionActive: !!sessionId,
    isInAnalysisPhase,
    isLoading: loading,
    sessionId,
    score,
    scoreTarget,
    awaiting_user_confirmation: status?.awaiting_user_confirmation
  });

  // Additional debug for button visibility
  console.log('[SystemDescriptionScreen] Button visibility:', {
    canConfirmReady,
    'status?.status': status?.status,
    'status === can_proceed': status?.status === 'can_proceed',
    'status === clarification_ready': status?.status === 'clarification_ready'
  });

  const handleStart = () => {
    if (!userInput.trim()) {
      message.warning('Please enter a system description');
      return;
    }
    onStartDiagram(userInput);
  };

  const handleClearAndChangeModel = () => {
    Modal.confirm({
      title: 'Change AI Model?',
      content: 'Are you sure you want to select a different model? Your current session will be reset.',
      okText: 'Yes, Change Model',
      cancelText: 'Cancel',
      onOk() {
        onChangeModel();
      },
    });
  };

  return (
    <Layout className={styles.diagramWizard}>
      {/* Unified Header Component */}
      <DiagramWizardHeader
        selectedModel={selectedModel}
        sessionId={sessionId}
        sseConnected={sseConnected}
        loading={loading}
        score={score}
        scoreTarget={scoreTarget}
        currentPhase={currentPhase}
        phases={phases}
        canConfirmReady={canConfirmReady}
        onConfirmReady={onConfirmReady}
      />

      <Layout.Content className={styles.content}>
        {error && (
          <Alert
            message="Error"
            description={error.message}
            type="error"
            closable
            style={{ marginBottom: 16 }}
          />
        )}

        {/* If in analysis/clarification phase, show chat panel */}
        {isInAnalysisPhase && sessionId ? (
          <div
            style={{
              padding: '0 24px 16px',
              height: 'calc(100vh - 230px)',
              minHeight: 360,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* Chat Panel */}
            <ChatPanel
              messages={chatHistory}
              clarifications={clarifications}
              onSubmitClarification={onSubmitClarification}
              isClarifying={isClarifying}
              sessionActive={!!sessionId}
              isLoading={loading}
            />
          </div>
        ) : (
          // Initial input phase
          <div className={styles.initialScreen}>
            <div
              style={{
                marginBottom: 24,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <h3>Describe Your System</h3>
                <p style={{ marginBottom: 0, color: '#666' }}>
                  Tell us about the system or process you want to visualize. We'll have a conversation
                  to gather all the details needed.
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '12px', color: '#999', marginBottom: '4px' }}>Using:</div>
                <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
                  {selectedModel.toUpperCase()}
                </Tag>
                <Button
                  type="text"
                  size="small"
                  style={{ display: 'block', marginTop: '8px' }}
                  onClick={handleClearAndChangeModel}
                  icon={<LeftOutlined />}
                >
                  Change Model
                </Button>
              </div>
            </div>

            <div style={{
              marginBottom: 16,
              border: '1px solid #d9d9d9',
              borderRadius: '4px',
              overflow: 'hidden',
              minHeight: '200px'
            }}>
              <Editor
                height="200px"
                defaultLanguage="plaintext"
                value={userInput}
                onChange={(value) => onInputChange(value || '')}
                onMount={(editor) => {
                  promptEditorRef.current = editor;
                  // Focus the editor when it mounts
                  editor.focus();
                }}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 13,
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  wrappingStrategy: 'advanced',
                  automaticLayout: true,
                  scrollbar: {
                    vertical: 'auto',
                    horizontal: 'auto',
                  },
                  padding: { top: 12, bottom: 12 },
                  readOnly: loading,
                  placeholder: `Describe the system, process, or architecture you want to diagram. For example:
• A user authentication flow for a web application
• The architecture of a microservices system
• A data processing pipeline
• An organizational hierarchy`,
                }}
              />
            </div>

            <Space style={{ marginBottom: 16 }}>
              <Button
                type="primary"
                size="large"
                onClick={handleStart}
                loading={loading}
                disabled={!userInput.trim() || loading}
                icon={<SendOutlined />}
              >
                Start Conversation
              </Button>
              <Button
                type="default"
                size="large"
                onClick={onClearInput}
                disabled={!userInput.trim() || loading}
                icon={<ClearOutlined />}
              >
                Clear
              </Button>
            </Space>
          </div>
        )}
      </Layout.Content>
    </Layout>
  );
};

export default SystemDescriptionScreen;
