/**
 * Panel1_Chat Component
 *
 * Displays conversation history and provides interface for user responses
 * to clarification questions from the LLM.
 */

import React, { useRef, useEffect, useState } from 'react';
import { Card, List, Input, Button, Empty, Spin, Avatar, Space, Tag, Collapse, Tooltip, Badge } from 'antd';
import { UserOutlined, RobotOutlined, SendOutlined, EyeOutlined, CodeOutlined } from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  score?: number;
  jsonData?: Record<string, unknown>;
}

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
  clarifications,
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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

  return (
    <Card
      title="Conversation"
      className={styles.chatPanel}
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
    >
      <div className={styles.messagesList} style={{ flex: 1, overflow: 'auto' }}>
        {messages.length === 0 ? (
          <Empty description="No messages yet" />
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg, index) => (
              <List.Item
                key={index}
                style={{
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: '80%',
                    display: 'flex',
                    gap: 8,
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a',
                    }}
                  />

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
                      <p style={{ margin: 0, fontSize: 14 }}>{msg.content}</p>

                      {/* Display LLM Score for assistant messages */}
                      {msg.role === 'assistant' && typeof msg.score === 'number' && (
                        <div style={{ marginTop: 8, marginBottom: 8 }}>
                          <Tooltip title="LLM assessment score for this response">
                            <Tag color={msg.score >= 8 ? 'green' : msg.score >= 6 ? 'blue' : 'orange'}>
                              📊 Score: {msg.score}/10
                            </Tag>
                          </Tooltip>
                        </div>
                      )}

                      {/* Display JSON data if available */}
                      {msg.role === 'assistant' && msg.jsonData && (
                        <div style={{ marginTop: 8 }}>
                          <Collapse
                            size="small"
                            items={[
                              {
                                key: `json-${index}`,
                                label: (
                                  <span>
                                    <CodeOutlined style={{ marginRight: 8 }} />
                                    JSON Representation
                                  </span>
                                ),
                                children: (
                                  <pre
                                    style={{
                                      backgroundColor: '#f5f5f5',
                                      padding: '8px',
                                      borderRadius: 4,
                                      fontSize: '12px',
                                      overflow: 'auto',
                                      maxHeight: '200px',
                                    }}
                                  >
                                    {JSON.stringify(msg.jsonData, null, 2)}
                                  </pre>
                                ),
                              },
                            ]}
                          />
                        </div>
                      )}

                      {msg.role === 'assistant' && onViewResponseDetails && (
                        <Button
                          type="link"
                          size="small"
                          style={{ padding: 0, marginTop: 8 }}
                          onClick={() => onViewResponseDetails(index)}
                        >
                          <EyeOutlined /> View full details
                        </Button>
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
    </Card>
  );
};

export default Panel1_Chat;
