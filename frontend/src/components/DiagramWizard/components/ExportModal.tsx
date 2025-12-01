import { DownloadOutlined } from '@ant-design/icons'
import { Alert,Form, Input, InputNumber, message, Modal, Radio, Space } from 'antd'
import React, { useState } from 'react'

import type { ExportFormat } from '@/services/diagram/exportService'
import { exportDiagram, getSVGElement } from '@/services/diagram/exportService'

interface ExportModalProps {
  visible: boolean
  onClose: () => void
  svgContainerRef: React.RefObject<HTMLDivElement | null>
  defaultFilename?: string
}

const ExportModal: React.FC<ExportModalProps> = ({
  visible,
  onClose,
  svgContainerRef,
  defaultFilename = 'diagram',
}) => {
  // Initialize state variables for export configuration and tracking
  const [format, setFormat] = useState<ExportFormat>('svg')
  const [filename, setFilename] = useState(defaultFilename)
  const [scale, setScale] = useState(2)
  const [backgroundColor, setBackgroundColor] = useState('#ffffff')
  const [exporting, setExporting] = useState(false)

  const handleExport = async () => {
    // Verify SVG container exists before attempting export
    if (!svgContainerRef.current) {
      message.error('No diagram to export')
      return
    }

    // Extract SVG element to be exported
    const svgElement = getSVGElement(svgContainerRef.current)
    if (!svgElement) {
      message.error('SVG element not found')
      return
    }

    // Begin export process and manage loading state
    setExporting(true)
    try {
      // Execute diagram export with selected configuration
      await exportDiagram(svgElement, {
        format,
        filename,
        scale,
        backgroundColor,
      })

      // Display success message and close modal on successful export
      message.success(`Diagram exported as ${format.toUpperCase()}`)
      onClose()
    } catch (error) {
      // Handle and log any export errors
      console.error('Export failed:', error)
      message.error(
        `Failed to export diagram: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    } finally {
      // Reset exporting state after export attempt
      setExporting(false)
    }
  }

  return (
    <Modal
      // Configure modal with export settings and interactions
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
        {/* Allow user to select export file format */}
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

        {/* Enable filename input with dynamic extension */}
        <Form.Item label="Filename">
          <Input
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="diagram"
            suffix={`.${format}`}
          />
        </Form.Item>

        {/* Render additional options for raster formats */}
        {(format === 'png' || format === 'pdf') && (
          <>
            {/* Allow background color customization for raster exports */}
            <Form.Item label="Background Color" extra="Set background color for the exported image">
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

            {/* Provide scale/quality control for PNG format */}
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

        {/* Display informative alert about selected export format */}
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
  )
}

export default ExportModal
