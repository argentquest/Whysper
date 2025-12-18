/**
 * Panel3_CodeEditor Component
 *
 * Provides a code editor for viewing and editing diagram source code.
 * Supports syntax highlighting and real-time validation.
 *
 * Enhanced with:
 * - Real-time code validation
 * - Error/warning display
 * - Auto-fix suggestions
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
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
import type { CSSProperties } from 'react';

interface Panel3CodeEditorProps {
  code: string;
  originalCode?: string;
  diagramType: string;
  isLoading: boolean;
  showTitle?: boolean;
  onCodeChange?: (code: string) => void;
}

const Panel3_CodeEditor: React.FC<Panel3CodeEditorProps> = ({
  code,
  diagramType,
  isLoading,
  showTitle = true,
  onCodeChange,
}) => {
  // Manage component state for validation
  const [editedCode, setEditedCode] = useState(code);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [isValidating, setIsValidating] = useState(false);

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

  // Sync code when input code changes
  const isInitialSync = useRef(true);

  useEffect(() => {
    // Allow initial validation even if prop === local state, then guard duplicates
    if (isInitialSync.current) {
      isInitialSync.current = false;
    } else if (code === editedCode) {
      return;
    }

    setEditedCode(code);

    if (code && code.trim()) {
      performValidation(code);
    } else {
      setValidationResult(null);
    }
  }, [code, editedCode, performValidation]);

  // Handle code changes and trigger validation
  const handleCodeChange = (value: string) => {
    setEditedCode(value);
    onCodeChange?.(value);
    performValidation(value);
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

  // Render the code editor with validation
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
      style={{
        height: '100%',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        minHeight: 0,
      }}
      bodyStyle={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0,
        padding: showTitle ? undefined : 8,
      } as CSSProperties}
    >
      {/* Render code editor with validation feedback */}
      <div style={{
        flex: 1,
        minHeight: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
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
            <div style={{ flex: 1, minHeight: 0, height: '100%' }}>
              <Editor
                height="100%"
                width="100%"
                defaultLanguage="plaintext"
                value={editedCode}
                onChange={(value) => handleCodeChange(value || '')}
                theme="vs-light"
                options={{
                  readOnly: false,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  fontSize: 14,
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  automaticLayout: true,
                }}
              />
            </div>
            {validationResult && (validationResult.errors.length > 0 || validationResult.warnings.length > 0) && (
              <div style={{ marginTop: 12, flexShrink: 0 }}>
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
