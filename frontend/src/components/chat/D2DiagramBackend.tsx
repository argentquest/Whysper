/**
 * D2 Diagram Component using Backend API
 * Renders D2 diagrams using the backend CLI service instead of client-side JavaScript
 */

import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Space, Tag, Spin, Alert, Collapse, Typography } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import d2Api from '../../services/d2Api';
import type { D2RenderResponse } from '../../services/d2Api';

const { Text } = Typography;
const { Panel } = Collapse;

interface D2DiagramBackendProps {
  code: string;
  title?: string;
  showCode?: boolean;
  onRenderComplete?: (success: boolean, svg?: string) => void;
}

export const D2DiagramBackend: React.FC<D2DiagramBackendProps> = ({ 
  code, 
  title = 'D2 Diagram', 
  showCode = false,
  onRenderComplete 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [renderResult, setRenderResult] = useState<D2RenderResponse | null>(null);
  const [showDebugInfo, setShowDebugInfo] = useState(false);

  useEffect(() => {
    if (code) {
      renderDiagram();
    }
  }, [code]);

  const renderDiagram = async () => {
    if (!code || !containerRef.current) {
      console.log('[D2 BACKEND] Skipping render - no container or code');
      return;
    }

    console.log('[D2 BACKEND] Starting D2 diagram render via backend API');
    setIsLoading(true);
    setError('');
    setRenderResult(null);

    try {
      // Basic check first - backend handles actual validation
      const basicCheck = d2Api.basicCheck(code);
      if (!basicCheck.isValid) {
        const errorMsg = `Basic check failed:\n${basicCheck.errors.join('\n')}`;
        console.warn('[D2 BACKEND] Basic check failed:', basicCheck.errors);
        setError(errorMsg);
        setIsLoading(false);
        if (onRenderComplete) onRenderComplete(false);
        return;
      }

      // Render via backend API
      const result = await d2Api.quickRender(code);
      setRenderResult(result);

      if (result.success && result.svg_content) {
        setSvg(result.svg_content);
        
        // Insert SVG into DOM
        if (containerRef.current) {
          containerRef.current.innerHTML = result.svg_content;
        }
        
        console.log('[D2 BACKEND] SVG rendered successfully via backend', {
          renderTime: result.metadata.render_time,
          codeLength: result.metadata.code_length
        });
        
        if (onRenderComplete) onRenderComplete(true, result.svg_content);
      } else {
        const errorMsg = result.error || 'Unknown error occurred during rendering';
        setError(errorMsg);
        console.error('[D2 BACKEND] Backend rendering failed:', errorMsg);
        if (onRenderComplete) onRenderComplete(false);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to render D2 diagram via backend';
      console.error('[D2 BACKEND] Rendering error:', err);
      setError(errorMessage);
      if (onRenderComplete) onRenderComplete(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopySVG = async () => {
    try {
      await navigator.clipboard.writeText(svg);
      // Use Ant Design message instead of window.alert
      const { message } = await import('antd');
      message.success('SVG copied to clipboard');
    } catch (err) {
      console.error('Failed to copy SVG:', err);
      const { message } = await import('antd');
      message.error('Failed to copy SVG');
    }
  };

  const handleDownloadSVG = () => {
    if (!svg) return;
    
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExpand = () => {
    if (!svg) return;
    
    const newWindow = window.open('', '_blank');
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
      `);
      newWindow.document.close();
    }
  };

  return (
    <Card
      title={
        <Space>
          {title}
          {renderResult?.validation.is_valid && (
            <Tag color="green" icon={<CheckCircleOutlined />}>
              Valid D2
            </Tag>
          )}
          {renderResult?.metadata.render_time && (
            <Tag color="blue">
              {renderResult.metadata.render_time.toFixed(2)}s
            </Tag>
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
            borderRadius: 4
          }}
        />
      )}

      {showDebugInfo && renderResult && (
        <Collapse style={{ marginTop: 10 }}>
          <Panel header="Debug Information" key="debug">
            <div style={{ fontSize: 12, fontFamily: 'monospace' }}>
              <div><strong>Success:</strong> {renderResult.success}</div>
              <div><strong>Code Length:</strong> {renderResult.metadata.code_length} chars</div>
              <div><strong>Render Time:</strong> {renderResult.metadata.render_time?.toFixed(3)}s</div>
              <div><strong>Timestamp:</strong> {renderResult.metadata.timestamp}</div>
              <div><strong>Validation:</strong> {renderResult.validation.is_valid ? 'Passed' : 'Failed'}</div>
              {renderResult.validation.error && (
                <div><strong>Validation Error:</strong> {renderResult.validation.error}</div>
              )}
              {renderResult.error && (
                <div><strong>Render Error:</strong> {renderResult.error}</div>
              )}
              {renderResult.file_path && (
                <div><strong>Saved to:</strong> {renderResult.file_path}</div>
              )}
            </div>
          </Panel>
        </Collapse>
      )}

      {showCode && code && (
        <Collapse style={{ marginTop: 10 }}>
          <Panel header="D2 Source Code" key="code">
            <pre style={{
              backgroundColor: '#f5f5f5',
              padding: 10,
              borderRadius: 4,
              fontSize: 12,
              overflow: 'auto',
              maxHeight: 300
            }}>
              {code}
            </pre>
          </Panel>
        </Collapse>
      )}
    </Card>
  );
};