/**
 * Panel1_Chat Component
 *
 * Displays conversation history and provides interface for user responses
 * to clarification questions from the LLM.
 */

import React, { useRef, useEffect, useState } from 'react';
import { Card, List, Input, Button, Empty, Spin, Avatar, Space } from 'antd';
import { UserOutlined, RobotOutlined, SendOutlined } from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';

interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface Panel1ChatProps {
  messages: ConversationMessage[];
  clarifications: string[];
  onSubmit: (message: string) => Promise<void>;
  isLoading: boolean;
  sessionActive: boolean;
}

const Panel1_Chat: React.FC<Panel1ChatProps> = ({
  messages,
  clarifications,
  onSubmit,
  isLoading,
  sessionActive,
}) => {
  const [userResponse, setUserResponse] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!userResponse.trim()) return;

    try {
      setSubmitting(true);
      await onSubmit(userResponse);
      setUserResponse('');
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
                    }}
                  >
                    <p style={{ margin: 0, fontSize: 14 }}>{msg.content}</p>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}

        <div ref={messagesEndRef} />
      </div>

      {sessionActive && clarifications.length < 5 && (
        <div style={{ marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
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
        </div>
      )}

      {isLoading && <Spin style={{ marginTop: 16 }} />}
    </Card>
  );
};

export default Panel1_Chat;
