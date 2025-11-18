```typescript
// Import necessary React and Ant Design components for UI rendering
import React from 'react';
import { Alert, List, Tag, Space, Empty, Button } from 'antd';
import {
  ExclamationCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import type { ValidationError } from '../../../services/diagram/validationService';

// Define the properties interface for the ErrorPanel component
interface ErrorPanelProps {
  errors: ValidationError[];
  warnings: ValidationError[];
  suggestions?: string[];
  onJumpToLine?: (line: number) => void;
  onAutoFix?: () => void;
  autoFixAvailable?: boolean;
}

// Main component to display validation errors, warnings, and suggestions
const ErrorPanel: React.FC<ErrorPanelProps> = ({
  errors,
  warnings,
  suggestions,
  onJumpToLine,
  onAutoFix,
  autoFixAvailable = false,
}) => {
  // Determine if there are any validation issues to display
  const hasErrors = errors.length > 0;
  const hasWarnings = warnings.length > 0;
  const hasSuggestions = suggestions && suggestions.length > 0;

  // Show empty state if no errors, warnings, or suggestions exist
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

  // Determine icon based on error/warning severity for visual representation
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

  // Get color tag for different severity levels
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
      {/* Display summary alert for errors with optional auto-fix functionality */}
      {hasErrors && (
        <Alert
          message={`${errors.length} error${errors.length > 1 ? 's' : ''} found`}
          type="error"
          showIcon
          style={{ marginBottom: '8px' }}
          action={
            // Render auto-fix button if available and callback provided
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

      {/* Render list of errors with line navigation and detailed information */}
      {hasErrors && (
        <List
          size="small"
          dataSource={errors}
          style={{ marginBottom: '8px' }}
          renderItem={(error) => (
            // Create clickable error items that can navigate to specific lines
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
              {/* Display error details with severity icon and line number */}
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

      {/* Similar rendering logic for warnings with different styling */}
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

      {/* Display additional suggestions if available */}
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