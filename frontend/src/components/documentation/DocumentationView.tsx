import React from 'react';
import { Card, Typography, Divider, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const { Title, Paragraph } = Typography;

interface DocumentationViewProps {
  content: string;
  metadata: Record<string, any>;
  onDownload: (session_guid: string) => void; // Pass session_guid
}

export const DocumentationView: React.FC<DocumentationViewProps> = ({ content, metadata, onDownload }) => {
  const session_guid = metadata.session_guid;

  return (
    <div style={{ padding: '24px', height: '100%', overflow: 'auto' }}>
      <Card>
        <Title level={2}>Generated Documentation</Title>
        <Paragraph>
          This documentation was generated for the selected files.
        </Paragraph>
        <Button type="primary" icon={<DownloadOutlined />} onClick={() => onDownload(session_guid)}>
          Download as Zip
        </Button>
        <Divider />
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </Card>
    </div>
  );
};
