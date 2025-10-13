import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { Card, Button, Space, message as antMessage } from 'antd';
import { CopyOutlined, DownloadOutlined, ExpandOutlined } from '@ant-design/icons';
import { ApiService } from '../../services/api';
import { validateAndCorrectMermaidSyntax, looksLikeValidMermaid } from '../../utils/mermaidSyntaxValidator';

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
        // Validate and correct Mermaid syntax
        console.log('🔧 [MERMAID DIAGRAM] Validating and correcting Mermaid syntax...');
        const validation = validateAndCorrectMermaidSyntax(code);
        setValidationResult(validation);
        
        if (!validation.isValid) {
          console.warn('⚠️ [MERMAID DIAGRAM] Syntax validation failed, but attempting to render with corrections');
          console.warn('⚠️ [MERMAID DIAGRAM] Validation errors:', validation.errors);
        }
        
        if (validation.corrections.length > 0) {
          console.log('✅ [MERMAID DIAGRAM] Applied syntax corrections:', validation.corrections);
        }
        
        if (validation.warnings.length > 0) {
          console.log('⚠️ [MERMAID DIAGRAM] Potential issues:', validation.warnings);
        }
        
        const codeToRender = validation.correctedCode;
        
        // Quick validation to check if the corrected code looks reasonable
        if (!looksLikeValidMermaid(codeToRender)) {
          throw new Error(
            `Mermaid syntax validation failed. The code appears to be invalid Mermaid syntax.\n\n` +
            `Validation errors:\n${validation.errors.join('\n')}\n\n` +
            `Corrections attempted:\n${validation.corrections.join('\n')}\n\n` +
            `Please check the Mermaid code and ensure it follows proper Mermaid syntax.`
          );
        }

        // Pre-validate: Use Mermaid's parse function to check if the syntax is valid
        // This prevents rendering invalid diagrams that would throw errors
        try {
          await mermaid.parse(codeToRender);
          setIsValid(true); // Mark as valid
          console.log('🎨 [MERMAID DIAGRAM] Syntax validation passed');
        } catch (parseError) {
          // If parse fails, this is not valid Mermaid syntax - fail silently
          console.warn('⚠️ [MERMAID DIAGRAM] Parse failed (invalid syntax, skipping render):', parseError);
          console.error('🔍 [MERMAID DEBUG] Parse error details:', {
            error: parseError,
            errorMessage: parseError instanceof Error ? parseError.message : 'Unknown error',
            originalCode: code,
            correctedCode: codeToRender,
            corrections: validation.corrections,
            validationErrors: validation.errors,
            codeLines: codeToRender.split('\n').map((line, idx) => `${idx + 1}: ${line}`)
          });
          setIsValid(false); // Mark as invalid
          setIsRendering(false);
          return; // Don't render, don't show error - just skip it
        }

        // Generate unique ID for this diagram
        const id = `mermaid-${Math.random().toString(36).substring(2, 11)}`;
        console.log('🎨 [MERMAID DIAGRAM] Rendering with ID:', id);

        // Render the diagram (only if parse succeeded)
        const { svg } = await mermaid.render(id, codeToRender);
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

        // Show notification if corrections were applied
        if (validation.corrections.length > 0) {
          antMessage.success(
            `Mermaid diagram rendered successfully with ${validation.corrections.length} syntax correction(s)`,
            4
          );
        }

        // Show warnings if any
        if (validation.warnings.length > 0) {
          console.warn('⚠️ [MERMAID DIAGRAM] Rendering completed with warnings:', validation.warnings);
        }

        // Log render success to backend
        ApiService.logDiagramEvent({
          event_type: 'render_success',
          diagram_type: 'mermaid',
          code_length: code.length,
          corrections_applied: validation.corrections.length,
          warnings: validation.warnings.length
        });
      } catch (err) {
        let errorMessage = err instanceof Error ? err.message : 'Failed to render diagram';

        // Provide more helpful error messages
        if (errorMessage.includes('Parse error') || errorMessage.includes('syntax')) {
          errorMessage = `Mermaid syntax error: ${errorMessage}\n\n` +
            `Common issues:\n` +
            `- Missing diagram type declaration (e.g., "graph TD", "sequenceDiagram")\n` +
            `- Incorrect arrow syntax (check Mermaid documentation)\n` +
            `- Invalid node definitions or labels\n` +
            `- Missing quotes around special characters\n\n` +
            `Please check the Mermaid code below for these issues.`;
        } else if (errorMessage.includes('Lexical error')) {
          errorMessage = `Mermaid lexical error: ${errorMessage}\n\n` +
            `This usually means there are unexpected characters in your diagram code. ` +
            `Check for typos or invalid syntax.`;
        }

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
      const codeToCopy = validationResult?.correctedCode || code;
      await navigator.clipboard.writeText(codeToCopy);
      
      if (validationResult && validationResult.corrections.length > 0) {
        antMessage.success(`Mermaid diagram code copied to clipboard (${validationResult.corrections.length} corrections applied)`);
      } else {
        antMessage.success('Mermaid diagram code copied to clipboard');
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