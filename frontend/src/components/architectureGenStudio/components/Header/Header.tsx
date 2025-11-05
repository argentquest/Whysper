/**
 * Header Component - Architecture Gen Studio
 * Main navigation and control header with agent selector
 */

import React, { useMemo } from 'react';
import { Layout, Row, Col, Select, Spin, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import type { HeaderProps } from '../../types';
import { BrandingSection } from './BrandingSection';
import { NavigationMenu } from './NavigationMenu';
import { UserAccountMenu } from './UserAccountMenu';
import { NotificationBadge } from './NotificationBadge';
import styles from '../../styles/architectureStudio.module.css';

const { Option } = Select;
const { Text } = Typography;

export const Header: React.FC<HeaderProps> = ({
  notificationCount,
  onLogout,
  onAgentChange,
  currentAgent,
  agents = [],
  agentsLoading = false,
}) => {
  const agentOptions = useMemo(
    () =>
      agents.map((agent) => ({
        label: agent.name,
        value: agent.id,
        agent,
      })),
    [agents]
  );

  return (
    <Layout.Header className={styles.header} style={{ paddingRight: '24px', paddingLeft: '24px' }}>
      <Row justify="space-between" align="middle" style={{ width: '100%', height: '100%', gap: '16px' }}>
        {/* Left: Branding */}
        <Col flex="0 0 auto" style={{ minWidth: '180px' }}>
          <BrandingSection />
        </Col>

        {/* Center-Left: Agent Selector */}
        <Col flex="0 0 300px">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <Text style={{ fontSize: '11px', fontWeight: 600, letterSpacing: '0.5px', color: '#64748b' }}>
              SELECT AGENT
            </Text>
            <Spin spinning={agentsLoading} indicator={<LoadingOutlined />}>
              <Select
                value={currentAgent?.id || undefined}
                onChange={(agentId) => {
                  const agent = agents.find((a) => a.id === agentId);
                  if (agent && onAgentChange) {
                    onAgentChange(agent);
                  }
                }}
                placeholder="Select an agent..."
                size="large"
                disabled={agentsLoading || agents.length === 0}
                allowClear
                optionLabelProp="label"
                style={{
                  width: '100%',
                  borderRadius: '8px',
                }}
                styles={{
                  popup: {
                    root: { width: '800px' }
                  }
                }}
                popupRender={(menu) => (
                  <div>
                    {/* Table Header */}
                    <div style={{
                      padding: '12px 16px',
                      backgroundColor: '#f5f5f5',
                      borderBottom: '2px solid #d9d9d9',
                      display: 'grid',
                      gridTemplateColumns: '200px 1fr 200px',
                      gap: '16px',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#595959'
                    }}>
                      <div style={{ paddingRight: '8px', borderRight: '1px solid #d9d9d9' }}>Agent</div>
                      <div style={{ paddingRight: '8px', borderRight: '1px solid #d9d9d9' }}>Description</div>
                      <div>Categories</div>
                    </div>
                    {menu}
                  </div>
                )}
              >
                {agentOptions.map((opt) => (
                  <Option
                    key={opt.value}
                    value={opt.value}
                    label={opt.label}
                  >
                    <div style={{
                      padding: '12px 0',
                      borderBottom: '1px solid #f0f0f0',
                      display: 'grid',
                      gridTemplateColumns: '200px 1fr 200px',
                      gap: '16px',
                      alignItems: 'start'
                    }}>
                      {/* Agent Name */}
                      <div style={{ paddingRight: '8px', borderRight: '1px solid #f0f0f0' }}>
                        <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '4px' }}>
                          {opt.agent.name}
                        </div>
                        <div style={{ fontSize: '11px', color: '#1890ff' }}>
                          {opt.agent.id}
                        </div>
                      </div>

                      {/* Description */}
                      <div style={{ paddingRight: '8px', borderRight: '1px solid #f0f0f0' }}>
                        <div style={{ fontSize: '12px', color: '#595959', lineHeight: '1.5' }}>
                          {opt.agent.description || 'No description available'}
                        </div>
                      </div>

                      {/* Categories/Tags */}
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {opt.agent.type && (
                          <span style={{
                            padding: '2px 8px',
                            backgroundColor: '#f6f8fb',
                            color: '#0050b3',
                            borderRadius: '4px',
                            fontSize: '11px',
                            fontWeight: 500
                          }}>
                            {opt.agent.type}
                          </span>
                        )}
                      </div>
                    </div>
                  </Option>
                ))}
              </Select>
            </Spin>
          </div>
        </Col>

        {/* Center: Navigation - Flex to fill space */}
        <Col flex="1" style={{ display: 'flex', justifyContent: 'center' }}>
          <NavigationMenu />
        </Col>

        {/* Right: User Actions */}
        <Col flex="0 0 auto" style={{ textAlign: 'right' }}>
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
