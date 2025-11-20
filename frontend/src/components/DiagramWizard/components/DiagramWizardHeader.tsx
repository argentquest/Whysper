/**
 * DiagramWizardHeader Component
 *
 * Unified header component for Diagram Wizard screens that displays:
 * - Title and completion status
 * - Model selection and session information
 * - Current LLM Assessment Score (prominently displayed)
 * - 4-Phase progression status (Analysis → Clarification → Generation → Rendering)
 * - Connection status indicator
 */

import React from 'react';
import { Layout, Space, Tag, Badge, Spin } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';
import type { ModelId } from '../screens/ModelSelectionScreen';

interface DiagramWizardHeaderProps {
  // Title and status
  title?: string;
  isComplete?: boolean;
  isError?: boolean;

  // Model and session info
  selectedModel: ModelId;
  sessionId: string | null;
  sseConnected: boolean;
  loading?: boolean;

  // LLM Score
  score: number;
  scoreTarget?: number; // Dynamic score target from backend .env (default: 80)

  // Progress phases
  currentPhase: number;
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>;
}

/**
 * DiagramWizardHeader component
 */
export const DiagramWizardHeader: React.FC<DiagramWizardHeaderProps> = ({
  title = 'Diagram Wizard',
  isComplete = false,
  isError = false,
  selectedModel,
  sessionId,
  sseConnected,
  loading = false,
  score,
  scoreTarget = 80, // Default to 80 if not provided by backend
  currentPhase,
  phases,
}) => {
  // Get model display name
  const getModelDisplayName = (model: ModelId): string => {
    switch (model) {
      case 'gpt5':
        return 'Deep';
      case 'grok':
        return 'Fast';
      case 'claude':
        return 'Thinking';
      case 'gemini':
        return 'Efficient';
      default:
        return model;
    }
  };

  // Get score tag color (1-100 scale)
  // Uses dynamic scoreTarget from backend .env (default: 80)
  const getScoreTagColor = (score: number): string => {
    if (score >= scoreTarget) return 'green';
    if (score >= scoreTarget * 0.75) return 'blue'; // 75% of target
    return 'orange';
  };

  return (
    <Layout.Header className={styles.header}>
      <div className={styles.headerContent}>
        {/* Compact Single-Row Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
          {/* Left: Title + Score */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h2 className={styles.title} style={{ margin: 0 }}>
              {title}
              {isComplete && (
                <Tag color="green" style={{ marginLeft: '8px' }}>
                  <CheckCircleOutlined /> Complete
                </Tag>
              )}
              {isError && (
                <Tag color="red" style={{ marginLeft: '8px' }}>
                  <ExclamationCircleOutlined /> Error
                </Tag>
              )}
            </h2>

            {/* LLM Score */}
            {score > 0 && (
              <Tag
                color={getScoreTagColor(score)}
                style={{
                  fontSize: '13px',
                  padding: '4px 10px',
                  fontWeight: 'bold',
                }}
              >
                📊 {score}/{scoreTarget}
              </Tag>
            )}
          </div>

          {/* Right: Phase + Model + Session + Status */}
          <Space size="middle" className={styles.headerMeta}>
            {/* Current Phase - Simplified */}
            <Tag color="purple" style={{ fontSize: '12px', padding: '4px 10px' }}>
              {phases[Math.min(currentPhase, phases.length - 1)].icon}{' '}
              {phases[Math.min(currentPhase, phases.length - 1)].title}
            </Tag>

            {selectedModel && (
              <Tag color="blue" style={{ fontSize: '12px', padding: '4px 8px' }}>
                🤖 {getModelDisplayName(selectedModel)}
              </Tag>
            )}
            {sessionId && (
              <>
                <span className={styles.sessionId} style={{ fontSize: '11px' }}>
                  {sessionId.substring(0, 8)}...
                </span>
                <Badge
                  status={sseConnected ? 'success' : 'error'}
                  text={sseConnected ? 'Connected' : 'Disconnected'}
                  style={{ fontSize: '11px' }}
                />
                {loading && <Spin size="small" />}
              </>
            )}
          </Space>
        </div>
      </div>
    </Layout.Header>
  );
};

export default DiagramWizardHeader;
