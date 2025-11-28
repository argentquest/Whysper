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

import React, { useRef, useEffect, useState } from 'react';
import { Card, List, Input, Button, Empty, Spin, Space, Tag, Tooltip, Tabs } from 'antd';
import { SendOutlined, CodeOutlined, EyeOutlined, FileTextOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import JsonPreview from '../components/JsonPreview';
import styles from '../diagram-wizard.module.css';

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
  role: 'user' | 'assistant';
  content: string;
  score?: number;
  jsonData?: Record<string, unknown>;
  fullAiResponse?: string;  // Full raw AI response for debugging
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
  messages: ConversationMessage[];
  clarifications: any[];
  onSubmitClarification?: (message: string) => void | Promise<void>;
  onSubmit?: (message: string) => Promise<void>;
  isLoading?: boolean;
  sessionActive?: boolean;
  onViewResponseDetails?: (messageIndex: number) => void;
  isClarifying?: boolean;
  canConfirmReady?: boolean;
  onConfirmReady?: () => void;
}

const Panel1_Chat: React.FC<Panel1ChatProps> = ({
  messages,
  onSubmitClarification,
  onSubmit,
  isLoading = false,
  sessionActive = false,
  onViewResponseDetails,
  isClarifying = false,
  canConfirmReady = false,
  onConfirmReady,
}) => {
  const [userResponse, setUserResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [activeResponseTab, setActiveResponseTab] = useState<'preview' | 'json' | 'fullResponse'>('preview');
  const [editorReady, setEditorReady] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<any>(null);
  const editorContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (activeResponseTab === 'json' && editorRef.current) {
      requestAnimationFrame(() => editorRef.current?.layout());
    }
  }, [activeResponseTab]);

  useEffect(() => {
    if (!editorReady || !editorContainerRef.current || !editorRef.current) {
      return;
    }
    const observer = new ResizeObserver(() => {
      editorRef.current?.layout();
    });
    observer.observe(editorContainerRef.current);
    return () => observer.disconnect();
  }, [editorReady]);

  const handleSubmit = async () => {
    if (!userResponse.trim()) return;

    try {
      setSubmitting(true);
      // Use onSubmitClarification if available (new interface), otherwise use onSubmit (legacy)
      const handler = onSubmitClarification || onSubmit;
      if (handler) {
        await handler(userResponse);
        setUserResponse('');
      }
    } catch (err) {
      console.error('Failed to submit clarification:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Get the latest assistant message with AI response data
  const latestAssistantMessage = [...messages].reverse().find(msg =>
    msg.role === 'assistant' && (msg.jsonData || msg.fullAiResponse)
  );

  return (
    <Card
      title="Conversation"
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
        {/* Left: Chat Messages */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden', minHeight: 0 }}>
          <div className={styles.messagesList} style={{ flex: 1, overflow: 'auto' }}>
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
                          backgroundColor:
                            msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
                          wordBreak: 'break-word',
                          minWidth: '200px',
                        }}
                      >
                        <p style={{ margin: 0, fontSize: 14, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                          {msg.content}
                        </p>

                        {/* Display LLM Score for assistant messages */}
                        {msg.role === 'assistant' && typeof msg.score === 'number' && (
                          <div style={{ marginTop: 8, marginBottom: 8 }}>
                            <Tooltip title="LLM assessment score for this response">
                              <Tag color={msg.score >= 80 ? 'green' : msg.score >= 60 ? 'blue' : 'orange'}>
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

            <div ref={messagesEndRef} />
          </div>

          {/* Response Input Section OR Confirm Ready Button */}
          {sessionActive && (
            <div style={{ marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
              {canConfirmReady && onConfirmReady ? (
                // Show Confirm Ready Button when clarifications are complete
                <Button
                  type="primary"
                  size="large"
                  onClick={onConfirmReady}
                  loading={isLoading}
                  style={{ width: '100%' }}
                >
                  ✓ Confirm Ready to Generate Diagram
                </Button>
              ) : isClarifying ? (
                // Show input for clarifications
                <Space.Compact style={{ width: '100%' }}>
                  <Input
                    placeholder="Enter your response to the clarification..."
                    value={userResponse}
                    onChange={(e) => setUserResponse(e.target.value)}
                    onPressEnter={handleSubmit}
                    disabled={isLoading || submitting}
                    autoFocus
                  />

                  <Button
                    type="primary"
                    icon={<SendOutlined />}
                    onClick={handleSubmit}
                    loading={isLoading || submitting}
                  >
                    Send
                  </Button>
                </Space.Compact>
              ) : null}
            </div>
          )}

          {isLoading && <Spin style={{ marginTop: 16 }} />}
        </div>

        {/* Right: AI Response */}
        <div style={{
          flex: '0 0 400px',
          borderLeft: '1px solid #f0f0f0',
          paddingLeft: '16px',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          height: '100%',
          minHeight: 0,
        }}>
          <h4 style={{ marginTop: 0, marginBottom: 12, flexShrink: 0 }}>AI Response</h4>

          {latestAssistantMessage ? (
            <div style={{ flex: 1, overflow: 'hidden', minHeight: 0 }}>
              <Tabs
                activeKey={activeResponseTab}
                onChange={(key) => setActiveResponseTab(key as 'preview' | 'json' | 'fullResponse')}
                size="small"
                destroyInactiveTabPane
                animated={false}
                className={styles.aiResponseTabs}
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
                      <div className={`${styles.aiResponseContent} ${styles.aiResponseScrollable}`}>
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
                        style={{ border: '1px solid #d9d9d9', borderRadius: '4px', overflow: 'hidden' }}
                        ref={editorContainerRef}
                      >
                        <Editor
                          height="700px"
                          width="100%"
                          defaultLanguage="json"
                          value={JSON.stringify(latestAssistantMessage.jsonData || {}, null, 2)}
                          theme="vs-light"
                          onMount={(editorInstance) => {
                            editorRef.current = editorInstance;
                            editorInstance.layout();
                            setEditorReady(true);
                          }}
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            scrollBeyondLastLine: false,
                            fontSize: 12,
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
                      <div className={`${styles.aiResponseContent} ${styles.aiResponseScrollable}`}>
                        <pre style={{
                          whiteSpace: 'pre-wrap',
                          wordWrap: 'break-word',
                          fontFamily: 'monospace',
                          fontSize: '12px',
                          backgroundColor: '#f5f5f5',
                          padding: '12px',
                          borderRadius: '4px',
                          border: '1px solid #d9d9d9',
                          margin: 0,
                        }}>
                          {latestAssistantMessage.fullAiResponse || 'No full AI response available'}
                        </pre>
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
    </Card>
  );
};

export default Panel1_Chat;
