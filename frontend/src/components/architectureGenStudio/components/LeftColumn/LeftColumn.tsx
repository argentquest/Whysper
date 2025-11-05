/**
 * Left Column Component - Prompt Control Panel
 * Agent options list, prompt editor, and submit button
 */

import React from 'react';
import { Layout, Button, Tooltip } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import type { LeftColumnProps } from '../../types';
import { AgentOptionList } from './AgentOptionList';
import { PromptEditor } from './PromptEditor';
import { SubmitButton } from './SubmitButton';
import styles from '../../styles/architectureStudio.module.css';

export const LeftColumn: React.FC<LeftColumnProps> = ({
  isCollapsed,
  onCollapsedChange,
  currentAgent,
  agentOptions,
  selectedOption,
  onOptionSelect,
  currentPrompt,
  onPromptChange,
  onSubmit,
  onCancel,
  isProcessing,
  optionsLoading,
  optionsError,
}) => {
  if (isCollapsed) {
    return (
      <Layout.Sider width={40} style={{ backgroundColor: 'var(--ant-color-bg-container)' }}>
        <Tooltip title="Expand Prompts" placement="right">
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

  return (
    <Layout.Sider
      style={{
        overflow: 'auto',
        backgroundColor: 'var(--ant-color-bg-container)',
        borderRight: '1px solid var(--ant-color-border)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div className={styles.columnHeader}>
        <span style={{ fontWeight: 'bold' }}>Prompt Control</span>
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
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'auto', padding: '16px' }}>
        {!currentAgent ? (
          <div className={styles.empty}>
            <p>Please select an agent from the header</p>
          </div>
        ) : (
          <>
            {/* Agent Options */}
            <div style={{ marginBottom: '16px' }}>
              <AgentOptionList
                options={agentOptions}
                selectedOptionId={selectedOption?.id || null}
                onOptionSelect={onOptionSelect}
                isLoading={optionsLoading}
                error={optionsError}
              />
            </div>

            {/* Prompt Editor */}
            <div style={{ flex: 1, minHeight: '200px', marginBottom: '12px' }}>
              <PromptEditor
                value={currentPrompt}
                onChange={onPromptChange}
                isReadOnly={isProcessing}
                maxCharacters={5000}
                placeholder="Enter your prompt or select a template above"
              />
            </div>

            {/* Submit/Cancel Buttons */}
            <SubmitButton
              isProcessing={isProcessing}
              onSubmit={() => onSubmit(currentPrompt)}
              onCancel={onCancel}
              prompt={currentPrompt}
              disabled={!currentPrompt.trim()}
            />

            {/* Character Count */}
            <div style={{ textAlign: 'right', fontSize: '12px', color: 'var(--ant-color-text-secondary)', marginTop: '8px' }}>
              {currentPrompt.length} / 5000
            </div>
          </>
        )}
      </div>
    </Layout.Sider>
  );
};

export default LeftColumn;
