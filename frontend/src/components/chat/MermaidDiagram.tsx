import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Card, Button, Space, message as antMessage } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined } from '@ant-design/icons';
import { ApiService } from '../../services/api';

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

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current || !code) {
        console.log('🎨 [MERMAID DIAGRAM] Skipping render - no container or code');
        return;
      }

      console.log('🎨 [MERMAID DIAGRAM] Starting Mermaid diagram render', {
        codeLength: code.length,
        codePreview: code.substring(0, 50) + '...',
        hasContainer: !!containerRef.current
      });
      // Log render start to backend
      ApiService.logDiagramEvent({
        event_type: 'render_start',
        diagram_type: 'mermaid',
        code_length: code.length,
        code_preview: code.substring(0, 100)
      });
      setIsRendering(true);
      setError(null);

      try {
        // Pre-validate: Use Mermaid's parse function to check if the syntax is valid
        // This prevents rendering invalid diagrams that would throw errors
        try {
          await mermaid.parse(code);
          setIsValid(true); // Mark as valid
          console.log('🎨 [MERMAID DIAGRAM] Syntax validation passed');
        } catch (parseError) {
          // If parse fails, this is not valid Mermaid syntax - fail silently
          console.warn('⚠️ [MERMAID DIAGRAM] Parse failed (invalid syntax, skipping render):', parseError);
          setIsValid(false); // Mark as invalid
          setIsRendering(false);
          return; // Don't render, don't show error - just skip it
        }

        // Generate unique ID for this diagram
        const id = `mermaid-${Math.random().toString(36).substring(2, 11)}`;
        console.log('🎨 [MERMAID DIAGRAM] Rendering with ID:', id);

        // Render the diagram (only if parse succeeded)
        const { svg } = await mermaid.render(id, code);
        console.log('🎨 [MERMAID DIAGRAM] SVG rendered successfully', {
          svgLength: svg.length
        });

        // Store SVG content for export
        setSvgContent(svg);

        // Insert the SVG into the container
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          console.log('🎨 [MERMAID DIAGRAM] SVG inserted into DOM');
        }

        // Log render success to backend
        ApiService.logDiagramEvent({
          event_type: 'render_success',
          diagram_type: 'mermaid',
          code_length: code.length
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to render diagram';
        setError(errorMessage);
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
  }, [code]);

  // If diagram is invalid, don't render anything (fail silently)
  if (isValid === false) {
    return null;
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      antMessage.success('Diagram code copied to clipboard');
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

  return (
    <Card
      title={title || 'Mermaid Diagram'}
      size="small"
      style={{ marginTop: 16 }}
      extra={
        <Space>
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
          <details style={{ marginTop: 12, fontSize: 12 }}>
            <summary style={{ cursor: 'pointer' }}>Show diagram code</summary>
            <pre style={{ marginTop: 8, backgroundColor: '#f5f5f5', padding: 8, borderRadius: 4 }}>
              {code}
            </pre>
          </details>
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