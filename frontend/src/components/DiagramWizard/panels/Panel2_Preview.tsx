/**
 * Panel2_Preview Component
 *
 * Displays the SVG preview of the generated diagram.
 * Supports zooming (mouse wheel, keyboard, buttons) and panning (drag).
 *
 * Enhanced with:
 * - Mouse wheel zoom (Ctrl + wheel)
 * - Keyboard shortcuts (Ctrl+/-/0)
 * - Pan/drag with mouse
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, Empty, Button, Space, Spin } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
  DragOutlined,
} from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';

/**
 * Panel2PreviewProps type definition
 * 
 * Describes the structure and properties of Panel2PreviewProps
 */
interface Panel2PreviewProps {
  svgOutput: string;
  diagramType: string;
  isLoading: boolean;
}

/**
 * Panel2_Preview component
 */
const Panel2_Preview: React.FC<Panel2PreviewProps> = ({
  svgOutput,
  diagramType,
  isLoading,
}) => {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [renderError, _setRenderError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = useCallback(() => {
    setScale((prev) => Math.min(prev + 0.1, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setScale((prev) => Math.max(prev - 0.1, 0.5));
  }, []);

  const handleReset = useCallback(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, []);

  // Mouse wheel zoom (with Ctrl key)
  const handleWheel = useCallback((e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      setScale((prev) => Math.min(Math.max(prev + delta, 0.5), 3));
    }
  }, []);

  // Keyboard shortcuts (Ctrl+/-/0)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && svgOutput) {
        if (e.key === '=' || e.key === '+') {
          e.preventDefault();
          handleZoomIn();
        } else if (e.key === '-' || e.key === '_') {
          e.preventDefault();
          handleZoomOut();
        } else if (e.key === '0') {
          e.preventDefault();
          handleReset();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [svgOutput, handleZoomIn, handleZoomOut, handleReset]);

  // Pan/drag functionality
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (svgOutput && scale !== 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
      e.preventDefault();
    }
  }, [svgOutput, scale, position]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  }, [isDragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const renderPreview = () => {
    if (!svgOutput) {
      return <Empty description="No diagram generated yet" />;
    }

    if (renderError) {
      return (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Empty
            description={`Error rendering ${diagramType} diagram`}
            style={{ marginBottom: 16 }}
          />
          <p style={{ color: '#ff4d4f', fontSize: 12 }}>{renderError}</p>
        </div>
      );
    }

    // For SVG content, render it directly
    return (
      <div
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        style={{
          overflow: 'auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          cursor: isDragging ? 'grabbing' : (scale !== 1 ? 'grab' : 'default'),
          position: 'relative',
        }}
      >
        <div
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
            transformOrigin: 'center',
            transition: isDragging ? 'none' : 'transform 0.2s ease',
            userSelect: 'none',
          }}
          dangerouslySetInnerHTML={{ __html: svgOutput }}
        />
      </div>
    );
  };

  return (
    <Card
      title="Preview"
      className={styles.previewPanel}
      extra={
        svgOutput && (
          <Space>
            <span style={{ fontSize: '12px', color: '#666', marginRight: '8px' }}>
              {Math.round(scale * 100)}%
            </span>
            <Button
              size="small"
              icon={<ZoomInOutlined />}
              onClick={handleZoomIn}
              disabled={scale >= 3}
              title="Zoom in (Ctrl + +)"
            />

            <Button
              size="small"
              icon={<ZoomOutOutlined />}
              onClick={handleZoomOut}
              disabled={scale <= 0.5}
              title="Zoom out (Ctrl + -)"
            />

            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleReset}
              title="Reset zoom and pan (Ctrl + 0)"
            />

            {scale !== 1 && (
              <span style={{ fontSize: '11px', color: '#999', marginLeft: '8px' }}>
                <DragOutlined style={{ marginRight: '4px' }} />
                Drag to pan
              </span>
            )}
          </Space>
        )
      }
      style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
    >
      <div style={{ flex: 1, overflow: 'auto', display: 'flex' }}>
        {isLoading ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '100%',
            }}
          >
            <Spin tip="Generating diagram...">
              <div style={{ height: 100 }} />
            </Spin>
          </div>
        ) : (
          renderPreview()
        )}
      </div>
    </Card>
  );
};

export default Panel2_Preview;
