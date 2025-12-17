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
import { Card, Space, Spin, Tooltip, Badge } from 'antd';
import {
  WarningOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { validateDiagramCode, debounce } from '../../../services/diagram/validationService';
import type { ValidationResult } from '../../../services/diagram/validationService';
import ErrorPanel from '../components/ErrorPanel';
import styles from '../diagram-wizard.module.css';

interface Panel3CodeEditorProps {
  code: string;
  originalCode?: string;
  diagramType: string;
  isLoading: boolean;
  defaultEditing?: boolean;
  showTitle?: boolean;
}

const Panel3_CodeEditor: React.FC<Panel3CodeEditorProps> = ({
  code,
  diagramType,
  isLoading,
  defaultEditing = false,
  showTitle = true,
}) => {
  // Manage component state for editing, validation, and code manipulation
  const [editedCode, setEditedCode] = useState(code);
  const [isEditing, setIsEditing] = useState(defaultEditing);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

  useEffect(() => {
    setIsEditing(defaultEditing);
  }, [defaultEditing]);

  // Sync code and trigger validation when input code changes
  useEffect(() => {
    setEditedCode(code);
    // Validate when code changes
    if (code && code.trim()) {
      performValidation(code);
    }
  }, [code]);

  // Debounced validation to prevent excessive API calls during typing
  const performValidation = useCallback(
    debounce(async (codeToValidate: string) => {
      // Skip validation for empty code
      if (!codeToValidate || !codeToValidate.trim()) {
        setValidationResult(null);
        return;
      }

      // Skip validation for non-renderable diagram types (JSON, etc.)
      // These are intermediate representations, not actual diagram code
      const nonRenderableTypes = ['JSON', 'json'];
      if (nonRenderableTypes.includes(diagramType)) {
        setValidationResult(null);
        return;
      }

      // Perform async code validation
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

  // Handle code changes during editing and trigger validation
  const handleCodeChange = (value: string) => {
    setEditedCode(value);
    if (isEditing) {
      performValidation(value);
    }
  };

  // Render validation status icon based on current validation state
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

  // Render the code editor with dynamic actions and validation
  return (
    <Card
      title={
        showTitle ? (
          <Space>
            Diagram Code
            {getValidationStatus()}
          </Space>
        ) : null
      }
      headStyle={showTitle ? undefined : { display: 'none' }}
      className={styles.codePanel}
      style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
    >
      {/* Render code editor with optional inline validation feedback */}
      <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
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
          <>
            <Editor
              height="100%"
              defaultLanguage="plaintext"
              value={isEditing ? editedCode : code}
              onChange={(value) => handleCodeChange(value || '')}
              theme="vs-light"
              options={{
                readOnly: !isEditing,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 14,
                lineNumbers: 'on',
                wordWrap: 'on',
                automaticLayout: true,
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
                Edit mode enabled. Updates are kept locally in this editor.
              </div>
            )}
            {validationResult && (validationResult.errors.length > 0 || validationResult.warnings.length > 0) && (
              <div style={{ marginTop: 12 }}>
                <ErrorPanel
                  errors={validationResult.errors}
                  warnings={validationResult.warnings}
                  suggestions={validationResult.suggestions}
                />
              </div>
            )}
          </>
        )}
      </div>
    </Card>
  );
};

export default Panel3_CodeEditor;
