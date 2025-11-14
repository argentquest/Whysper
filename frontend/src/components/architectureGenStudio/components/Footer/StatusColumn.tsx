/**
 * Status Column Component
 * Displays current processing status
 */

import React from 'react';
import { Tag, Spin, theme } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons';

interface StatusColumnProps {
  status: string;
}

export const StatusColumn: React.FC<StatusColumnProps> = ({ status }) => {
  const { token } = theme.useToken();
  const brandTokens = token as Record<string, string>;
  const STATUS_STYLES = {
    base: {
      backgroundColor: brandTokens.colorBrandFooterBg ?? '#f8f4f1',
      borderColor: brandTokens.colorBrandFooterBorder ?? '#e3ded8',
      color: brandTokens.colorBrandFooterText ?? '#231f20',
    },
    processing: {
      backgroundColor: brandTokens.colorBrandStatusProcessingBg ?? '#fff3cf',
      borderColor: brandTokens.colorBrandStatusProcessingBorder ?? '#f7b500',
      color: brandTokens.colorBrandStatusProcessingText ?? '#7a5600',
    },
    success: {
      backgroundColor: brandTokens.colorBrandStatusSuccessBg ?? '#e6f3ec',
      borderColor: brandTokens.colorBrandStatusSuccessBorder ?? '#8abf9b',
      color: brandTokens.colorBrandStatusSuccessText ?? '#1f4f2f',
    },
    error: {
      backgroundColor: brandTokens.colorBrandStatusErrorBg ?? '#fbeaea',
      borderColor: brandTokens.colorBrandStatusErrorBorder ?? '#d71e28',
      color: brandTokens.colorBrandStatusErrorText ?? '#8b0d16',
    },
  };

  const isProcessing = status.includes('Execution') || status.includes('Rendering');
  const isSuccess = status.includes('Generated') || status.includes('success');
  const isError = status.includes('Error');

  let icon = null;
  let tagStyle = STATUS_STYLES.base;

  if (isProcessing) {
    icon = <LoadingOutlined />;
    tagStyle = STATUS_STYLES.processing;
  } else if (isSuccess) {
    icon = <CheckCircleOutlined />;
    tagStyle = STATUS_STYLES.success;
  } else if (isError) {
    icon = <CloseCircleOutlined />;
    tagStyle = STATUS_STYLES.error;
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {isProcessing && <Spin size="small" />}
      <Tag
        icon={icon}
        style={{
          margin: 0,
          fontSize: '12px',
          maxWidth: '200px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          borderRadius: 999,
          border: `1px solid ${tagStyle.borderColor}`,
          backgroundColor: tagStyle.backgroundColor,
          color: tagStyle.color,
        }}
      >
        {status}
      </Tag>
    </div>
  );
};

export default StatusColumn;
