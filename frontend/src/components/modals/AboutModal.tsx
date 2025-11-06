import React from 'react';
import { Typography, Space, Tag, Button, Divider } from 'antd';
import { useNavigate } from 'react-router-dom';
import {
  GithubOutlined,
  BookOutlined,
  BugOutlined,
  HeartOutlined,
  HomeOutlined,
  DesktopOutlined,
} from '@ant-design/icons';
import { Modal } from '../common/Modal';

const { Title, Text, Paragraph } = Typography;

/**
 * Props interface for the AboutModal component
 * 
 * @interface AboutModalProps
 * @property {boolean} open - Controls modal visibility state
 * @property {() => void} onCancel - Callback triggered when modal is cancelled
 */
interface AboutModalProps {
  open: boolean;
  onCancel: () => void;
}

/**
 * AboutModal Component
 * 
 * An informational modal that displays comprehensive information about the Whysper application:
 * - Application branding and version information
 * - Feature overview and capabilities
 * - Technology stack details
 * - Navigation links to different application sections
 * - External links to repository, documentation, and issue reporting
 * 
 * Features:
 * - Responsive design with centered content layout
 * - Version tagging and build date display
 * - Interactive navigation buttons to different app sections
 * - External link integration with proper target handling
 * - Professional styling with consistent theming
 * 
 * @param {AboutModalProps} props - Component props
 * @returns {JSX.Element} Rendered about modal
 */
export const AboutModal: React.FC<AboutModalProps> = ({
  open,
  onCancel,
}) => {
  const navigate = useNavigate();
  const version = '2.0.0';
  const buildDate = new Date().toLocaleDateString();

  /**
   * Handles navigation to the root chat interface
   * Closes modal and navigates to the main chat page
   */
  const handleNavigateToRoot = () => {
    onCancel();
    navigate('/');
  };

  /**
   * Handles navigation to the architecture generation studio
   * Closes modal and navigates to the GenStudio interface
   */
  const handleNavigateToStudio = () => {
    onCancel();
    navigate('/studio');
  };

  return (
    <Modal
      title="About Whysper"
      open={open}
      onCancel={onCancel}
      width={600}
      footer={
        <div className="flex justify-center">
          <Button type="primary" onClick={onCancel}>
            Close
          </Button>
        </div>
      }
    >
      <div className="text-center space-y-6">
        {/* Logo and Title */}
        <div>
          <div className="text-6xl mb-4">🧠</div>
          <Title level={2} className="!mb-2">Whysper</Title>
          <Text type="secondary" className="text-lg">
            AI-Powered Code Analysis & Development Assistant
          </Text>
        </div>

        {/* Version Info */}
        <Space direction="vertical" size="small">
          <Space>
            <Tag color="blue">Version {version}</Tag>
            <Tag color="green">Web2 Release</Tag>
            <Tag color="purple">React + Ant Design</Tag>
          </Space>
          <Text type="secondary" className="text-sm">
            Built on {buildDate}
          </Text>
        </Space>

        <Divider />

        {/* Description */}
        <div className="text-left space-y-4">
          <Paragraph>
            Whysper is a modern, full-stack web application that brings AI assistance 
            directly to your development workflow. It enables developers to select any 
            codebase, choose from specialized AI experts, and get intelligent insights, 
            code reviews, and architectural guidance through an intuitive web interface.
          </Paragraph>

          <Title level={4}>Key Features</Title>
          <ul className="space-y-2 text-sm">
            <li>• <strong>Multi-Provider AI Support:</strong> OpenRouter, OpenAI, Anthropic, Google, and more</li>
            <li>• <strong>Context-Aware Analysis:</strong> Upload and analyze entire codebases</li>
            <li>• <strong>Code Extraction:</strong> Automatically extract code blocks from AI responses</li>
            <li>• <strong>Mermaid Diagrams:</strong> Generate and export visual diagrams as PNG</li>
            <li>• <strong>Theme System:</strong> Beautiful light and dark themes</li>
            <li>• <strong>Tab Management:</strong> Multiple conversations with save/restore</li>
            <li>• <strong>Quick Commands:</strong> Pre-built prompts for common tasks</li>
            <li>• <strong>Real-time Chat:</strong> Streaming responses with syntax highlighting</li>
          </ul>

          <Title level={4}>Technology Stack</Title>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <Text strong>Frontend:</Text>
              <ul className="mt-1 space-y-1">
                <li>• React 18 + TypeScript</li>
                <li>• Ant Design Components</li>
                <li>• Tailwind CSS</li>
                <li>• Vite Build Tool</li>
              </ul>
            </div>
            <div>
              <Text strong>Backend:</Text>
              <ul className="mt-1 space-y-1">
                <li>• FastAPI (Python)</li>
                <li>• RESTful API Design</li>
                <li>• File System Integration</li>
                <li>• Multi-Provider AI SDK</li>
              </ul>
            </div>
          </div>
        </div>

        <Divider />

        {/* Navigation Links */}
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div className="flex justify-center gap-2">
            <Button
              type="primary"
              icon={<HomeOutlined />}
              onClick={handleNavigateToRoot}
            >
              Go to Chat
            </Button>
            <Button
              type="default"
              icon={<DesktopOutlined />}
              onClick={handleNavigateToStudio}
            >
              Go to GenStudio
            </Button>
          </div>
        </Space>

        <Divider />

        {/* Links */}
        <Space size="large">
          <Button
            type="link"
            icon={<GithubOutlined />}
            href="https://github.com/argentquest/Whysper"
            target="_blank"
          >
            Source Code
          </Button>
          <Button
            type="link"
            icon={<BookOutlined />}
            href="https://github.com/argentquest/Whysper#readme"
            target="_blank"
          >
            Documentation
          </Button>
          <Button
            type="link"
            icon={<BugOutlined />}
            href="https://github.com/argentquest/Whysper/issues"
            target="_blank"
          >
            Report Bug
          </Button>
        </Space>

        {/* Credits */}
        <div className="text-center">
          <Text type="secondary" className="text-sm flex items-center justify-center gap-1">
            Made with <HeartOutlined className="text-red-500" /> by the Whysper Team
          </Text>
        </div>
      </div>
    </Modal>
  );
};

export default AboutModal;