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

// Define the structure of props for the Footer component
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
  // Determine the status configuration based on current session state
  // Provides visual and textual representation of the current process
  const getStatusConfig = () => {
    // Handle case when no active session exists
    if (!sessionId) {
      return {
        status: 'default' as const,
        text: 'No active session',
        icon: <CloseCircleOutlined />,
      };
    }

    // Map different status states to visual representations
    // Provides dynamic status indication based on current process stage
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

  // Compute status configuration for current session
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
      {/* Left section: Display session and connection status */}
      <Space size="large">
        {/* Show current session status with tooltip */}
        <Tooltip title={sessionId ? `Session ID: ${sessionId}` : 'No active session'}>
          <Space size="small">
            {statusConfig.icon}
            <Text type="secondary">{statusConfig.text}</Text>
          </Space>
        </Tooltip>

        {/* Display Server-Sent Events (SSE) connection status */}
        <Tooltip title={sseConnected ? 'Real-time updates active' : 'Not connected'}>
          <Space size="small">
            <ApiOutlined style={{ color: sseConnected ? '#52c41a' : '#d9d9d9' }} />
            <Text type="secondary">
              {sseConnected ? 'Connected' : 'Disconnected'}
            </Text>
          </Space>
        </Tooltip>

        {/* Show the most recent message if available */}
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

      {/* Right section: Display usage statistics */}
      <Space size="large">
        {/* Total number of sessions created */}
        <Tooltip title="Total sessions created">
          <Space size="small">
            <HistoryOutlined />
            <Text type="secondary">{totalSessions} sessions</Text>
          </Space>
        </Tooltip>

        {/* Number of successfully completed diagrams */}
        <Tooltip title="Successfully completed diagrams">
          <Space size="small">
            <RocketOutlined />
            <Text type="secondary">{successfulGenerations} completed</Text>
          </Space>
        </Tooltip>

        {/* Calculate and display success rate if sessions exist */}
        {totalSessions > 0 && (
          <Tooltip title="Success rate">
            <Badge
              count={`${Math.round((successfulGenerations / totalSessions) * 100)}%`}
              style={{
                // Color-code success rate: green for high, yellow for moderate
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
