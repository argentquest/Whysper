import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Card, Button, Space, message as antMessage, Tooltip, Tag } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined, ZoomInOutlined, ZoomOutOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { ApiService } from '../../services/api';
import { validateAndCorrectMermaidSyntax, looksLikeValidMermaid } from '../../utils/mermaidSyntaxValidator';
import diagramProviderService from '../../services/diagramProviderService';
import type { ProviderInfo, DiagramRenderResponse } from '../../services/diagramProviderService';

interface MermaidDiagramProps {
  code: string;
  title?: string;
}

// Initialize mermaid with configuration
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'Arial, sans-serif',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
  },
  sequence: {
    useMaxWidth: true,
  },
  gantt: {
    useMaxWidth: true,
  },
});

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({ code, title }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null); // null = checking, true = valid, false = invalid
  const [svgContent, setSvgContent] = useState<string>('');
  const [validationResult, setValidationResult] = useState<any>(null);
  const [renderKey, setRenderKey] = useState(0); // Force re-render trigger
  const [zoom, setZoom] = useState(1); // Zoom level (1 = 100%)
  const [pan, setPan] = useState({ x: 0, y: 0 }); // Pan position
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [providerInfo, setProviderInfo] = useState<ProviderInfo | null>(null);
  const [renderResult, setRenderResult] = useState<DiagramRenderResponse | null>(null);

  // Get provider info on mount
  useEffect(() => {
    const fetchProviderInfo = async () => {
      try {
        const info = await diagramProviderService.getProviderInfo('mermaid');
        setProviderInfo(info);
        console.log('🎨 [MERMAID DIAGRAM] Provider info loaded:', info.provider_name);
      } catch (err) {
        console.warn('🎨 [MERMAID DIAGRAM] Failed to get provider info:', err);
      }
    };
    fetchProviderInfo();
  }, []);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current || !code) {
        console.log('🎨 [MERMAID DIAGRAM] Skipping render - no container or code');
        return;
      }

      console.log('🎨 [MERMAID DIAGRAM] Starting Mermaid diagram render via provider', {
        codeLength: code.length,
        codePreview: code.substring(0, 50) + '...',
        provider: providerInfo?.provider_id || 'mermaidv1'
      });

      // Log render start to backend
      ApiService.logDiagramEvent({
        event_type: 'render_start',
        diagram_type: 'mermaid',
        code_length: code.length,
        code_preview: code.substring(0, 100),
        provider: providerInfo?.provider_id || 'mermaidv1'
      });

      setIsRendering(true);
      setError(null);

      try {
        // Validate using provider service (with auto-fix)
        console.log('🔧 [MERMAID DIAGRAM] Validating via provider service...');
        const validationResponse = await diagramProviderService.validate({
          code,
          diagram_type: 'mermaid',
          auto_fix: true
        });

        console.log('🎨 [MERMAID DIAGRAM] Validation result:', {
          is_valid: validationResponse.is_valid,
          auto_fixed: validationResponse.auto_fixed,
          llm_corrected: validationResponse.llm_corrected
        });

        // Use fixed code if available, otherwise use original
        const codeToRender = validationResponse.fixed_code || code;

        // Still do client-side parse check as fallback
        try {
          await mermaid.parse(codeToRender);
          setIsValid(true);
          console.log('🎨 [MERMAID DIAGRAM] Client-side parse validation passed');
        } catch (parseError) {
          // If client-side parse fails, still try with backend rendering
          console.warn('⚠️ [MERMAID DIAGRAM] Client-side parse failed, attempting backend render:', parseError);
        }

        // Render using backend provider (which will use mermaid.js CLI or similar)
        console.log('🎨 [MERMAID DIAGRAM] Rendering via backend provider...');
        const renderResponse = await diagramProviderService.render({
          code: codeToRender,
          diagram_type: 'mermaid',
          output_format: 'svg'
        });

        setRenderResult(renderResponse);

        if (renderResponse.success && renderResponse.content) {
          setSvgContent(renderResponse.content);
          setIsValid(true);

          console.log('🎨 [MERMAID DIAGRAM] SVG rendered successfully via provider', {
            provider: renderResponse.metadata.provider_id,
            renderTime: renderResponse.metadata.render_time,
            svgLength: renderResponse.content.length
          });

          // Show notification if auto-fixed
          if (validationResponse.auto_fixed) {
            antMessage.success(
              `Mermaid diagram rendered successfully (${validationResponse.correction_method})`,
              4
            );
          }

          // Log render success to backend
          ApiService.logDiagramEvent({
            event_type: 'render_success',
            diagram_type: 'mermaid',
            code_length: code.length,
            provider: renderResponse.metadata.provider_id,
            render_time: renderResponse.metadata.render_time
          });
        } else {
          const errorMsg = renderResponse.error || 'Rendering failed';
          setError(errorMsg);
          setIsValid(false);

          ApiService.logDiagramEvent({
            event_type: 'render_error',
            diagram_type: 'mermaid',
            error_message: errorMsg,
            code_length: code.length
          });
        }
      } catch (err) {
        let errorMessage = err instanceof Error ? err.message : 'Failed to render diagram';

        setError(errorMessage);
        setIsValid(false);
        console.error('❌ [MERMAID DIAGRAM] Rendering error:', err);

        // Log render error to backend
        ApiService.logDiagramEvent({
          event_type: 'render_error',
          diagram_type: 'mermaid',
          error_message: errorMessage,
          code_length: code.length,
          code_preview: code.substring(0, 100)
        });
      } finally {
        setIsRendering(false);
        console.log('🎨 [MERMAID DIAGRAM] Render process finished');
      }
    };

    renderDiagram();
  }, [code, renderKey]); // Re-render when code OR renderKey changes

  // Monitor container visibility and size changes to trigger re-render
  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new ResizeObserver(() => {
      // Trigger re-render when container size changes (e.g., fullscreen toggle)
      console.log('🎨 [MERMAID DIAGRAM] Container resized, triggering re-render');
      setRenderKey(prev => prev + 1);
    });

    observer.observe(containerRef.current);

    return () => observer.disconnect();
  }, []);

  // If diagram is invalid, don't render anything (fail silently)
  if (isValid === false) {
    return null;
  }

  const handleCopy = async () => {
    try {
      // Try to copy the fixed/rendered code if available
      const codeToCopy = renderResult?.metadata?.code_length
        ? svgContent || code
        : code;
      await navigator.clipboard.writeText(codeToCopy);

      antMessage.success('Mermaid diagram code copied to clipboard');
    } catch (err) {
      antMessage.error('Failed to copy code');
    }
  };

  const handleDownloadSVG = () => {
    try {
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${title || 'diagram'}.svg`;
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
            link.download = `${title || 'diagram'}.png`;
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

  // Zoom controls
  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3)); // Max 300%
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.25)); // Min 25%
  };

  const handleResetZoom = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Pan controls
  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom === 1) return; // Only allow panning when zoomed
    setIsPanning(true);
    setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan({ x: e.clientX - startPan.x, y: e.clientY - startPan.y });
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  // Mouse wheel zoom
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom(prev => Math.max(0.25, Math.min(3, prev + delta)));
  };

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>{title || 'Mermaid Diagram'}</span>
          {renderResult && (
            <>
              <Tag icon={<CheckCircleOutlined />} color="green">
                {renderResult.metadata.provider_name}
              </Tag>
              <Tag>
                {renderResult.metadata.render_time?.toFixed(0)}ms
              </Tag>
            </>
          )}
        </div>
      }
      size="small"
      style={{ marginTop: 16 }}
      extra={
        <Space>
          <Tooltip title={`Zoom: ${Math.round(zoom * 100)}%`}>
            <Space.Compact size="small">
              <Button
                icon={<ZoomOutOutlined />}
                size="small"
                onClick={handleZoomOut}
                disabled={zoom <= 0.25}
              />
              <Button
                size="small"
                onClick={handleResetZoom}
                style={{ minWidth: 50 }}
              >
                {Math.round(zoom * 100)}%
              </Button>
              <Button
                icon={<ZoomInOutlined />}
                size="small"
                onClick={handleZoomIn}
                disabled={zoom >= 3}
              />
            </Space.Compact>
          </Tooltip>
          <Button
            icon={<CopyOutlined />}
            size="small"
            onClick={handleCopy}
            title="Copy diagram code to clipboard"
          >
            Copy
          </Button>
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
          Rendering diagram...
        </div>
      )}

      {error && (
        <div style={{ padding: 20, color: '#ff4d4f', backgroundColor: '#fff2f0', borderRadius: 4 }}>
          <strong>Error rendering diagram:</strong>
          <pre style={{ marginTop: 8, fontSize: 12 }}>{error}</pre>
          
          {validationResult && validationResult.corrections.length > 0 && (
            <div style={{ marginTop: 12, padding: 8, backgroundColor: '#fff7e6', borderRadius: 4 }}>
              <strong>Applied corrections:</strong>
              <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
                {validationResult.corrections.map((correction: string, idx: number) => (
                  <li key={idx} style={{ fontSize: 12 }}>{correction}</li>
                ))}
              </ul>
            </div>
          )}
          
          {validationResult && validationResult.warnings.length > 0 && (
            <div style={{ marginTop: 12, padding: 8, backgroundColor: '#f6ffed', borderRadius: 4 }}>
              <strong>Warnings:</strong>
              <ul style={{ margin: '8px 0', paddingLeft: 20 }}>
                {validationResult.warnings.map((warning: string, idx: number) => (
                  <li key={idx} style={{ fontSize: 12 }}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
          
          <details style={{ marginTop: 12, fontSize: 12 }}>
            <summary style={{ cursor: 'pointer' }}>Show original diagram code</summary>
            <pre style={{ marginTop: 8, backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4 }}>
              {code}
            </pre>
          </details>
          
          {validationResult && validationResult.correctedCode !== code && (
            <details style={{ marginTop: 8, fontSize: 12 }}>
              <summary style={{ cursor: 'pointer' }}>Show corrected diagram code</summary>
              <pre style={{ marginTop: 8, backgroundColor: '#f6ffed', padding: 8, borderRadius: 4 }}>
                {validationResult.correctedCode}
              </pre>
            </details>
          )}
        </div>
      )}

      {!isRendering && !error && (
        <div
          style={{
            position: 'relative',
            overflow: 'hidden',
            cursor: zoom > 1 ? (isPanning ? 'grabbing' : 'grab') : 'default',
            background: '#f5f5f5',
            borderRadius: '4px',
            minHeight: '200px',
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          <div
            ref={containerRef}
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              padding: '20px',
              transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
              transformOrigin: 'center center',
              transition: isPanning ? 'none' : 'transform 0.1s ease-out',
            }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
          {zoom > 1 && (
            <div
              style={{
                position: 'absolute',
                bottom: '10px',
                right: '10px',
                background: 'rgba(0, 0, 0, 0.7)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '12px',
                pointerEvents: 'none',
              }}
            >
              Click and drag to pan • Scroll to zoom
            </div>
          )}
        </div>
      )}
    </Card>
  );
};