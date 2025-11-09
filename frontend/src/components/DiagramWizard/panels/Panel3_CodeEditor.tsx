/**
 * Panel3_CodeEditor Component
 *
 * Provides a code editor for viewing and editing diagram source code.
 * Supports syntax highlighting and manual re-rendering.
 */

import React, { useState, useEffect } from 'react';
import { Card, Button, Space, Input, Spin, message, Tooltip } from 'antd';
import {
  CopyOutlined,
  CheckOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
} from '@ant-design/icons';
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

  useEffect(() => {
    setEditedCode(code);
  }, [code]);

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

  return (
    <Card
      title={`${diagramType} Code`}
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
          <Input.TextArea
            value={isEditing ? editedCode : code}
            onChange={(e) => setEditedCode(e.target.value)}
            disabled={!isEditing || isLoading}
            readOnly={!isEditing}
            style={{
              fontFamily: 'monospace',
              fontSize: 12,
              height: '100%',
              border: 'none',
              backgroundColor: '#f5f5f5',
            }}
            rows={20}
          />
        )}
      </div>

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
    </Card>
  );
};

export default Panel3_CodeEditor;
