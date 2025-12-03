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

import {
  BulbOutlined,
  CheckCircleOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  MessageOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import { Badge, Button, Layout, Space, Spin, Steps, Tag, Tooltip } from 'antd'
import React from 'react'

import styles from '../diagram-wizard.module.css'
import type { ModelId } from '../screens/ModelSelectionScreen'

interface DiagramWizardHeaderProps {
  // Title and status
  title?: string
  isComplete?: boolean
  isError?: boolean

  // Model and session info
  selectedModel: ModelId
  sessionId: string | null
  sseConnected: boolean
  loading?: boolean

  // LLM Score
  score: number
  scoreTarget?: number // Dynamic score target from backend .env (default: 80)

  // Progress phases
  currentPhase: number
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>

  // Confirm Ready button
  canConfirmReady?: boolean
  onConfirmReady?: () => void

  // Debug/inspection
  onShowState?: () => void
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
  canConfirmReady = false,
  onConfirmReady,
  onShowState,
}) => {
  // Get model display name
  const getModelDisplayName = (model: ModelId): string => {
    switch (model) {
      case 'gpt5':
        return 'Deep'
      case 'grok':
        return 'Fast'
      case 'claude':
        return 'Thinking'
      case 'gemini':
        return 'Efficient'
      default:
        return model
    }
  }

  // Get score tag color (1-100 scale)
  // Uses dynamic scoreTarget from backend .env (default: 80)
  const getScoreTagColor = (score: number): string => {
    if (score >= scoreTarget) return 'green'
    if (score >= scoreTarget * 0.75) return 'blue' // 75% of target
    return 'orange'
  }

  // Map phase icons to Ant Design icons
  const getPhaseIcon = (phaseTitle: string): React.ReactNode => {
    switch (phaseTitle) {
      case 'Analysis':
        return <SearchOutlined />
      case 'Clarification':
        return <MessageOutlined />
      case 'Generation':
        return <EditOutlined />
      case 'Rendering':
        return <BulbOutlined />
      default:
        return null
    }
  }

  return (
    <Layout.Header className={styles.header}>
      <div className={styles.headerContent}>
        {/* Single Row Header with Progress */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '20px',
            flexWrap: 'wrap',
          }}
        >
          {/* Left: Title + Score */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '200px' }}>
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

          {/* Center: Progress Steps */}
          <div className={styles.progressSteps}>
            <Steps
              current={currentPhase}
              size="small"
              items={phases.map((phase, index) => ({
                title: (
                  <Tooltip title={phase.description} placement="bottom">
                    <span className={styles.progressStepTitle}>{phase.title}</span>
                  </Tooltip>
                ),
                icon: getPhaseIcon(phase.title),
                status:
                  index < currentPhase ? 'finish' : index === currentPhase ? 'process' : 'wait',
              }))}
            />
          </div>

          {/* Right: Confirm Button + Model + Session + Status */}
          <Space size="middle" className={styles.headerMeta}>
            {onShowState && (
              <Button size="small" onClick={onShowState}>
                View State
              </Button>
            )}
            {/* Confirm Ready Button - Prominent placement */}
            {canConfirmReady && onConfirmReady && (
              <Button
                type="primary"
                size="large"
                onClick={onConfirmReady}
                loading={loading}
                style={{
                  backgroundColor: '#52c41a',
                  borderColor: '#52c41a',
                  fontWeight: 'bold',
                  boxShadow: '0 2px 8px rgba(82, 196, 26, 0.3)',
                }}
              >
                ✓ Confirm Ready
              </Button>
            )}

            {selectedModel && (
              <Tag color="blue" style={{ fontSize: '12px', padding: '4px 8px' }}>
                🤖 {getModelDisplayName(selectedModel)}
              </Tag>
            )}
            {sessionId && (
              <>
                <span className={styles.sessionId}>{sessionId.substring(0, 8)}...</span>
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
  )
}

export default DiagramWizardHeader
