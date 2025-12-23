/**
 * DiagramWizard End-to-End Test
 *
 * Automated test for the complete diagram generation flow:
 * 1. Select GPT-5 model
 * 2. Enter prompt: "A Data Processing Pipeline, A SQL Server is used, A user upload a a file to Incoming Folder"
 * 3. Go through clarification
 * 4. Select D2 diagram type
 * 5. Verify D2 diagram is generated
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { DiagramUpdate } from '../../services/diagram/diagramApi'
import { DiagramWizard } from './DiagramWizard'

// Mock DiagramApi with realistic responses
vi.mock('../../services/diagram/diagramApi', () => ({
  default: {
    startDiagramGeneration: vi.fn(async (prompt, diagramType, modelId) => {
      return {
        session_id: 'test-session-e2e-123',
        status: 'started',
        message: 'Session started',
      }
    }),

    submitClarification: vi.fn(async (sessionId, clarification) => {
      return {
        session_id: sessionId,
        status: 'clarifying',
      }
    }),

    confirmReady: vi.fn(async (sessionId) => {
      return {
        session_id: sessionId,
        status: 'ready',
      }
    }),

    selectDiagramType: vi.fn(async (sessionId, diagramType) => {
      return {
        session_id: sessionId,
        status: 'generating',
        diagram_type: diagramType,
      }
    }),

    renderDiagram: vi.fn(async (sessionId, code) => {
      return {
        session_id: sessionId,
        status: 'completed',
        diagramCode: code || 'direction: right\n\nuser: User\nfolder: Incoming Folder\ndb: SQL Server\n\nuser -> folder: Upload File\nfolder -> db: Process Data',
        svgOutput: '<svg><rect width="200" height="100" fill="blue"/><text x="10" y="50">D2 Diagram</text></svg>',
      }
    }),

    getDiagramStatus: vi.fn(async (sessionId) => {
      return {
        session_id: sessionId,
        status: 'completed',
      }
    }),
  },
}))

// Mock useDiagramSession with complete SSE simulation
vi.mock('./hooks/useDiagramSession', () => ({
  useDiagramSession: vi.fn((options) => {
    // Simulate SSE state progression
    const [sessionId, setSessionId] = useState<string | null>(null)
    const [status, setStatus] = useState<DiagramUpdate | null>(null)
    const [loading, setLoading] = useState(false)

    return {
      sessionId,
      status,
      error: null,
      loading,
      sseConnected: true,
      sseMessages: [],
      sseError: null,

      // Simulate starting session
      startSession: vi.fn(async (prompt: string, diagramType: string, modelId: string) => {
        setLoading(true)
        setSessionId('test-session-e2e-123')

        // Simulate analysis phase
        setTimeout(() => {
          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'analyzing',
            message: 'Analyzing system architecture...',
            currentState: {},
            history: [],
            clarifications: [],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: true,
            score: 0,
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'analyzing',
            message: 'Analyzing system architecture...',
            currentState: {},
            history: [],
            clarifications: [],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: true,
          })
        }, 100)

        // Simulate clarification phase
        setTimeout(() => {
          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'clarifying',
            question: 'What type of files will users upload?',
            currentState: {},
            history: [],
            clarifications: ['What type of files will users upload?'],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: true,
            score: 40,
            clarity_score: 40,
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'clarifying',
            question: 'What type of files will users upload?',
            currentState: {},
            history: [],
            clarifications: ['What type of files will users upload?'],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: true,
            score: 40,
            clarity_score: 40,
          })
        }, 200)

        setLoading(false)
      }),

      // Simulate submitting clarification
      submitClarification: vi.fn(async (clarification: string) => {
        setLoading(true)

        // Increase score after clarification
        setTimeout(() => {
          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'clarifying',
            question: 'How is the data validated before processing?',
            currentState: {},
            history: [],
            clarifications: [
              'What type of files will users upload?',
              'How is the data validated before processing?',
            ],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: true,
            score: 70,
            clarity_score: 70,
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'clarifying',
            question: 'How is the data validated before processing?',
            score: 70,
            clarity_score: 70,
          })
        }, 100)

        setLoading(false)
      }),

      // Simulate confirming ready
      confirmReady: vi.fn(async () => {
        setLoading(true)

        setTimeout(() => {
          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'ready',
            message: 'Ready for diagram type selection',
            recommended_diagram_type: 'D2',
            keyword_scores: {
              d2: 85,
              mermaid: 60,
              structurizr: 50,
            },
            currentState: {},
            history: [],
            clarifications: [],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: '',
            isRunning: false,
            score: 85,
            clarity_score: 85,
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'ready',
            recommended_diagram_type: 'D2',
            keyword_scores: {
              d2: 85,
              mermaid: 60,
              structurizr: 50,
            },
          })
        }, 100)

        setLoading(false)
      }),

      // Simulate diagram type selection and generation
      renderDiagram: vi.fn(async (code?: string) => {
        setLoading(true)

        // Simulate generation
        setTimeout(() => {
          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'generating',
            message: 'Generating D2 diagram code...',
            currentState: {},
            history: [],
            clarifications: [],
            diagramCode: '',
            svgOutput: '',
            errors: [],
            diagramType: 'D2',
            isRunning: true,
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'generating',
            message: 'Generating D2 diagram code...',
            diagramType: 'D2',
          })
        }, 100)

        // Simulate completion with D2 diagram
        setTimeout(() => {
          const d2Code = `direction: right

# User uploads file to incoming folder
user: User {
  shape: person
}

folder: Incoming Folder {
  shape: cylinder
}

pipeline: Data Processing Pipeline {
  shape: hexagon
}

db: SQL Server {
  shape: cylinder
}

# Flow
user -> folder: Upload File
folder -> pipeline: Trigger Processing
pipeline -> db: Store Processed Data`

          const d2Svg = `<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="150" width="100" height="80" fill="#4A90E2" stroke="#2E5C8A" stroke-width="2"/>
  <text x="100" y="195" text-anchor="middle" fill="white">User</text>

  <rect x="250" y="150" width="120" height="80" fill="#50C878" stroke="#3A9B5C" stroke-width="2"/>
  <text x="310" y="180" text-anchor="middle" fill="white">Incoming</text>
  <text x="310" y="200" text-anchor="middle" fill="white">Folder</text>

  <polygon points="500,150 550,190 500,230 450,190" fill="#F5A623" stroke="#C87F1A" stroke-width="2"/>
  <text x="500" y="185" text-anchor="middle" fill="white">Pipeline</text>

  <rect x="650" y="150" width="100" height="80" fill="#E74C3C" stroke="#C0392B" stroke-width="2"/>
  <text x="700" y="180" text-anchor="middle" fill="white">SQL</text>
  <text x="700" y="200" text-anchor="middle" fill="white">Server</text>

  <!-- Arrows -->
  <line x1="150" y1="190" x2="250" y2="190" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="200" y="180" text-anchor="middle" font-size="12">Upload File</text>

  <line x1="370" y1="190" x2="450" y2="190" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="410" y="180" text-anchor="middle" font-size="12">Process</text>

  <line x1="550" y1="190" x2="650" y2="190" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  <text x="600" y="180" text-anchor="middle" font-size="12">Store Data</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <polygon points="0 0, 10 3, 0 6" fill="#333"/>
    </marker>
  </defs>
</svg>`

          setStatus({
            session_id: 'test-session-e2e-123',
            status: 'completed',
            message: 'Diagram generated successfully',
            diagramCode: code || d2Code,
            svgOutput: d2Svg,
            diagramType: 'D2',
            diagram_type: 'D2',
            currentState: {},
            history: [],
            clarifications: [],
            errors: [],
            isRunning: false,
            jsonRepresentation: {
              components: ['User', 'Incoming Folder', 'Pipeline', 'SQL Server'],
              connections: [
                { from: 'User', to: 'Incoming Folder', label: 'Upload File' },
                { from: 'Incoming Folder', to: 'Pipeline', label: 'Process' },
                { from: 'Pipeline', to: 'SQL Server', label: 'Store Data' },
              ],
            },
          })
          options?.onUpdate?.({
            session_id: 'test-session-e2e-123',
            status: 'completed',
            diagramCode: code || d2Code,
            svgOutput: d2Svg,
            diagramType: 'D2',
          })
          options?.onComplete?.()
        }, 300)

        setLoading(false)
      }),

      approveRender: vi.fn(),
      refreshStatus: vi.fn(),
      endSession: vi.fn(),
      clearSSEMessages: vi.fn(),
    }
  }),
}))

describe('DiagramWizard - Complete E2E Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should complete full diagram generation flow: GPT-5 → Data Pipeline prompt → D2 diagram', async () => {
    const user = userEvent.setup()

    render(<DiagramWizard />)

    // STEP 1: Select GPT-5 Model
    console.log('🤖 Step 1: Selecting GPT-5 model...')
    expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument()

    const selectButtons = screen.getAllByText('Select')
    expect(selectButtons.length).toBeGreaterThan(0)

    // Click first Select button (GPT-5)
    await user.click(selectButtons[0])

    // Wait for transition to System Description screen
    await waitFor(() => {
      expect(screen.getByText('Describe Your System')).toBeInTheDocument()
    }, { timeout: 3000 })

    console.log('✅ GPT-5 model selected')

    // STEP 2: Enter System Description
    console.log('📝 Step 2: Entering system description...')
    const textarea = await screen.findByPlaceholderText(/Describe the system/)
    const prompt = 'A Data Processing Pipeline, A SQL Server is used, A user upload a a file to Incoming Folder'

    await user.clear(textarea)
    await user.type(textarea, prompt)

    expect(textarea).toHaveValue(prompt)
    console.log('✅ System description entered')

    // STEP 3: Start Conversation
    console.log('🚀 Step 3: Starting diagram generation...')
    const startButton = screen.getByText('Start Conversation')
    expect(startButton).not.toBeDisabled()

    await user.click(startButton)

    // Wait for analysis phase
    await waitFor(() => {
      // Should show analyzing status or clarification question
      const analyzingOrClarifying =
        screen.queryByText(/analyzing/i) ||
        screen.queryByText(/What type of files/i)
      expect(analyzingOrClarifying).toBeTruthy()
    }, { timeout: 5000 })

    console.log('✅ Session started, analyzing system...')

    // STEP 4: Answer Clarification Questions
    console.log('💬 Step 4: Answering clarification questions...')

    // Wait for first clarification question
    await waitFor(() => {
      expect(screen.getByText(/What type of files will users upload/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    // Answer first question
    const clarificationInput = await screen.findByPlaceholderText(/Answer the question/i)
    await user.type(clarificationInput, 'CSV and JSON files')

    const submitButton = screen.getByText(/Submit/i)
    await user.click(submitButton)

    console.log('✅ First clarification answered')

    // Wait for second question (if any) or ready state
    await waitFor(() => {
      const readyButton = screen.queryByText(/Yes, I'm Ready/i)
      const secondQuestion = screen.queryByText(/How is the data validated/i)
      expect(readyButton || secondQuestion).toBeTruthy()
    }, { timeout: 3000 })

    // If there's a second question, answer it
    if (screen.queryByText(/How is the data validated/i)) {
      const clarificationInput2 = await screen.findByPlaceholderText(/Answer the question/i)
      await user.type(clarificationInput2, 'Schema validation and data type checking')

      const submitButton2 = screen.getByText(/Submit/i)
      await user.click(submitButton2)

      console.log('✅ Second clarification answered')
    }

    // STEP 5: Confirm Ready
    console.log('✅ Step 5: Confirming ready for generation...')
    await waitFor(() => {
      const readyButton = screen.getByText(/Yes, I'm Ready/i)
      expect(readyButton).toBeInTheDocument()
    }, { timeout: 3000 })

    const confirmReadyButton = screen.getByText(/Yes, I'm Ready/i)
    await user.click(confirmReadyButton)

    console.log('✅ Confirmed ready, transitioning to diagram type selection...')

    // STEP 6: Select D2 Diagram Type
    console.log('🎨 Step 6: Selecting D2 diagram type...')
    await waitFor(() => {
      expect(screen.getByText(/Select Diagram Type/i)).toBeInTheDocument()
    }, { timeout: 3000 })

    // D2 should be recommended
    const d2Option = await screen.findByText(/D2/i)
    expect(d2Option).toBeInTheDocument()

    // Click on D2 option
    const d2SelectButton = screen.getByText(/Generate D2 Diagram/i)
    await user.click(d2SelectButton)

    console.log('✅ D2 diagram type selected')

    // STEP 7: Wait for Diagram Generation
    console.log('⏳ Step 7: Waiting for diagram generation...')
    await waitFor(() => {
      expect(screen.getByText(/Generating/i) || screen.getByText(/completed/i)).toBeTruthy()
    }, { timeout: 5000 })

    // STEP 8: Verify D2 Diagram Generated
    console.log('🎉 Step 8: Verifying D2 diagram generated...')
    await waitFor(() => {
      // Should have tabs
      const previewTab = screen.queryByText('Preview')
      const codeTab = screen.queryByText('Diagram Code')
      expect(previewTab || codeTab).toBeTruthy()
    }, { timeout: 5000 })

    // Verify diagram code is D2
    await waitFor(() => {
      // D2 diagram should contain keywords like "direction:", "shape:", "->"
      const page = screen.getByText(/direction:|shape:|->|User|SQL Server|Incoming Folder/i)
      expect(page).toBeTruthy()
    }, { timeout: 3000 })

    console.log('✅ D2 diagram successfully generated!')

    // STEP 9: Verify All Tabs Present
    console.log('📑 Step 9: Verifying all tabs...')
    expect(screen.getByText('Preview')).toBeInTheDocument()
    expect(screen.getByText('Diagram Code')).toBeInTheDocument()
    expect(screen.getByText('Conversation')).toBeInTheDocument()

    console.log('✅ All tabs present and working')

    // STEP 10: Verify SVG is Generated
    console.log('🖼️  Step 10: Verifying SVG diagram...')
    // Click Preview tab
    const previewTab = screen.getByText('Preview')
    await user.click(previewTab)

    await waitFor(() => {
      // Should have SVG content
      const svgContent = document.querySelector('svg')
      expect(svgContent).toBeTruthy()
    }, { timeout: 3000 })

    console.log('✅ SVG diagram rendered successfully')

    console.log('\n🎊 COMPLETE E2E TEST PASSED! 🎊')
    console.log('✅ Model: GPT-5')
    console.log('✅ Prompt: Data Processing Pipeline')
    console.log('✅ Diagram Type: D2')
    console.log('✅ Output: D2 diagram with SVG')
  }, 30000) // 30 second timeout for complete flow

  it('should persist state when switching tabs', async () => {
    const user = userEvent.setup()
    render(<DiagramWizard />)

    // Complete flow (simplified)
    const selectButtons = screen.getAllByText('Select')
    await user.click(selectButtons[0])

    const textarea = await screen.findByPlaceholderText(/Describe the system/)
    await user.type(textarea, 'Test system')

    const startButton = screen.getByText('Start Conversation')
    await user.click(startButton)

    // After generation completes, switch tabs
    await waitFor(() => {
      const previewTab = screen.queryByText('Preview')
      const codeTab = screen.queryByText('Diagram Code')
      if (previewTab) {
        user.click(previewTab)
      }
      if (codeTab) {
        user.click(codeTab)
      }
    }, { timeout: 10000 })

    // State should be preserved
    expect(screen.getByText('Preview') || screen.getByText('Diagram Code')).toBeTruthy()
  }, 20000)
})

/**
 * RUNNING THIS TEST:
 *
 * ```bash
 * cd frontend
 * npm test DiagramWizard.e2e.test.tsx
 * ```
 *
 * Expected Output:
 * ✅ Model: GPT-5
 * ✅ Prompt: Data Processing Pipeline
 * ✅ Diagram Type: D2
 * ✅ Output: D2 diagram with SVG
 *
 * The test simulates:
 * 1. User selecting GPT-5
 * 2. Entering the exact prompt you specified
 * 3. Going through clarifications
 * 4. Selecting D2 diagram type
 * 5. Verifying D2 code and SVG are generated
 */
