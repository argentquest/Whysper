/**
 * ErrorPanel Component
 *
 * Displays validation errors and warnings for diagram code.
 * Provides actionable suggestions and allows jumping to error lines.
 */

import React from 'react';
import { Alert, List, Tag, Space, Empty, Button } from 'antd';
import {
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ValidationError } from '../../../services/diagram/validationService';

interface ErrorPanelProps {
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions?: string[];
  onJumpToLine?: (line: number) => void;
  onAutoFix?: () => void;
  autoFixAvailable?: boolean;
}

const ErrorPanel: React.FC<ErrorPanelProps> = ({
  errors,
  warnings,
  suggestions,
  onJumpToLine,
  onAutoFix,
  autoFixAvailable = false,
}) => {
  const hasErrors = errors.length > 0;
  const hasWarnings = warnings.length > 0;
  const hasSuggestions = suggestions && suggestions.length > 0;

  if (!hasErrors && !hasWarnings && !hasSuggestions) {
    return (
      <div style={{ padding: '16px', textAlign: 'center' }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No validation errors"
        />
      </div>
    );
  }

  const getSeverityIcon = (severity: ValidationError['severity']) => {
    switch (severity) {
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      case 'info':
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
      default:
        return null;
    }
  };

  const getSeverityColor = (severity: ValidationError['severity']) => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <div style={{ padding: '8px' }}>
      {/* Summary Alert */}
      {hasErrors && (
        <Alert
          message={`${errors.length} error${errors.length > 1 ? 's' : ''} found`}
          type="error"
          showIcon
          style={{ marginBottom: '8px' }}
          action={
            autoFixAvailable && onAutoFix ? (
              <Button
                size="small"
                type="primary"
                icon={<ThunderboltOutlined />}
                onClick={onAutoFix}
              >
                Auto Fix
              </Button>
            ) : null
          }
        />
      )}

      {/* Errors List */}
      {hasErrors && (
        <List
          size="small"
          dataSource={errors}
          style={{ marginBottom: '8px' }}
          renderItem={(error) => (
            <List.Item
              style={{
                padding: '8px 12px',
                background: '#fff2f0',
                borderLeft: '3px solid #ff4d4f',
                marginBottom: '4px',
                cursor: error.line && onJumpToLine ? 'pointer' : 'default',
              }}
              onClick={() => error.line && onJumpToLine && onJumpToLine(error.line)}
            >
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Space>
                  {getSeverityIcon(error.severity)}
                  <Tag color={getSeverityColor(error.severity)}>
                    {error.line ? `Line ${error.line}` : 'Syntax Error'}
                  </Tag>
                </Space>
                <div style={{ fontSize: '13px', color: '#262626' }}>
                  {error.message}
                </div>
              </Space>
            </List.Item>
          )}
        />
      )}

      {/* Warnings List */}
      {hasWarnings && (
        <List
          size="small"
          dataSource={warnings}
          style={{ marginBottom: '8px' }}
          renderItem={(warning) => (
            <List.Item
              style={{
                padding: '8px 12px',
                background: '#fffbe6',
                borderLeft: '3px solid #faad14',
                marginBottom: '4px',
                cursor: warning.line && onJumpToLine ? 'pointer' : 'default',
              }}
              onClick={() => warning.line && onJumpToLine && onJumpToLine(warning.line)}
            >
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <Space>
                  {getSeverityIcon(warning.severity)}
                  <Tag color={getSeverityColor(warning.severity)}>
                    {warning.line ? `Line ${warning.line}` : 'Warning'}
                  </Tag>
                </Space>
                <div style={{ fontSize: '13px', color: '#262626' }}>
                  {warning.message}
                </div>
              </Space>
            </List.Item>
          )}
        />
      )}

      {/* Suggestions */}
      {hasSuggestions && (
        <Alert
          message="Suggestions"
          description={
            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
              {suggestions.map((suggestion, index) => (
                <li key={index} style={{ marginBottom: '4px' }}>
                  {suggestion}
                </li>
              ))}
            </ul>
          }
          type="info"
          showIcon
          style={{ marginBottom: '8px' }}
        />
      )}
    </div>
  );
};

export default ErrorPanel;
