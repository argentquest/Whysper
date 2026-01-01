/**
 * DiagramWizardHeader Component
 *
 * Unified header component for Diagram Wizard screens that displays:
 * - Completion status tags
 * - Current LLM Assessment Score (prominently displayed)
 * - 4-Phase progression status (Analysis → Clarification → Generation → Rendering)
 * - Action buttons (View State, Generate Diagram)
 */

import {
  BulbOutlined,
  CheckCircleOutlined,
  EditOutlined,
  ExclamationCircleOutlined,
  MessageOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import { Button, Layout, Space, Spin, Steps, Tag, Tooltip } from 'antd'
import React from 'react'

import styles from '../diagram-wizard.module.css'

interface DiagramWizardHeaderProps {
  // Title and status
  title?: string
  isComplete?: boolean
  isError?: boolean

  // Session info
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
  title: _title = 'Diagram Wizard', // Unused - title display removed
  isComplete = false,
  isError = false,
  sessionId: _sessionId, // Unused - session ID moved to footer
  sseConnected: _sseConnected, // Unused - connection status moved to footer
  loading = false,
  score,
  scoreTarget = 80, // Default to 80 if not provided by backend
  currentPhase,
  phases,
  canConfirmReady = false,
  onConfirmReady,
  onShowState,
}) => {
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
          {/* Left: Status Tags + Score */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: '200px' }}>
            {/* Status Tags */}
            {isComplete && (
              <Tag color="green">
                <CheckCircleOutlined /> Complete
              </Tag>
            )}
            {isError && (
              <Tag color="red">
                <ExclamationCircleOutlined /> Error
              </Tag>
            )}

            {/* LLM Score */}
            {score > 0 && (
              <Tooltip title={`AI clarity assessment score. Target: ${scoreTarget} or higher to proceed.`}>
                <Tag
                  color={getScoreTagColor(score)}
                  style={{
                    fontSize: '16px',
                    padding: '8px 16px',
                    fontWeight: 'bold',
                  }}
                >
                  Score: 📊 {score}/{scoreTarget}
                </Tag>
              </Tooltip>
            )}
          </div>

          {/* Center: Progress Steps */}
          <div className={styles.progressSteps}>
            <Steps
              current={currentPhase}
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

          {/* Right: Session Info + Actions */}
          <Space size="middle" className={styles.headerMeta} align="center">
            {onShowState && (
              <Tooltip title="View current session state and debug information">
                <Button size="large" type="default" onClick={onShowState}>
                  View State
                </Button>
              </Tooltip>
            )}

            {loading && <Spin size="small" />}

            {/* Generate Diagram Button - Most right placement */}
            {canConfirmReady && onConfirmReady && (
              <Tooltip title="Start generating the diagram based on the current description">
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
                  Generate Diagram
                </Button>
              </Tooltip>
            )}
          </Space>
        </div>
      </div>
    </Layout.Header>
  )
}

export default DiagramWizardHeader
