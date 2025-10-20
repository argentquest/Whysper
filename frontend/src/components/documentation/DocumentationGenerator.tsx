/**
 * Documentation Generator component for Whysper.
 * 
 * This component provides a user interface for generating documentation
 * from selected code files with various options and formats.
 */

import React, { useState, useEffect } from 'react';
import { Button, Select, Switch, Card, Space, Typography, Divider, Alert, Spin } from 'antd';
import { FileTextOutlined, DownloadOutlined, SettingOutlined } from '@ant-design/icons';
import ApiService from '../../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface DocumentationGeneratorProps {
  selectedFiles: string[];
  onDocumentationGenerated?: (content: string) => void;
}

interface DocumentationRequest {
  file_paths: string[];
  documentation_type: string;
  output_format: string;
  template?: string;
  include_examples: boolean;
  include_diagrams: boolean;
  target_audience: string;
  language?: string;
}

const DocumentationGenerator: React.FC<DocumentationGeneratorProps> = ({
  selectedFiles,
  onDocumentationGenerated
}) => {
  const [loading, setLoading] = useState(false);
  const [documentation, setDocumentation] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [templates, setTemplates] = useState<Array<Record<string, any>>>([]);
  const [request, setRequest] = useState<DocumentationRequest>({
    file_paths: selectedFiles,
    documentation_type: 'api',
    output_format: 'markdown',
    include_examples: true,
    include_diagrams: true,
    target_audience: 'developers'
  });

  // Load available templates
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await ApiService.get('/api/v1/documentation/templates');
        setTemplates(response.data.templates || []);
      } catch (err) {
        console.error('Failed to load templates:', err);
      }
    };

    loadTemplates();
  }, []);

  // Update request when selected files change
  useEffect(() => {
    setRequest(prev => ({
      ...prev,
      file_paths: selectedFiles
    }));
  }, [selectedFiles]);

  const handleGenerateDocumentation = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one file to generate documentation');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await ApiService.post(
        '/api/v1/documentation/generate',
        request
      );

      const { content } = response.data;
      setDocumentation(content);
      
      if (onDocumentationGenerated) {
        onDocumentationGenerated(content);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to generate documentation';
      setError(errorMessage);
      console.error('Documentation generation error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportDocumentation = async (format: string) => {
    if (!documentation) {
      setError('No documentation to export');
      return;
    }

    try {
      const response = await ApiService.post(
        '/api/v1/documentation/export',
        {
          documentation_id: 'temp',
          content: documentation,
          export_format: format,
          filename: `documentation.${format}`
        }
      );

      // Create download link
      const blob = new Blob([response.data.content], { 
        type: response.data.content_type 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = response.data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to export documentation';
      setError(errorMessage);
      console.error('Documentation export error:', err);
    }
  };

  const documentationTypes = [
    { value: 'api', label: 'API Documentation' },
    { value: 'readme', label: 'README File' },
    { value: 'architecture', label: 'Architecture Documentation' },
    { value: 'examples', label: 'Usage Examples' },
    { value: 'all', label: 'Comprehensive Documentation' }
  ];

  const outputFormats = [
    { value: 'markdown', label: 'Markdown' },
    { value: 'html', label: 'HTML' },
    { value: 'pdf', label: 'PDF' }
  ];

  const targetAudiences = [
    { value: 'developers', label: 'Developers' },
    { value: 'users', label: 'End Users' },
    { value: 'mixed', label: 'Mixed Audience' }
  ];

  return (
    <Card 
      title={
        <Space>
          <FileTextOutlined />
          <span>Documentation Generator</span>
        </Space>
      }
      extra={<SettingOutlined />}
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {error && (
          <Alert 
            message="Error" 
            description={error} 
            type="error" 
            showIcon 
            closable 
            onClose={() => setError('')}
          />
        )}

        <div>
          <Title level={4}>Configuration</Title>
          
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>Documentation Type:</Text>
              <Select
                value={request.documentation_type}
                onChange={(value) => setRequest(prev => ({ ...prev, documentation_type: value }))}
                style={{ width: '100%', marginTop: 8 }}
              >
                {documentationTypes.map(type => (
                  <Option key={type.value} value={type.value}>
                    {type.label}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <Text strong>Output Format:</Text>
              <Select
                value={request.output_format}
                onChange={(value) => setRequest(prev => ({ ...prev, output_format: value }))}
                style={{ width: '100%', marginTop: 8 }}
              >
                {outputFormats.map(format => (
                  <Option key={format.value} value={format.value}>
                    {format.label}
                  </Option>
                ))}
              </Select>
            </div>

            {templates.length > 0 && (
              <div>
                <Text strong>Template:</Text>
                <Select
                  value={request.template}
                  onChange={(value) => setRequest(prev => ({ ...prev, template: value }))}
                  allowClear
                  placeholder="Select template (optional)"
                  style={{ width: '100%', marginTop: 8 }}
                >
                  {templates.map(template => (
                    <Option key={template.name} value={template.name}>
                      {template.title || template.name}
                    </Option>
                  ))}
                </Select>
              </div>
            )}

            <div>
              <Text strong>Target Audience:</Text>
              <Select
                value={request.target_audience}
                onChange={(value) => setRequest(prev => ({ ...prev, target_audience: value }))}
                style={{ width: '100%', marginTop: 8 }}
              >
                {targetAudiences.map(audience => (
                  <Option key={audience.value} value={audience.value}>
                    {audience.label}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <Space>
                <Switch
                  checked={request.include_examples}
                  onChange={(checked) => setRequest(prev => ({ ...prev, include_examples: checked }))}
                />
                <Text>Include Usage Examples</Text>
              </Space>
            </div>

            <div>
              <Space>
                <Switch
                  checked={request.include_diagrams}
                  onChange={(checked) => setRequest(prev => ({ ...prev, include_diagrams: checked }))}
                />
                <Text>Include Diagrams</Text>
              </Space>
            </div>
          </Space>
        </div>

        <Divider />

        <div>
          <Space>
            <Button
              type="primary"
              icon={<FileTextOutlined />}
              onClick={handleGenerateDocumentation}
              loading={loading}
              disabled={selectedFiles.length === 0}
            >
              Generate Documentation
            </Button>
            
            {documentation && (
              <Button.Group>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExportDocumentation('markdown')}
                >
                  Export MD
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExportDocumentation('html')}
                >
                  Export HTML
                </Button>
                <Button
                  icon={<DownloadOutlined />}
                  onClick={() => handleExportDocumentation('pdf')}
                >
                  Export PDF
                </Button>
              </Button.Group>
            )}
          </Space>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>Generating documentation...</Text>
            </div>
          </div>
        )}

        {documentation && !loading && (
          <div>
            <Title level={4}>Generated Documentation</Title>
            <Card>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                maxHeight: 400, 
                overflow: 'auto',
                fontSize: 14,
                lineHeight: 1.5
              }}>
                {documentation}
              </pre>
            </Card>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default DocumentationGenerator;