/**
 * DocumentationView Components
 * 
 * This module contains component definitions and exports for DocumentationView.
 */
import React from 'react';
import { Card, Typography, Divider, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const { Title, Paragraph } = Typography;

/**
 * DocumentationViewProps type definition
 * 
 * Describes the structure and properties of DocumentationViewProps
 */
interface DocumentationViewProps {
  content: string; // Raw markdown content to be rendered
  metadata: Record<string, any>; // Flexible object containing additional metadata
  onDownload: (session_guid: string) => void; // Function to handle download with session ID
}

/**
 * DocumentationView component renders documentation with download functionality
 */
export const DocumentationView: React.FC<DocumentationViewProps> = ({ content, metadata, onDownload }) => {
  // Extract session GUID from metadata for download tracking
  const session_guid = metadata.session_guid;

  return (
    <div style={{ padding: '24px', height: '100%', overflow: 'auto' }}>
      {/* Card container for documentation with consistent styling */}
      <Card>
        {/* Title and description of generated documentation */}
        <Title level={2}>Generated Documentation</Title>
        <Paragraph>
          This documentation was generated for the selected files.
        </Paragraph>

        {/* Download button that triggers onDownload with session GUID */}
        <Button type="primary" icon={<DownloadOutlined />} onClick={() => onDownload(session_guid)}>
          Download as Zip
        </Button>

        {/* Visual separator between description and content */}
        <Divider />

        {/* Render markdown content with GitHub Flavored Markdown support */}
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </Card>
    </div>
  );
};