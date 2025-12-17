/**
 * GenerationScreen Component
 *
 * Third screen of DiagramWizard: Shows the three-panel layout for
 * diagram generation, validation, refinement, and rendering.
 * - Left: Chat panel for viewing conversation
 * - Center: SVG preview of the diagram
 * - Right: Code editor for manual edits
 */

import { CopyOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Input, Layout, message, Spin, Tabs } from 'antd'
import React from 'react'

import type { DiagramUpdate } from '../../../services/diagram/diagramApi'
import type { Message } from '../../../types'
import DiagramWizardHeader from '../components/DiagramWizardHeader'
import ExportModal from '../components/ExportModal'
import Footer from '../components/Footer'
import styles from '../diagram-wizard.module.css'
import ChatPanel from '../panels/Panel1_Chat'
import PreviewPanel from '../panels/Panel2_Preview'
import CodeEditorPanel from '../panels/Panel3_CodeEditor'
import type { ModelId } from './ModelSelectionScreen'

/**
 * GenerationScreenProps type definition
 *
 * Describes the structure and properties of GenerationScreenProps
 */
interface GenerationScreenProps {
  selectedModel: ModelId
  currentPhase: number
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>
  loading: boolean
  sessionId: string | null
  status: DiagramUpdate | null
  score: number
  scoreTarget: number
  diagramCode: string
  originalDiagramCode: string
  svgOutput: string
  chatHistory: Message[]
  clarifications: Array<{ question: string; answer?: string }>
  sseConnected: boolean
  exportModalOpen: boolean
  structurizrWorkspace?: string
  cleanStructurizr?: string
  jsonRepresentation?: Record<string, unknown> | null
  onChangeModel: () => void
  onNewDiagram: () => void
  onExportClick: () => void
  onExportModalClose: () => void
  onExportSubmit: (filename: string, format: string) => void
  onRenderClick?: (code: string) => void
  onShowState?: () => void
  error?: { message: string }
  diagramTypeLoading?: boolean
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
  originalDiagramCode,
  svgOutput,
  chatHistory,
  clarifications,
  sseConnected,
  exportModalOpen,
  structurizrWorkspace: _structurizrWorkspace,
  cleanStructurizr: _cleanStructurizr,
  jsonRepresentation,
  onExportModalClose,
  onRenderClick,
  onShowState,
  error,
  diagramTypeLoading = false,
}) => {
  const isComplete = status?.status === 'completed'
  const isError = status?.status === 'error' || status?.status === 'failed'
  const isValidationIssue = status?.status === 'refining' || status?.status === 'fallback_fix'

  const handleCopyCode = () => {
    navigator.clipboard.writeText(diagramCode)
    message.success('Diagram code copied to clipboard!')
  }

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
        onShowState={onShowState}
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
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            padding: '0 24px',
            minHeight: 0,
            position: 'relative',
          }}
        >
          <Tabs
            defaultActiveKey="preview"
            style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}
            destroyOnHidden={false}
            tabBarStyle={{
              marginBottom: 0,
            }}
            className="full-height-tabs"
            items={[
              {
                key: 'conversation',
                label: 'Conversation',
                children: (
                  <div
                    style={{
                      height: 'calc(100vh - 280px)',
                      minHeight: 360,
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                  >
                    <div
                      className={styles.panel}
                      style={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                      }}
                    >
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
                  <div
                    style={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                  >
                    <div
                      className={styles.panel}
                      style={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                      }}
                    >
                      <PreviewPanel
                        svgOutput={svgOutput}
                        isLoading={loading && !svgOutput}
                        diagramType={status?.diagramType || status?.diagram_type || 'Mermaid'}
                        error={status?.error_message || status?.error || error?.message || null}
                        validationError={status?.validation_error || null}
                      />
                    </div>
                  </div>
                ),
              },
              {
                key: 'code',
                label: <span style={{ color: '#000000' }}>Diagram Code</span>,
                children: (
                  <div
                    style={{
                      height: '100%',
                      minHeight: 600,
                      display: 'flex',
                      gap: 16,
                      paddingTop: 8,
                    }}
                  >
                    {/* Column 1: Editor (40%) */}
                    <div
                      style={{
                        flex: '0 0 40%',
                        maxWidth: '40%',
                        display: 'flex',
                        flexDirection: 'column',
                        minHeight: 0,
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: 8,
                          gap: 8,
                        }}
                      >
                        <Button
                          type="primary"
                          size="small"
                          onClick={() => onRenderClick?.(diagramCode)}
                          disabled={!diagramCode || !sessionId || loading}
                          title="Render diagram with current code (skips validation)"
                        >
                          Refresh Diagram
                        </Button>
                        <div style={{ display: 'flex', gap: 8 }}>
                          <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={handleCopyCode}
                            title="Copy code"
                          />
                        </div>
                      </div>
                      <div style={{ flex: 1, minHeight: 0 }}>
                        <CodeEditorPanel
                          code={diagramCode}
                          originalCode={originalDiagramCode}
                          diagramType={status?.diagramType || status?.diagram_type || 'Diagram'}
                          isLoading={loading}
                          showTitle={false}
                        />
                      </div>
                    </div>

                    {/* Column 2: Rendered diagram preview (60%) */}
                    <div
                      style={{
                        flex: '0 0 60%',
                        maxWidth: '60%',
                        display: 'flex',
                        flexDirection: 'column',
                        minHeight: 0,
                      }}
                    >
                      <Card
                        title="Rendered Diagram"
                        size="small"
                        style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
                        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}
                      >
                        <div style={{ flex: 1, minHeight: 0 }}>
                          <PreviewPanel
                            svgOutput={svgOutput}
                            isLoading={loading && !svgOutput}
                            diagramType={status?.diagramType || status?.diagram_type || 'Mermaid'}
                            error={status?.error_message || status?.error || error?.message || null}
                            validationError={status?.validation_error || null}
                          />
                        </div>
                      </Card>
                    </div>
                  </div>
                ),
              },
              {
                key: 'svg',
                label: <span style={{ color: '#000000' }}>SVG</span>,
                children: (
                  <div
                    style={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                  >
                    <div
                      className={styles.panel}
                      style={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          marginBottom: 8,
                          gap: 8,
                        }}
                      >
                        <Button
                          type='text'
                          size='small'
                          icon={<CopyOutlined />}
                          onClick={() => svgOutput && navigator.clipboard.writeText(svgOutput)}
                          title="Copy SVG"
                          disabled={!svgOutput}
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'auto' }}>
                        {svgOutput ? (
                          <Input.TextArea
                            value={svgOutput}
                            readOnly
                            style={{
                              fontFamily: 'monospace',
                              fontSize: 12,
                              height: '100%',
                              color: '#000000',
                            }}
                            autoSize={{ minRows: 12, maxRows: 30 }}
                          />
                        ) : (
                          <div
                            style={{
                              color: '#999',
                              textAlign: 'center',
                              paddingTop: '20px',
                            }}
                          >
                            No SVG generated yet
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ),
              },
              {
                key: 'fullJson',
                label: <span style={{ color: '#000000' }}>Full JSON</span>,
                children: (
                  <div
                    style={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                  >
                    <div
                      className={styles.panel}
                      style={{
                        flex: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'flex-end',
                          marginBottom: 8,
                          gap: 8,
                        }}
                      >
                        <Button
                          type="text"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() =>
                            jsonRepresentation &&
                            navigator.clipboard.writeText(
                              JSON.stringify(jsonRepresentation, null, 2)
                            )
                          }
                          title="Copy JSON"
                          disabled={!jsonRepresentation}
                        />
                      </div>
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <CodeEditorPanel
                          code={
                            jsonRepresentation ? JSON.stringify(jsonRepresentation, null, 2) : ''
                          }
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
          {diagramTypeLoading && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: 'rgba(255,255,255,0.8)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 5,
                padding: 24,
              }}
            >
              <Card
                size="small"
                style={{ width: 360, textAlign: 'center', boxShadow: '0 12px 30px rgba(0,0,0,0.12)' }}
                bodyStyle={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'center' }}
              >
                <Spin size="large" />
                <div style={{ fontWeight: 600, marginTop: 4 }}>Calculating diagram options...</div>
                <div style={{ color: '#555', fontSize: 13 }}>
                  Please hold while we finish scoring. We will continue automatically.
                </div>
              </Card>
            </div>
          )}
        </div>

        {/* Footer with Actions */}
        <Footer sessionId={sessionId} sseConnected={sseConnected} currentStatus={status?.status} />
      </Layout.Content>

      {/* Export Modal */}
      <ExportModal
        visible={exportModalOpen}
        onClose={onExportModalClose}
        svgContainerRef={{ current: null }}
      />
    </Layout>
  )
}

export default GenerationScreen
