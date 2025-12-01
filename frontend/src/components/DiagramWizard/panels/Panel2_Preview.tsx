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
 * - Error display for validation and rendering failures
 */

import {
  DragOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined,
  ZoomInOutlined,
  ZoomOutOutlined,
} from '@ant-design/icons'
import { Alert,Button, Card, Empty, Space, Spin } from 'antd'
import React, { useCallback,useEffect, useRef, useState } from 'react'

import styles from '../diagram-wizard.module.css'

// Define the props structure for the preview component
interface Panel2PreviewProps {
  svgOutput: string
  diagramType: string
  isLoading: boolean
  error?: string | null
  validationError?: string | null
}

const Panel2_Preview: React.FC<Panel2PreviewProps> = ({
  svgOutput,
  diagramType,
  isLoading,
  error,
  validationError,
}) => {
  // State management for zoom, position, and dragging interactions
  const [scale, setScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const containerRef = useRef<HTMLDivElement>(null)

  // Zoom in function with controlled maximum scale limit
  const handleZoomIn = useCallback(() => {
    setScale((prev) => Math.min(prev + 0.1, 3))
  }, [])

  // Zoom out function with controlled minimum scale limit
  const handleZoomOut = useCallback(() => {
    setScale((prev) => Math.max(prev - 0.1, 0.5))
  }, [])

  // Reset zoom and position to default state
  const handleReset = useCallback(() => {
    setScale(1)
    setPosition({ x: 0, y: 0 })
  }, [])

  // Handle mouse wheel zooming with Ctrl key modifier
  const handleWheel = useCallback((e: React.WheelEvent) => {
    // Prevent default scrolling and allow zoom with Ctrl key
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault()
      const delta = e.deltaY > 0 ? -0.1 : 0.1
      // Constrain zoom between predefined min and max values
      setScale((prev) => Math.min(Math.max(prev + delta, 0.5), 3))
    }
  }, [])

  // Add keyboard shortcuts for zooming and resetting
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if Ctrl key is pressed and SVG is available
      if ((e.ctrlKey || e.metaKey) && svgOutput) {
        // Zoom in on Ctrl + = or +
        if (e.key === '=' || e.key === '+') {
          e.preventDefault()
          handleZoomIn()
        }
        // Zoom out on Ctrl + - or _
        else if (e.key === '-' || e.key === '_') {
          e.preventDefault()
          handleZoomOut()
        }
        // Reset zoom on Ctrl + 0
        else if (e.key === '0') {
          e.preventDefault()
          handleReset()
        }
      }
    }

    // Add and remove event listener for keyboard interactions
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [svgOutput, handleZoomIn, handleZoomOut, handleReset])

  // Start dragging when mouse is pressed
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      // Only allow dragging when SVG is loaded and not at default zoom
      if (svgOutput && scale !== 1) {
        setIsDragging(true)
        // Calculate drag start position relative to current position
        setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y })
        e.preventDefault()
      }
    },
    [svgOutput, scale, position]
  )

  // Update position while mouse is moving during drag
  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isDragging) {
        // Update position based on mouse movement
        setPosition({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        })
      }
    },
    [isDragging, dragStart]
  )

  // Stop dragging when mouse is released
  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
  }, [])

  // Stop dragging if mouse leaves the component
  const handleMouseLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  // Render the preview content with various states
  const renderPreview = () => {
    // Determine if there are any errors to display
    const hasError = error || validationError

    // Show validation error if present (code is invalid)
    if (validationError) {
      return (
        <div style={{ padding: '20px', width: '100%' }}>
          <Alert
            message="Validation Error"
            description={
              <div>
                <p style={{ marginBottom: 8 }}>
                  The generated {diagramType} code contains syntax errors:
                </p>
                <pre
                  style={{
                    background: '#fff1f0',
                    padding: '12px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    maxHeight: '200px',
                    overflow: 'auto',
                    border: '1px solid #ffccc7',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {validationError}
                </pre>
                <p style={{ marginTop: 12, fontSize: '12px', color: '#8c8c8c' }}>
                  The AI will attempt to fix these errors automatically, or you can edit the code
                  manually in the right panel.
                </p>
              </div>
            }
            type="error"
            showIcon
            icon={<ExclamationCircleOutlined />}
          />
        </div>
      )
    }

    // Show rendering error if present (code is valid but rendering failed)
    if (error) {
      return (
        <div style={{ padding: '20px', width: '100%' }}>
          <Alert
            message="Rendering Error"
            description={
              <div>
                <p style={{ marginBottom: 8 }}>Failed to render the {diagramType} diagram:</p>
                <pre
                  style={{
                    background: '#fff1f0',
                    padding: '12px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    maxHeight: '200px',
                    overflow: 'auto',
                    border: '1px solid #ffccc7',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {error}
                </pre>
              </div>
            }
            type="error"
            showIcon
            icon={<ExclamationCircleOutlined />}
          />
        </div>
      )
    }

    // Show empty state if no SVG is generated and no errors
    if (!svgOutput) {
      return <Empty description="No diagram generated yet" />
    }

    // Render SVG with interactive zoom and pan capabilities
    return (
      <div
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        style={{
          // Styling for container with dynamic cursor and overflow handling
          overflow: 'auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          cursor: isDragging ? 'grabbing' : scale !== 1 ? 'grab' : 'default',
          position: 'relative',
        }}
      >
        <div
          style={{
            // Apply zoom and pan transformations dynamically
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
            transformOrigin: 'center',
            transition: isDragging ? 'none' : 'transform 0.2s ease',
            userSelect: 'none',
          }}
          dangerouslySetInnerHTML={{ __html: svgOutput }}
        />
      </div>
    )
  }

  // Render the full preview component with zoom controls
  return (
    <Card
      title="Preview"
      className={styles.previewPanel}
      extra={
        svgOutput && (
          // Render zoom control buttons when SVG is available
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
      style={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
    >
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex' }}>
        {/* Show loading spinner while diagram is generating */}
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
          // Render the preview content when not loading
          renderPreview()
        )}
      </div>
    </Card>
  )
}

export default Panel2_Preview
