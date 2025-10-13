import React, { useEffect, useRef, useState } from 'react';
import { Card, Button, Space, message as antMessage } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined } from '@ant-design/icons';
import { D2 } from '@terrastruct/d2';
import { ApiService } from '../../services/api';
import { validateAndCorrectD2Syntax, looksLikeValidD2 } from '../../utils/d2SyntaxValidator';

interface D2DiagramProps {
  code: string;
  title?: string;
}

export const D2Diagram: React.FC<D2DiagramProps> = ({ code, title }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [svgContent, setSvgContent] = useState<string>('');
  const [validationResult, setValidationResult] = useState<any>(null);

  useEffect(() => {
    const renderDiagram = async () => {
      if (!containerRef.current || !code) {
        console.log('🎯 [D2 DIAGRAM] Skipping render - no container or code');
        return;
      }

      console.log('🎯 [D2 DIAGRAM] Starting D2 diagram render', {
        codeLength: code.length,
        codePreview: code.substring(0, 100) + '...',
        hasContainer: !!containerRef.current,
        codeLines: code.split('\n').length
      });
      
      // DEBUG: Log the full D2 code for syntax analysis
      console.log('🔍 [D2 DEBUG] Full D2 code:', code);
      
      // DEBUG: Check for common syntax issues
      const lines = code.split('\n');
      const openBraces = (code.match(/{/g) || []).length;
      const closeBraces = (code.match(/}/g) || []).length;
      const hasUnclosedBraces = openBraces !== closeBraces;
      
      console.log('🔍 [D2 DEBUG] Syntax analysis:', {
        openBraces,
        closeBraces,
        hasUnclosedBraces,
        linesWithBraces: lines.filter(line => line.includes('{') || line.includes('}')).map((line, idx) => `${idx + 1}: ${line.trim()}`)
      });
      // Log render start to backend
      ApiService.logDiagramEvent({
        event_type: 'render_start',
        diagram_type: 'd2',
        code_length: code.length,
        code_preview: code.substring(0, 100)
      });
      setIsRendering(true);
      setError(null);

      try {
        // Validate D2 code is not empty
        if (!code || code.trim().length === 0) {
          throw new Error('D2 diagram code is empty. Please provide valid D2 syntax.');
        }

        // Validate and correct D2 syntax
        console.log('🔧 [D2 DIAGRAM] Validating and correcting D2 syntax...');
        const validation = validateAndCorrectD2Syntax(code);
        setValidationResult(validation);
        
        if (!validation.isValid) {
          console.warn('⚠️ [D2 DIAGRAM] Syntax validation failed, but attempting to render with corrections');
          console.warn('⚠️ [D2 DIAGRAM] Validation errors:', validation.errors);
        }
        
        if (validation.corrections.length > 0) {
          console.log('✅ [D2 DIAGRAM] Applied syntax corrections:', validation.corrections);
        }
        
        const codeToRender = validation.correctedCode;
        
        // Quick validation to check if the corrected code looks reasonable
        if (!looksLikeValidD2(codeToRender)) {
          throw new Error(
            `D2 syntax validation failed. The code appears to be invalid D2 syntax.\n\n` +
            `Validation errors:\n${validationResult.errors.join('\n')}\n\n` +
            `Corrections attempted:\n${validationResult.corrections.join('\n')}\n\n` +
            `Please check the D2 code and ensure it follows proper D2 syntax.`
          );
        }

        // Create D2 instance
        const d2 = new D2();
        console.log('🎯 [D2 DIAGRAM] D2 instance created, compiling...');

        // Compile D2 code with options
        let result;
        try {
          result = await d2.compile(codeToRender, {
            options: {
              layout: 'dagre', // Use dagre layout (works client-side)
              sketch: false,
            }
          });
          console.log('🎯 [D2 DIAGRAM] Compilation successful, rendering SVG...');
        } catch (compileError) {
          // DEBUG: Enhanced error logging
          console.error('🔍 [D2 DEBUG] Compilation error details:', {
            error: compileError,
            errorMessage: compileError instanceof Error ? compileError.message : 'Unknown error',
            errorStack: compileError instanceof Error ? compileError.stack : 'No stack trace',
            originalCode: code,
            correctedCode: codeToRender,
            corrections: validation.corrections,
            validationErrors: validation.errors,
            codeLines: codeToRender.split('\n').map((line, idx) => `${idx + 1}: ${line}`)
          });
          
          throw new Error(
            `D2 compilation failed: ${compileError instanceof Error ? compileError.message : 'Unknown error'}.\n\n` +
            `This usually means the D2 code has syntax errors. ` +
            `Common issues:\n` +
            `- Missing colons after node names (e.g., "node: label")\n` +
            `- Incorrect arrow syntax (use -> for connections)\n` +
            `- Unmatched braces { }\n` +
            `- Invalid property names\n\n` +
            `Please check the D2 code below for these issues.`
          );
        }

        // Render the compiled diagram to SVG
        let svg;
        try {
          svg = await d2.render(result.diagram, result.renderOptions);
          console.log('🎯 [D2 DIAGRAM] SVG rendered successfully', {
            svgLength: svg.length
          });
        } catch (renderError) {
          throw new Error(
            `D2 rendering failed: ${renderError instanceof Error ? renderError.message : 'Unknown error'}.\n\n` +
            `The diagram compiled successfully but could not be rendered to SVG. ` +
            `This is usually due to layout engine issues or complex diagram structures.`
          );
        }

        // Store SVG content for export
        setSvgContent(svg);

        // Insert the SVG into the container
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          console.log('🎯 [D2 DIAGRAM] SVG inserted into DOM');
        }

        // Show notification if corrections were applied
        if (validation.corrections.length > 0) {
          antMessage.success(
            `D2 diagram rendered successfully with ${validation.corrections.length} syntax correction(s)`,
            4
          );
        }

        // Log render success to backend
        ApiService.logDiagramEvent({
          event_type: 'render_success',
          diagram_type: 'd2',
          code_length: code.length,
          corrections_applied: validation.corrections.length
        });
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to render D2 diagram: Unknown error';
        console.error('❌ [D2 DIAGRAM] Rendering error:', err);
        setError(errorMessage);

        // Log render error to backend
        ApiService.logDiagramEvent({
          event_type: 'render_error',
          diagram_type: 'd2',
          error_message: errorMessage,
          code_length: code.length,
          code_preview: code.substring(0, 100)
        });
      } finally {
        setIsRendering(false);
        console.log('🎯 [D2 DIAGRAM] Render process finished');
      }
    };

    renderDiagram();
  }, [code]);

  const handleCopy = async () => {
    try {
      const codeToCopy = validationResult?.correctedCode || code;
      await navigator.clipboard.writeText(codeToCopy);
      
      if (validationResult && validationResult.corrections.length > 0) {
        antMessage.success(`D2 diagram code copied to clipboard (${validationResult.corrections.length} corrections applied)`);
      } else {
        antMessage.success('D2 diagram code copied to clipboard');
      }
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
      title={title || 'D2 Diagram'}
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
          Rendering D2 diagram...
        </div>
      )}

      {error && (
        <div style={{ padding: 20, color: '#ff4d4f', backgroundColor: '#fff2f0', borderRadius: 4 }}>
          <strong>Error rendering D2 diagram:</strong>
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
