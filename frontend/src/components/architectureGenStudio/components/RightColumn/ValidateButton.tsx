/**
 * Validate Button Component
 * Validates diagram code
 */

import React from 'react';
import { Button } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import type { DiagramType } from '../../types';

interface ValidateButtonProps {
  code: string;
  diagramType: DiagramType;
  onValidate: (code: string) => Promise<void>;
  isLoading: boolean;
}

export const ValidateButton: React.FC<ValidateButtonProps> = ({
  code,
  onValidate,
  isLoading,
}) => {
  return (
    <Button
      icon={<CheckOutlined />}
      onClick={() => onValidate(code)}
      loading={isLoading}
      disabled={!code.trim() || isLoading}
    >
      Validate
    </Button>
  );
};

export default ValidateButton;
