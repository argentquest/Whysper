import React from 'react';
import { Layout, Typography } from 'antd';
import { DiagramWizard } from '../components/DiagramWizard';

const { Content } = Layout;
const { Title } = Typography;

/**
 * DiagramWizard Page Component
 * 
 * Provides a dedicated page for the AI-powered diagram generation wizard.
 * Features a clean, focused interface for creating diagrams through natural language.
 */
export const DiagramWizardPage: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      <Content style={{ padding: '24px' }}>
        <div style={{ marginBottom: '24px', textAlign: 'center' }}>
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            🧙‍♂️ AI Diagram Wizard
          </Title>
          <Typography.Text type="secondary" style={{ fontSize: '16px' }}>
            Generate professional diagrams using natural language with AI assistance
          </Typography.Text>
        </div>
        
        <div style={{ 
          background: '#fff', 
          borderRadius: '12px', 
          padding: '24px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          minHeight: 'calc(100vh - 200px)'
        }}>
          <DiagramWizard />
        </div>
      </Content>
    </Layout>
  );
};

export default DiagramWizardPage;