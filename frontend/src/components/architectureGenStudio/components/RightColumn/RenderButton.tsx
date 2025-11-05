/**
 * Render Button Component
 * Renders diagram from code
 */

import React from 'react';
import { Button, message } from 'antd';
import { PlayCircleOutlined } from '@ant-design/icons';
import type { DiagramType } from '../../types';

interface RenderButtonProps {
  code: string;
  diagramType: DiagramType;
  onRender: (code: string) => Promise<void>;
  isLoading: boolean;
  canRender: boolean;
}

export const RenderButton: React.FC<RenderButtonProps> = ({
  code,
  onRender,
  isLoading,
  canRender,
}) => {
  const handleRender = async () => {
    if (!canRender) {
      message.warning('Please validate code first');
      return;
    }
    await onRender(code);
  };

  return (
    <Button
      type="primary"
      icon={<PlayCircleOutlined />}
      onClick={handleRender}
      loading={isLoading}
      disabled={!code.trim() || isLoading || !canRender}
    >
      Render
    </Button>
  );
};

export default RenderButton;
