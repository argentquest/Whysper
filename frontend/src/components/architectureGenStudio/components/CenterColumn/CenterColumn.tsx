/**
 * Center Column Component - Diagram Rendering
 * Displays generated diagrams with zoom and export controls
 */

import React from 'react';
import { Layout, Button, Tooltip, Row, Tabs, Empty, Spin, message } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined, DownloadOutlined } from '@ant-design/icons';
import type { CenterColumnProps } from '../../types';
import { DIAGRAM_TYPES, DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM, ZOOM_STEP } from '../../types';
import { DiagramRenderingArea } from './DiagramRenderingArea';
import { ZoomControls } from './ZoomControls';
import styles from '../../styles/architectureStudio.module.css';

export const CenterColumn: React.FC<CenterColumnProps> = ({
  isCollapsed,
  onCollapsedChange,
  selectedDiagramType,
  onDiagramTypeChange,
  generatedDiagrams,
  isLoading,
  error,
  zoomLevel,
  onZoomChange,
  onExport,
}) => {
  if (isCollapsed) {
    return (
      <Layout.Content style={{ width: '40px', backgroundColor: 'var(--ant-color-bg-container)' }}>
        <Tooltip title="Expand Diagrams" placement="left">
          <Button
            type="text"
            icon={<MenuUnfoldOutlined />}
            onClick={() => onCollapsedChange(false)}
            block
          />
        </Tooltip>
      </Layout.Content>
    );
  }

  const diagram = generatedDiagrams.get(selectedDiagramType);

  const tabItems = DIAGRAM_TYPES.map((type) => ({
    key: type,
    label: `${type.charAt(0).toUpperCase() + type.slice(1)}${generatedDiagrams.has(type) ? ' ✓' : ''}`,
  }));

  const handleExport = (format: 'svg' | 'pdf' | 'code') => {
    if (!diagram) {
      message.warning('No diagram generated yet');
      return;
    }
    onExport(format);
    message.success(`Exporting as ${format.toUpperCase()}`);
  };

  return (
    <Layout.Content
      style={{
        flex: 1,
        overflow: 'hidden',
        backgroundColor: 'var(--ant-color-bg-layout)',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid var(--ant-color-border)',
      }}
    >
      {/* Header */}
      <div className={styles.columnHeader}>
        <span style={{ fontWeight: 'bold' }}>Diagram Rendering</span>
        <Row gap={8}>
          <Tooltip title="Download">
            <Button
              type="text"
              icon={<DownloadOutlined />}
              size="small"
              onClick={() => handleExport('svg')}
              disabled={!diagram}
            />
          </Tooltip>
          <Tooltip title="Minimize">
            <Button
              type="text"
              icon={<MenuFoldOutlined />}
              size="small"
              onClick={() => onCollapsedChange(true)}
            />
          </Tooltip>
        </Row>
      </div>

      {/* Tabs */}
      <Tabs
        activeKey={selectedDiagramType}
        onChange={onDiagramTypeChange}
        items={tabItems}
        style={{ borderBottom: '1px solid var(--ant-color-border)' }}
      />

      {/* Zoom Controls */}
      <ZoomControls
        zoomLevel={zoomLevel}
        onZoomChange={onZoomChange}
        onReset={() => onZoomChange(DEFAULT_ZOOM)}
        minZoom={MIN_ZOOM}
        maxZoom={MAX_ZOOM}
        step={ZOOM_STEP}
      />

      {/* Rendering Area */}
      <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
        {isLoading && (
          <div className={styles.loading}>
            <Spin tip="Generating diagram..." />
          </div>
        )}
        {error && (
          <div className={styles.error}>
            <strong>Error:</strong> {error}
          </div>
        )}
        {!isLoading && !diagram && (
          <div className={styles.empty}>
            <Empty description="Select a diagram type and render to see preview" />
          </div>
        )}
        {diagram && !isLoading && (
          <DiagramRenderingArea
            diagram={diagram.response}
            zoom={zoomLevel / 100}
          />
        )}
      </div>
    </Layout.Content>
  );
};

export default CenterColumn;
