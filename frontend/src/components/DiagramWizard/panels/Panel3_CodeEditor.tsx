/**
 * Panel3_CodeEditor Component
 *
 * Provides a code editor for viewing and editing diagram source code.
 * Supports syntax highlighting, manual re-rendering, and real-time validation.
 *
 * Enhanced with:
 * - Real-time code validation
 * - Error/warning display
 * - Auto-fix suggestions
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, Button, Space, Input, Spin, message, Tooltip, Tabs, Badge } from 'antd';
import {
  CopyOutlined,
  CheckOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  WarningOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { validateDiagramCode, debounce } from '../../../services/diagram/validationService';
import type { ValidationResult } from '../../../services/diagram/validationService';
import ErrorPanel from '../components/ErrorPanel';
import styles from '../diagram-wizard.module.css';

interface Panel3CodeEditorProps {
  code: string;
  diagramType: string;
  onChange: (code: string) => Promise<void>;
  isLoading: boolean;
}

const Panel3_CodeEditor: React.FC<Panel3CodeEditorProps> = ({
  code,
  diagramType,
  onChange,
  isLoading,
}) => {
  const [editedCode, setEditedCode] = useState(code);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    setEditedCode(code);
    // Validate when code changes
    if (code && code.trim()) {
      performValidation(code);
    }
  }, [code]);

  // Debounced validation function
  const performValidation = useCallback(
    debounce(async (codeToValidate: string) => {
      if (!codeToValidate || !codeToValidate.trim()) {
        setValidationResult(null);
        return;
      }

      setIsValidating(true);
      try {
        const result = await validateDiagramCode(codeToValidate, diagramType);
        setValidationResult(result);
      } catch (error) {
        console.error('Validation error:', error);
      } finally {
        setIsValidating(false);
      }
    }, 500),
    [diagramType]
  );

  // Handle code change in editor
  const handleCodeChange = (value: string) => {
    setEditedCode(value);
    if (isEditing) {
      performValidation(value);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedCode || code);
      setCopied(true);
      message.success('Code copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      message.error('Failed to copy code');
    }
  };

  const handleSave = async () => {
    if (editedCode === code) {
      message.info('No changes to save');
      setIsEditing(false);
      return;
    }

    try {
      setIsSaving(true);
      await onChange(editedCode);
      message.success('Diagram updated successfully');
      setIsEditing(false);
    } catch (err) {
      message.error(`Failed to update diagram: ${err}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedCode(code);
    setIsEditing(false);
  };

  // Get validation status icon
  const getValidationStatus = () => {
    if (isValidating) {
      return <Spin size="small" />;
    }
    if (!validationResult) {
      return null;
    }
    if (validationResult.isValid) {
      return (
        <Tooltip title="No errors">
          <CheckCircleOutlined style={{ color: '#52c41a' }} />
        </Tooltip>
      );
    }
    return (
      <Tooltip title={`${validationResult.errors.length} error(s)`}>
        <Badge count={validationResult.errors.length} offset={[5, 0]}>
          <WarningOutlined style={{ color: '#ff4d4f' }} />
        </Badge>
      </Tooltip>
    );
  };

  return (
    <Card
      title={
        <Space>
          {`${diagramType} Code`}
          {getValidationStatus()}
        </Space>
      }
      className={styles.codePanel}
      extra={
        <Space>
          {!isEditing ? (
            <>
              <Tooltip title="Copy code">
                <Button
                  size="small"
                  icon={copied ? <CheckOutlined /> : <CopyOutlined />}
                  onClick={handleCopy}
                  disabled={!code}
                />
              </Tooltip>

              <Tooltip title="Edit code">
                <Button
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => setIsEditing(true)}
                  disabled={!code}
                />
              </Tooltip>
            </>
          ) : (
            <>
              <Button
                size="small"
                icon={<SaveOutlined />}
                onClick={handleSave}
                loading={isSaving}
                type="primary"
              >
                Save
              </Button>

              <Button
                size="small"
                icon={<CloseOutlined />}
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>
            </>
          )}
        </Space>
      }
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
    >
      <div style={{ flex: 1, overflow: 'auto' }}>
        {isLoading ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <Spin tip="Generating code..." />
          </div>
        ) : !code ? (
          <div
            style={{
              color: '#999',
              textAlign: 'center',
              paddingTop: '20px',
            }}
          >
            No code generated yet
          </div>
        ) : (
          <Tabs
            defaultActiveKey="code"
            items={[
              {
                key: 'code',
                label: 'Code',
                children: (
                  <>
                    <Input.TextArea
                      value={isEditing ? editedCode : code}
                      onChange={(e) => handleCodeChange(e.target.value)}
                      disabled={!isEditing || isLoading}
                      readOnly={!isEditing}
                      style={{
                        fontFamily: 'monospace',
                        fontSize: 12,
                        height: '400px',
                        border: 'none',
                        backgroundColor: '#f5f5f5',
                      }}
                    />
                    {isEditing && (
                      <div
                        style={{
                          marginTop: 8,
                          padding: 8,
                          backgroundColor: '#fff7e6',
                          borderRadius: 4,
                          fontSize: 12,
                          color: '#666',
                        }}
                      >
                        Edit the code above and click Save to update the diagram.
                      </div>
                    )}
                  </>
                ),
              },
              {
                key: 'errors',
                label: (
                  <Badge
                    count={
                      validationResult
                        ? validationResult.errors.length + validationResult.warnings.length
                        : 0
                    }
                    offset={[10, 0]}
                  >
                    <span>Validation</span>
                  </Badge>
                ),
                children: validationResult ? (
                  <ErrorPanel
                    errors={validationResult.errors}
                    warnings={validationResult.warnings}
                    suggestions={validationResult.suggestions}
                  />
                ) : (
                  <div style={{ padding: '16px', textAlign: 'center', color: '#999' }}>
                    No validation results
                  </div>
                ),
              },
            ]}
          />
        )}
      </div>
    </Card>
  );
};

export default Panel3_CodeEditor;
