/**
 * Headless Diagram Renderer Page
 *
 * This page is designed for headless rendering via Playwright.
 * It accepts URL parameters and renders diagrams without any UI chrome.
 *
 * URL Parameters:
 * - type: 'mermaid' | 'd2' | 'c4'
 * - code: URL-encoded diagram code
 *
 * Example: /render?type=mermaid&code=flowchart%20TD%0A%20%20%20%20A%5BStart%5D
 */

import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import mermaid from 'mermaid';
import { D2 } from '@terrastruct/d2';
import { convertC4ToD2 } from '../utils/c4ToD2';

// Initialize Mermaid
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
});

export const DiagramRenderer = () => {
  const [searchParams] = useSearchParams();
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(true);

  useEffect(() => {
    const renderDiagram = async () => {
      try {
        // Get parameters
        const type = searchParams.get('type') || 'mermaid';
        const code = searchParams.get('code');

        if (!code) {
          throw new Error('No diagram code provided');
        }

        console.log('🎨 Rendering diagram:', { type, codeLength: code.length });

        let svg = '';

        if (type === 'mermaid') {
          // Render Mermaid
          await mermaid.parse(code);
          const id = `mermaid-${Date.now()}`;
          const result = await mermaid.render(id, code);
          svg = result.svg;
          console.log('✅ Mermaid rendered');
        } else if (type === 'd2') {
          // Render D2
          const d2 = new D2();
          const result = await d2.compile(code, {
            options: {
              layout: 'dagre',
              sketch: false,
            }
          });
          svg = await d2.render(result.diagram, result.renderOptions);
          console.log('✅ D2 rendered');
        } else if (type === 'c4') {
          // Convert C4 to D2, then render
          console.log('🏗️ Converting C4 to D2...');
          const d2Code = convertC4ToD2(code);
          const d2 = new D2();
          const result = await d2.compile(d2Code, {
            options: {
              layout: 'dagre',
              sketch: false,
            }
          });
          svg = await d2.render(result.diagram, result.renderOptions);
          console.log('✅ C4 converted and rendered');
        } else {
          throw new Error(`Unknown diagram type: ${type}`);
        }

        // Insert SVG
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
          console.log('✅ SVG inserted into DOM');
        }

        // Mark as complete for Playwright
        document.body.classList.add('render-complete');
        setIsRendering(false);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        console.error('❌ Rendering error:', err);
        setError(errorMessage);
        document.body.classList.add('render-error');
        setIsRendering(false);
      }
    };

    renderDiagram();
  }, [searchParams]);

  if (isRendering) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        color: '#666',
        fontSize: '18px',
      }}>
        Rendering diagram...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: '20px',
        background: '#fff2f0',
        border: '1px solid #ffccc7',
        borderRadius: '4px',
        color: '#cf1322',
        maxWidth: '800px',
        margin: '20px auto',
      }}>
        <h3 style={{ marginBottom: '10px' }}>Rendering Error</h3>
        <pre style={{
          background: '#f5f5f5',
          padding: '10px',
          borderRadius: '4px',
          overflow: 'auto',
          fontSize: '12px',
        }}>
          {error}
        </pre>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        padding: '20px',
      }}
    />
  );
};
