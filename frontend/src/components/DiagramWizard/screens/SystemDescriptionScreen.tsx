/**
 * SystemDescriptionScreen Component
 *
 * Second screen of DiagramWizard: User enters system description
 * and initiates the analysis. Also handles the clarification phase
 * where the AI asks questions to better understand the system.
 */

import React from 'react';
import { Layout, Button, Input, Spin, Alert, message, Space, Steps, Tag, Modal, Card, Collapse } from 'antd';
import { SendOutlined, ClearOutlined, LeftOutlined, CodeOutlined } from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';
import ChatPanel from '../panels/Panel1_Chat';
import type { ModelId } from './ModelSelectionScreen';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';

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
  const isClarifying = status?.status === 'clarifying';
  const canConfirmReady = status?.status === 'can_proceed' || status?.status === 'clarification_ready';

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
      {/* Header */}
      <Layout.Header className={styles.header}>
        <div className={styles.headerContent}>
          <h2 className={styles.title}>Diagram Wizard</h2>

          <Space>
            {selectedModel && (
              <Tag color="blue" style={{ fontSize: '12px', padding: '4px 8px' }}>
                🤖 {selectedModel === 'gpt5'
                  ? 'DEEP'
                  : selectedModel === 'grok'
                  ? 'FASY'
                  : selectedModel === 'claude'
                  ? 'Thinking'
                  : 'EFficient'}
              </Tag>
            )}
            {sessionId && (
              <>
                <span className={styles.sessionId}>Session: {sessionId.substring(0, 8)}...</span>
                <span style={{ color: sseConnected ? '#52c41a' : '#ff4d4f' }}>
                  {sseConnected ? '● Connected' : '● Disconnected'}
                </span>
                {loading && <Spin size="small" />}
              </>
            )}
          </Space>
        </div>
      </Layout.Header>

      <Layout.Content className={styles.content}>
        {/* Progress Steps */}
        <div style={{ marginBottom: 24, padding: '0 24px' }}>
          <Steps
            current={currentPhase}
            size="small"
            items={phases.map((phase, index) => ({
              title: phase.title,
              description: phase.description,
              icon: phase.icon,
              status: currentPhase > index ? 'finish' : currentPhase === index ? 'process' : 'wait',
            }))}
          />
          <div className={styles.phaseIndicator} style={{ marginTop: '16px' }}>
            <div>
              <span className={styles.phaseLabel}>Current Phase:</span>{' '}
              <strong>{phases[Math.min(currentPhase, phases.length - 1)].title}</strong>
            </div>
            {score > 0 && (
              <div>
                <span className={styles.phaseLabel}>Clarity Score:</span>{' '}
                <strong>{score}/10</strong>
              </div>
            )}
          </div>
        </div>

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
          <div style={{ padding: '0 24px' }}>
            {/* Score and JSON Summary - Show at Top */}
            {(score > 0 || status?.jsonRepresentation) && (
              <Card
                style={{
                  marginBottom: 24,
                  backgroundColor: '#fafafa',
                  borderColor: '#f0f0f0',
                }}
              >
                <div style={{ display: 'flex', gap: '24px', alignItems: 'flex-start', marginBottom: score > 0 && status?.jsonRepresentation ? '16px' : '0' }}>
                  {/* Score Display */}
                  {score > 0 && (
                    <div style={{ flex: '0 0 auto' }}>
                      <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px', fontWeight: 500 }}>
                        LLM Assessment Score
                      </div>
                      <Tag color={score >= 8 ? 'green' : score >= 6 ? 'blue' : 'orange'} style={{ fontSize: '16px', padding: '4px 12px' }}>
                        📊 {score}/10
                      </Tag>
                    </div>
                  )}
                </div>

                {/* JSON Representation */}
                {status?.jsonRepresentation && (
                  <Collapse
                    items={[
                      {
                        key: 'json-representation',
                        label: (
                          <span>
                            <CodeOutlined style={{ marginRight: 8 }} />
                            <strong>JSON Representation</strong>
                          </span>
                        ),
                        children: (
                          <div style={{
                            backgroundColor: '#fff',
                            border: '1px solid #e8e8e8',
                            borderRadius: '4px',
                            padding: '12px',
                            maxHeight: '250px',
                            overflow: 'auto',
                          }}>
                            <pre style={{
                              margin: 0,
                              fontFamily: 'monospace',
                              fontSize: '12px',
                              whiteSpace: 'pre-wrap',
                              wordWrap: 'break-word',
                            }}>
                              {JSON.stringify(status.jsonRepresentation, null, 2)}
                            </pre>
                          </div>
                        ),
                      },
                    ]}
                  />
                )}
              </Card>
            )}

            {/* Chat Panel Below Score/JSON */}
            <ChatPanel
              messages={chatHistory}
              clarifications={clarifications}
              onSubmitClarification={onSubmitClarification}
              isClarifying={isClarifying}
              canConfirmReady={canConfirmReady}
              onConfirmReady={onConfirmReady}
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

            <Input.TextArea
              placeholder={`Describe the system, process, or architecture you want to diagram. For example:
• A user authentication flow for a web application
• The architecture of a microservices system
• A data processing pipeline
• An organizational hierarchy`}
              value={userInput}
              onChange={(e) => onInputChange(e.target.value)}
              rows={8}
              disabled={loading}
              style={{ marginBottom: 16, fontFamily: 'monospace', fontSize: '13px' }}
            />

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
