/**
 * ModelSelectionScreen Component
 *
 * First screen of DiagramWizard: User selects which AI model to use
 * for diagram generation. Displays 4 model options with descriptions.
 */

import { ApiOutlined,BulbOutlined, FileTextOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { Card, Col, Row, Space, Typography } from 'antd'
import React from 'react'

import DiagramWizardHeader from '../components/DiagramWizardHeader'
import styles from '../diagram-wizard.module.css'

export type ModelId = 'gpt5' | 'grok' | 'claude' | 'gemini'

/**
 * ModelOption type definition
 *
 * Describes the structure and properties of ModelOption
 */
export interface ModelOption {
  id: ModelId
  name: string
  displayName: string
  description: string
  strengths: string[]
  icon: React.ReactNode
  color: string
}

const MODELS: ModelOption[] = [
  {
    id: 'gpt5',
    name: 'Deep Context',
    displayName: 'Deep Context',
    description: 'Deep contextual analysis with long-context reasoning',
    strengths: [
      'Complex system architectures',
      'Comprehensive validation',
      'Rich metadata extraction',
      'Deep verification',
    ],
    icon: <BulbOutlined />,
    color: '#1890ff',
  },
  {
    id: 'grok',
    name: 'Fast',
    displayName: 'Fast',
    description: 'Fast, deterministic analysis with lean efficiency',
    strengths: ['Quick analysis', 'Deterministic results', 'Simple systems', 'Minimal overhead'],
    icon: <ThunderboltOutlined />,
    color: '#faad14',
  },
  {
    id: 'claude',
    name: 'Thinking',
    displayName: 'Thinking',
    description: 'Transparent thinking with structured reasoning',
    strengths: [
      'Clear explanations',
      'Structured output',
      'Visible reasoning',
      'Complete metadata',
    ],
    icon: <FileTextOutlined />,
    color: '#52c41a',
  },
  {
    id: 'gemini',
    name: 'Efficient',
    displayName: 'Efficient',
    description: 'Efficient output with pragmatic approach',
    strengths: [
      'Fast processing',
      'Practical approach',
      'Resource efficient',
      'Real-time feedback',
    ],
    icon: <ApiOutlined />,
    color: '#ff7a45',
  },
]

/**
 * ModelSelectionScreenProps type definition
 *
 * Describes the structure and properties of ModelSelectionScreenProps
 */
interface ModelSelectionScreenProps {
  onSelect: (modelId: ModelId) => void
  loading?: boolean
  currentPhase: number
  phases: Array<{ title: string; description: string; icon: React.ReactNode }>
  sessionId: string | null
  sseConnected: boolean
  score: number
  scoreTarget: number
  onShowState?: () => void
}

/**
 * ModelSelectionScreen component
 */
export const ModelSelectionScreen: React.FC<ModelSelectionScreenProps> = ({
  onSelect,
  loading = false,
  currentPhase,
  phases,
  sessionId,
  sseConnected,
  score,
  scoreTarget,
  onShowState,
}) => {
  return (
    <div
      style={{
        padding: '40px',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #e8f4f8 0%, #d4e9f0 100%)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <DiagramWizardHeader
        selectedModel={'gpt5'}
        sessionId={sessionId}
        sseConnected={sseConnected}
        loading={loading}
        score={score}
        scoreTarget={scoreTarget}
        currentPhase={currentPhase}
        phases={phases}
        onShowState={onShowState}
      />
      <Space direction="vertical" size="large" style={{ width: '100%', maxWidth: '1200px' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <Typography.Title level={2} style={{ color: '#1a1a1a', marginBottom: '8px' }}>
            Choose Your AI Model
          </Typography.Title>
          <Typography.Paragraph style={{ color: '#595959', fontSize: '16px' }}>
            Select the AI model that best fits your architecture needs. You can use a different
            model for each diagram.
          </Typography.Paragraph>
        </div>

        {/* Model Cards */}
        <Row gutter={[24, 24]} justify="center">
          {MODELS.map((model) => (
            <Col key={model.id} xs={24} sm={12} md={6} lg={5}>
              <Card
                hoverable
                style={{
                  borderTop: `4px solid ${model.color}`,
                  height: '100%',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.6 : 1,
                  transition: 'all 0.3s ease',
                }}
                onClick={() => !loading && onSelect(model.id)}
                className={styles.modelCard}
              >
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  {/* Model Icon and Name */}
                  <div style={{ textAlign: 'center' }}>
                    <div
                      style={{
                        fontSize: '32px',
                        color: model.color,
                        marginBottom: '8px',
                      }}
                    >
                      {model.icon}
                    </div>
                    <Typography.Title level={4} style={{ marginBottom: '4px' }}>
                      {model.displayName}
                    </Typography.Title>
                    <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
                      {model.description}
                    </Typography.Text>
                  </div>

                  {/* Strengths */}
                  <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: '12px' }}>
                    <Typography.Text
                      strong
                      type="secondary"
                      style={{ display: 'block', marginBottom: '8px', fontSize: '12px' }}
                    >
                      Best For:
                    </Typography.Text>
                    <Space direction="vertical" size={4} style={{ width: '100%' }}>
                      {model.strengths.map((strength, idx) => (
                        <div key={idx} style={{ fontSize: '12px', color: '#666' }}>
                          ✓ {strength}
                        </div>
                      ))}
                    </Space>
                  </div>

                  {/* Select Button */}
                  <button
                    onClick={() => !loading && onSelect(model.id)}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '8px 16px',
                      backgroundColor: model.color,
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: 'bold',
                      opacity: loading ? 0.6 : 1,
                      transition: 'all 0.3s ease',
                    }}
                  >
                    {loading ? 'Loading...' : 'Select'}
                  </button>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>

        {/* Info Footer */}
        <div
          style={{
            textAlign: 'center',
            marginTop: '40px',
            fontSize: '12px',
          }}
        >
          <Typography.Text style={{ color: '#595959' }}>
            💡 Tip: Different models handle architectures differently. Feel free to experiment!
          </Typography.Text>
        </div>
      </Space>
    </div>
  )
}

export default ModelSelectionScreen
