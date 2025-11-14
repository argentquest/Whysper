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
import { Layout, Button, Input, Spin, Alert, message, Divider, Space, Steps, Tabs, Modal } from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  DownloadOutlined,
  CopyOutlined,
  DeleteOutlined,
  SearchOutlined,
  SettingOutlined,
  CodeOutlined,
  PictureOutlined,
} from '@ant-design/icons';
import { useDiagramSession } from './hooks/useDiagramSession';
import ChatPanel from './panels/Panel1_Chat';
import PreviewPanel from './panels/Panel2_Preview';
import CodeEditorPanel from './panels/Panel3_CodeEditor';
import styles from './diagram-wizard.module.css';
import type { ScoreInfo, DiagramUpdate } from '../../services/diagram/diagramApi';

interface DiagramWizardProps {
  onDiagramGenerated?: (code: string, svg: string) => void;
  initialPrompt?: string;
}

type DiagramType = 'Mermaid' | 'D2' | 'PlantUML';

interface AssistantResponseDetail {
  id: string;
  messageIndex: number;
  message?: string;
  score?: number;
  scoreInfo?: ScoreInfo;
  clarityScore?: number;
  jsonRepresentation?: Record<string, unknown> | null;
  rawUpdate?: Record<string, unknown>;
}

type DiagramUpdateWithVariants = DiagramUpdate & {
  json_representation?: unknown;
  score_info?: ScoreInfo;
  scoreInfo?: ScoreInfo;
};

export const DiagramWizard: React.FC<DiagramWizardProps> = ({
  onDiagramGenerated,
  initialPrompt,
}) => {
  const [diagramType, setDiagramType] = useState<DiagramType>('Mermaid');
  const [userInput, setUserInput] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [isInAnalysisPhase, setIsInAnalysisPhase] = useState(false);
  const [clarificationInput, setClarificationInput] = useState('');
  const [score, setScore] = useState(0);
  const [assistantResponses, setAssistantResponses] = useState<Record<number, AssistantResponseDetail>>({});
  const [selectedResponse, setSelectedResponse] = useState<AssistantResponseDetail | null>(null);

  const normalizeJsonRepresentation = (jsonData: unknown): Record<string, unknown> | null => {
    if (!jsonData) {
      return null;
    }

    if (typeof jsonData === 'string') {
      try {
        return JSON.parse(jsonData);
      } catch (err) {
        console.warn('Failed to parse JSON representation for assistant response', err);
        return null;
      }
    }

    if (typeof jsonData === 'object') {
      return jsonData as Record<string, unknown>;
    }

    return null;
  };

  const getScoreInfo = (payload?: DiagramUpdateWithVariants): ScoreInfo | undefined => {
    if (!payload) return undefined;
    if (payload.score_info) return payload.score_info;
    if (payload.scoreInfo) return payload.scoreInfo;
    return undefined;
  };

  const trackAssistantResponse = (update: DiagramUpdateWithVariants) => {
    const historyLength = update.history?.length ?? 0;
    if (!historyLength) {
      return;
    }

    const latestIndex = historyLength - 1;
    const latestEntry = update.history?.[latestIndex];
    if (!latestEntry) {
      return;
    }

    const [role, entryContent] = latestEntry;
    if (role !== 'assistant') {
      return;
    }

    const normalizedJson =
      normalizeJsonRepresentation(update.jsonRepresentation ?? update.json_representation ?? null) ??
      null;

    setAssistantResponses((prev) => {
      const existing = prev[latestIndex];
      const detail: AssistantResponseDetail = {
        id: existing?.id ?? `${update.session_id}-${latestIndex}`,
        messageIndex: latestIndex,
        message: update.message ?? entryContent ?? existing?.message,
        score:
          typeof update.score === 'number'
            ? update.score
            : typeof update.assessment_score === 'number'
            ? update.assessment_score
            : existing?.score,
        scoreInfo: getScoreInfo(update) ?? existing?.scoreInfo,
        clarityScore:
          typeof update.clarity_score === 'number' ? update.clarity_score : existing?.clarityScore,
        jsonRepresentation: normalizedJson ?? existing?.jsonRepresentation ?? null,
        rawUpdate: update as Record<string, unknown>,
      };

      if (
        existing &&
        existing.message === detail.message &&
        existing.score === detail.score &&
        existing.clarityScore === detail.clarityScore &&
        existing.scoreInfo === detail.scoreInfo &&
        existing.jsonRepresentation === detail.jsonRepresentation
      ) {
        return prev;
      }

      return {
        ...prev,
        [latestIndex]: detail,
      };
    });
  };

  const {
    sessionId,
    status,
    loading,
    error,
    startSession,
    submitClarification,
    renderDiagram,
    approveRender,
    endSession,
  } = useDiagramSession({
    onUpdate: (update) => {
      // Handle incoming updates from SSE and respect LangGraph phases
      console.log('🔄 LangGraph SSE update received:', update);
      const latestScore =
        typeof update.score === 'number'
          ? update.score
          : typeof update.assessment_score === 'number'
          ? update.assessment_score
          : undefined;

      if (typeof latestScore === 'number') {
        setScore(latestScore);
      }

      // Cache assistant responses so we can show full details later
      trackAssistantResponse(update);

      // PHASE 1: Information Gathering & Analysis
      if (update.status === 'analyzing') {
        setCurrentPhase(1);
        setIsInAnalysisPhase(true);
        message.info('🔍 AI is analyzing your system description...');
        
      } else if (update.status === 'clarifying') {
        setCurrentPhase(1);
        setIsInAnalysisPhase(true);
        if (status && update.message) {
          status.history.push(['assistant', update.message]);
        }
        message.info('❓ AI needs more information - please provide additional details');
        
      } else if (update.status === 'can_proceed') {
        setCurrentPhase(1);
        setIsInAnalysisPhase(true);
        if (status && update.message) {
          status.history.push(['assistant', update.message]);
        }
        message.success('✅ AI has sufficient information - ready to proceed!');
        
      } else if (update.status === 'type_selection') {
        setCurrentPhase(1);
        setIsInAnalysisPhase(true);
        if (status && update.message) {
          status.history.push(['assistant', update.message]);
        }
        message.info('🎯 AI analysis complete - please select diagram type');
        
      } else if (update.status === 'ai_thinking') {
        // AI is processing - show thinking state but don't change phase
        if (status && update.message) {
          status.history.push(['assistant', update.message]);
        }
        message.loading('🧠 AI is thinking...');
        
      } else if (update.status === 'ai_response') {
        // AI has responded but still in same phase - update message only
        if (status && update.message) {
          status.history.push(['assistant', update.message]);
        }
        
      } else if (update.status === 'clarification_received') {
        // User provided clarification - wait for AI to process
        message.info('📝 Clarification received, AI is processing...');
        
      // PHASE 2: Diagram Generation (only advance when LLM actually starts)
      } else if (update.status === 'started') {
        setCurrentPhase(2);
        setIsInAnalysisPhase(false);
        message.info('🚀 Starting diagram generation...');
        
      } else if (update.status === 'generating') {
        setCurrentPhase(2);
        setIsInAnalysisPhase(false);
        message.loading('⚡ AI is generating diagram code...');
        
      // PHASE 3: Completion (only when actually done)
      } else if (update.status === 'completed') {
        setCurrentPhase(3);
        setIsInAnalysisPhase(false);
        message.success('🎉 Diagram generated successfully!');
        if (onDiagramGenerated && status) {
          onDiagramGenerated(status.diagramCode, status.svgOutput);
        }
      } else if (update.status === 'error') {
        setIsInAnalysisPhase(false);
        message.error(`Error: ${update.message || 'Unknown error occurred'}`);
      }
    },
    onError: (err) => {
      console.error('Session error:', err);
      message.error(`Session error: ${err.message}`);
    },
  });

  // Handle initial prompt if provided - but don't auto-start
  useEffect(() => {
    if (initialPrompt && !sessionId && !isInitializing) {
      setUserInput(initialPrompt);
      // NOTE: Do NOT auto-start here - wait for explicit user interaction
      console.log('📝 Initial prompt set, waiting for user to start manually');
    }
  }, [initialPrompt, sessionId, isInitializing]);

  useEffect(() => {
    setAssistantResponses({});
    setSelectedResponse(null);
    if (!sessionId) {
      setScore(0);
    }
  }, [sessionId]);

  // Handle starting diagram generation - respect phases
  const handleStartDiagram = async () => {
    if (!userInput.trim()) {
      message.warning('Please enter a system description');
      return;
    }

    // Prevent starting if already in progress
    if (sessionId || isInitializing || loading) {
      console.warn('⚠️ Session already in progress, ignoring start request');
      message.warning('Session already in progress');
      return;
    }

    try {
      setIsInitializing(true);
      setCurrentPhase(0); // Reset to initial phase
      console.log('🚀 Starting new diagram session with:', userInput.substring(0, 100) + '...');
      
      // Let the backend AI analyze first - no auto diagram type
      await startSession(userInput, 'auto');
      console.log('✅ Session started, waiting for AI analysis...');
      
    } catch (err) {
      console.error('❌ Failed to start session:', err);
      message.error(`Failed to start AI analysis: ${err}`);
      setCurrentPhase(0); // Reset on error
    } finally {
      setIsInitializing(false);
      setUserInput(''); // Clear input after starting
    }
  };

  // Handle submitting clarification - ensure proper phase management
  const handleSubmitClarification = async (clarification: string) => {
    if (!clarification.trim()) {
      message.warning('Please provide clarification details');
      return;
    }
    
    if (!sessionId) {
      message.error('No active session for clarification');
      return;
    }
    
    try {
      console.log('📤 Submitting clarification to LangGraph:', clarification.substring(0, 100) + '...');
      // Keep current phase - let LLM determine next step
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

  const handleViewResponseDetails = (messageIndex: number) => {
    if (!status?.history || status.history.length <= messageIndex) {
      return;
    }

    const detail = assistantResponses[messageIndex];
    if (detail) {
      setSelectedResponse(detail);
      return;
    }

    const [, content] = status.history[messageIndex];
    setSelectedResponse({
      id: `${sessionId ?? 'session'}-${messageIndex}`,
      messageIndex,
      message: content,
      score,
      scoreInfo: status?.score_info,
      jsonRepresentation: status?.jsonRepresentation ?? null,
    });
  };

  const closeResponseModal = () => setSelectedResponse(null);

  // Handle diagram type selection during analysis phase
  const handleDiagramTypeSelection = async (selectedType: string) => {
    try {
      setIsInitializing(true);
      if (['Mermaid', 'D2', 'PlantUML'].includes(selectedType)) {
        setDiagramType(selectedType as DiagramType);
      }
      await submitClarification(selectedType);
    } catch (err) {
      message.error(`Failed to submit diagram type selection: ${err}`);
    } finally {
      setIsInitializing(false);
    }
  };

  // Handle clarification response
  const handleClarificationSubmit = async () => {
    if (!clarificationInput.trim()) {
      message.warning('Please provide additional details');
      return;
    }
    
    try {
      setIsInitializing(true);
      await submitClarification(clarificationInput);
      setClarificationInput('');
    } catch (err) {
      message.error(`Failed to submit clarification: ${err}`);
    } finally {
      setIsInitializing(false);
    }
  };

  // Handle ending session
  const handleEndSession = async () => {
    try {
      await endSession();
      setCurrentPhase(0);
      setIsInAnalysisPhase(false);
      setAssistantResponses({});
      setSelectedResponse(null);
      setScore(0);
      message.info('Session ended');
    } catch (err) {
      message.error(`Failed to end session: ${err}`);
    }
  };

  // Define the phases
  const phases = [
    {
      title: 'Describe',
      description: 'Describe your system',
      icon: <SearchOutlined />
    },
    {
      title: 'Analyze',
      description: 'AI analyzes & suggests',
      icon: <SettingOutlined />
    },
    {
      title: 'Generate',
      description: 'Create diagram code',
      icon: <CodeOutlined />
    },
    {
      title: 'Visualize',
      description: 'Render final diagram',
      icon: <PictureOutlined />
    }
  ];

  const conversationMessages = (status?.history ?? []).map(([role, content]) => ({
    role: role === 'assistant' ? 'assistant' : 'user',
    content,
  }));

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
        {/* Progress Steps */}
        <div style={{ marginBottom: 24, padding: '0 24px' }}>
          <Steps
            current={currentPhase}
            size="small"
            items={phases.map((phase, index) => ({
              title: phase.title,
              description: phase.description,
              icon: phase.icon,
              status: currentPhase > index ? 'finish' : currentPhase === index ? 'process' : 'wait'
            }))}
          />
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

        {!sessionId ? (
          // Initial system description phase
          <div className={styles.initialScreen}>
            <h3>Describe Your System</h3>
            <p style={{ marginBottom: 16, color: '#666' }}>
              Tell us about the system or process you want to visualize. We'll have a conversation to gather all the details needed.
            </p>

            <Input.TextArea
              placeholder="Describe the system, process, or architecture you want to diagram. For example:
• A user authentication flow for a web application
• The architecture of a microservices system
• A data processing pipeline
• An organizational hierarchy"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              rows={6}
              disabled={loading}
            />

            <div className={styles.controls}>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleStartDiagram}
                loading={loading || isInitializing}
                size="large"
              >
                Start Conversation
              </Button>
            </div>
          </div>
        ) : isInAnalysisPhase ? (
          // Analysis conversation phase - show chat interface
          <div className={styles.conversationContainer}>
            <div style={{ display: 'flex', height: '500px', gap: '16px' }}>
              {/* Chat History Panel */}
              <div style={{ 
                flex: 1, 
                border: '1px solid #d9d9d9', 
                borderRadius: '8px', 
                padding: '16px',
                backgroundColor: '#fafafa',
                overflowY: 'auto'
              }}>
                <h4 style={{ marginTop: 0, marginBottom: 16 }}>💬 Conversation</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {status?.history?.map(([role, content], index) => (
                    <div 
                      key={index}
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        backgroundColor: role === 'user' ? '#e6f4ff' : '#f6ffed',
                        border: `1px solid ${role === 'user' ? '#91caff' : '#b7eb8f'}`,
                        alignSelf: role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%'
                      }}
                    >
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        {role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                      </div>
                      <div dangerouslySetInnerHTML={{ 
                        __html: content.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                      }} />
                      {role === 'assistant' && (
                        <Button
                          type="link"
                          size="small"
                          style={{ padding: 0, marginTop: 8 }}
                          onClick={() => handleViewResponseDetails(index)}
                        >
                          View full response
                        </Button>
                      )}
                    </div>
                  ))}
                  {status?.clarifications?.slice(-1).map((clarification, index) => (
                    <div 
                      key={`clarification-${index}`}
                      style={{
                        padding: '12px',
                        borderRadius: '8px',
                        backgroundColor: '#f6ffed',
                        border: '1px solid #b7eb8f',
                        alignSelf: 'flex-start',
                        maxWidth: '80%'
                      }}
                    >
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        🤖 AI Assistant
                      </div>
                      <div dangerouslySetInnerHTML={{ 
                        __html: clarification.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') 
                      }} />
                    </div>
                  ))}
                  {(loading || isInitializing) && (
                    <div style={{
                      padding: '12px',
                      borderRadius: '8px',
                      backgroundColor: '#f0f0f0',
                      border: '1px solid #d9d9d9',
                      alignSelf: 'flex-start',
                      maxWidth: '80%'
                    }}>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
                        🤖 AI Assistant
                      </div>
                      <Spin size="small" /> Thinking...
                    </div>
                  )}
                </div>
              </div>

              {/* Response Panel */}
              <div style={{ 
                flex: 1, 
                border: '1px solid #d9d9d9', 
                borderRadius: '8px', 
                padding: '16px',
                display: 'flex',
                flexDirection: 'column'
              }}>
                <h4 style={{ marginTop: 0, marginBottom: 16 }}>
                  {status?.status === 'type_selection' ? '📊 Ready to Generate' : '💭 Your Response'}
                </h4>
                
                {status?.status === 'type_selection' ? (
                  // Diagram type selection
                  <div style={{ flex: 1 }}>
                    <div style={{ marginBottom: 16, padding: 12, backgroundColor: '#f0f9ff', borderRadius: 6 }}>
                      <strong>Great! I have enough information to create your diagram.</strong>
                    </div>
                    
                    <p style={{ marginBottom: 16 }}>
                      Please confirm the recommended diagram type:
                    </p>

                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Button
                        type="primary"
                        onClick={() => handleDiagramTypeSelection('yes')}
                        loading={loading || isInitializing}
                        block
                      >
                        ✅ Use AI Recommendation
                      </Button>
                      <Button
                        onClick={() => handleDiagramTypeSelection('Mermaid')}
                        loading={loading || isInitializing}
                        block
                      >
                        🌊 Mermaid (Flowcharts, Sequences)
                      </Button>
                      <Button
                        onClick={() => handleDiagramTypeSelection('D2')}
                        loading={loading || isInitializing}
                        block
                      >
                        🏗️ D2 (Architecture, Systems)
                      </Button>
                      <Button
                        onClick={() => handleDiagramTypeSelection('PlantUML')}
                        loading={loading || isInitializing}
                        block
                      >
                        🌱 PlantUML (UML, Databases)
                      </Button>
                    </Space>
                  </div>
                ) : (
                  // Clarification input
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    {status?.score_info && (
                      <div style={{ 
                        marginBottom: 16, 
                        padding: 12, 
                        backgroundColor: status.score_info.has_good_info ? '#f6ffed' : 
                                        status.score_info.has_minimum_info ? '#fff7e6' : '#f0f2f5', 
                        borderRadius: 6,
                        border: `1px solid ${status.score_info.has_good_info ? '#b7eb8f' : 
                                              status.score_info.has_minimum_info ? '#ffd591' : '#d9d9d9'}`
                      }}>
                        <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: 8 }}>
                          📊 Information Progress: {status.score_info.info_score}/3
                        </div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: 8 }}>
                          🎯 AI Score: {score}/10
                        </div>
                        <div style={{ display: 'flex', gap: '12px', fontSize: '12px', marginBottom: 8 }}>
                          <span style={{ color: status.score_info.entities ? '#52c41a' : '#ff4d4f' }}>
                            {status.score_info.entities ? '✅' : '❌'} Entities
                          </span>
                          <span style={{ color: status.score_info.actions ? '#52c41a' : '#ff4d4f' }}>
                            {status.score_info.actions ? '✅' : '❌'} Actions
                          </span>
                          <span style={{ color: status.score_info.structure ? '#52c41a' : '#ff4d4f' }}>
                            {status.score_info.structure ? '✅' : '❌'} Structure
                          </span>
                          <span style={{ color: status.score_info.word_count >= 20 ? '#52c41a' : status.score_info.word_count >= 12 ? '#faad14' : '#ff4d4f' }}>
                            📝 {status.score_info.word_count} words
                          </span>
                        </div>
                        {status.score_info.has_minimum_info && (
                          <div style={{ fontSize: '12px', color: '#389e0d', fontWeight: 'bold' }}>
                            {status.score_info.has_good_info ? '🎉 Excellent! Ready for high-quality diagram' : '✅ Good! Can proceed or add more details'}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {status?.status === 'can_proceed' ? (
                      // Show both options when ready to proceed
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        <Button
                          type="primary"
                          icon={<SendOutlined />}
                          onClick={() => handleDiagramTypeSelection('proceed')}
                          loading={loading || isInitializing}
                          size="large"
                          style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
                        >
                          🎯 Proceed to Diagram Generation
                        </Button>
                        
                        <div style={{ textAlign: 'center', color: '#666', fontSize: '12px' }}>
                          or continue adding more details below
                        </div>
                        
                        <Input.TextArea
                          placeholder="Add more details to improve the diagram (optional)..."
                          value={clarificationInput}
                          onChange={(e) => setClarificationInput(e.target.value)}
                          rows={3}
                          disabled={loading}
                        />

                        <Button
                          icon={<SendOutlined />}
                          onClick={handleClarificationSubmit}
                          loading={loading || isInitializing}
                          disabled={!clarificationInput.trim()}
                        >
                          Add More Details
                        </Button>
                      </div>
                    ) : (
                      // Normal clarification input
                      <div style={{ display: 'flex', flexDirection: 'column' }}>
                        <Input.TextArea
                          placeholder="Type your response here..."
                          value={clarificationInput}
                          onChange={(e) => setClarificationInput(e.target.value)}
                          rows={6}
                          disabled={loading}
                          style={{ marginBottom: 16 }}
                        />

                        <Button
                          type="primary"
                          icon={<SendOutlined />}
                          onClick={handleClarificationSubmit}
                          loading={loading || isInitializing}
                          block
                          size="large"
                        >
                          Send Response
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          // Multi-panel view
          <div className={styles.panelsContainer}>
            <div className={styles.panelRow}>
              <div className={styles.leftPanel}>
                <ChatPanel
                  messages={conversationMessages}
                  clarifications={status?.clarifications || []}
                  onSubmit={handleSubmitClarification}
                  isLoading={loading}
                  sessionActive={status?.isRunning || false}
                  onViewResponseDetails={handleViewResponseDetails}
                />
              </div>

              <Divider type="vertical" style={{ height: '100%' }} />

              <div className={styles.rightPanel}>
                <Tabs defaultActiveKey="1" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <Tabs.TabPane tab="Preview" key="1" style={{ height: '100%', overflow: 'auto' }}>
                    <PreviewPanel
                      svgOutput={status?.svgOutput || ''}
                      diagramType={diagramType}
                      isLoading={loading || status?.isRunning}
                    />
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="Code" key="2" style={{ height: '100%' }}>
                    <CodeEditorPanel
                      code={status?.diagramCode || ''}
                      diagramType={diagramType}
                      onChange={handleCodeChange}
                      isLoading={loading}
                    />
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="JSON" key="3" style={{ height: '100%' }}>
                    <CodeEditorPanel
                      code={JSON.stringify(status?.jsonRepresentation, null, 2) || ''}
                      diagramType="json"
                      isLoading={loading}
                    />
                  </Tabs.TabPane>
                </Tabs>
              </div>
            </div>

            <Divider />

            {/* Action buttons */}
            <div className={styles.actionBar}>
              <Space>
                {status?.diagramCode && !status?.svgOutput && (
                  <Button
                    type="primary"
                    onClick={() => approveRender()}
                    loading={loading}
                  >
                    Render Diagram
                  </Button>
                )}

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

      <Modal
        open={Boolean(selectedResponse)}
        onCancel={closeResponseModal}
        footer={null}
        title="Full AI Assistant Response"
        width={840}
        destroyOnClose
      >
        {selectedResponse && (
          <>
            <div
              style={{
                marginBottom: 16,
                padding: '8px 12px',
                backgroundColor: '#f6ffed',
                borderRadius: 6,
                border: '1px solid #b7eb8f',
              }}
            >
              <div
                dangerouslySetInnerHTML={{
                  __html:
                    (selectedResponse.message || '')
                      .replace(/\n/g, '<br/>')
                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') || '<em>No summary available for this turn.</em>',
                }}
              />
            </div>

            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 16,
                marginBottom: 16,
                fontSize: 14,
              }}
            >
              <span>
                <strong>AI Score:</strong>{' '}
                {typeof selectedResponse.score === 'number' ? `${selectedResponse.score}/10` : 'N/A'}
              </span>
              {typeof selectedResponse.clarityScore === 'number' && (
                <span>
                  <strong>Clarity Score:</strong> {selectedResponse.clarityScore}/10
                </span>
              )}
              {selectedResponse.scoreInfo && (
                <span>
                  <strong>Information Score:</strong> {selectedResponse.scoreInfo.info_score}/3 &nbsp;(
                  {selectedResponse.scoreInfo.word_count} words)
                </span>
              )}
            </div>

            <div
              style={{
                backgroundColor: '#0f172a',
                color: '#e2e8f0',
                borderRadius: 8,
                padding: 16,
                maxHeight: 360,
                overflow: 'auto',
                fontFamily: 'Menlo, Consolas, monospace',
                fontSize: 13,
              }}
            >
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                {selectedResponse.jsonRepresentation
                  ? JSON.stringify(selectedResponse.jsonRepresentation, null, 2)
                  : 'No structured JSON captured for this turn yet.'}
              </pre>
            </div>
          </>
        )}
      </Modal>
    </Layout>
  );
};

export default DiagramWizard;
