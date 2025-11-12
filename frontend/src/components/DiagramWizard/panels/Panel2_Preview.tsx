/**
 * Panel2_Preview Component
 *
 * Displays the SVG preview of the generated diagram.
 * Supports zooming and panning for better visualization.
 */

import React, { useState } from 'react';
import { Card, Empty, Button, Space, Spin, message } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import styles from '../diagram-wizard.module.css';

interface Panel2PreviewProps {
  svgOutput: string;
  diagramType: string;
  isLoading: boolean;
}

const Panel2_Preview: React.FC<Panel2PreviewProps> = ({
  svgOutput,
  diagramType,
  isLoading,
}) => {
  const [scale, setScale] = useState(1);
  const [renderError, setRenderError] = useState<string | null>(null);

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.1, 3));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.1, 0.5));
  };

  const handleReset = () => {
    setScale(1);
  };

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
        style={{
          overflow: 'auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
        }}
      >
        <div
          style={{
            transform: `scale(${scale})`,
            transformOrigin: 'center',
            transition: 'transform 0.2s ease',
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
            <Button
              size="small"
              icon={<ZoomInOutlined />}
              onClick={handleZoomIn}
              disabled={scale >= 3}
            />

            <Button
              size="small"
              icon={<ZoomOutOutlined />}
              onClick={handleZoomOut}
              disabled={scale <= 0.5}
            />

            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleReset}
            />
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
