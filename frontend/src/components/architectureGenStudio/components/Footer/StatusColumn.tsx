/**
 * Status Column Component
 * Displays current processing status
 */

import React from 'antd';
import { Tag, Spin } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons';

interface StatusColumnProps {
  status: string;
}

export const StatusColumn: React.FC<StatusColumnProps> = ({ status }) => {
  const isProcessing = status.includes('Execution') || status.includes('Rendering');
  const isSuccess = status.includes('Generated') || status.includes('success');
  const isError = status.includes('Error');
  const isIdle = status === 'Idle';

  let icon = null;
  let color = 'default';

  if (isProcessing) {
    icon = <LoadingOutlined />;
    color = 'processing';
  } else if (isSuccess) {
    icon = <CheckCircleOutlined />;
    color = 'success';
  } else if (isError) {
    icon = <CloseCircleOutlined />;
    color = 'error';
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {isProcessing && <Spin size="small" />}
      <Tag
        icon={icon}
        color={color}
        style={{
          margin: 0,
          fontSize: '12px',
          maxWidth: '200px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {status}
      </Tag>
    </div>
  );
};

export default StatusColumn;
