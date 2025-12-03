/**
 * DiagramTypeSelectionScreen Component
 *
 * Intermediate screen shown after clarification phase is complete.
 * Displays 4 diagram type options with keyword scores and allows user to select.
 *
 * ## Screen Purpose
 * - Shows after user confirms ready (after clarification reaches target score)
 * - Displays all diagram types: Mermaid, D2, PlantUML, Structurizr
 * - Each type shows its suitability score based on keyword analysis
 * - User selects their preferred diagram type before code generation
 *
 * ## Data Flow
 * Backend Analysis → keyword_scores → Display Cards → User Selection → onSelectDiagramType
 *
 * ## Layout
 * ```
 * Header (Model, Session ID, Score)
 *   ↓
 * Progress Steps (Analysis → Clarification → Generation → Rendering)
 *   ↓
 * Title: "Select Diagram Type"
 *   ↓
 * Grid of 4 Cards:
 *   [Mermaid Card] [D2 Card]
 *   [PlantUML Card] [Structurizr Card]
 * ```
 */

import {
  ApartmentOutlined,
  CheckCircleOutlined,
  ClusterOutlined,
  DeploymentUnitOutlined,
  FileTextOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { Card, Col, Layout, Row, Table, Tag, Typography } from 'antd'
import React from 'react'

import DiagramWizardHeader from '../components/DiagramWizardHeader'
import styles from '../diagram-wizard.module.css'
import type { ModelId } from './ModelSelectionScreen'

const { Title, Paragraph } = Typography

interface DiagramTypeRecord {
  key: string
  type: string
  score: number
  isRecommended: boolean
}

/**
 * Props for DiagramTypeSelectionScreen component
 */
interface DiagramTypeSelectionScreenProps {
  selectedModel: ModelId
  currentPhase: number
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>
  sessionId: string | null
  score: number
  scoreTarget: number
  sseConnected: boolean
  loading: boolean
  recommendedDiagramType: string
  keywordScores: { [key: string]: number }
  analysisText?: string
  jsonGenerationOutput?: string
  onSelectDiagramType: (diagramType: string) => void
  onShowState?: () => void
}

/**
 * Diagram type configuration with icons, descriptions, and use cases
 */
const DIAGRAM_TYPES = [
  {
    type: 'Mermaid',
    icon: <FileTextOutlined style={{ fontSize: 48, color: '#ff6b6b' }} />,
    title: 'Mermaid',
    description: 'Flowcharts, sequence diagrams, and state machines',
    useCases: ['Process flows', 'User interactions', 'State transitions'],
  },
  {
    type: 'D2',
    icon: <DeploymentUnitOutlined style={{ fontSize: 48, color: '#4dabf7' }} />,
    title: 'D2',
    description: 'System architecture and infrastructure diagrams',
    useCases: ['Microservices', 'Cloud infrastructure', 'Service topology'],
  },
  {
    type: 'PlantUML',
    icon: <ApartmentOutlined style={{ fontSize: 48, color: '#51cf66' }} />,
    title: 'PlantUML',
    description: 'UML diagrams and class structures',
    useCases: ['Class diagrams', 'Component models', 'Use cases'],
  },
  {
    type: 'Structurizr',
    icon: <ClusterOutlined style={{ fontSize: 48, color: '#cc5de8' }} />,
    title: 'Structurizr',
    description: 'C4 model architecture diagrams',
    useCases: ['System context', 'Container views', 'Component views'],
  },
]

/**
 * DiagramTypeSelectionScreen component
 */
export const DiagramTypeSelectionScreen: React.FC<DiagramTypeSelectionScreenProps> = ({
  selectedModel,
  currentPhase,
  phases,
  sessionId,
  score,
  scoreTarget,
  sseConnected,
  loading,
  recommendedDiagramType,
  keywordScores,
  analysisText,
  jsonGenerationOutput,
  onSelectDiagramType,
  onShowState,
}) => {
  return (
    <Layout className={styles.diagramWizard}>
      {/* Unified Header Component */}
      <DiagramWizardHeader
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
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '40px 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              Select Diagram Type
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666' }}>
              Based on your system description, we've analyzed which diagram type would work best.
              Choose your preferred option below.
            </Paragraph>
          </div>

          {/* Summary Table of Diagram Type Scores */}
          <div style={{ marginBottom: 32 }}>
            <Table
              dataSource={DIAGRAM_TYPES.map((dt) => ({
                key: dt.type,
                type: dt.type,
                score: keywordScores[dt.type] || 0,
                isRecommended: dt.type === recommendedDiagramType,
              }))}
              columns={[
                {
                  title: 'Diagram Type',
                  dataIndex: 'type',
                  key: 'type',
                  render: (type: string, record: DiagramTypeRecord) => (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <strong>{type}</strong>
                      {record.isRecommended && (
                        <Tag color="blue" icon={<TrophyOutlined />}>
                          Recommended
                        </Tag>
                      )}
                    </div>
                  ),
                },
                {
                  title: 'Match Score',
                  dataIndex: 'score',
                  key: 'score',
                  align: 'center' as const,
                  sorter: (a: DiagramTypeRecord, b: DiagramTypeRecord) => b.score - a.score,
                  defaultSortOrder: 'descend' as const,
                  render: (score: number) => (
                    <Tag
                      color={score >= 40 ? 'green' : score >= 25 ? 'blue' : 'orange'}
                      style={{ fontSize: 14, padding: '4px 12px', fontWeight: 'bold' }}
                    >
                      {score.toFixed(1)}%
                    </Tag>
                  ),
                },
                {
                  title: 'Suitability',
                  dataIndex: 'score',
                  key: 'suitability',
                  align: 'center' as const,
                  render: (score: number) => {
                    if (score >= 40) return <Tag color="green">Excellent</Tag>
                    if (score >= 30) return <Tag color="blue">Good</Tag>
                    if (score >= 20) return <Tag color="orange">Fair</Tag>
                    return <Tag color="default">Low</Tag>
                  },
                },
              ]}
              pagination={false}
              size="small"
              style={{ backgroundColor: '#fff', borderRadius: 8 }}
            />
          </div>

          <Row gutter={[24, 24]} style={{ marginBottom: 32 }}>
            {DIAGRAM_TYPES.map((diagramType) => {
              const isRecommended = diagramType.type === recommendedDiagramType
              const scoreValue = keywordScores[diagramType.type] || 0

              return (
                <Col xs={24} sm={12} key={diagramType.type}>
                  <Card
                    hoverable
                    onClick={() => onSelectDiagramType(diagramType.type)}
                    style={{
                      height: '100%',
                      border: isRecommended ? '2px solid #1890ff' : '1px solid #f0f0f0',
                      boxShadow: isRecommended
                        ? '0 4px 12px rgba(24, 144, 255, 0.2)'
                        : '0 2px 8px rgba(0, 0, 0, 0.06)',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                    }}
                    bodyStyle={{ padding: 24 }}
                  >
                    <div style={{ textAlign: 'center', marginBottom: 16 }}>{diagramType.icon}</div>

                    <div style={{ textAlign: 'center', marginBottom: 16 }}>
                      <Title level={4} style={{ marginBottom: 4 }}>
                        {diagramType.title}
                        {isRecommended && (
                          <Tag
                            color="blue"
                            icon={<CheckCircleOutlined />}
                            style={{ marginLeft: 8 }}
                          >
                            Recommended
                          </Tag>
                        )}
                      </Title>
                      <Tag
                        color={scoreValue >= 40 ? 'green' : scoreValue >= 25 ? 'blue' : 'orange'}
                      >
                        {scoreValue.toFixed(1)}% Match
                      </Tag>
                    </div>

                    <Paragraph
                      style={{
                        textAlign: 'center',
                        color: '#666',
                        marginBottom: 16,
                        minHeight: 48,
                      }}
                    >
                      {diagramType.description}
                    </Paragraph>

                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
                      <Paragraph
                        style={{ fontSize: 12, color: '#8c8c8c', marginBottom: 8, fontWeight: 600 }}
                      >
                        Best for:
                      </Paragraph>
                      <ul style={{ fontSize: 12, color: '#666', paddingLeft: 20, margin: 0 }}>
                        {diagramType.useCases.map((useCase, idx) => (
                          <li key={idx}>{useCase}</li>
                        ))}
                      </ul>
                    </div>
                  </Card>
                </Col>
              )
            })}
          </Row>

          {analysisText && (
            <Card
              title="AI Response"
              size="small"
              style={{ marginBottom: 24, borderRadius: 8 }}
              bodyStyle={{ background: '#fafafa' }}
            >
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'Consolas, Menlo, Monaco, "Courier New", monospace',
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              >
                {analysisText}
              </pre>
            </Card>
          )}

          {jsonGenerationOutput && (
            <Card
              title="JSON Generation Output"
              size="small"
              style={{ marginBottom: 24, borderRadius: 8 }}
              bodyStyle={{ background: '#fafafa' }}
            >
              <pre
                style={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'Consolas, Menlo, Monaco, "Courier New", monospace',
                  fontSize: 13,
                  lineHeight: 1.5,
                }}
              >
                {jsonGenerationOutput}
              </pre>
            </Card>
          )}
        </div>
      </Layout.Content>
    </Layout>
  )
}

export default DiagramTypeSelectionScreen
