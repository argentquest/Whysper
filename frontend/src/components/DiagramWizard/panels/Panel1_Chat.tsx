/**
 * Panel1_Chat Component - Interactive Chat Interface
 *
 * Core component for displaying the conversational interface between user and AI.
 * Renders conversation history, AI clarification questions, clarity scores,
 * and provides input field for user responses.
 *
 * ## Features
 * - **Conversation Display**: Shows all messages with role avatars (user/assistant)
 * - **Score Badges**: Displays clarity_score on assistant messages (color-coded)
 * - **JSON Viewer**: Collapsible section showing structured architecture data
 * - **Auto-scroll**: Automatically scrolls to latest message
 * - **Responsive Messages**: Color-coded backgrounds (user: light blue, assistant: light green)
 * - **Confirmation Button**: Shows when user is ready to proceed to generation
 * - **Error Handling**: Safe scroll handling with fallback for browser compatibility
 * - **Loading State**: Shows spinner while awaiting response
 *
 * ## Layout
 * ```
 * Messages Container (scrollable):
 *   For each message:
 *     [Avatar] [Content] [Score Badge] [JSON]
 *
 * Input Section:
 *   Textarea for user response
 *   Submit Button
 *   Confirm Ready Button (optional)
 *
 * Connection Status:
 *   Loading spinner if submitting
 * ```
 *
 * ## Message Scoring
 * - Green Badge (≥8): System is well understood, ready to proceed
 * - Blue Badge (6-7): Good understanding, may need minor clarifications
 * - Orange Badge (<6): Incomplete understanding, more questions needed
 *
 * ## Props Flow
 * ```
 * Parent passes:
 *   - messages: Conversation history
 *   - clarifications: List of AI questions
 *   - isClarifying: Whether in clarification phase
 *
 * Child calls:
 *   - onSubmitClarification: When user submits response
 *   - onConfirmReady: When user confirms they're done
 * ```
 *
 * ## Auto-scroll Behavior
 * Scrolls to bottom when:
 * - New messages arrive
 * - Component mounts
 * - User submits response
 *
 * Scroll error handling ensures compatibility across browsers (scrollIntoView check).
 */

import {
  CodeOutlined,
  EyeOutlined,
  FileTextOutlined,
  FormOutlined,
  LoadingOutlined,
  RobotOutlined,
  SendOutlined,
} from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { Button, Card, Empty, List, message, Spin, Tabs, Tag, Tooltip } from 'antd'
import * as monaco from 'monaco-editor'
import React, { useEffect, useRef, useState } from 'react'


import JsonPreview from '../components/JsonPreview'
import styles from '../diagram-wizard.module.css'
import { DiagramInputControls } from '../components/DiagramInputControls'

/**
 * Represents a single message in the conversation
 *
 * @interface ConversationMessage
 * @property {string} role - Message originator: 'user' or 'assistant'
 * @property {string} content - The message text content
 * @property {number} [score] - Optional clarity_score (1-10) from AI assessment (only on assistant messages)
 * @property {Object} [jsonData] - Optional structured data (only on latest assistant message during clarification)
 */
interface ConversationMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  score?: number
  jsonData?: Record<string, unknown>
  fullAiResponse?: string // Full raw AI response for debugging
  analysisSummary?: string // Analysis summary from AI
  question?: string // Single clarification question from AI (legacy)
  questions?: string[] // Array of clarification questions from AI (1-3 questions)
}

/**
 * Props for Panel1_Chat component
 *
 * @interface Panel1ChatProps
 * @property {ConversationMessage[]} messages - Array of conversation messages in chronological order
 * @property {Array} clarifications - List of clarification questions from AI
 * @property {Function} [onSubmitClarification] - Callback when user submits response to clarification.
 *                                               Receives the user's response as string parameter.
 * @property {Function} [onSubmit] - Alternative callback for generic message submission
 * @property {boolean} [isLoading=false] - Whether waiting for response from AI
 * @property {boolean} [sessionActive=false] - Whether session is currently active
 * @property {Function} [onViewResponseDetails] - Callback to view details of specific message (index parameter)
 * @property {boolean} [isClarifying=false] - Whether currently in clarification phase (shows input field)
 * @property {boolean} [canConfirmReady=false] - Whether to show "Confirm Ready" button to proceed to generation
 * @property {Function} [onConfirmReady] - Callback when user clicks "Confirm Ready" button
 *
 * ## Callback Behavior
 * - `onSubmitClarification`: Required during clarification phase for user responses
 * - `onConfirmReady`: Called when user is satisfied with clarifications and ready to generate
 * - Both callbacks should handle async operations (AI processing)
 */
interface Panel1ChatProps {
  messages: ConversationMessage[]
  clarifications: Array<{ question: string; answer?: string }>
  onSubmitClarification?: (message: string) => void | Promise<void>
  onSubmit?: (message: string) => Promise<void>
  isLoading?: boolean
  sessionActive?: boolean
  isClarifying?: boolean
  sessionId?: string
  formsData?: any[]
}

const Panel1_Chat: React.FC<Panel1ChatProps> = ({
  messages,
  onSubmitClarification,
  onSubmit,
  isLoading = false,
  sessionActive = false,
  isClarifying = false,
  sessionId = 'unknown-session',
  formsData = [],
}) => {
  const [userResponse, setUserResponse] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // State to track individual question answers
  const [questionAnswers, setQuestionAnswers] = useState<Record<number, string>>({})

  const [editorReady, setEditorReady] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const editorContainerRef = useRef<HTMLDivElement>(null)
  const inputEditorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const [activeResponseTab, setActiveResponseTab] = useState<'preview' | 'json' | 'fullResponse' | 'formsData'>(
    'preview'
  )


  useEffect(() => {
    if (activeResponseTab === 'json' && editorRef.current) {
      requestAnimationFrame(() => editorRef.current?.layout())
    }
  }, [activeResponseTab])

  useEffect(() => {
    if (!editorReady || !editorContainerRef.current || !editorRef.current) {
      return
    }
    const observer = new ResizeObserver(() => {
      editorRef.current?.layout()
    })
    observer.observe(editorContainerRef.current)
    return () => observer.disconnect()
  }, [editorReady])

  // Helper function to generate short tab title from question (2-3 words)
  const getShortTitle = (question: string): string => {
    const words = question.split(' ')
    // Take first 2-3 meaningful words (skip common question words)
    const skipWords = ['what', 'how', 'when', 'where', 'why', 'who', 'are', 'is', 'the', 'a', 'an']
    const meaningfulWords = words.filter(w => !skipWords.includes(w.toLowerCase()))
    return meaningfulWords.slice(0, 3).join(' ')
  }

  const handleSubmit = async () => {
    // Check if either free-form text or any question answers are provided
    const hasAnswers = Object.values(questionAnswers).some(answer => answer.trim())
    const hasFreeformText = userResponse.trim()

    if (!hasAnswers && !hasFreeformText) {
      message.warning('Please provide at least one answer or enter text in the response field')
      return
    }

    try {
      setSubmitting(true)

      // Build combined response
      let combinedResponse = ''

      // Add individual question answers first
      const answeredQuestions: string[] = []
      Object.entries(questionAnswers).forEach(([index, answer]) => {
        if (answer.trim()) {
          // Get the question text from the latest assistant message
          const latestMsg = [...messages].reverse().find(m => m.role === 'assistant' && m.questions)
          const questionText = latestMsg?.questions?.[parseInt(index)]
          if (questionText) {
            answeredQuestions.push(`Q${parseInt(index) + 1}: ${questionText}\nA: ${answer.trim()}`)
          }
        }
      })

      if (answeredQuestions.length > 0) {
        combinedResponse += answeredQuestions.join('\n\n')
      }

      // Add free-form text if provided
      if (hasFreeformText) {
        if (combinedResponse) {
          combinedResponse += '\n\n---\nAdditional Information:\n' + userResponse.trim()
        } else {
          combinedResponse = userResponse.trim()
        }
      }

      // Use onSubmitClarification if available (new interface), otherwise use onSubmit (legacy)
      const handler = onSubmitClarification || onSubmit
      if (handler) {
        await handler(combinedResponse)
        setUserResponse('')
        setQuestionAnswers({}) // Clear question answers
      }
    } catch (err) {
      console.error('Failed to submit clarification:', err)
    } finally {
      setSubmitting(false)
    }
  }

  // Get the latest assistant message with AI response data
  const latestAssistantMessage = [...messages]
    .reverse()
    .find((msg) => msg.role === 'assistant' && (msg.jsonData || msg.fullAiResponse))

  // Strip markdown code fences from full AI response
  const cleanFullAiResponse = (response: string | undefined): string => {
    if (!response) return 'No full AI response available'

    // Remove markdown code fences (```json ... ``` or ``` ... ```)
    return response
      .replace(/^```(?:json)?\s*\n?/i, '') // Remove opening fence
      .replace(/\n?```\s*$/i, '') // Remove closing fence
      .trim()
  }

  return (
    <Card
      className={styles.chatPanel}
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        minHeight: 0,
      }}
    >
      <div style={{ flex: 1, display: 'flex', gap: '16px', overflow: 'hidden', minHeight: 0 }}>
        {/* Left: Chat Messages - Scrollable */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            minHeight: 0,
            overflow: 'hidden',
          }}
        >
          <div
            className={styles.messagesList}
            style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}
          >
            {messages.length === 0 ? (
              <Empty description="No messages yet" />
            ) : (
              <List
                split={false}
                dataSource={messages}
                renderItem={(msg, index) => (
                  <List.Item
                    key={index}
                    style={{
                      justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      border: 'none',
                      padding: '6px 0',
                    }}
                  >
                    <div
                      style={{
                        maxWidth: '80%',
                        display: 'flex',
                        justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      }}
                    >
                      <div
                        style={{
                          padding: '8px 12px',
                          borderRadius: 8,
                          backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
                          wordBreak: 'break-word',
                          minWidth: '200px',
                        }}
                      >
                        {/* Display two-column table if both analysisSummary and questions are available */}
                        {msg.role === 'assistant' && msg.analysisSummary && (msg.questions || msg.question) ? (
                          <div style={{ width: '100%' }}>
                            <table
                              style={{
                                width: '100%',
                                borderCollapse: 'collapse',
                                fontSize: 18,
                              }}
                            >
                              <thead>
                                <tr style={{ borderBottom: '2px solid #d9d9d9' }}>
                                  <th
                                    style={{
                                      padding: '8px',
                                      textAlign: 'left',
                                      backgroundColor: '#f0f0f0',
                                      fontWeight: 600,
                                    }}
                                  >
                                    Analysis Summary
                                  </th>
                                  <th
                                    style={{
                                      padding: '8px',
                                      textAlign: 'left',
                                      backgroundColor: '#f0f0f0',
                                      fontWeight: 600,
                                    }}
                                  >
                                    {msg.questions && msg.questions.length > 1 ? 'Questions' : 'Question'}
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr>
                                  <td
                                    style={{
                                      padding: '8px',
                                      verticalAlign: 'top',
                                      borderRight: '1px solid #d9d9d9',
                                    }}
                                  >
                                    {msg.analysisSummary}
                                  </td>
                                  <td
                                    style={{
                                      padding: '8px',
                                      verticalAlign: 'top',
                                    }}
                                  >
                                    {/* Display multiple questions as numbered list */}
                                    {msg.questions && msg.questions.length > 0 ? (
                                      msg.questions.length > 1 ? (
                                        <ol style={{ margin: 0, paddingLeft: '20px' }}>
                                          {msg.questions.map((q, idx) => (
                                            <li key={idx} style={{ marginBottom: '8px' }}>{q}</li>
                                          ))}
                                        </ol>
                                      ) : (
                                        msg.questions[0]
                                      )
                                    ) : (
                                      msg.question
                                    )}
                                  </td>
                                </tr>
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <p
                            style={{
                              margin: 0,
                              fontSize: 18,
                              textAlign: msg.role === 'user' ? 'right' : 'left',
                            }}
                          >
                            {msg.content}
                          </p>
                        )}

                        {/* Display LLM Score for assistant messages */}
                        {msg.role === 'assistant' && typeof msg.score === 'number' && (
                          <div style={{ marginTop: 8, marginBottom: 8 }}>
                            <Tooltip title="LLM assessment score for this response">
                              <Tag
                                color={
                                  msg.score >= 80 ? 'green' : msg.score >= 60 ? 'blue' : 'orange'
                                }
                              >
                                📊 Score: {msg.score}/100
                              </Tag>
                            </Tooltip>
                          </div>
                        )}
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            )}

            {/* AI Thinking Indicator */}
            {isLoading && (
              <div className={styles.aiThinkingIndicator}>
                <Spin
                  indicator={<LoadingOutlined style={{ fontSize: 20, color: '#1890ff' }} spin />}
                />
                <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
                  <div className={styles.aiThinkingTitle}>
                    <RobotOutlined style={{ marginRight: '6px' }} />
                    AI is thinking...
                  </div>
                  <div className={styles.aiThinkingSubtitle}>
                    Analyzing your response and preparing next question
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Response Input Section */}
          {sessionActive && isClarifying && (
            <div style={{ marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
              {/* Tabbed Interface for Questions, Additional Info, and Forms */}
              {(() => {
                const latestMsg = [...messages].reverse().find(m => m.role === 'assistant' && m.questions && m.questions.length > 0)

                // Build tab items
                const tabItems = [
                  // Default "Additional Info" tab
                  {
                    key: 'additional',
                    label: 'Additional Info',
                    children: (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div
                          style={{
                            border: '1px solid #d9d9d9',
                            borderRadius: '4px',
                            overflow: 'hidden',
                            minHeight: '140px',
                            position: 'relative',
                          }}
                        >
                          <Editor
                            height="140px"
                            defaultLanguage="plaintext"
                            value={userResponse}
                            onChange={(value) => setUserResponse(value || '')}
                            onMount={(editor) => {
                              inputEditorRef.current = editor
                              editor.focus()
                              editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () =>
                                handleSubmit()
                              )
                            }}
                            options={{
                              minimap: { enabled: false },
                              scrollBeyondLastLine: false,
                              fontSize: 16,
                              lineNumbers: 'off',
                              wordWrap: 'on',
                              wrappingStrategy: 'advanced',
                              automaticLayout: true,
                              scrollbar: {
                                vertical: 'auto',
                                horizontal: 'auto',
                              },
                              padding: { top: 8, bottom: 8 },
                              readOnly: isLoading || submitting,
                              placeholder: 'Add any additional details or context here...',
                            }}
                            loading={<Spin />}
                          />
                        </div>
                      </div>
                    )
                  },
                  // Forms tab
                  {
                    key: 'forms',
                    label: (
                      <span>
                        <FormOutlined style={{ marginRight: 4 }} />
                        Tools
                      </span>
                    ),
                    children: (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '8px' }}>
                        <div style={{
                          padding: '12px',
                          backgroundColor: '#f0f9ff',
                          borderRadius: '4px',
                          borderLeft: '3px solid #1890ff'
                        }}>
                          <p style={{ margin: 0, fontSize: '14px', color: '#595959' }}>
                            <strong>🛠️ Input Tools:</strong> Use forms to provide structured data or upload images to add context.
                          </p>
                        </div>

                        <DiagramInputControls
                          loading={isLoading || submitting}
                          sessionId={sessionId || undefined}
                          onAppendText={(text) => {
                            setUserResponse(prev => {
                              const prefix = prev.trim() ? prev + '\n\n' : ''
                              return prefix + text.trim()
                            })
                          }}
                        />
                      </div>
                    )
                  }
                ]

                // Add question tabs if available
                if (latestMsg?.questions && latestMsg.questions.length > 0) {
                  latestMsg.questions.forEach((question, index) => {
                    tabItems.push({
                      key: `q${index}`,
                      label: `Q${index + 1}: ${getShortTitle(question)}`,
                      children: (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                          <div style={{
                            padding: '12px',
                            backgroundColor: '#f5f5f5',
                            borderRadius: '4px',
                            fontSize: '14px',
                            fontWeight: 500
                          }}>
                            <strong>Question:</strong> {question}
                          </div>
                          <div
                            style={{
                              border: '1px solid #d9d9d9',
                              borderRadius: '4px',
                              overflow: 'hidden',
                            }}
                          >
                            <Editor
                              height="100px"
                              defaultLanguage="plaintext"
                              value={questionAnswers[index] || ''}
                              onChange={(value) => {
                                setQuestionAnswers(prev => ({
                                  ...prev,
                                  [index]: value || ''
                                }))
                              }}
                              options={{
                                minimap: { enabled: false },
                                scrollBeyondLastLine: false,
                                fontSize: 16,
                                lineNumbers: 'off',
                                wordWrap: 'on',
                                wrappingStrategy: 'advanced',
                                automaticLayout: true,
                                scrollbar: {
                                  vertical: 'auto',
                                  horizontal: 'auto'
                                },
                                padding: { top: 8, bottom: 8 },
                                readOnly: isLoading || submitting,
                                placeholder: 'Type your answer here...',
                              }}
                            />
                          </div>
                        </div>
                      )
                    })
                  })
                }

                return (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                    <Tabs
                      defaultActiveKey="additional"
                      items={tabItems}
                      style={{ marginBottom: '8px' }}
                    />

                    <div
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                      <span style={{ fontSize: '14px', color: '#999' }}>Press Ctrl+Enter to send</span>
                      <Button
                        type="primary"
                        icon={<SendOutlined />}
                        onClick={handleSubmit}
                        loading={isLoading || submitting}
                        disabled={!userResponse.trim() && !Object.values(questionAnswers).some(a => a.trim())}
                      >
                        Send
                      </Button>
                    </div>
                  </div>
                )
              })()}
            </div>
          )}
        </div>

        {/* Right: AI Response - Fixed, No Scroll */}
        <div
          style={{
            flex: '0 0 40%',
            minWidth: '350px',
            maxWidth: '500px',
            borderLeft: '1px solid #f0f0f0',
            paddingLeft: '16px',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            minHeight: 0,
            maxHeight: '100%',
          }}
        >
          <h4 style={{ marginTop: 0, marginBottom: 12, flexShrink: 0, fontSize: '20px' }}>AI Response</h4>

          {latestAssistantMessage ? (
            <div
              style={{
                flex: 1,
                overflow: 'hidden',
                minHeight: 0,
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
              }}
            >
              <Tabs
                activeKey={activeResponseTab}
                onChange={(key) => setActiveResponseTab(key as 'preview' | 'json' | 'fullResponse' | 'formsData')}
                size="middle"
                animated={false}
                className={styles.aiResponseTabs}
                tabBarStyle={{
                  marginBottom: '12px',
                  paddingBottom: '8px',
                  borderBottom: '1px solid #f0f0f0',
                }}
                items={[
                  {
                    key: 'preview',
                    label: (
                      <span>
                        <EyeOutlined style={{ marginRight: 4 }} />
                        Preview
                      </span>
                    ),
                    children: (
                      <div
                        style={{
                          height: '100%',
                          overflowY: 'auto',
                          overflowX: 'hidden',
                          padding: '8px',
                          backgroundColor: '#fafafa',
                        }}
                      >
                        <JsonPreview data={latestAssistantMessage.jsonData || {}} />
                      </div>
                    ),
                  },
                  {
                    key: 'json',
                    label: (
                      <span>
                        <CodeOutlined style={{ marginRight: 4 }} />
                        JSON
                      </span>
                    ),
                    children: (
                      <div
                        className={styles.aiResponseContent}
                        style={{
                          border: '1px solid #d9d9d9',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                        ref={editorContainerRef}
                      >
                        <Editor
                          height="700px"
                          width="100%"
                          defaultLanguage="json"
                          value={JSON.stringify(latestAssistantMessage.jsonData || {}, null, 2)}
                          theme="vs-light"
                          onMount={(editorInstance) => {
                            editorRef.current = editorInstance
                            editorInstance.layout()
                            setEditorReady(true)
                          }}
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            fontSize: 16,
                            lineNumbers: 'on',
                            wordWrap: 'on',
                            automaticLayout: true,
                          }}
                        />
                      </div>
                    ),
                  },
                  {
                    key: 'fullResponse',
                    label: (
                      <span>
                        <FileTextOutlined style={{ marginRight: 4 }} />
                        Full AI Response
                      </span>
                    ),
                    children: (
                      <div
                        className={styles.aiResponseContent}
                        style={{
                          border: '1px solid #d9d9d9',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                      >
                        <Editor
                          height="700px"
                          width="100%"
                          defaultLanguage="json"
                          value={cleanFullAiResponse(latestAssistantMessage.fullAiResponse)}
                          theme="vs-light"
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            fontSize: 16,
                            lineNumbers: 'on',
                            wordWrap: 'on',
                            automaticLayout: true,
                          }}
                        />
                      </div>
                    ),
                  },
                  {
                    key: 'formsData',
                    label: (
                      <span>
                        <FormOutlined style={{ marginRight: 4 }} />
                        Forms ({formsData.length})
                      </span>
                    ),
                    children: (
                      <div
                        className={styles.aiResponseContent}
                        style={{
                          border: '1px solid #d9d9d9',
                          borderRadius: '4px',
                          overflow: 'hidden',
                        }}
                      >
                        {formsData.length > 0 ? (
                          <Editor
                            height="700px"
                            width="100%"
                            defaultLanguage="json"
                            value={JSON.stringify(formsData, null, 2)}
                            theme="vs-light"
                            options={{
                              readOnly: true,
                              minimap: { enabled: false },
                              scrollBeyondLastLine: false,
                              fontSize: 16,
                              lineNumbers: 'on',
                              wordWrap: 'on',
                              automaticLayout: true,
                            }}
                          />
                        ) : (
                          <Empty
                            description="No forms submitted yet"
                            style={{ marginTop: '40px' }}
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
                          />
                        )}
                      </div>
                    ),
                  },
                ]}
              />
            </div>
          ) : (
            <Empty
              description="No AI response data yet"
              style={{ marginTop: '40px' }}
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          )}
        </div>
      </div>

      {/* Form Renderer Modal */}

    </Card>
  )
}

export default Panel1_Chat
