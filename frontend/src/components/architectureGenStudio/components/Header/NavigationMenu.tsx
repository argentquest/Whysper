/**
 * Navigation Menu Component
 * Display-only navigation breadcrumbs
 */

import React from 'react';
import { Typography } from 'antd';
import { RightOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const NavigationMenu: React.FC = () => {
  return (
    <div style={{ display: 'flex', gap: '8px', alignItems: 'center', justifyContent: 'center' }}>
      <Text style={{ fontSize: '14px' }}>Home</Text>
      <RightOutlined style={{ fontSize: '12px', color: 'var(--ant-color-text-secondary)' }} />
      <Text style={{ fontSize: '14px' }}>Architecture Gen Studio</Text>
      <RightOutlined style={{ fontSize: '12px', color: 'var(--ant-color-text-secondary)' }} />
      <Text style={{ fontSize: '14px' }} type="secondary">
        New Page
      </Text>
    </div>
  );
};

export default NavigationMenu;
