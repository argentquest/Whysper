import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, message as antMessage, Tag } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined, CodeOutlined } from '@ant-design/icons';
import { ApiService } from '../../services/api';
import { convertC4ToD2, simpleC4ToD2, extractC4Level } from '../../utils/c4ToD2';
import d2Api from '../../services/d2Api';

/**
 * C4 Diagram Component
 *
 * Converts C4 PlantUML syntax to D2 and renders using backend D2 CLI service.
 * All rendering happens server-side to avoid client-side D2 library dependencies.
 */

interface C4DiagramProps {
  code: string;
  title?: string;
}

export const C4Diagram: React.FC<C4DiagramProps> = ({ code, title }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [svgContent, setSvgContent] = useState<string>('');
  const [c4Level, setC4Level] = useState<string>('Context');
  const [d2Code, setD2Code] = useState<string>('');
  const [showD2Code, setShowD2Code] = useState(false);
  const [renderKey, setRenderKey] = useState(0); // Force re-render trigger

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current || !code) {
        console.log('🏗️ [C4 DIAGRAM] Skipping render - no container or code');
        return;
      }

      console.log('🏗️ [C4 DIAGRAM] Starting C4 diagram render (will use D2)', {
        codeLength: code.length,
        codePreview: code.substring(0, 50) + '...',
        hasContainer: !!containerRef.current
      });

      // Extract C4 level
      const level = extractC4Level(code);
      setC4Level(level);

      // Log render start to backend
      ApiService.logDiagramEvent({
        event_type: 'render_start',
        diagram_type: 'c4' as any,
        code_length: code.length,
        code_preview: code.substring(0, 100),
        detection_method: `c4_level:${level}`
      });

      setIsRendering(true);
      setError(null);

      try {
        // Convert C4 to D2
        console.log('🏗️ [C4 DIAGRAM] Converting C4 syntax to D2...');
        let convertedD2 = '';
        let usedFallback = false;

        try {
          // Try main conversion first
          convertedD2 = convertC4ToD2(code);
          console.log('🏗️ [C4 DIAGRAM] Main conversion successful');
        } catch (conversionError) {
          console.warn('⚠️ [C4 DIAGRAM] Main conversion failed, trying fallback:', conversionError);

          // Try fallback conversion
          try {
            convertedD2 = simpleC4ToD2(code);
            usedFallback = true;
            console.log('🏗️ [C4 DIAGRAM] Fallback conversion successful');
          } catch (fallbackError) {
            // Both conversions failed
            throw new Error(
              `C4 to D2 conversion failed.\n\n` +
              `Main error: ${conversionError instanceof Error ? conversionError.message : 'Unknown error'}\n\n` +
              `Fallback error: ${fallbackError instanceof Error ? fallbackError.message : 'Unknown error'}\n\n` +
              `Please check that your C4 diagram syntax is correct. ` +
              `Expected format: Person(id, "label"), System(id, "label"), Rel(from, to, "label")`
            );
          }
        }

        setD2Code(convertedD2);
        console.log('🏗️ [C4 DIAGRAM] Conversion complete', {
          originalLength: code.length,
          d2Length: convertedD2.length,
          usedFallback
        });

        // Validate D2 code is not empty
        if (!convertedD2 || convertedD2.trim().length === 0) {
          throw new Error(
            'C4 to D2 conversion produced empty output. ' +
            'The C4 code may not contain any recognizable entities or relationships.'
          );
        }

        // Render D2 code using backend API (server-side rendering via D2 CLI)
        console.log('🏗️ [C4 DIAGRAM] Sending D2 code to backend for rendering...');

        let svg: string;
        try {
          const renderResponse = await d2Api.renderD2({ code: convertedD2 });

          if (!renderResponse.success || !renderResponse.svg_content) {
            throw new Error(
              renderResponse.error ||
              'Backend D2 rendering failed - no SVG content returned'
            );
          }

          svg = renderResponse.svg_content;
          console.log('🏗️ [C4 DIAGRAM] Backend rendering successful', {
            svgLength: svg.length
          });
        } catch (renderError) {
          throw new Error(
            `Backend D2 rendering failed: ${renderError instanceof Error ? renderError.message : 'Unknown error'}.\n\n` +
            `The converted D2 code could not be rendered by the backend service. ` +
            `Check that the D2 CLI is properly installed and configured.`
          );
        }

        // Store SVG content for export
        setSvgContent(svg);

        // Insert the SVG into the container
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          console.log('🏗️ [C4 DIAGRAM] SVG inserted into DOM');
        }

        // Log render success to backend
        ApiService.logDiagramEvent({
          event_type: 'render_success',
          diagram_type: 'c4' as any,
          code_length: code.length,
          detection_method: `c4_level:${level}${usedFallback ? '_fallback' : ''}`
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to render C4 diagram: Unknown error';
        console.error('❌ [C4 DIAGRAM] Rendering error:', err);
        setError(errorMessage);

        // Log render error to backend
        ApiService.logDiagramEvent({
          event_type: 'render_error',
          diagram_type: 'c4' as any,
          error_message: errorMessage,
          code_length: code.length,
          code_preview: code.substring(0, 100),
          detection_method: `c4_level:${level}`
        });
      } finally {
        setIsRendering(false);
        console.log('🏗️ [C4 DIAGRAM] Render process finished');
      }
    };

    renderDiagram();
  }, [code, renderKey]); // Re-render when code OR renderKey changes

  // Monitor container visibility and size changes to trigger re-render
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver(() => {
      // Trigger re-render when container size changes (e.g., fullscreen toggle)
      console.log('🏗️ [C4 DIAGRAM] Container resized, triggering re-render');
      setRenderKey(prev => prev + 1);
    });

    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, []);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      antMessage.success('C4 diagram code copied to clipboard');
    } catch (err) {
      antMessage.error('Failed to copy code');
    }
  };

  const handleCopyD2 = async () => {
    try {
      await navigator.clipboard.writeText(d2Code);
      antMessage.success('D2 code copied to clipboard');
    } catch (err) {
      antMessage.error('Failed to copy D2 code');
    }
  };

  const handleDownloadSVG = () => {
    try {
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title || 'c4-diagram'}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      antMessage.success('SVG downloaded');
    } catch (err) {
      antMessage.error('Failed to download SVG');
    }
  };

  const handleDownloadPNG = async () => {
    try {
      const svgElement = containerRef.current?.querySelector('svg');
      if (!svgElement) {
        antMessage.error('No diagram to download');
        return;
      }

      // Create canvas and convert SVG to PNG
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const svgData = new XMLSerializer().serializeToString(svgElement);
      const img = new Image();

      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);

        canvas.toBlob((blob) => {
          if (blob) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${title || 'c4-diagram'}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            antMessage.success('PNG downloaded');
          }
        });
      };

      img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    } catch (err) {
      antMessage.error('Failed to download PNG');
      console.error('PNG download error:', err);
    }
  };

  const handleExpand = () => {
    const svgElement = containerRef.current?.querySelector('svg');
    if (!svgElement) return;

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);

    window.open(url, '_blank');
  };

  return (
    <Card
      title={
        <Space>
          <span>{title || 'C4 Diagram'}</span>
          <Tag color="purple">C4 {c4Level}</Tag>
          <Tag color="blue">Rendered with D2</Tag>
        </Space>
      }
      size="small"
      style={{ marginTop: 16 }}
      extra={
        <Space>
          <Button
            icon={<CopyOutlined />}
            size="small"
            onClick={handleCopy}
            title="Copy C4 source code to clipboard"
          >
            Copy C4
          </Button>
          <Button
            icon={<CodeOutlined />}
            size="small"
            onClick={() => setShowD2Code(!showD2Code)}
            title="Show/hide generated D2 code"
          >
            {showD2Code ? 'Hide' : 'Show'} D2
          </Button>
          {showD2Code && (
            <Button
              icon={<CopyOutlined />}
              size="small"
              onClick={handleCopyD2}
              title="Copy generated D2 code to clipboard"
            >
              Copy D2
            </Button>
          )}
          <Button
            icon={<DownloadOutlined />}
            size="small"
            onClick={handleDownloadSVG}
            title="Download as SVG vector image"
          >
            SVG
          </Button>
          <Button
            icon={<DownloadOutlined />}
            size="small"
            onClick={handleDownloadPNG}
            title="Download as PNG raster image"
            type="primary"
          >
            PNG
          </Button>
          <Button
            icon={<ExpandOutlined />}
            size="small"
            onClick={handleExpand}
            title="Open diagram in new tab"
          />
        </Space>
      }
    >
      {isRendering && (
        <div style={{ padding: 20, textAlign: 'center', color: '#999' }}>
          Rendering C4 diagram using D2...
        </div>
      )}

      {error && (
        <div style={{ padding: 20, color: '#ff4d4f', backgroundColor: '#fff2f0', borderRadius: 4 }}>
          <strong>Error rendering C4 diagram:</strong>
          <pre style={{ marginTop: 8, fontSize: 12 }}>{error}</pre>
          <details style={{ marginTop: 12, fontSize: 12 }}>
            <summary style={{ cursor: 'pointer' }}>Show C4 source code</summary>
            <pre style={{ marginTop: 8, backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4 }}>
              {code}
            </pre>
          </details>
          {d2Code && (
            <details style={{ marginTop: 12, fontSize: 12 }}>
              <summary style={{ cursor: 'pointer' }}>Show converted D2 code</summary>
              <pre style={{ marginTop: 8, backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4 }}>
                {d2Code}
              </pre>
            </details>
          )}
        </div>
      )}

      {showD2Code && d2Code && !error && (
        <div style={{ padding: 12, backgroundColor: '#f5f5f5', borderRadius: 4, marginBottom: 12 }}>
          <strong>Generated D2 Code:</strong>
          <pre style={{
            marginTop: 8,
            fontSize: 11,
            backgroundColor: '#1e293b',
            color: '#e2e8f0',
            padding: 12,
            borderRadius: 4,
            overflow: 'auto',
            maxHeight: 200
          }}>
            {d2Code}
          </pre>
        </div>
      )}

      {!isRendering && !error && (
        <div
          ref={containerRef}
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: '20px',
            overflow: 'auto',
          }}
        />
      )}
    </Card>
  );
};
