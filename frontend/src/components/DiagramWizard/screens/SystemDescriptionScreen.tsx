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

import { ClearOutlined, SendOutlined } from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { Alert, Button, Layout, message, Space } from 'antd'
import type * as Monaco from 'monaco-editor'
import React, { useEffect, useRef, useState } from 'react'

import ApiService from '../../../services/api'
import type { DiagramUpdate } from '../../../services/diagram/diagramApi'
import type { Message } from '../../../types'
import DiagramWizardHeader from '../components/DiagramWizardHeader'
import { DiagramInputControls } from '../components/DiagramInputControls'
import styles from '../diagram-wizard.module.css'
import ChatPanel from '../panels/Panel1_Chat'

/**
 * Props for SystemDescriptionScreen component
 *
 * @interface SystemDescriptionScreenProps
 * @property {number} currentPhase - Current phase index (0-3) for progress indicator
 * @property {Array} phases - Array of phase objects with title, description, and icon
 * @property {string} userInput - Current value of system description textarea
 * @property {boolean} loading - Whether a request is being processed
 * @property {boolean} isInAnalysisPhase - Whether currently in analysis/clarification phase
 * @property {string | null} sessionId - Unique session ID from backend (null if not started)
 * @property {DiagramUpdate | null} status - Latest status update from backend (includes scores, json_representation)
 * @property {number} score - Current clarity_score (0-10) from AI assessment
 * @property {number} scoreTarget - Target clarity_score (usually 80)
 * @property {Array} clarifications - List of AI questions asked
 * @property {Array} chatHistory - Array of message objects with role, content, and optional score/jsonData
 * @property {boolean} sseConnected - Whether SSE connection to backend is active
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
  currentPhase: number
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>
  userInput: string
  loading: boolean
  isInAnalysisPhase: boolean
  sessionId: string | null
  status: DiagramUpdate | null
  score: number
  scoreTarget: number
  clarifications: Array<{ question: string; answer?: string }>
  chatHistory: Message[]
  sseConnected: boolean
  onStartDiagram: (prompt: string) => void
  onClearInput: () => void
  onInputChange: (value: string) => void
  onSubmitClarification: (clarification: string) => void
  onConfirmReady: () => void
  error?: { message: string }
  onShowState?: () => void
}

/**
 * SystemDescriptionScreen component
 */
export const SystemDescriptionScreen: React.FC<SystemDescriptionScreenProps> = ({
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
  onStartDiagram,
  onClearInput,
  onInputChange,
  onSubmitClarification,
  onConfirmReady,
  error,
  onShowState,
}) => {
  const promptEditorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null)

  // Track submission IDs from forms filled before session starts
  const [preSessionSubmissionIds, setPreSessionSubmissionIds] = useState<string[]>([])

  // When session starts, add any pre-session forms to the session
  useEffect(() => {
    const addPreSessionForms = async () => {
      if (sessionId && preSessionSubmissionIds.length > 0) {
        console.log(`Adding ${preSessionSubmissionIds.length} pre-session forms to session ${sessionId}`)

        for (const submissionId of preSessionSubmissionIds) {
          try {
            await ApiService.post('/diagram/add_form_data', {
              session_id: sessionId,
              submission_id: submissionId
            })
            console.log(`Added pre-session form ${submissionId} to session`)
          } catch (err) {
            console.error(`Failed to add pre-session form ${submissionId}:`, err)
          }
        }

        // Clear the pre-session submission IDs after adding them
        setPreSessionSubmissionIds([])
        message.success(`Added ${preSessionSubmissionIds.length} form(s) to diagram session`)
      }
    }

    addPreSessionForms()
  }, [sessionId]) // Only run when sessionId changes

  // Show input field during clarification phase (includes initial analysis and follow-up questions)
  // Keep input visible as long as we're in analysis phase (hasn't moved to generation yet)
  const isClarifying = !!(
    isInAnalysisPhase &&
    sessionId &&
    (status?.status === 'started' ||
      status?.status === 'analyzing' ||
      status?.status === 'analysis_complete' ||
      status?.status === 'clarifying' ||
      status?.status === 'clarifying_processing' ||
      status?.status === 'clarification_received' ||
      status?.status === 'clarification_ready' ||
      status?.status === 'can_proceed' ||
      status?.status === 'waiting' ||
      clarifications.length > 0)
  )
  // ALWAYS allow user to press "Confirm Ready" button whenever there's an active session
  // User can skip clarification at any time and proceed to diagram generation
  const canConfirmReady = !!sessionId

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
    awaiting_user_confirmation: status?.awaiting_user_confirmation,
  })

  // Additional debug for button visibility
  console.log('[SystemDescriptionScreen] Button visibility:', {
    canConfirmReady,
    'status?.status': status?.status,
    'status === can_proceed': status?.status === 'can_proceed',
    'status === clarification_ready': status?.status === 'clarification_ready',
  })

  const handleStart = () => {
    if (!userInput.trim()) {
      message.warning('Please enter a system description')
      return
    }
    onStartDiagram(userInput)
  }

  return (
    <Layout className={styles.diagramWizard}>
      {/* Unified Header Component */}
      <DiagramWizardHeader
        sessionId={sessionId}
        sseConnected={sseConnected}
        loading={loading}
        score={score}
        scoreTarget={scoreTarget}
        currentPhase={currentPhase}
        phases={phases}
        canConfirmReady={canConfirmReady}
        onConfirmReady={onConfirmReady}
        {...(onShowState && { onShowState })}
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
              sessionId={sessionId || undefined}
              formsData={status?.FormsData || []}
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
                <h3 style={{ fontSize: '42px', fontWeight: 600 }}>Describe Your System</h3>
                <p style={{ marginBottom: 0, color: '#666', fontSize: '18px' }}>
                  Tell us about the system or process you want to visualize. We'll have a
                  conversation to gather all the details needed.
                </p>
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <DiagramInputControls
                loading={loading}
                sessionId={sessionId || undefined}
                onAppendText={(text) => {
                  const newText = userInput.trim() ? userInput + '\n\n' + text : text.trim()
                  onInputChange(newText)
                }}
                onFormSubmissionId={(submissionId) => {
                  // If session hasn't started yet, store the submission ID
                  if (!sessionId && submissionId) {
                    setPreSessionSubmissionIds(prev => [...prev, submissionId])
                    console.log('Stored pre-session submission ID:', submissionId)
                  }
                }}
              />
            </div>

            <div
              style={{
                marginBottom: 16,
                border: '1px solid #d9d9d9',
                borderRadius: '4px',
                overflow: 'hidden',
                minHeight: '120px',
              }}
            >
              <Editor
                height="240px"
                defaultLanguage="plaintext"
                value={userInput}
                onChange={(value) => onInputChange(value || '')}
                onMount={(editor) => {
                  promptEditorRef.current = editor
                  // Focus the editor when it mounts
                  editor.focus()
                }}
                options={{
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 17,
                  lineNumbers: 'off',
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
    </Layout >
  )
}

export default SystemDescriptionScreen

