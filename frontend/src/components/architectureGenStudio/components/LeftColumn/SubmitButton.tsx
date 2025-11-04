/**
 * Submit Button Component
 * Handles prompt submission with loading states
 */

import React, { useState } from 'react';
import { Button, Space, message } from 'antd';
import { SendOutlined, StopOutlined } from '@ant-design/icons';

interface SubmitButtonProps {
  isProcessing: boolean;
  onSubmit: () => Promise<void>;
  onCancel: () => Promise<void>;
  prompt: string;
  disabled?: boolean;
}

export const SubmitButton: React.FC<SubmitButtonProps> = ({
  isProcessing,
  onSubmit,
  onCancel,
  prompt,
  disabled = false,
}) => {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      message.warning('Please enter a prompt');
      return;
    }

    try {
      setLoading(true);
      await onSubmit();
    } catch (error) {
      message.error(error instanceof Error ? error.message : 'Failed to submit prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    try {
      await onCancel();
      message.info('Request cancelled');
    } catch (error) {
      message.error(error instanceof Error ? error.message : 'Failed to cancel request');
    }
  };

  return (
    <Space style={{ width: '100%' }}>
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={handleSubmit}
        loading={loading || isProcessing}
        disabled={disabled || loading || isProcessing}
        block
      >
        {isProcessing ? 'Generating...' : 'Submit'}
      </Button>
      {isProcessing && (
        <Button
          danger
          icon={<StopOutlined />}
          onClick={handleCancel}
          loading={loading}
        >
          Cancel
        </Button>
      )}
    </Space>
  );
};

export default SubmitButton;
