/**
 * GenerationScreen Component
 *
 * Third screen of DiagramWizard: Shows the three-panel layout for
 * diagram generation, validation, refinement, and rendering.
 * - Left: Chat panel for viewing conversation
 * - Center: SVG preview of the diagram
 * - Right: Code editor for manual edits
 */

import React from 'react';
import { Layout, Button, Spin, Alert, Space, Badge, Tag, Steps, message } from 'antd';
import {
  CopyOutlined,
} from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';
import ChatPanel from '../panels/Panel1_Chat';
import PreviewPanel from '../panels/Panel2_Preview';
import CodeEditorPanel from '../panels/Panel3_CodeEditor';
import ExportModal from '../components/ExportModal';
import Footer from '../components/Footer';
import type { ModelId } from './ModelSelectionScreen';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';

/**
 * GenerationScreenProps type definition
 * 
 * Describes the structure and properties of GenerationScreenProps
 */
interface GenerationScreenProps {
  selectedModel: ModelId;
  currentPhase: number;
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>;
  loading: boolean;
  sessionId: string | null;
  status: DiagramUpdate | null;
  score: number;
  diagramCode: string;
  svgOutput: string;
  chatHistory: any[];
  clarifications: Array<{ question: string; answer?: string }>;
  sseConnected: boolean;
  exportModalOpen: boolean;
  onChangeModel: () => void;
  onNewDiagram: () => void;
  onExportClick: () => void;
  onExportModalClose: () => void;
  onExportSubmit: (filename: string, format: string) => void;
  onCodeChange?: (code: string) => void;
  error?: { message: string };
}

/**
 * GenerationScreen component
 */
export const GenerationScreen: React.FC<GenerationScreenProps> = ({
  selectedModel,
  currentPhase,
  phases,
  loading,
  sessionId,
  status,
  score,
  diagramCode,
  svgOutput,
  chatHistory,
  clarifications,
  sseConnected,
  exportModalOpen,
  onExportModalClose,
  onCodeChange,
  error,
}) => {
  const isComplete = status?.status === 'completed';
  const isError = status?.status === 'error' || status?.status === 'failed';
  const isValidationIssue = status?.status === 'refining' || status?.status === 'fallback_fix';

  const handleCopyCode = () => {
    navigator.clipboard.writeText(diagramCode);
    message.success('Diagram code copied to clipboard!');
  };

  return (
    <Layout className={styles.diagramWizard}>
      {/* Header */}
      <Layout.Header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerTop}>
            <div>
              <h2 className={styles.title}>
                Diagram Wizard
                {isComplete && <Tag color="green" style={{ marginLeft: '12px' }}>Complete ?</Tag>}
                {isError && <Tag color="red" style={{ marginLeft: '12px' }}>Error ?</Tag>}
              </h2>
            </div>
            <Space className={styles.headerMeta}>
              {selectedModel && (
                <Tag color="blue" style={{ fontSize: '12px', padding: '4px 8px' }}>
                  ?? {selectedModel === 'gpt5'
                    ? 'Deep'
                    : selectedModel === 'grok'
                    ? 'Fast'
                    : selectedModel === 'claude'
                    ? 'Thinking'
                    : 'Efficient'}
                </Tag>
              )}
              {sessionId && (
                <>
                  <span style={{ fontSize: '12px' }}>Session: {sessionId.substring(0, 8)}...</span>
                  <Badge
                    status={sseConnected ? 'success' : 'error'}
                    text={sseConnected ? 'Connected' : 'Disconnected'}
                  />
                  {loading && <Spin size="small" />}
                </>
              )}
            </Space>
          </div>

          <div className={styles.headerProgress}>
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
            <div className={styles.phaseIndicator}>
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
        </div>
      </Layout.Header>

      <Layout.Content className={styles.content}>
        {error && (
          <Alert
            message="Error"
            description={error.message}
            type="error"
            closable
            style={{ marginBottom: 16, margin: '0 24px 16px 24px' }}
          />
        )}

        {isValidationIssue && (
          <Alert
            message="Code Refinement in Progress"
            description="The AI is fixing validation errors in your diagram code."
            type="warning"
            style={{ marginBottom: 16, margin: '0 24px 16px 24px' }}
          />
        )}

        {/* Three-Panel Layout */}
        <div style={{ display: 'flex', gap: '16px', padding: '0 24px', height: '100%' }}>
          {/* Left Panel: Chat */}
          <div style={{ flex: '0 0 25%', minWidth: '250px', overflow: 'hidden' }}>
            <div className={styles.panel}>
              <h4 style={{ marginBottom: '12px' }}>Conversation</h4>
              <ChatPanel
                messages={chatHistory}
                clarifications={clarifications}
                onSubmitClarification={() => {}}
                isClarifying={false}
                canConfirmReady={false}
                onConfirmReady={() => {}}
              />
            </div>
          </div>

          {/* Center Panel: Preview */}
          <div style={{ flex: '1', minWidth: '400px', overflow: 'hidden' }}>
            <div className={styles.panel}>
              <h4 style={{ marginBottom: '12px' }}>Preview</h4>
              <PreviewPanel
                svgOutput={svgOutput}
                isLoading={loading && !svgOutput}
                diagramType="Mermaid"
              />
            </div>
          </div>

          {/* Right Panel: Code Editor */}
          <div style={{ flex: '0 0 25%', minWidth: '250px', overflow: 'hidden' }}>
            <div className={styles.panel}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h4 style={{ margin: 0 }}>Code</h4>
                <Space size="small">
                  <Button
                    type="text"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopyCode}
                    title="Copy code"
                  />
                </Space>
              </div>
              <CodeEditorPanel
                code={diagramCode}
                onChange={async (code: string) => onCodeChange?.(code)}
                diagramType="Mermaid"
                isLoading={loading}
              />
            </div>
          </div>
        </div>

        {/* Footer with Actions */}
        <Footer
          sessionId={sessionId}
          sseConnected={sseConnected}
          currentStatus={status?.status}
        />
      </Layout.Content>

      {/* Export Modal */}
      <ExportModal
        visible={exportModalOpen}
        onClose={onExportModalClose}
        svgContainerRef={{ current: null }}
      />
    </Layout>
  );
};

export default GenerationScreen;
