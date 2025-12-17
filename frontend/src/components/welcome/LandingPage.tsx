// @ts-nocheck
/**
 * LandingPage Component
 *
 * Initial welcome screen showcasing main features of Whysper
 * with a modern card-based layout similar to AI model selection
 */
import './LandingPage.css'

import {
  BookOutlined,
  CodeOutlined,
  DeploymentUnitOutlined,
  FileTextOutlined,
  MessageOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { Button, Card, Col,Row, Typography } from 'antd'
import { Brand } from 'branding'
import React from 'react'

const { Title, Paragraph } = Typography

interface FeatureCardProps {
  title: string
  description: string
  icon: React.ReactNode
  color: string
  bestFor: string[]
  onSelect: () => void
  buttonText?: string
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  title,
  description,
  icon,
  color,
  bestFor,
  onSelect,
  buttonText = 'Start',
}) => {
  return (
    <Card className="feature-card" hoverable>
      <Title level={4} className="feature-card-title">
        {title}
      </Title>
      <Paragraph className="feature-card-description">{description}</Paragraph>

      <div className="feature-card-benefits">
        <div className="benefits-label">Best For:</div>
        <ul className="benefits-list">
          {bestFor.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      <Button
        type="primary"
        size="large"
        block
        onClick={onSelect}
        className="feature-select-btn"
        style={{ backgroundColor: color, borderColor: color }}
      >
        {buttonText}
      </Button>
    </Card>
  )
}

interface LandingPageProps {
  onNewChat: () => void
  onOpenFile: () => void
  onDiagramWizard: () => void
  onDocumentation: () => void
  onSetContext: () => void
}

export const LandingPage: React.FC<LandingPageProps> = ({
  onNewChat,
  onOpenFile,
  onDiagramWizard,
  onDocumentation,
  onSetContext,
}) => {
  const brandTagline = Brand.tagline || Brand.name || 'Our AI Assistant'

  const diagramWizardFeature = {
    title: 'Diagram Wizard',
    description: 'AI-powered diagram generation from natural language',
    icon: <DeploymentUnitOutlined style={{ fontSize: '30px' }} />,
    color: '#52c41a',
    bestFor: [
      'System architecture diagrams',
      'Workflow visualizations',
      'Mermaid & D2 diagrams',
      'Interactive clarification',
    ],
    onSelect: onDiagramWizard,
    buttonText: 'Create Diagram',
  }

  return (
    <div className="landing-page">
      <div className="landing-content">
        <div className="landing-header">
          <Title level={1} className="landing-title">
            Welcome to {brandTagline}
          </Title>
          <Paragraph className="landing-subtitle">
            Create beautiful system architecture diagrams with AI-powered assistance. Describe your
            system in natural language and let the wizard guide you through clarification and
            generation.
          </Paragraph>
        </div>

        <div className="features-sections">
          <div className="feature-section">
            <Row gutter={[24, 24]} className="features-grid" justify="center">
              <Col key="diagram-wizard" xs={24} sm={20} md={16} lg={12} xl={10}>
                <FeatureCard {...diagramWizardFeature} />
              </Col>
            </Row>
          </div>
        </div>

        <div className="landing-footer">
          <ThunderboltOutlined style={{ marginRight: '8px', color: '#faad14' }} />
          <span>
            Tip: Access other tools like AI Chat, File Editor, and Documentation from the Tools menu
            in the header!
          </span>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
