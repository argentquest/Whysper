/**
 * Architecture Gen Studio - Main Component
 * Three-column layout for generating and editing architectural diagrams
 */

import React, { useEffect } from 'react';
import { Layout, message } from 'antd';
import { useArchitectureStudioState, useAPIClient, useSSE } from './hooks';
import {
  Header,
  LeftColumn,
  CenterColumn,
  RightColumn,
  Footer,
} from './components';

import styles from './styles/architectureStudio.module.css';

/**
 * ArchitectureGenStudio Component
 *
 * Main component that orchestrates:
 * - Three-column layout (Left: Prompts, Center: Diagrams, Right: Code)
 * - State management
 * - API integration
 * - SSE streaming
 */
export const ArchitectureGenStudio: React.FC = () => {
  // Get state management
  const stateManager = useArchitectureStudioState();
  const apiClient = useAPIClient();
  const { messages: sseMessages, isConnected: sseConnected, connect: connectSSE, disconnect: disconnectSSE, clearMessages: clearSSEMessages } = useSSE();

  const { state } = stateManager;

  // ============================================================================
  // Initialization Effects
  // ============================================================================

  // Load agents on mount
  useEffect(() => {
    const loadAgents = async () => {
      try {
        stateManager.setAgentsLoading(true);
        const agents = await apiClient.fetchAgents();
        stateManager.setAgents(agents);
      } catch (error) {
        stateManager.setAgentsError(
          error instanceof Error ? error.message : 'Failed to load agents'
        );
      } finally {
        stateManager.setAgentsLoading(false);
      }
    };

    loadAgents();
  }, []);

  // Load agent options when current agent changes
  useEffect(() => {
    if (!state.currentAgent) return;

    const loadOptions = async () => {
      try {
        stateManager.setOptionsLoading(true);
        const options = await apiClient.fetchAgentOptions(state.currentAgent!.id);
        stateManager.setCurrentAgentOptions(options);
      } catch (error) {
        stateManager.setOptionsError(
          error instanceof Error ? error.message : 'Failed to load agent options'
        );
      } finally {
        stateManager.setOptionsLoading(false);
      }
    };

    loadOptions();
  }, [state.currentAgent?.id]);

  // Connect SSE when processing request ID changes
  useEffect(() => {
    if (state.processingRequestId) {
      connectSSE(state.processingRequestId);
    } else {
      disconnectSSE();
    }
  }, [state.processingRequestId]);

  // Update state with SSE messages
  useEffect(() => {
    stateManager.setSseMessages(sseMessages);
  }, [sseMessages]);

  // ============================================================================
  // Handlers
  // ============================================================================

  const handleAgentChange = (agent: React.SetStateAction<any>) => {
    // TODO: Check for unsaved prompt and show confirmation dialog
    stateManager.setCurrentAgent(agent);
  };

  const handleSubmit = async (prompt: string) => {
    if (!state.currentAgent) {
      stateManager.setCurrentStatus('Please select an agent', 'error');
      return;
    }

    try {
      stateManager.setIsProcessing(true);
      stateManager.setCurrentStatus('LLM Execution...', 'processing');

      const result = await apiClient.submitPrompt({
        agentId: state.currentAgent.id,
        prompt,
        diagramType: state.selectedDiagramType,
      });

      stateManager.setProcessingRequestId(result.requestId);
      stateManager.setCurrentStatus('Diagram Generated', 'success');

      // If immediate response available, add to generated diagrams
      if (result.initialResponse) {
        stateManager.addGeneratedDiagram(state.selectedDiagramType, result.initialResponse);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to generate diagram';
      stateManager.setProcessingError(errorMsg);
      stateManager.setCurrentStatus(`Error: ${errorMsg}`, 'error');
    } finally {
      stateManager.setIsProcessing(false);
    }
  };

  const handleCancel = async () => {
    if (state.processingRequestId) {
      try {
        await apiClient.cancelRequest(state.processingRequestId);
        stateManager.setIsProcessing(false);
        stateManager.setProcessingRequestId(null);
        stateManager.setCurrentStatus('Cancelled', 'idle');
      } catch (error) {
        console.error('Error canceling request:', error);
      }
    }
  };

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <Layout className={styles.architectureStudio}>
      {/* Skip to main content link - accessibility */}
      <a
        href="#main-content"
        style={{
          position: 'absolute',
          top: '-40px',
          left: '0',
          background: 'var(--ant-color-primary)',
          color: 'white',
          padding: '8px',
          zIndex: 100,
        }}
        onFocus={(e) => {
          e.currentTarget.style.top = '0';
        }}
        onBlur={(e) => {
          e.currentTarget.style.top = '-40px';
        }}
      >
        Skip to main content
      </a>

      {/* Header */}
      <Header
        onAgentChange={handleAgentChange}
        currentAgent={state.currentAgent}
        agents={state.agents}
        agentsLoading={state.agentsLoading}
        notificationCount={0}
        onLogout={() => message.info('Logged out')}
      />

      <Layout className={styles.mainContent} id="main-content" role="main" style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Column - Prompt Section */}
        <LeftColumn
          isCollapsed={state.collapsedColumns.left}
          onCollapsedChange={(collapsed) => stateManager.setCollapsedColumn('left', collapsed)}
          width={state.columnWidths.left}
          onWidthChange={(width) =>
            stateManager.setColumnWidths({
              left: width,
              center: state.columnWidths.center,
              right: state.columnWidths.right,
            })
          }
          currentAgent={state.currentAgent}
          agentOptions={state.currentAgentOptions}
          selectedOption={state.selectedAgentOption}
          onOptionSelect={(option) => stateManager.setSelectedAgentOption(option)}
          currentPrompt={state.currentPrompt}
          onPromptChange={(prompt) => stateManager.setCurrentPrompt(prompt)}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isProcessing={state.isProcessing}
          hasUnsavedPrompt={state.promptHasUnsavedChanges}
          optionsLoading={state.optionsLoading}
          optionsError={state.optionsError}
        />

        {/* Center Column */}
        <CenterColumn
          isCollapsed={state.collapsedColumns.center}
          onCollapsedChange={(collapsed) => stateManager.setCollapsedColumn('center', collapsed)}
          width={state.columnWidths.center}
          onWidthChange={(width) =>
            stateManager.setColumnWidths({
              left: state.columnWidths.left,
              center: width,
              right: state.columnWidths.right,
            })
          }
          selectedDiagramType={state.selectedDiagramType}
          onDiagramTypeChange={(type) => stateManager.setSelectedDiagramType(type)}
          generatedDiagrams={state.generatedDiagrams}
          isLoading={state.isProcessing}
          error={state.processingError}
          zoomLevel={state.zoomLevel}
          onZoomChange={(level) => stateManager.setZoomLevel(level)}
          onExport={(format) => {
            stateManager.setCurrentStatus(`Exporting as ${format}`, 'processing');
            message.success(`Exported as ${format.toUpperCase()}`);
          }}
          onMinimize={() => stateManager.setCollapsedColumn('center', true)}
        />

        {/* Right Column */}
        <RightColumn
          isCollapsed={state.collapsedColumns.right}
          onCollapsedChange={(collapsed) => stateManager.setCollapsedColumn('right', collapsed)}
          width={state.columnWidths.right}
          onWidthChange={(width) =>
            stateManager.setColumnWidths({
              left: state.columnWidths.left,
              center: state.columnWidths.center,
              right: width,
            })
          }
          code={state.codeEditorContent}
          onCodeChange={(code) => stateManager.setCodeEditorContent(code)}
          diagramType={state.selectedDiagramType}
          onValidate={async (code) => {
            try {
              stateManager.setIsValidating(true);
              const result = await apiClient.validateCode({
                code,
                diagramType: state.selectedDiagramType,
              });
              stateManager.setValidationResult(result);
              if (result.isValid) {
                stateManager.setCurrentStatus('Validation passed', 'success');
                message.success('Code validation passed');
              } else {
                stateManager.setCurrentStatus('Validation errors found', 'error');
                message.error(`Found ${result.errors.length} validation error(s)`);
              }
            } catch (error) {
              const errorMsg = error instanceof Error ? error.message : 'Validation failed';
              stateManager.setCurrentStatus(`Validation error: ${errorMsg}`, 'error');
              message.error(errorMsg);
            } finally {
              stateManager.setIsValidating(false);
            }
          }}
          onRender={async (code) => {
            try {
              stateManager.setIsRendering(true);
              const diagram = await apiClient.renderDiagram({
                code,
                diagramType: state.selectedDiagramType,
              });
              stateManager.addGeneratedDiagram(state.selectedDiagramType, diagram);
              stateManager.setCurrentStatus('Diagram rendered successfully', 'success');
              message.success('Diagram rendered successfully');
            } catch (error) {
              const errorMsg = error instanceof Error ? error.message : 'Render failed';
              stateManager.setCurrentStatus(`Render error: ${errorMsg}`, 'error');
              message.error(errorMsg);
            } finally {
              stateManager.setIsRendering(false);
            }
          }}
          validationResult={state.validationResult}
          isValidating={state.isValidating}
          isRendering={state.isRendering}
          hasUnsavedChanges={state.codeEditorHasUnsavedChanges}
          errors={state.validationResult?.errors || []}
          onErrorDismiss={() => stateManager.setValidationResult(null)}
        />
      </Layout>

      {/* Footer */}
      <Footer
        currentStatus={state.currentStatus}
        sseMessages={state.sseMessages}
        unreadMessageCount={sseMessages.filter((m) => !m.isRead).length}
        isSSEConnected={sseConnected}
      />
    </Layout>
  );
};

export default ArchitectureGenStudio;
