/**
 * Footer Component - Status Bar
 * Displays status, SSE messages, and links
 */

import React from 'react';
import { Layout, Row, Col, Divider } from 'antd';
import type { FooterProps } from '../../types';
import { StatusColumn } from './StatusColumn';
import { SSEMessagesColumn } from './SSEMessagesColumn';
import { LinksColumn } from './LinksColumn';

export const Footer: React.FC<FooterProps> = ({
  currentStatus,
  sseMessages,
  unreadMessageCount,
  isSSEConnected = false,
}) => {
  return (
    <Layout.Footer
      style={{
        padding: '12px 16px',
        borderTop: '1px solid var(--ant-color-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        minHeight: '60px',
        backgroundColor: 'var(--ant-color-bg-container)',
      }}
    >
      <Row style={{ width: '100%', gap: '16px' }} align="middle">
        {/* Left: Status */}
        <Col flex="auto" style={{ minWidth: '150px' }}>
          <StatusColumn status={currentStatus} />
        </Col>

        <Divider type="vertical" style={{ height: '40px' }} />

        {/* Center: SSE Messages */}
        <Col flex="auto">
          <SSEMessagesColumn
            messages={sseMessages}
            isConnected={isSSEConnected}
            unreadCount={unreadMessageCount}
          />
        </Col>

        <Divider type="vertical" style={{ height: '40px' }} />

        {/* Right: Links */}
        <Col flex="auto" style={{ textAlign: 'right', minWidth: '200px' }}>
          <LinksColumn />
        </Col>
      </Row>
    </Layout.Footer>
  );
};

export default Footer;
