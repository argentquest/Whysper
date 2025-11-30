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
import { Layout, Button, Alert, Space, message, Tabs } from 'antd';
import { CopyOutlined } from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';
import ChatPanel from '../panels/Panel1_Chat';
import PreviewPanel from '../panels/Panel2_Preview';
import CodeEditorPanel from '../panels/Panel3_CodeEditor';
import ExportModal from '../components/ExportModal';
import Footer from '../components/Footer';
import DiagramWizardHeader from '../components/DiagramWizardHeader';
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
  scoreTarget: number;
  diagramCode: string;
  svgOutput: string;
  chatHistory: any[];
  clarifications: Array<{ question: string; answer?: string }>;
  sseConnected: boolean;
  exportModalOpen: boolean;
  structurizrWorkspace?: string;
  cleanStructurizr?: string;
  jsonRepresentation?: Record<string, unknown> | null;
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
  scoreTarget,
  diagramCode,
  svgOutput,
  chatHistory,
  clarifications,
  sseConnected,
  exportModalOpen,
  structurizrWorkspace,
  cleanStructurizr,
  jsonRepresentation,
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
      {/* Unified Header Component */}
      <DiagramWizardHeader
        isComplete={isComplete}
        isError={isError}
        selectedModel={selectedModel}
        sessionId={sessionId}
        sseConnected={sseConnected}
        loading={loading}
        score={score}
        scoreTarget={scoreTarget}
        currentPhase={currentPhase}
        phases={phases}
      />

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

        {/* Tabbed layout for Conversation / Preview / Diagram Code */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '0 24px', minHeight: 0 }}>
          <Tabs
            defaultActiveKey="preview"
            style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
            destroyOnHidden={false}
            items={[
              {
                key: 'conversation',
                label: 'Conversation',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <ChatPanel
                        messages={chatHistory}
                        clarifications={clarifications}
                        onSubmitClarification={() => {}}
                        isClarifying={false}
                      />
                    </div>
                  </div>
                ),
              },
              {
                key: 'preview',
                label: 'Preview',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <PreviewPanel
                        svgOutput={svgOutput}
                        isLoading={loading && !svgOutput}
                        diagramType={status?.diagramType || status?.diagram_type || "Mermaid"}
                        error={status?.error_message || status?.error || error?.message || null}
                        validationError={status?.validation_error || null}
                      />
                    </div>
                  </div>
                ),
              },
              {
                key: 'code',
                label: 'Diagram Code',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8, gap: 8 }}>
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={handleCopyCode}
                          title="Copy code"
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <CodeEditorPanel
                          code={diagramCode}
                          onChange={async (code: string) => onCodeChange?.(code)}
                          diagramType={status?.diagramType || status?.diagram_type || "Mermaid"}
                          isLoading={loading}
                        />
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'workspace',
                label: 'Workspace',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8, gap: 8 }}>
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() => structurizrWorkspace && navigator.clipboard.writeText(structurizrWorkspace)}
                          title="Copy workspace"
                          disabled={!structurizrWorkspace}
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <CodeEditorPanel
                          code={structurizrWorkspace || ''}
                          onChange={(code: string) => {}}
                          diagramType="Structurizr"
                          isLoading={loading}
                        />
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'cleanWorkspace',
                label: 'Clean Workspace',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8, gap: 8 }}>
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() => cleanStructurizr && navigator.clipboard.writeText(cleanStructurizr)}
                          title="Copy clean workspace"
                          disabled={!cleanStructurizr}
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <CodeEditorPanel
                          code={cleanStructurizr || ''}
                          onChange={(code: string) => {}}
                          diagramType="Structurizr"
                          isLoading={loading}
                        />
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'fullJson',
                label: 'Full JSON',
                children: (
                  <div style={{ height: 'calc(100vh - 280px)', minHeight: 360, display: 'flex', flexDirection: 'column' }}>
                    <div className={styles.panel} style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 8, gap: 8 }}>
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() => jsonRepresentation && navigator.clipboard.writeText(JSON.stringify(jsonRepresentation, null, 2))}
                          title="Copy JSON"
                          disabled={!jsonRepresentation}
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <CodeEditorPanel
                          code={jsonRepresentation ? JSON.stringify(jsonRepresentation, null, 2) : ''}
                          onChange={(code: string) => {}}
                          diagramType="JSON"
                          isLoading={loading}
                        />
                      </div>
                    </div>
                  </div>
                ),
              },
            ]}
          />
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
