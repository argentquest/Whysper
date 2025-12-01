/**
 * D2 Diagram Component using Backend Provider Service
 * Renders D2 diagrams using the unified diagram provider service
 */

import {
  CheckCircleOutlined,
  CopyOutlined,
  DownloadOutlined,
  ExpandOutlined,
} from '@ant-design/icons'
import {
  Alert,
  Button,
  Card,
  Collapse,
  message as antMessage,
  Space,
  Spin,
  Tag,
  Typography,
} from 'antd'
import React, { useEffect, useRef,useState } from 'react'

import type { DiagramRenderResponse, ProviderInfo } from '../../services/diagramProviderService'
import diagramProviderService from '../../services/diagramProviderService'

const { Text } = Typography
const { Panel } = Collapse

/**
 * D2DiagramBackendProps type definition
 *
 * Describes the structure and properties of D2DiagramBackendProps
 * @interface D2DiagramBackendProps
 * @property {string} code - The D2 diagram code to render
 * @property {string} [title] - Optional title for the diagram card
 * @property {boolean} [showCode] - Whether to show the source code by default
 * @property {Function} [onRenderComplete] - Callback when rendering completes
 */
interface D2DiagramBackendProps {
  code: string
  title?: string
  showCode?: boolean
  onRenderComplete?: (success: boolean, svg?: string) => void
}

/**
 * D2DiagramBackend component
 *
 * Renders a D2 diagram using the backend rendering service.
 * Includes features for:
 * - Server-side rendering
 * - Auto-fix validation
 * - SVG export and copy
 * - Debug information
 *
 * @param {D2DiagramBackendProps} props - Component props
 * @returns {JSX.Element} Rendered D2 diagram card
 */
export const D2DiagramBackend: React.FC<D2DiagramBackendProps> = ({
  code,
  title = 'D2 Diagram',
  showCode = false,
  onRenderComplete,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [renderResult, setRenderResult] = useState<DiagramRenderResponse | null>(null)
  const [showDebugInfo, setShowDebugInfo] = useState(false)
  const [renderKey, setRenderKey] = useState(0) // Force re-render trigger
  const [providerInfo, setProviderInfo] = useState<ProviderInfo | null>(null)

  // Get provider info on mount
  useEffect(() => {
    const fetchProviderInfo = async () => {
      try {
        const info = await diagramProviderService.getProviderInfo('d2')
        setProviderInfo(info)
        console.log('🎯 [D2 DIAGRAM] Provider info loaded:', info.provider_name)
      } catch (err) {
        console.warn('🎯 [D2 DIAGRAM] Failed to get provider info:', err)
      }
    }
    fetchProviderInfo()
  }, [])

  useEffect(() => {
    if (code) {
      renderDiagram()
    }
  }, [code, renderKey]) // Re-render when code OR renderKey changes

  // Monitor container visibility and size changes to trigger re-render
  useEffect(() => {
    if (!containerRef.current) return

    const observer = new ResizeObserver(() => {
      // Trigger re-render when container size changes (e.g., fullscreen toggle)
      console.log('🎯 [D2 DIAGRAM] Container resized, triggering re-render')
      setRenderKey((prev) => prev + 1)
    })

    observer.observe(containerRef.current)

    return () => observer.disconnect()
  }, [])

  const renderDiagram = async () => {
    if (!code || !containerRef.current) {
      console.log('🎯 [D2 DIAGRAM] Skipping render - no container or code')
      return
    }

    console.log('🎯 [D2 DIAGRAM] Starting D2 diagram render via provider service', {
      codeLength: code.length,
      provider: providerInfo?.provider_id || 'd2v1',
    })

    setIsLoading(true)
    setError('')
    setRenderResult(null)

    try {
      // Validate using provider service (with auto-fix)
      console.log('🎯 [D2 DIAGRAM] Validating D2 code via provider...')
      const validationResponse = await diagramProviderService.validate({
        code,
        diagram_type: 'd2',
        auto_fix: true,
      })

      console.log('🎯 [D2 DIAGRAM] Validation result:', {
        is_valid: validationResponse.is_valid,
        auto_fixed: validationResponse.auto_fixed,
        llm_corrected: validationResponse.llm_corrected,
      })

      // Use fixed code if available, otherwise use original
      const codeToRender = validationResponse.fixed_code || code

      // Render using backend provider
      console.log('🎯 [D2 DIAGRAM] Rendering via backend provider...')
      const result = await diagramProviderService.render({
        code: codeToRender,
        diagram_type: 'd2',
        output_format: 'svg',
      })

      setRenderResult(result)

      if (result.success && result.content) {
        setSvg(result.content)

        // Insert SVG into DOM
        if (containerRef.current) {
          containerRef.current.innerHTML = result.content
        }

        console.log('🎯 [D2 DIAGRAM] SVG rendered successfully via provider', {
          provider: result.metadata.provider_id,
          renderTime: result.metadata.render_time,
          svgLength: result.content.length,
        })

        // Show notification if auto-fixed
        if (validationResponse.auto_fixed) {
          antMessage.success(
            `D2 diagram rendered successfully (${validationResponse.correction_method})`,
            4
          )
        }

        if (onRenderComplete) onRenderComplete(true, result.content)
      } else {
        const errorMsg = result.error || 'Unknown error occurred during rendering'
        setError(errorMsg)
        console.error('🎯 [D2 DIAGRAM] Provider rendering failed:', errorMsg)
        if (onRenderComplete) onRenderComplete(false)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to render D2 diagram'
      console.error('🎯 [D2 DIAGRAM] Rendering error:', err)
      setError(errorMessage)
      if (onRenderComplete) onRenderComplete(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopySVG = async () => {
    try {
      await navigator.clipboard.writeText(svg)
      antMessage.success('SVG copied to clipboard')
    } catch (err) {
      console.error('Failed to copy SVG:', err)
      antMessage.error('Failed to copy SVG')
    }
  }

  const handleDownloadSVG = () => {
    if (!svg) return

    const blob = new Blob([svg], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.svg`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleExpand = () => {
    if (!svg) return

    const newWindow = window.open('', '_blank')
    if (newWindow) {
      newWindow.document.write(`
        <html>
          <head>
            <title>${title}</title>
            <style>
              body { margin: 20px; font-family: Arial, sans-serif; }
              h1 { color: #333; }
              svg { max-width: 100%; height: auto; }
            </style>
          </head>
          <body>
            <h1>${title}</h1>
            ${svg}
          </body>
        </html>
      `)
      newWindow.document.close()
    }
  }

  return (
    <Card
      title={
        <Space>
          {title}
          {renderResult && renderResult.success && (
            <>
              <Tag color="green" icon={<CheckCircleOutlined />}>
                {renderResult.metadata.provider_name}
              </Tag>
              <Tag color="blue">{renderResult.metadata.render_time?.toFixed(0)}ms</Tag>
            </>
          )}
        </Space>
      }
      size="small"
      extra={
        <Space>
          {svg && (
            <>
              <Button
                size="small"
                icon={<CopyOutlined />}
                onClick={handleCopySVG}
                title="Copy SVG"
              />
              <Button
                size="small"
                icon={<DownloadOutlined />}
                onClick={handleDownloadSVG}
                title="Download SVG"
              />
              <Button
                size="small"
                icon={<ExpandOutlined />}
                onClick={handleExpand}
                title="Open in new window"
              />
            </>
          )}
          <Button
            size="small"
            onClick={() => setShowDebugInfo(!showDebugInfo)}
            title="Toggle debug information"
          >
            {showDebugInfo ? 'Hide' : 'Show'} Debug
          </Button>
        </Space>
      }
    >
      {isLoading && (
        <div style={{ padding: 20, textAlign: 'center' }}>
          <Spin size="large" />
          <div style={{ marginTop: 10 }}>Rendering D2 diagram via backend...</div>
        </div>
      )}

      {error && (
        <Alert
          message="Rendering Error"
          description={
            <div>
              <Text type="danger">{error}</Text>
              {renderResult && (
                <div style={{ marginTop: 10 }}>
                  <Text type="secondary">
                    Validation: {renderResult.validation.is_valid ? 'Passed' : 'Failed'}
                    {renderResult.validation.error && (
                      <div>Error: {renderResult.validation.error}</div>
                    )}
                  </Text>
                </div>
              )}
            </div>
          }
          type="error"
          showIcon
          style={{ marginBottom: 10 }}
        />
      )}

      {!isLoading && !error && (
        <div
          ref={containerRef}
          style={{
            minHeight: 100,
            textAlign: 'center',
            backgroundColor: '#fafafa',
            padding: 10,
            borderRadius: 4,
          }}
        />
      )}

      {showDebugInfo && renderResult && (
        <Collapse style={{ marginTop: 10 }}>
          <Panel header="Debug Information" key="debug">
            <div style={{ fontSize: 12, fontFamily: 'monospace' }}>
              <div>
                <strong>Success:</strong> {renderResult.success}
              </div>
              <div>
                <strong>Code Length:</strong> {renderResult.metadata.code_length} chars
              </div>
              <div>
                <strong>Render Time:</strong> {renderResult.metadata.render_time?.toFixed(3)}s
              </div>
              <div>
                <strong>Timestamp:</strong> {renderResult.metadata.timestamp}
              </div>
              <div>
                <strong>Validation:</strong>{' '}
                {renderResult.validation.is_valid ? 'Passed' : 'Failed'}
              </div>
              {renderResult.validation.error && (
                <div>
                  <strong>Validation Error:</strong> {renderResult.validation.error}
                </div>
              )}
              {renderResult.error && (
                <div>
                  <strong>Render Error:</strong> {renderResult.error}
                </div>
              )}
              {renderResult.file_path && (
                <div>
                  <strong>Saved to:</strong> {renderResult.file_path}
                </div>
              )}
            </div>
          </Panel>
        </Collapse>
      )}

      {showCode && code && (
        <Collapse style={{ marginTop: 10 }}>
          <Panel header="D2 Source Code" key="code">
            <pre
              style={{
                backgroundColor: '#f5f5f5',
                padding: 10,
                borderRadius: 4,
                fontSize: 12,
                overflow: 'auto',
                maxHeight: 300,
              }}
            >
              {code}
            </pre>
          </Panel>
        </Collapse>
      )}
    </Card>
  )
}
