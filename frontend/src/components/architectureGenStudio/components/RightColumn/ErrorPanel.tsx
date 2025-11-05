/**
 * Error Panel Component
 * Displays validation and render errors
 */

import React from 'react';
import { Collapse } from 'antd';
import type { ValidationError } from '../../types';

interface ErrorPanelProps {
  errors: ValidationError[];
  type: 'syntax' | 'validation' | 'render' | 'llm';
  isVisible: boolean;
  onDismiss: () => void;
}

export const ErrorPanel: React.FC<ErrorPanelProps> = ({
  errors,
  type,
  isVisible,
}) => {
  if (!isVisible || errors.length === 0) {
    return null;
  }

  const items = errors.map((error) => ({
    key: error.id,
    label: `${error.code || 'Error'}: ${error.message}`,
    children: (
      <div style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '12px' }}>
        {error.details || error.message}
      </div>
    ),
  }));

  return (
    <Collapse
      items={items}
      style={{
        marginBottom: '12px',
        border: `1px solid var(--ant-color-error)`,
        borderRadius: '4px',
      }}
      header={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ color: 'var(--ant-color-error)', fontWeight: 'bold' }}>
            {errors.length} {type} error{errors.length !== 1 ? 's' : ''}
          </span>
        </div>
      }
    />
  );
};

export default ErrorPanel;
