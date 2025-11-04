/**
 * Branding Section Component
 * Displays company name and application title
 */

import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

export const BrandingSection: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
      <Text strong style={{ fontSize: '12px', color: 'var(--ant-color-text-secondary)' }}>
        Wells Fargo
      </Text>
      <Title level={4} style={{ margin: 0, fontSize: '16px' }}>
        Architecture Gen Studio
      </Title>
    </div>
  );
};

export default BrandingSection;
