/**
 * Right Column Component - Code Editor
 * Monaco editor for diagram code and validation
 */

import React from 'antd';
import { Layout, Button, Tooltip, Space, message } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { RightColumnProps } from '../../types';
import { CodeEditor } from './CodeEditor';
import { ValidateButton } from './ValidateButton';
import { RenderButton } from './RenderButton';
import { ErrorPanel } from './ErrorPanel';
import styles from '../../styles/architectureStudio.module.css';

export const RightColumn: React.FC<RightColumnProps> = ({
  isCollapsed,
  onCollapsedChange,
  width,
  onWidthChange,
  code,
  onCodeChange,
  diagramType,
  onValidate,
  onRender,
  validationResult,
  isValidating,
  isRendering,
  hasUnsavedChanges,
  errors,
  onErrorDismiss,
}) => {
  if (isCollapsed) {
    return (
      <Layout.Sider width={40} style={{ backgroundColor: 'var(--ant-color-bg-container)' }}>
        <Tooltip title="Expand Code" placement="left">
          <Button
            type="text"
            icon={<MenuUnfoldOutlined />}
            onClick={() => onCollapsedChange(false)}
            block
          />
        </Tooltip>
      </Layout.Sider>
    );
  }

  const canRender = validationResult?.isValid || !validationResult;

  return (
    <Layout.Sider
      width={`${width}%`}
      style={{
        overflow: 'auto',
        backgroundColor: 'var(--ant-color-bg-container)',
        borderLeft: '1px solid var(--ant-color-border)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div className={styles.columnHeader}>
        <span style={{ fontWeight: 'bold' }}>Code Editor</span>
        <Tooltip title="Collapse">
          <Button
            type="text"
            icon={<MenuFoldOutlined />}
            size="small"
            onClick={() => onCollapsedChange(true)}
          />
        </Tooltip>
      </div>

      {/* Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto', padding: '12px' }}>
        {/* Code Editor */}
        <div style={{ flex: 1, minHeight: '300px', marginBottom: '12px', border: '1px solid var(--ant-color-border)', borderRadius: '4px', overflow: 'hidden' }}>
          <CodeEditor
            code={code}
            onChange={onCodeChange}
            diagramType={diagramType}
            isReadOnly={false}
          />
        </div>

        {/* Action Buttons */}
        <Space style={{ marginBottom: '12px', width: '100%' }}>
          <ValidateButton
            code={code}
            diagramType={diagramType}
            onValidate={onValidate}
            isLoading={isValidating}
          />
          <RenderButton
            code={code}
            diagramType={diagramType}
            onRender={onRender}
            isLoading={isRendering}
            canRender={canRender}
          />
        </Space>

        {/* Error Panel */}
        {errors.length > 0 && (
          <ErrorPanel
            errors={errors}
            type="validation"
            isVisible={true}
            onDismiss={onErrorDismiss}
          />
        )}

        {/* Unsaved Changes Indicator */}
        {hasUnsavedChanges && (
          <div style={{ padding: '8px', backgroundColor: 'var(--ant-color-warning-bg)', borderRadius: '4px', fontSize: '12px', color: 'var(--ant-color-warning)' }}>
            ⚠️ Unsaved changes
          </div>
        )}
      </div>
    </Layout.Sider>
  );
};

export default RightColumn;
