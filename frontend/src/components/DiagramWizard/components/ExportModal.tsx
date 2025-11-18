/**
 * ExportModal Component
 *
 * Provides UI for exporting diagrams in various formats (SVG, PNG, PDF).
 * Allows users to customize export options.
 */

import React, { useState } from 'react';
import { Modal, Radio, Input, InputNumber, Form, message, Space, Alert } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { exportDiagram, getSVGElement } from '@/services/diagram/exportService';
import type { ExportFormat } from '@/services/diagram/exportService';

/**
 * ExportModalProps type definition
 * 
 * Describes the structure and properties of ExportModalProps
 */
interface ExportModalProps {
  visible: boolean;
  onClose: () => void;
  svgContainerRef: React.RefObject<HTMLDivElement | null>;
  defaultFilename?: string;
}

/**
 * ExportModal component
 */
const ExportModal: React.FC<ExportModalProps> = ({
  visible,
  onClose,
  svgContainerRef,
  defaultFilename = 'diagram',
}) => {
  const [format, setFormat] = useState<ExportFormat>('svg');
  const [filename, setFilename] = useState(defaultFilename);
  const [scale, setScale] = useState(2);
  const [backgroundColor, setBackgroundColor] = useState('#ffffff');
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (!svgContainerRef.current) {
      message.error('No diagram to export');
      return;
    }

    const svgElement = getSVGElement(svgContainerRef.current);
    if (!svgElement) {
      message.error('SVG element not found');
      return;
    }

    setExporting(true);
    try {
      await exportDiagram(svgElement, {
        format,
        filename,
        scale,
        backgroundColor,
      });
      message.success(`Diagram exported as ${format.toUpperCase()}`);
      onClose();
    } catch (error) {
      console.error('Export failed:', error);
      message.error(`Failed to export diagram: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <Modal
      title={
        <Space>
          <DownloadOutlined />
          Export Diagram
        </Space>
      }
      open={visible}
      onCancel={onClose}
      onOk={handleExport}
      confirmLoading={exporting}
      okText="Export"
      width={500}
    >
      <Form layout="vertical" style={{ marginTop: '16px' }}>
        <Form.Item label="Export Format">
          <Radio.Group
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            buttonStyle="solid"
          >
            <Radio.Button value="svg">SVG</Radio.Button>
            <Radio.Button value="png">PNG</Radio.Button>
            <Radio.Button value="pdf">PDF</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item label="Filename">
          <Input
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="diagram"
            suffix={`.${format}`}
          />
        </Form.Item>

        {(format === 'png' || format === 'pdf') && (
          <>
            <Form.Item
              label="Background Color"
              extra="Set background color for the exported image"
            >
              <Space>
                <Input
                  type="color"
                  value={backgroundColor}
                  onChange={(e) => setBackgroundColor(e.target.value)}
                  style={{ width: '80px' }}
                />
                <Input
                  value={backgroundColor}
                  onChange={(e) => setBackgroundColor(e.target.value)}
                  placeholder="#ffffff"
                  style={{ width: '120px' }}
                />
              </Space>
            </Form.Item>

            {format === 'png' && (
              <Form.Item
                label="Quality (Scale)"
                extra="Higher values produce better quality but larger files"
              >
                <InputNumber
                  min={1}
                  max={4}
                  value={scale}
                  onChange={(value) => setScale(value || 2)}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            )}
          </>
        )}

        <Alert
          message="Export Information"
          description={
            format === 'svg'
              ? 'SVG format preserves vector quality and is editable in design tools.'
              : format === 'png'
              ? 'PNG format produces a raster image suitable for presentations and documents.'
              : 'PDF format is ideal for printing and sharing professional documents.'
          }
          type="info"
          showIcon
          style={{ marginTop: '8px' }}
        />
      </Form>
    </Modal>
  );
};

export default ExportModal;
