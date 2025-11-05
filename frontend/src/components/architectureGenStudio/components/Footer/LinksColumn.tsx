/**
 * Links Column Component
 * Displays about/help links and disclaimer
 */

import React from 'react';
import { Button, Space, Divider, Typography } from 'antd';
import { QuestionCircleOutlined, InfoCircleOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const LinksColumn: React.FC = () => {
  const handleOpenLink = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <Space direction="vertical" size={0} style={{ width: '100%', textAlign: 'right' }}>
      <Space size={8}>
        <Button
          type="link"
          size="small"
          icon={<QuestionCircleOutlined />}
          onClick={() => handleOpenLink('https://docs.example.com')}
        >
          Help
        </Button>
        <Divider type="vertical" style={{ height: '16px', margin: 0 }} />
        <Button
          type="link"
          size="small"
          icon={<InfoCircleOutlined />}
          onClick={() => handleOpenLink('https://example.com/about')}
        >
          About
        </Button>
      </Space>
      <Text type="secondary" style={{ fontSize: '11px' }}>
        Information was AI Generated
      </Text>
    </Space>
  );
};

export default LinksColumn;
