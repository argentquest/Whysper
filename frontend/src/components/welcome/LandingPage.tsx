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

  const features = [
    {
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
    },
    {
      title: 'AI Chat',
      description: 'Interactive conversations with multiple AI providers',
      icon: <MessageOutlined style={{ fontSize: '30px' }} />,
      color: '#1890ff',
      bestFor: [
        'Code analysis and review',
        'Technical questions',
        'Multi-file context support',
        'Real-time streaming responses',
      ],
      onSelect: onNewChat,
      buttonText: 'New Chat',
    },
    {
      title: 'Set Context',
      description: 'Select files and folders to ground AI responses',
      icon: <FileTextOutlined style={{ fontSize: '30px' }} />,
      color: '#13c2c2',
      bestFor: [
        'Attaching repo snippets',
        'Grounded chat responses',
        'Sharing logs and specs',
        'Quickly updating context files',
      ],
      onSelect: onSetContext,
      buttonText: 'Select Files',
    },
    {
      title: 'File Editor',
      description: 'Monaco-powered code editor with AI assistance',
      icon: <CodeOutlined style={{ fontSize: '30px' }} />,
      color: '#722ed1',
      bestFor: [
        'Direct file editing',
        'Syntax highlighting',
        'Multiple language support',
        'Real-time validation',
      ],
      onSelect: onOpenFile,
      buttonText: 'Open File',
    },
    {
      title: 'Documentation',
      description: 'Browse and search project documentation',
      icon: <BookOutlined style={{ fontSize: '30px' }} />,
      color: '#fa8c16',
      bestFor: ['API documentation', 'Code examples', 'Architecture guides', 'Best practices'],
      onSelect: onDocumentation,
      buttonText: 'Browse Docs',
    },
  ]

  return (
    <div className="landing-page">
      <div className="landing-content">
        <div className="landing-header">
          <Title level={1} className="landing-title">
            Welcome to {brandTagline}
          </Title>
          <Paragraph className="landing-subtitle">
            Choose a feature to get started. Each tool is designed to enhance your development
            workflow with AI-powered assistance.
          </Paragraph>
        </div>

        <Row gutter={[24, 24]} className="features-grid">
          {features.map((feature, index) => (
            <Col key={index} xs={24} sm={12} lg={6}>
              <FeatureCard {...feature} />
            </Col>
          ))}
        </Row>

        <div className="landing-footer">
          <ThunderboltOutlined style={{ marginRight: '8px', color: '#faad14' }} />
          <span>
            Tip: You can open multiple tabs and switch between different features seamlessly!
          </span>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
