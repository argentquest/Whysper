/**
 * DiagramWizard Component
 *
 * Main component for the diagram generation wizard interface.
 * Provides a multi-panel UI for iterative diagram creation with:
 * - Chat panel for Q&A with the LLM
 * - Preview panel for SVG rendering
 * - Code editor panel for manual edits
 */

import React, { useState, useEffect } from 'react';
import { Layout, Button, Select, Input, Spin, Alert, message, Divider, Space } from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  DownloadOutlined,
  CopyOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useDiagramSession } from './hooks/useDiagramSession';
import ChatPanel from './panels/Panel1_Chat';
import PreviewPanel from './panels/Panel2_Preview';
import CodeEditorPanel from './panels/Panel3_CodeEditor';
import styles from './diagram-wizard.module.css';

interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
}

type DiagramType = 'Mermaid' | 'D2' | 'PlantUML';

export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
}) => {
  const [diagramType, setDiagramType] = useState<DiagramType>('Mermaid');
  const [userInput, setUserInput] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);

  const {
    sessionId,
    status,
    loading,
    error,
    startSession,
    submitClarification,
    renderDiagram,
    endSession,
  } = useDiagramSession({
    onUpdate: (update) => {
      // Handle incoming updates from SSE
      if (update.status === 'completed') {
        message.success('Diagram generated successfully!');
        if (onDiagramGenerated && status) {
          onDiagramGenerated(status.diagramCode, status.svgOutput);
        }
      } else if (update.status === 'error') {
        message.error(`Error: ${update.message || 'Unknown error occurred'}`);
      }
    },
    onError: (err) => {
      message.error(`Session error: ${err.message}`);
    },
  });

  // Handle initial prompt if provided
  useEffect(() => {
    if (initialPrompt && !sessionId && !isInitializing) {
      setUserInput(initialPrompt);
    }
  }, [initialPrompt, sessionId, isInitializing]);

  // Handle starting diagram generation
  const handleStartDiagram = async () => {
    if (!userInput.trim()) {
      message.warning('Please enter a diagram description');
      return;
    }

    try {
      setIsInitializing(true);
      await startSession(userInput, diagramType);
    } catch (err) {
      message.error(`Failed to start diagram generation: ${err}`);
    } finally {
      setIsInitializing(false);
      setUserInput('');
    }
  };

  // Handle submitting clarification
  const handleSubmitClarification = async (clarification: string) => {
    try {
      await submitClarification(clarification);
    } catch (err) {
      message.error(`Failed to submit clarification: ${err}`);
    }
  };

  // Handle code changes and re-rendering
  const handleCodeChange = async (newCode: string) => {
    try {
      await renderDiagram(newCode);
    } catch (err) {
      message.error(`Failed to render diagram: ${err}`);
    }
  };

  // Handle downloading SVG
  const handleDownloadSVG = () => {
    if (!status?.svgOutput) {
      message.warning('No SVG output available');
      return;
    }

    const element = document.createElement('a');
    const file = new Blob([status.svgOutput], { type: 'image/svg+xml' });
    element.href = URL.createObjectURL(file);
    element.download = `diagram_${Date.now()}.svg`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Handle copying code
  const handleCopyCode = () => {
    if (!status?.diagramCode) {
      message.warning('No diagram code available');
      return;
    }

    navigator.clipboard.writeText(status.diagramCode);
    message.success('Diagram code copied to clipboard');
  };

  // Handle ending session
  const handleEndSession = async () => {
    try {
      await endSession();
      message.info('Session ended');
    } catch (err) {
      message.error(`Failed to end session: ${err}`);
    }
  };

  return (
    <Layout className={styles.diagramWizard}>
      <Layout.Header className={styles.header}>
        <div className={styles.headerContent}>
          <h2 className={styles.title}>Diagram Wizard</h2>

          {sessionId && (
            <Space>
              <span className={styles.sessionId}>Session: {sessionId.substring(0, 8)}...</span>
              {status?.isRunning && <Spin size="small" />}
            </Space>
          )}
        </div>
      </Layout.Header>

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

        {!sessionId ? (
          // Initial prompt screen
          <div className={styles.initialScreen}>
            <h3>Create a New Diagram</h3>

            <Input.TextArea
              placeholder="Describe the diagram you want to create..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              rows={4}
              disabled={loading}
            />

            <div className={styles.controls}>
              <Select
                value={diagramType}
                onChange={(value) => setDiagramType(value)}
                style={{ width: 150 }}
                options={[
                  { label: 'Mermaid', value: 'Mermaid' },
                  { label: 'D2', value: 'D2' },
                  { label: 'PlantUML', value: 'PlantUML' },
                ]}
              />

              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleStartDiagram}
                loading={loading || isInitializing}
              >
                Start Diagram Generation
              </Button>
            </div>
          </div>
        ) : (
          // Multi-panel view
          <div className={styles.panelsContainer}>
            <div className={styles.panelRow}>
              <div className={styles.leftPanel}>
                <ChatPanel
                  messages={status?.history || []}
                  clarifications={status?.clarifications || []}
                  onSubmit={handleSubmitClarification}
                  isLoading={loading}
                  sessionActive={status?.isRunning || false}
                />
              </div>

              <Divider type="vertical" style={{ height: '100%' }} />

              <div className={styles.rightPanel}>
                <div className={styles.previewPanel}>
                  <PreviewPanel
                    svgOutput={status?.svgOutput || ''}
                    diagramType={diagramType}
                    isLoading={loading || status?.isRunning}
                  />
                </div>

                <Divider />

                <div className={styles.codePanel}>
                  <CodeEditorPanel
                    code={status?.diagramCode || ''}
                    diagramType={diagramType}
                    onChange={handleCodeChange}
                    isLoading={loading}
                  />
                </div>
              </div>
            </div>

            <Divider />

            {/* Action buttons */}
            <div className={styles.actionBar}>
              <Space>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={handleDownloadSVG}
                  disabled={!status?.svgOutput}
                >
                  Download SVG
                </Button>

                <Button
                  icon={<CopyOutlined />}
                  onClick={handleCopyCode}
                  disabled={!status?.diagramCode}
                >
                  Copy Code
                </Button>

                <Button
                  icon={<ClearOutlined />}
                  onClick={() => setUserInput('')}
                >
                  Clear Input
                </Button>

                <Button
                  icon={<DeleteOutlined />}
                  danger
                  onClick={handleEndSession}
                >
                  End Session
                </Button>
              </Space>
            </div>
          </div>
        )}
      </Layout.Content>
    </Layout>
  );
};

export default DiagramWizard;
