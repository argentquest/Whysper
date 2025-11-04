/**
 * Header Component - Architecture Gen Studio
 * Main navigation and control header
 */

import React from 'react';
import { Layout, Row, Col } from 'antd';
import { HeaderProps } from '../../types';
import { BrandingSection } from './BrandingSection';
import { AgentSelector } from './AgentSelector';
import { NavigationMenu } from './NavigationMenu';
import { UserAccountMenu } from './UserAccountMenu';
import { NotificationBadge } from './NotificationBadge';
import styles from '../../styles/architectureStudio.module.css';

export const Header: React.FC<HeaderProps> = ({
  onAgentChange,
  currentAgent,
  agents,
  agentsLoading,
  notificationCount,
  onLogout,
}) => {
  return (
    <Layout.Header className={styles.header}>
      <Row justify="space-between" align="middle" style={{ width: '100%', height: '100%' }}>
        {/* Left: Branding */}
        <Col flex="auto" style={{ minWidth: '200px' }}>
          <BrandingSection />
        </Col>

        {/* Center: Navigation */}
        <Col flex="auto">
          <NavigationMenu />
        </Col>

        {/* Right: User Actions */}
        <Col flex="auto" style={{ textAlign: 'right' }}>
          <Row justify="end" align="middle" gap={16}>
            <Col>
              <NotificationBadge count={notificationCount} />
            </Col>
            <Col>
              <UserAccountMenu onLogout={onLogout} />
            </Col>
          </Row>
        </Col>
      </Row>
    </Layout.Header>
  );
};

export default Header;
