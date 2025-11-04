/**
 * Zoom Controls Component
 * Zoom in/out controls with keyboard support
 */

import React, { useEffect } from 'react';
import { Button, Row, Col, Slider, InputNumber } from 'antd';
import { ZoomInOutlined, ZoomOutOutlined, ReloadOutlined } from '@ant-design/icons';

interface ZoomControlsProps {
  zoomLevel: number;
  onZoomChange: (level: number) => void;
  onReset: () => void;
  minZoom: number;
  maxZoom: number;
  step: number;
}

export const ZoomControls: React.FC<ZoomControlsProps> = ({
  zoomLevel,
  onZoomChange,
  onReset,
  minZoom,
  maxZoom,
  step,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === '+' || e.key === '=') {
          e.preventDefault();
          onZoomChange(Math.min(zoomLevel + step, maxZoom));
        } else if (e.key === '-') {
          e.preventDefault();
          onZoomChange(Math.max(zoomLevel - step, minZoom));
        } else if (e.key === '0') {
          e.preventDefault();
          onReset();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [zoomLevel, onZoomChange, onReset, minZoom, maxZoom, step]);

  return (
    <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--ant-color-border)', backgroundColor: 'var(--ant-color-bg-container)' }}>
      <Row align="middle" gap={8}>
        <Button
          type="text"
          icon={<ZoomOutOutlined />}
          size="small"
          onClick={() => onZoomChange(Math.max(zoomLevel - step, minZoom))}
        />
        <Col flex="auto" style={{ minWidth: '100px' }}>
          <Slider
            value={zoomLevel}
            onChange={onZoomChange}
            min={minZoom}
            max={maxZoom}
            step={step}
            tooltip={{ formatter: (v) => `${v}%` }}
          />
        </Col>
        <Button
          type="text"
          icon={<ZoomInOutlined />}
          size="small"
          onClick={() => onZoomChange(Math.min(zoomLevel + step, maxZoom))}
        />
        <InputNumber
          value={zoomLevel}
          onChange={(v) => v && onZoomChange(v)}
          min={minZoom}
          max={maxZoom}
          step={step}
          suffix="%"
          style={{ width: '80px' }}
        />
        <Button
          type="text"
          icon={<ReloadOutlined />}
          size="small"
          onClick={onReset}
          title="Reset zoom"
        />
      </Row>
    </div>
  );
};

export default ZoomControls;
