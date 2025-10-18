import React, { useRef, useEffect, useState } from 'react';
import { Card, Button, Typography, Tooltip, Avatar, Dropdown, Modal, App } from 'antd';
import {
  ExpandOutlined,
  CompressOutlined,
  CopyOutlined,
  CodeOutlined,
  FileTextOutlined,
  Html5Outlined,
  UserOutlined,
  RobotOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  PrinterOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types';
import { MermaidDiagram } from './MermaidDiagram';
import { D2DiagramBackend } from './D2DiagramBackend';
import { C4Diagram } from './C4Diagram';
import {
  isMermaidSyntax,
  prepareMermaidCode,
  isMermaidCode,
  isD2Syntax,
  prepareD2Code,
  isC4Syntax,
  prepareC4Code,
  isC4Code,
  processMixedHtmlContent
} from '../../utils/mermaidUtils';
import { useTheme } from '../../themes';


// Function to print the visual output of a message element
const printMessageElement = (messageId: string, fullContent: string) => {
  // Find the message element by ID
  const messageElement = document.getElementById(`message-${messageId}`);
  
  if (!messageElement) {
    console.error(`Message element with ID message-${messageId} not found`);
    return;
  }
  
  // Create a unique ID for this print session
  const printId = `print-${messageId}-${Date.now()}`;
  
  // Create a new iframe for printing
  const printFrame = document.createElement('iframe');
  printFrame.id = printId;
  printFrame.style.position = 'absolute';
  printFrame.style.left = '-9999px';
  printFrame.style.top = '-9999px';
  document.body.appendChild(printFrame);
  
  // Get the iframe document
  const frameDoc = printFrame.contentWindow || printFrame.contentDocument.document;
  
  // Clone the message content
  const messageContent = messageElement.querySelector('.message-content');
  if (!messageContent) {
    console.error('Message content element not found');
    document.body.removeChild(printFrame);
    return;
  }
  
  const clonedContent = messageContent.cloneNode(true);
  
  // Expand all collapsible elements in the cloned content
  const detailsElements = clonedContent.querySelectorAll('details');
  detailsElements.forEach(details => {
    details.setAttribute('open', '');
  });
  
  // Write the content to the iframe with the full content
  frameDoc.document.open();
  frameDoc.document.write(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Whysper AI Response</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          line-height: 1.6;
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          color: #333;
        }
        pre {
          background: #f4f4f4;
          padding: 10px;
          border-radius: 5px;
          overflow-x: auto;
          white-space: pre-wrap;
        }
        code {
          background: #f4f4f4;
          padding: 2px 4px;
          border-radius: 3px;
        }
        h1, h2, h3 { color: #333; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { border-bottom: 1px solid #eee; padding-bottom: 5px; }
        img { max-width: 100%; height: auto; }
        details { margin-bottom: 16px; }
        summary {
          font-weight: 500;
          padding: 8px 12px;
          background-color: #f1f5f9;
          border: 1px solid #cbd5e1;
          border-radius: 6px;
          cursor: pointer;
        }
        @media print {
          body { margin: 0; padding: 10px; }
          .show-more-less { display: none; }
          summary {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
          }
        }
      </style>
    </head>
    <body>
      <h1>Whysper AI Response</h1>
      <div id="printed-content"></div>
    </body>
    </html>
  `);
  frameDoc.document.close();
  
  // Append the cloned content to the iframe
  const printedContent = frameDoc.document.getElementById('printed-content');
  printedContent.appendChild(clonedContent);
  
  // Wait for the content to load, then trigger print
  setTimeout(() => {
    printFrame.contentWindow.focus();
    printFrame.contentWindow.print();
    
    // Remove the iframe after printing
    setTimeout(() => {
      document.body.removeChild(printFrame);
    }, 1000);
  }, 500);
};

interface MessageItemProps {
  message: Message;
  onShowCode?: (code: string, language: string, title?: string) => void;
}

/**
 * Custom code component renderer for ReactMarkdown
 * Handles Mermaid diagrams, D2 diagrams, and regular code blocks
 */
const CodeComponentRenderer = (props: React.ComponentProps<'code'> & { inline?: boolean }) => {
  const { inline, className, children, ...rest } = props;
  const match = /language-(\w+)/.exec(className || '');
  const language = match ? match[1] : '';

  // Handle C4 diagrams (must check BEFORE Mermaid, as C4 keywords might be in Mermaid)
  // Supports: c4, c4diagram, plantuml (with C4 content), mermaid (with C4 content)
  const codeString = String(children);
  const isPlantUML = language === 'plantuml' || language === 'puml';
  const isC4Mermaid = language === 'mermaid' && isC4Syntax(codeString);
  const isC4PlantUML = isPlantUML && isC4Syntax(codeString);

  if (isC4Code(language, inline || false) || isC4Mermaid || isC4PlantUML) {
    const code = prepareC4Code(codeString);
    const diagramSource = isC4PlantUML ? 'PlantUML' : isC4Mermaid ? 'Mermaid' : 'C4';
    console.log(`🏗️ [DIAGRAM RENDER] Rendering C4 diagram from ${diagramSource} (using D2)`, {
      language,
      codeLength: code.length,
      codePreview: code.substring(0, 60) + '...'
    });
    return <C4Diagram code={code} title={`C4 Architecture Diagram (${diagramSource})`} />;
  }

  // Handle Mermaid diagrams
  if (isMermaidCode(language, inline || false)) {
    const code = prepareMermaidCode(String(children));
    console.log('🎨 [DIAGRAM RENDER] Rendering Mermaid diagram', {
      language,
      codeLength: code.length,
      codePreview: code.substring(0, 60) + '...'
    });
    return <MermaidDiagram code={code} title="Mermaid Diagram" />;
  }

  // Handle D2 diagrams
  if (isD2Code(language, inline || false)) {
    const code = prepareD2Code(String(children));
    console.log('🎯 [DIAGRAM RENDER] Rendering D2 diagram via backend', {
      language,
      codeLength: code.length,
      codePreview: code.substring(0, 60) + '...'
    });
    return <D2DiagramBackend code={code} title="D2 Diagram" />;
  }

  // Regular code blocks
  return !inline && match ? (
    <pre
      className={`${className || ''} bg-gray-50 border border-gray-200 p-4 rounded-lg overflow-x-auto`}
      style={{
        fontSize: '14px',
        lineHeight: '1.2',
        color: '#1e293b',
        backgroundColor: '#f8fafc'
      }}
    >
      <code className={className} style={{ color: '#1e293b' }} {...rest}>
        {children}
      </code>
    </pre>
  ) : (
    <code
      className={`${className || ''} bg-gray-100 px-2 py-1 rounded border`}
      style={{
        fontSize: '14px',
        color: '#dc2626',
        backgroundColor: '#f1f5f9',
        border: '1px solid #e2e8f0'
      }}
      {...rest}
    >
      {children}
    </code>
  );
};

/**
 * Process HTML content to detect and replace diagram code blocks with rendered diagrams
 * This handles cases where LLMs return HTML <pre><code> blocks instead of Markdown
 *
 * Supports:
 * - Mermaid diagrams
 * - D2 diagrams
 *
 * Strategy:
 * - First diagram block: Show as collapsible code (for copying)
 * - Second identical block: Render as diagram
 * - This matches LLM pattern: "Code" then "Rendered Diagram"
 */
// Type for tracking diagram occurrences
type DiagramOccurrence = {
  count: number;
  type: 'mermaid' | 'd2';
};

const processDiagramsInHTML = (htmlContent: string): React.ReactNode[] => {
  // Use enhanced detection for mixed HTML content
  const { originalHtml, diagrams } = processMixedHtmlContent(htmlContent);
  
  // If no diagrams detected, return original HTML
  if (diagrams.length === 0) {
    return [<div key="full" dangerouslySetInnerHTML={{ __html: originalHtml }} />];
  }

  // Process HTML with detected diagrams
  const parts: React.ReactNode[] = [];
  let diagramCount = 0;
  const diagramOccurrences = new Map<string, DiagramOccurrence>();


  // Process each detected diagram
  for (const diagram of diagrams) {
    const { code, type, confidence } = diagram;

    // Track occurrences for duplicate handling
    const existingEntry = diagramOccurrences.get(code);
    const occurrenceCount = existingEntry?.count || 0;
    diagramOccurrences.set(code, { count: occurrenceCount + 1, type });

    // Skip duplicate diagrams (only render the first occurrence)
    if (occurrenceCount > 0) {
      continue;
    }

    diagramCount++;

    // Render diagram directly by default with optional code view below
    const diagramLabel = type === 'mermaid' ? 'Mermaid' : 'D2';
    const confidenceIcon = confidence === 'high' ? '✅' : confidence === 'medium' ? '⚠️' : '❓';

    // Create the rendered diagram
    const diagramComponent = type === 'mermaid' ? (
      <MermaidDiagram
        key={`diagram-render-${diagramCount}-${type}`}
        code={code}
        title={`${diagramLabel} Diagram ${confidenceIcon}`}
      />
    ) : (
      <D2DiagramBackend
        key={`diagram-render-${diagramCount}-${type}`}
        code={code}
        title={`${diagramLabel} Diagram ${confidenceIcon}`}
      />
    );

    // Add the rendered diagram
    parts.push(diagramComponent);

    // Add optional collapsible code view below the diagram
    const codeBlock = (
      <details
        key={`diagram-code-${diagramCount}`}
        style={{
          marginTop: '8px',
          marginBottom: '16px'
        }}
      >
        <summary
          style={{
            cursor: 'pointer',
            padding: '8px 12px',
            backgroundColor: '#f1f5f9',
            border: '1px solid #cbd5e1',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 500,
            color: '#475569',
            userSelect: 'none'
          }}
        >
          📝 View {diagramLabel} Source Code (click to expand/copy)
        </summary>
        <pre
          style={{
            backgroundColor: '#1e293b',
            color: '#e2e8f0',
            padding: '16px',
            borderRadius: '0 0 6px 6px',
            border: '1px solid #cbd5e1',
            borderTop: 'none',
            overflowX: 'auto',
            fontSize: '13px',
            lineHeight: '1.2',
            marginTop: '0'
          }}
        >
          <code>{code}</code>
        </pre>
      </details>
    );

    parts.push(codeBlock);
  }

  // Also process remaining HTML for traditional <pre><code> blocks not caught by enhanced detection
  const codeBlockRegex = /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(originalHtml)) !== null) {
    // Add HTML before the code block
    if (match.index > lastIndex) {
      const beforeHtml = originalHtml.substring(lastIndex, match.index);
      if (beforeHtml.trim()) {
        parts.push(
          <div
            key={`html-${lastIndex}`}
            dangerouslySetInnerHTML={{ __html: beforeHtml }}
          />
        );
      }
    }

    // Extract and decode the code content
    const rawCode = match[1];
    const decodedMermaid = prepareMermaidCode(rawCode);
    const decodedD2 = prepareD2Code(rawCode);

    // Check if this is a diagram not already processed by enhanced detection
    const isMermaid = isMermaidSyntax(decodedMermaid);
    const isD2 = isD2Syntax(decodedD2);
    
    if (isMermaid || isD2) {
      const diagramType = isMermaid ? 'mermaid' : 'd2';
      const decodedCode = isMermaid ? decodedMermaid : decodedD2;
      
      // Check if we already processed this diagram
      const alreadyProcessed = diagrams.some(d => d.code === decodedCode && d.type === diagramType);
      
      if (!alreadyProcessed) {
        // This is a new diagram not caught by enhanced detection
        const existingEntry = diagramOccurrences.get(decodedCode);
        const occurrenceCount = existingEntry?.count || 0;
        diagramOccurrences.set(decodedCode, { count: occurrenceCount + 1, type: diagramType });

        if (occurrenceCount === 0) {
          // Show as collapsible code block
          diagramCount++;
          const diagramLabel = isMermaid ? 'Mermaid' : 'D2';
          
          parts.push(
            <details
              key={`fallback-diagram-code-${match.index}`}
              style={{
                marginTop: '8px',
                marginBottom: '8px'
              }}
            >
              <summary
                style={{
                  cursor: 'pointer',
                  padding: '8px 12px',
                  backgroundColor: '#f1f5f9',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 500,
                  color: '#475569',
                  userSelect: 'none'
                }}
              >
                📝 {diagramLabel} Code (click to view/copy)
              </summary>
              <pre
                style={{
                  backgroundColor: '#1e293b',
                  color: '#e2e8f0',
                  padding: '16px',
                  borderRadius: '0 0 6px 6px',
                  border: '1px solid #cbd5e1',
                  borderTop: 'none',
                  overflowX: 'auto',
                  fontSize: '13px',
                  lineHeight: '1.2',
                  marginTop: '0'
                }}
              >
                <code>{decodedCode}</code>
              </pre>
            </details>
          );
        } else {
          // Render as diagram
          parts.push(
            diagramType === 'mermaid' ? (
              <MermaidDiagram
                key={`fallback-diagram-render-${match.index}`}
                code={decodedCode}
                title="Mermaid Diagram"
              />
            ) : (
              <D2DiagramBackend
                key={`fallback-diagram-render-${match.index}`}
                code={decodedCode}
                title="D2 Diagram"
              />
            )
          );
        }
      }
    } else {
      // Not a diagram, render as regular code block
      parts.push(
        <pre
          key={`code-${match.index}`}
          style={{
            backgroundColor: '#f8fafc',
            padding: '16px',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            overflowX: 'auto',
            fontSize: '14px',
            lineHeight: '1.2'
          }}
        >
          <code dangerouslySetInnerHTML={{ __html: rawCode }} />
        </pre>
      );
    }

    lastIndex = match.index + match[0].length;
  }

  // Add remaining HTML after processing
  if (lastIndex < originalHtml.length) {
    const afterHtml = originalHtml.substring(lastIndex);
    if (afterHtml.trim()) {
      parts.push(
        <div
          key={`html-${lastIndex}`}
          dangerouslySetInnerHTML={{ __html: afterHtml }}
        />
      );
    }
  }

  // If no parts were created, return the original HTML with detected diagrams
  if (parts.length === 0) {
    return [<div key="full" dangerouslySetInnerHTML={{ __html: originalHtml }} />];
  }

  return parts;
};

const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onShowCode
}) => {
  const { theme } = useTheme();
  const { message: appMessage } = App.useApp();
  const renderMetadataStats = (
    metadata: Message['metadata'],
    options: { theme?: 'light' | 'dark' } = {}
  ) => {
    if (!metadata) {
      return null;
    }

    const {
      model,
      provider,
      tokens,
      inputTokens,
      outputTokens,
      cachedTokens,
      elapsedTime,
    } = metadata;

    const theme = options.theme ?? 'light';
    const isDark = theme === 'dark';

    const containerClass = isDark
      ? 'flex items-center gap-3 text-xs font-medium'
      : 'flex items-center gap-2 text-xs font-medium text-slate-500';

    const modelStyle = isDark
      ? { color: 'rgba(255, 255, 255, 0.95)', fontWeight: 600 }
      : { color: '#0f172a', fontWeight: 600 };

    const providerStyle = isDark
      ? { color: 'rgba(255, 255, 255, 0.8)' }
      : { color: '#334155' };

    const statTextStyle = isDark
      ? { color: 'rgba(255, 255, 255, 0.85)' }
      : { color: '#0f172a' };

    const stats: React.ReactNode[] = [];

    if (model) {
      stats.push(
        <span key="model" style={modelStyle}>
          {model}
        </span>
      );
    }

    if (provider) {
      stats.push(
        <Tooltip title="Provider" key="provider-tip">
          <span key="provider" style={providerStyle}>
            🛰️ {provider}
          </span>
        </Tooltip>
      );
    }

    if (tokens !== undefined) {
      stats.push(
        <Tooltip title="Total tokens" key="tokens-tip">
          <span key="tokens" style={statTextStyle}>
            🧮 {tokens}
          </span>
        </Tooltip>
      );
    }

    if (inputTokens !== undefined) {
      stats.push(
        <Tooltip title="Input (prompt) tokens" key="input-tip">
          <span key="input" style={statTextStyle}>
            📥 {inputTokens}
          </span>
        </Tooltip>
      );
    }

    if (outputTokens !== undefined) {
      stats.push(
        <Tooltip title="Output (completion) tokens" key="output-tip">
          <span key="output" style={statTextStyle}>
            📤 {outputTokens}
          </span>
        </Tooltip>
      );
    }

    if (cachedTokens !== undefined && cachedTokens > 0) {
      stats.push(
        <Tooltip title="Cached tokens" key="cached-tip">
          <span key="cached" style={statTextStyle}>
            ♻️ {cachedTokens}
          </span>
        </Tooltip>
      );
    }

    if (elapsedTime !== undefined) {
      stats.push(
        <Tooltip title="Elapsed time" key="elapsed-tip">
          <span key="elapsed" style={statTextStyle}>
            ⏱️ {elapsedTime.toFixed(2)}s
          </span>
        </Tooltip>
      );
    }

    if (stats.length === 0) {
      return null;
    }

    return (
      <div className={containerClass} style={{ flexWrap: 'wrap' }}>
        {stats.map((stat) => stat)}
      </div>
    );
  };

  const [isExpanded, setIsExpanded] = useState(true);
  const [showFullContent, setShowFullContent] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Detect HTML content to determine initial view mode
  const detectHtmlContent = (content: string): boolean => {
    // Only show HTML view for substantial HTML content, not just scattered tags
    
    // Check for HTML document structure or substantial HTML blocks
    const substantialHtmlPatterns = [
      /<html[\s>]/i,           // Full HTML document
      /<head[\s>]/i,           // HTML document head
      /<body[\s>]/i,           // HTML document body
      /<table[\s>][\s\S]*?<\/table>/i,  // Complete table
      /<ul[\s>][\s\S]*?<\/ul>/i,        // Complete unordered list
      /<ol[\s>][\s\S]*?<\/ol>/i,        // Complete ordered list
      /<div[\s>][\s\S]*?<\/div>/i,      // Complete div blocks
      /<pre[\s>][\s\S]*?<\/pre>/i,      // Complete pre blocks
      /<p[\s>][\s\S]*?<\/p>/i,          // Complete paragraph blocks
      /<span[\s>][\s\S]*?<\/span>/i,    // Complete span blocks
      /<h[1-6][\s>][\s\S]*?<\/h[1-6]>/i, // Complete heading blocks
    ];
    
    // Check if content has substantial HTML structure
    const hasSubstantialHtml = substantialHtmlPatterns.some(pattern => pattern.test(content));
    
    // Additional check: count HTML tags - only show if there are multiple structural tags
    const htmlTagCount = (content.match(/<\/?[a-zA-Z][^>]*>/g) || []).length;
    const hasMultipleTags = htmlTagCount >= 3; // Reduced threshold to 3 HTML tags
    
    // Check for HTML attributes which are strong indicators of HTML content
    const hasHtmlAttributes = /class\s*=|id\s*=|style\s*=|src\s*=|href\s*=|alt\s*=/i.test(content);
    
    // Check for HTML entities which indicate HTML content
    const hasHtmlEntities = /&[a-zA-Z]+;|&#\d+;/.test(content);
    
    // Check for self-closing HTML tags
    const hasSelfClosingTags = /<(br|hr|img|input|meta|link)[^>]*?\/?>/i.test(content);
    
    // Only show HTML view if there's substantial HTML structure OR multiple HTML tags OR other HTML indicators
    return hasSubstantialHtml || hasMultipleTags || hasHtmlAttributes || hasHtmlEntities || hasSelfClosingTags;
  };
  
  const hasHtmlContent = detectHtmlContent(message.content);
  const [viewMode, setViewMode] = useState<'markdown' | 'html'>(
    hasHtmlContent ? 'html' : 'markdown'
  );
  
  const isLongContent = message.content.length > 1000;
  const shouldTruncate = isLongContent && !showFullContent;
  const displayContent = shouldTruncate 
    ? message.content.substring(0, 1000) + '...' 
    : message.content;

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };


  const handleCopyContent = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy content:', err);
    }
  };

  const handlePrintContent = () => {
    Modal.confirm({
      title: 'Print Response',
      content: (
        <div>
          <p>This will open the browser's print dialog to print or save the response as PDF.</p>
          <p style={{ color: '#ff4d4f', fontWeight: 'bold' }}>
            ⚠️ Please note: For large responses with images, this operation may take up to 20 seconds.
          </p>
        </div>
      ),
      okText: 'Print',
      cancelText: 'Cancel',
      onOk: () => {
        // Show loading message
        const loadingMessage = appMessage.loading('Preparing response for printing...', 0);
        
        // Add a timeout to ensure the loading message is visible
        setTimeout(() => {
          printMessageElement(message.id, message.content);
          
          // Hide the loading message after a delay to give the print dialog time to appear
          setTimeout(() => {
            loadingMessage();
            appMessage.success('Print dialog opened. You can now print or save the response.');
          }, 2000);
        }, 500);
      },
    });
  };

  const detectCodeBlocks = (content: string) => {
    const matches = [];
    
    // 1. Detect markdown-style code blocks: ```language
    const markdownRegex = /```(\w+)?\n([\s\S]*?)\n```/g;
    let match;
    while ((match = markdownRegex.exec(content)) !== null) {
      matches.push({
        language: match[1] || 'text',
        code: match[2],
        fullMatch: match[0],
      });
    }
    
    // 2. Detect substantial HTML code blocks if no markdown blocks found
    // Only look for <pre><code> blocks, ignore inline <code> tags
    if (matches.length === 0) {
      const htmlCodeRegex = /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi;
      while ((match = htmlCodeRegex.exec(content)) !== null) {
        let codeContent = match[1].trim();
        
        // Decode HTML entities
        codeContent = codeContent
          .replace(/&lt;/g, '<')
          .replace(/&gt;/g, '>')
          .replace(/&amp;/g, '&')
          .replace(/&quot;/g, '"')
          .replace(/&#39;/g, "'");
        
        // Only include substantial code blocks (multi-line or reasonable length)
        if (codeContent.includes('\n') || codeContent.length > 30) {
          // Try to detect language from the content (improved heuristics)
          let language = 'text';
          if (isMermaidSyntax(codeContent)) {
            language = 'mermaid';
          } else if (/class\s+\w+|def\s+\w+|import\s+\w+/.test(codeContent)) {
            language = 'python';
          } else if (/function\s+\w+|const\s+\w+|let\s+\w+/.test(codeContent)) {
            language = 'javascript';
          }

          matches.push({
            language: language,
            code: codeContent,
            fullMatch: match[0],
          });
        }
      }
    }
    
    return matches;
  };

  const createCodeMenuItems = () => {
    const codeBlocks = detectCodeBlocks(message.content);
    if (codeBlocks.length === 0) return [];

    return codeBlocks.map((block, index) => ({
      key: `code-${index}`,
      label: `${block.language.toUpperCase()} Code ${codeBlocks.length > 1 ? `#${index + 1}` : ''}`,
      onClick: () => onShowCode?.(block.code, block.language, `${block.language.toUpperCase()} Code Block`),
    }));
  };

  const codeBlocks = detectCodeBlocks(message.content);

  // Fullscreen overlay component
  if (isFullscreen) {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 9999,
          backgroundColor: 'rgba(0, 0, 0, 0.95)',
          display: 'flex',
          flexDirection: 'column',
          padding: '20px',
        }}
      >
        {/* Fullscreen Header */}
        <div
          style={{
            background: message.role === 'user' 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
              : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            padding: '12px 14px 10px 14px',
            borderRadius: '20px 20px 0 0',
            marginBottom: '0',
          }}
        >
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <Avatar 
                size={32}
                icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                }}
              />
              <div className="flex flex-col">
                <span 
                  style={{ 
                    color: 'rgba(255, 255, 255, 0.9)',
                    fontWeight: 600,
                    fontSize: '13px',
                    letterSpacing: '0.5px'
                  }}
                >
                  {message.role === 'user' ? 'You' : 'Whysper AI'}
                </span>
                <span 
                  style={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: '11px',
                    marginTop: '2px'
                  }}
                >
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
            </div>

            {/* Center - Token and Model Information */}
            {renderMetadataStats(message.metadata, { theme: 'dark' })}
            
            {/* Header Actions */}
            <div className="flex items-center gap-2">
              {/* View Mode Toggle Buttons - Only show for assistant messages with HTML content */}
              {message.role === 'assistant' && hasHtmlContent && (
                <>
                  <Tooltip title="Markdown View">
                    <Button
                      type="text"
                      icon={<FileTextOutlined />}
                      onClick={() => setViewMode('markdown')}
                      size="small"
                      style={{ 
                        color: viewMode === 'markdown' ? 'white' : 'rgba(255, 255, 255, 0.6)',
                        backgroundColor: viewMode === 'markdown' ? 'rgba(255, 255, 255, 0.2)' : 'transparent'
                      }}
                    />
                  </Tooltip>
                  
                  <Tooltip title="HTML View">
                    <Button
                      type="text"
                      icon={<Html5Outlined />}
                      onClick={() => setViewMode('html')}
                      size="small"
                      style={{ 
                        color: viewMode === 'html' ? 'white' : 'rgba(255, 255, 255, 0.6)',
                        backgroundColor: viewMode === 'html' ? 'rgba(255, 255, 255, 0.2)' : 'transparent'
                      }}
                    />
                  </Tooltip>
                </>
              )}

              {/* Print Button - Only for assistant messages */}
              {message.role === 'assistant' && (
                <Tooltip title="Print Response">
                  <Button
                    type="text"
                    icon={<PrinterOutlined />}
                    onClick={handlePrintContent}
                    size="small"
                    style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                  />
                </Tooltip>
              )}

              {/* Show Code Button/Dropdown */}
              {codeBlocks.length > 0 && onShowCode && (
                codeBlocks.length === 1 ? (
                  <Tooltip title="Show Code Block">
                    <Button
                      type="text"
                      icon={<CodeOutlined />}
                      onClick={() => onShowCode?.(codeBlocks[0].code, codeBlocks[0].language, `${codeBlocks[0].language.toUpperCase()} Code Block`)}
                      size="small"
                      style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                    />
                  </Tooltip>
                ) : (
                  <Dropdown
                    menu={{
                      items: createCodeMenuItems()
                    }}
                    trigger={['click']}
                    placement="bottomRight"
                  >
                    <Tooltip title={`Show code from ${codeBlocks.length} blocks`}>
                      <Button
                        type="text"
                        icon={<CodeOutlined />}
                        size="small"
                        style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                      />
                    </Tooltip>
                  </Dropdown>
                )
              )}

              <Tooltip title="Exit Fullscreen">
                <Button
                  type="text"
                  icon={<FullscreenExitOutlined />}
                  onClick={() => setIsFullscreen(false)}
                  size="small"
                  style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                />
              </Tooltip>

              <Tooltip title="Copy Message">
                <Button
                  type="text"
                  icon={<CopyOutlined />}
                  onClick={handleCopyContent}
                  size="small"
                  style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                />
              </Tooltip>
            </div>
          </div>
        </div>

        {/* Fullscreen Content */}
        <div
          style={{
            background: 'white',
            padding: '14px',
            borderRadius: '0 0 20px 20px',
            flex: 1,
            overflow: 'auto',
          }}
        >
          <div className="message-content">
            {viewMode === 'html' && hasHtmlContent ? (
              // HTML View - Detect and render Mermaid diagrams from HTML
              <div
                className="prose max-w-none"
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  padding: '20px',
                  backgroundColor: '#f8fafc',
                  lineHeight: '1.2',
                  fontSize: '15px',
                  color: '#1e293b'
                }}
              >
                {processDiagramsInHTML(displayContent)}
              </div>
            ) : (
              // Markdown View - Use ReactMarkdown (default)
              <div 
                className="prose prose-slate max-w-none" 
                style={{ 
                  lineHeight: '1.2', 
                  fontSize: '15px',
                  color: '#1e293b'
                }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code: CodeComponentRenderer,
                    // Style other markdown elements for dark text
                    h1: (props) => <h1 style={{ color: '#1e293b', fontWeight: 700 }} {...props} />,
                    h2: (props) => <h2 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h3: (props) => <h3 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h4: (props) => <h4 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h5: (props) => <h5 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h6: (props) => <h6 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    p: (props) => <p style={{ color: '#374151', lineHeight: '1.275' }} {...props} />,
                    strong: (props) => <strong style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    em: (props) => <em style={{ color: '#374151' }} {...props} />,
                    blockquote: (props) => (
                      <blockquote 
                        style={{ 
                          color: '#6b7280',
                          borderLeft: '4px solid #667eea',
                          paddingLeft: '16px',
                          fontStyle: 'italic'
                        }} 
                        {...props} 
                      />
                    ),
                    ul: (props) => <ul style={{ color: '#374151' }} {...props} />,
                    ol: (props) => <ol style={{ color: '#374151' }} {...props} />,
                    li: (props) => <li style={{ color: '#374151', marginBottom: '4px' }} {...props} />,
                  }}
                >
                  {displayContent}
                </ReactMarkdown>
              </div>
            )}
            
            {/* Show More/Less for long content */}
            {isLongContent && (
              <div className="mt-4 text-center">
                <Button
                  type="link"
                  onClick={() => setShowFullContent(!showFullContent)}
                  size="small"
                  style={{ color: '#667eea' }}
                >
                  {showFullContent ? 'Show Less' : 'Show More'}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      id={`message-${message.id}`}
      className="mb-6 w-full"
      style={{
        paddingLeft: '0',
        paddingRight: '0',
      }}
    >
      <Card
        className="message-card"
        style={{
          border: 'none',
          borderRadius: message.role === 'user'
            ? '20px 20px 4px 20px'
            : '20px 20px 20px 4px',
          boxShadow: message.role === 'user'
            ? '0 8px 24px rgba(102, 126, 234, 0.25)'
            : '0 8px 24px rgba(240, 147, 251, 0.25)',
          overflow: 'hidden',
          width: '100%',
          background: 'transparent',
          backdropFilter: 'blur(10px)',
        }}
        size="default"
        styles={{
          body: {
            padding: '0',
            background: 'transparent',
            borderRadius: message.role === 'user'
              ? '20px 20px 4px 20px'
              : '20px 20px 20px 4px',
          }
        }}
      >
        {/* Gradient Header */}
        <div 
          style={{
            background: message.role === 'user' 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
              : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            padding: '12px 14px 10px 14px',
            borderRadius: message.role === 'user' 
              ? '20px 20px 0 0' 
              : '20px 20px 0 0',
          }}
        >
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <Avatar 
                size={32}
                icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                }}
              />
              <div className="flex flex-col">
                <span 
                  style={{ 
                    color: 'rgba(255, 255, 255, 0.9)',
                    fontWeight: 600,
                    fontSize: '13px',
                    letterSpacing: '0.5px'
                  }}
                >
                  {message.role === 'user' ? 'You' : 'Whysper AI'}
                </span>
                <span 
                  style={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: '11px',
                    marginTop: '2px'
                  }}
                >
                  {formatTimestamp(message.timestamp)}
                </span>
              </div>
            </div>

            {/* Center - Token and Model Information */}
            {renderMetadataStats(message.metadata, { theme: 'dark' })}
            
            {/* Header Actions */}
            <div className="flex items-center gap-2">
              {/* View Mode Toggle Buttons - Only show for assistant messages with HTML content */}
              {message.role === 'assistant' && hasHtmlContent && (
                <>
                  <Tooltip title="Markdown View">
                    <Button
                      type="text"
                      icon={<FileTextOutlined />}
                      onClick={() => setViewMode('markdown')}
                      size="small"
                      style={{ 
                        color: viewMode === 'markdown' ? 'white' : 'rgba(255, 255, 255, 0.6)',
                        backgroundColor: viewMode === 'markdown' ? 'rgba(255, 255, 255, 0.2)' : 'transparent'
                      }}
                    />
                  </Tooltip>
                  
                  <Tooltip title="HTML View">
                    <Button
                      type="text"
                      icon={<Html5Outlined />}
                      onClick={() => setViewMode('html')}
                      size="small"
                      style={{ 
                        color: viewMode === 'html' ? 'white' : 'rgba(255, 255, 255, 0.6)',
                        backgroundColor: viewMode === 'html' ? 'rgba(255, 255, 255, 0.2)' : 'transparent'
                      }}
                    />
                  </Tooltip>
                </>
              )}

              {/* Print Button - Only for assistant messages */}
              {message.role === 'assistant' && (
                <Tooltip title="Print Response">
                  <Button
                    type="text"
                    icon={<PrinterOutlined />}
                    onClick={handlePrintContent}
                    size="small"
                    style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                  />
                </Tooltip>
              )}

              {/* Show Code Button/Dropdown */}
              {codeBlocks.length > 0 && onShowCode && (
                codeBlocks.length === 1 ? (
                  <Tooltip title="Show Code Block">
                    <Button
                      type="text"
                      icon={<CodeOutlined />}
                      onClick={() => onShowCode?.(codeBlocks[0].code, codeBlocks[0].language, `${codeBlocks[0].language.toUpperCase()} Code Block`)}
                      size="small"
                      style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                    />
                  </Tooltip>
                ) : (
                  <Dropdown
                    menu={{
                      items: createCodeMenuItems()
                    }}
                    trigger={['click']}
                    placement="bottomRight"
                  >
                    <Tooltip title={`Show code from ${codeBlocks.length} blocks`}>
                      <Button
                        type="text"
                        icon={<CodeOutlined />}
                        size="small"
                        style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                      />
                    </Tooltip>
                  </Dropdown>
                )
              )}

              <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Maximize"}>
                <Button
                  type="text"
                  icon={isFullscreen ? <FullscreenExitOutlined /> : <FullscreenOutlined />}
                  onClick={() => setIsFullscreen(!isFullscreen)}
                  size="small"
                  style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                />
              </Tooltip>

              <Tooltip title="Copy Message">
                <Button
                  type="text"
                  icon={<CopyOutlined />}
                  onClick={handleCopyContent}
                  size="small"
                  style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                />
              </Tooltip>
              
              <Tooltip title={isExpanded ? "Collapse" : "Expand"}>
                <Button
                  type="text"
                  icon={isExpanded ? <CompressOutlined /> : <ExpandOutlined />}
                  onClick={() => setIsExpanded(!isExpanded)}
                  size="small"
                  style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                />
              </Tooltip>
            </div>
          </div>
        </div>

        {/* White Content Area */}
        <div
          style={{
            background: message.role === 'assistant' && (theme === 'modernGradient' || theme === 'modernGradientDark')
              ? 'rgba(255, 255, 255, 0.95)'
              : 'white',
            padding: '14px',
            borderRadius: message.role === 'user'
              ? '0 0 4px 20px'
              : '0 0 20px 4px',
            backdropFilter: (theme === 'modernGradient' || theme === 'modernGradientDark') ? 'blur(10px)' : 'none',
          }}
        >
          
          {/* Message Content */}
          {isExpanded && (
            <div className="message-content">
              {viewMode === 'html' && hasHtmlContent ? (
                // HTML View - Detect and render Mermaid diagrams from HTML
                <div
                  className="prose max-w-none"
                  style={{
                    border: theme === 'modernGradient' || theme === 'modernGradientDark'
                      ? '1px solid rgba(226, 232, 240, 0.6)'
                      : '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '12px',
                    backgroundColor: theme === 'modernGradient' || theme === 'modernGradientDark'
                      ? 'rgba(248, 250, 252, 0.8)'
                      : '#f8fafc',
                    maxHeight: '500px',
                    overflowY: 'auto',
                    lineHeight: '1.2',
                    fontSize: '14px',
                    color: '#1e293b',
                    backdropFilter: (theme === 'modernGradient' || theme === 'modernGradientDark') ? 'blur(5px)' : 'none',
                  }}
                >
                  {processDiagramsInHTML(displayContent)}
                </div>
              ) : (
                // Markdown View - Use ReactMarkdown (default)
                <div 
                  className="prose prose-slate max-w-none" 
                  style={{ 
                    lineHeight: '1.2', 
                    fontSize: '14px',
                    color: '#1e293b'
                  }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code: CodeComponentRenderer,
                      // Style other markdown elements for dark text
                      h1: (props) => <h1 style={{ color: '#1e293b', fontWeight: 700 }} {...props} />,
                      h2: (props) => <h2 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h3: (props) => <h3 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h4: (props) => <h4 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h5: (props) => <h5 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h6: (props) => <h6 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      p: (props) => <p style={{ color: '#374151', lineHeight: '1.275' }} {...props} />,
                      strong: (props) => <strong style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      em: (props) => <em style={{ color: '#374151' }} {...props} />,
                      blockquote: (props) => (
                        <blockquote 
                          style={{ 
                            color: '#6b7280',
                            borderLeft: '4px solid #667eea',
                            paddingLeft: '16px',
                            fontStyle: 'italic'
                          }} 
                          {...props} 
                        />
                      ),
                      ul: (props) => <ul style={{ color: '#374151' }} {...props} />,
                      ol: (props) => <ol style={{ color: '#374151' }} {...props} />,
                      li: (props) => <li style={{ color: '#374151', marginBottom: '4px' }} {...props} />,
                    }}
                  >
                    {displayContent}
                  </ReactMarkdown>
                </div>
              )}
              
              {/* Show More/Less for long content */}
              {isLongContent && (
                <div className="mt-4 text-center">
                  <Button
                    type="link"
                    onClick={() => setShowFullContent(!showFullContent)}
                    size="small"
                    style={{ color: '#667eea' }}
                  >
                    {showFullContent ? 'Show Less' : 'Show More'}
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

interface ChatViewProps {
  messages: Message[];
  loading?: boolean;
  onShowCode?: (code: string, language: string, title?: string) => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  loading = false,
  onShowCode,
}) => {
  const { theme } = useTheme();
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="text-center max-w-md">
          <div className="text-8xl mb-6">💬</div>
          <Typography.Title level={2} className="!text-gray-700 !font-semibold !mb-4">
            Start your conversation
          </Typography.Title>
          <Typography.Text type="secondary" className="text-lg leading-relaxed">
            Begin by selecting files for context, then type your first question to start chatting with the AI assistant.
          </Typography.Text>
        </div>
      </div>
    );
  }

  // Get theme-specific chat view styles
  const getChatViewStyles = () => {
    // Check if we're in a modern gradient theme
    const isModernGradient = theme === 'modernGradient' || theme === 'modernGradientDark';
    
    if (isModernGradient) {
      return {
        padding: '24px',
        background: 'transparent'
      };
    }
    
    return {
      padding: '24px',
      background: 'transparent'
    };
  };

  return (
    <div className="flex-1 overflow-y-auto" style={getChatViewStyles()}>
      <div className="w-full px-0">
        {messages.map((message) => (
          <MessageItem
            key={message.id}
            message={message}
            onShowCode={onShowCode}
          />
        ))}
        
        {loading && (
          <div 
            className="mb-6 w-full"
            style={{ paddingRight: '0' }}
          >
            <Card
              className="message-card"
              style={{
                border: 'none',
                borderRadius: '20px 20px 20px 4px',
                boxShadow: '0 8px 24px rgba(16, 185, 129, 0.15)',
                overflow: 'hidden',
                width: '100%',
                background: 'transparent',
              }}
              styles={{
                body: {
                  padding: '14px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white',
                  borderRadius: '20px 20px 20px 4px',
                }
              }}
            >
            <div className="flex items-center gap-3">
              <Avatar 
                size={32}
                icon={<RobotOutlined />}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                }}
              />
              <div className="flex flex-col">
                <span 
                  style={{ 
                    color: 'rgba(255, 255, 255, 0.9)',
                    fontWeight: 600,
                    fontSize: '13px',
                    letterSpacing: '0.5px'
                  }}
                >
                  Whysper AI
                </span>
                <div className="flex items-center gap-2 mt-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce opacity-70"></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce opacity-70" style={{animationDelay: '0.15s'}}></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce opacity-70" style={{animationDelay: '0.3s'}}></div>
                  <span 
                    style={{ 
                      color: 'rgba(255, 255, 255, 0.8)',
                      fontSize: '11px',
                      marginLeft: '8px'
                    }}
                  >
                    Thinking...
                  </span>
                </div>
              </div>
            </div>
          </Card>
          </div>
        )}
        
        <div ref={chatEndRef} />
      </div>
    </div>
  );
};

export default ChatView;
