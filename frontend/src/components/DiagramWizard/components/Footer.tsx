/**
 * Footer Component
 *
 * Displays status information at the bottom of the DiagramWizard:
 * - Current session status
 * - SSE connection state
 * - Recent messages/notifications
 * - Usage statistics
 */

import React from 'react';
import { Space, Badge, Tooltip, Typography } from 'antd';
import {
  CheckCircleOutlined,
  SyncOutlined,
  CloseCircleOutlined,
  ApiOutlined,
  HistoryOutlined,
  RocketOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface FooterProps {
  sessionId?: string | null;
  sseConnected: boolean;
  currentStatus?: string;
  totalSessions?: number;
  successfulGenerations?: number;
  lastMessage?: string;
}

const Footer: React.FC<FooterProps> = ({
  sessionId,
  sseConnected,
  currentStatus,
  totalSessions = 0,
  successfulGenerations = 0,
  lastMessage,
}) => {
  // Status badge configuration
  const getStatusConfig = () => {
    if (!sessionId) {
      return {
        status: 'default' as const,
        text: 'No active session',
        icon: <CloseCircleOutlined />,
      };
    }

    switch (currentStatus) {
      case 'completed':
        return {
          status: 'success' as const,
          text: 'Completed',
          icon: <CheckCircleOutlined />,
        };
      case 'error':
        return {
          status: 'error' as const,
          text: 'Error',
          icon: <CloseCircleOutlined />,
        };
      case 'running':
      case 'analyzing':
      case 'generating':
      case 'validating':
      case 'refining':
      case 'rendering':
        return {
          status: 'processing' as const,
          text: currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1),
          icon: <SyncOutlined spin />,
        };
      default:
        return {
          status: 'default' as const,
          text: 'Ready',
          icon: <CheckCircleOutlined />,
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <div
      style={{
        background: '#fafafa',
        borderTop: '1px solid #d9d9d9',
        padding: '8px 16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '12px',
      }}
    >
      {/* Left: Session and SSE status */}
      <Space size="large">
        {/* Session Status */}
        <Tooltip title={sessionId ? `Session ID: ${sessionId}` : 'No active session'}>
          <Space size="small">
            {statusConfig.icon}
            <Text type="secondary">{statusConfig.text}</Text>
          </Space>
        </Tooltip>

        {/* SSE Connection */}
        <Tooltip title={sseConnected ? 'Real-time updates active' : 'Not connected'}>
          <Space size="small">
            <ApiOutlined style={{ color: sseConnected ? '#52c41a' : '#d9d9d9' }} />
            <Text type="secondary">
              {sseConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </Space>
        </Tooltip>

        {/* Last Message */}
        {lastMessage && (
          <Tooltip title="Latest update">
            <Text
              type="secondary"
              ellipsis
              style={{ maxWidth: '300px', fontStyle: 'italic' }}
            >
              {lastMessage}
            </Text>
          </Tooltip>
        )}
      </Space>

      {/* Right: Statistics */}
      <Space size="large">
        {/* Total Sessions */}
        <Tooltip title="Total sessions created">
          <Space size="small">
            <HistoryOutlined />
            <Text type="secondary">{totalSessions} sessions</Text>
          </Space>
        </Tooltip>

        {/* Successful Generations */}
        <Tooltip title="Successfully completed diagrams">
          <Space size="small">
            <RocketOutlined />
            <Text type="secondary">{successfulGenerations} completed</Text>
          </Space>
        </Tooltip>

        {/* Success Rate */}
        {totalSessions > 0 && (
          <Tooltip title="Success rate">
            <Badge
              count={`${Math.round((successfulGenerations / totalSessions) * 100)}%`}
              style={{
                backgroundColor:
                  successfulGenerations / totalSessions > 0.7 ? '#52c41a' : '#faad14',
              }}
            />
          </Tooltip>
        )}
      </Space>
    </div>
  );
};

export default Footer;
