import React, { useRef, useEffect, useState } from 'react';
import { Card, Button, Typography, Tooltip, Avatar, Dropdown } from 'antd';
import {
  ExpandOutlined,
  CompressOutlined,
  CopyOutlined,
  DownloadOutlined,
  CodeOutlined,
  FileTextOutlined,
  Html5Outlined,
  UserOutlined,
  RobotOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types';


interface MessageItemProps {
  message: Message;
  onExtractCode?: (messageId: string) => void;
  onRenderMermaid?: (code: string) => void;
  onShowCode?: (code: string, language: string, title?: string) => void;
}

const MessageItem: React.FC<MessageItemProps> = ({ 
  message, 
  onExtractCode, 
  onRenderMermaid,
  onShowCode
}) => {
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
    ];
    
    // Check if content has substantial HTML structure
    const hasSubstantialHtml = substantialHtmlPatterns.some(pattern => pattern.test(content));
    
    // Additional check: count HTML tags - only show if there are multiple structural tags
    const htmlTagCount = (content.match(/<\/?[a-zA-Z][^>]*>/g) || []).length;
    const hasMultipleTags = htmlTagCount >= 5; // At least 5 HTML tags
    
    // Only show HTML view if there's substantial HTML structure OR many HTML tags
    return hasSubstantialHtml || hasMultipleTags;
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
          // Try to detect language from the content (basic heuristics)
          let language = 'text';
          if (/class\s+\w+|def\s+\w+|import\s+\w+/.test(codeContent)) {
            language = 'python';
          } else if (/function\s+\w+|const\s+\w+|let\s+\w+/.test(codeContent)) {
            language = 'javascript';
          } else if (/classDiagram|sequenceDiagram|graph\s+(TD|LR)/.test(codeContent)) {
            language = 'mermaid';
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
  
  const hasCodeFragments = (content: string): boolean => {
    // Check for markdown-style code blocks: ```code```
    if (/```[\s\S]*?```/.test(content)) {
      return true;
    }
    
    // Only check for substantial HTML code blocks (multi-line content in <pre><code>)
    // Ignore small inline <code> tags like <code>ai.py</code>
    const htmlBlockRegex = /<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi;
    const matches = content.match(htmlBlockRegex);
    
    if (matches) {
      // Only consider it a code fragment if it has multiple lines or reasonable content
      return matches.some(match => {
        const innerContent = match.replace(/<\/?[^>]+(>|$)/g, '').trim();
        return innerContent.includes('\n') || innerContent.length > 30;
      });
    }
    
    return false;
  };

  const detectMermaidDiagrams = (content: string) => {
    const matches = [];
    
    // 1. Detect markdown-style mermaid blocks: ```mermaid
    const markdownRegex = /```mermaid\n([\s\S]*?)```/g;
    let match;
    while ((match = markdownRegex.exec(content)) !== null) {
      matches.push(match[1].trim());
    }
    
    // 2. Only check HTML patterns if no markdown patterns were found
    // This prevents detecting the same diagram twice
    if (matches.length === 0) {
      // Detect HTML-style code blocks containing mermaid diagrams
      // Look for <pre><code> or <code> blocks that contain mermaid keywords
      const htmlCodeRegex = /<(?:pre><code[^>]*>|code[^>]*>)([\s\S]*?)<\/(?:code><\/pre>|code)>/gi;
      while ((match = htmlCodeRegex.exec(content)) !== null) {
        let codeContent = match[1].trim();
        
        // Decode HTML entities that might be present in the code
        codeContent = codeContent
          .replace(/&lt;/g, '<')
          .replace(/&gt;/g, '>')
          .replace(/&amp;/g, '&')
          .replace(/&quot;/g, '"')
          .replace(/&#39;/g, "'");
        
        // Check if the content contains mermaid diagram keywords
        if (isMermaidContent(codeContent)) {
          matches.push(codeContent);
        }
      }
    }
    
    // Remove duplicates by comparing normalized content
    const uniqueMatches = [];
    const seen = new Set();
    
    for (const diagram of matches) {
      // Normalize the diagram content for comparison
      const normalized = diagram.replace(/\s+/g, ' ').trim().toLowerCase();
      if (!seen.has(normalized)) {
        seen.add(normalized);
        uniqueMatches.push(diagram);
      }
    }
    
    return uniqueMatches;
  };

  const isMermaidContent = (content: string): boolean => {
    // Check for common mermaid diagram types and syntax
    const mermaidKeywords = [
      /^graph\s+(TD|LR|TB|RL|BT)/i,           // Flowcharts
      /^classDiagram/i,                       // Class diagrams  
      /^sequenceDiagram/i,                    // Sequence diagrams
      /^stateDiagram/i,                       // State diagrams
      /^journey/i,                            // User journey
      /^gitgraph/i,                           // Git graphs
      /^pie\s+title/i,                        // Pie charts
      /^gantt/i,                              // Gantt charts
      /^erDiagram/i,                          // Entity relationship
      /^flowchart\s+(TD|LR|TB|RL|BT)/i,      // Flowcharts (alternative syntax)
      /direction\s+(TD|LR|TB|RL|BT)/i,       // Direction declarations
    ];
    
    return mermaidKeywords.some(regex => regex.test(content.trim()));
  };

  const getMermaidDiagramType = (content: string): string => {
    const trimmed = content.trim();
    if (/^classDiagram/i.test(trimmed)) return 'Class Diagram';
    if (/^sequenceDiagram/i.test(trimmed)) return 'Sequence Diagram';
    if (/^stateDiagram/i.test(trimmed)) return 'State Diagram';
    if (/^journey/i.test(trimmed)) return 'User Journey';
    if (/^gitgraph/i.test(trimmed)) return 'Git Graph';
    if (/^pie\s+title/i.test(trimmed)) return 'Pie Chart';
    if (/^gantt/i.test(trimmed)) return 'Gantt Chart';
    if (/^erDiagram/i.test(trimmed)) return 'ER Diagram';
    if (/^(graph|flowchart)\s+(TD|LR|TB|RL|BT)/i.test(trimmed)) return 'Flowchart';
    return 'Diagram';
  };

  const createMermaidMenuItems = () => {
    if (mermaidDiagrams.length === 0) return [];
    
    return mermaidDiagrams.map((diagram, index) => ({
      key: `mermaid-${index}`,
      label: `${getMermaidDiagramType(diagram)} ${mermaidDiagrams.length > 1 ? `#${index + 1}` : ''}`,
      onClick: () => onRenderMermaid?.(diagram),
    }));
  };

  const createCodeMenuItems = () => {
    if (codeBlocks.length === 0) return [];
    
    return codeBlocks.map((block, index) => ({
      key: `code-${index}`,
      label: `${block.language.toUpperCase()} Code ${codeBlocks.length > 1 ? `#${index + 1}` : ''}`,
      onClick: () => onShowCode?.(block.code, block.language, `${block.language.toUpperCase()} Code Block`),
    }));
  };

  const codeBlocks = detectCodeBlocks(message.content);
  const mermaidDiagrams = detectMermaidDiagrams(message.content);
  
  // Debug logging for mermaid detection
  if (message.role === 'assistant') {
    console.log('Mermaid Debug:', {
      messageId: message.id,
      contentLength: message.content.length,
      hasHtmlContent,
      mermaidCount: mermaidDiagrams.length,
      mermaidDiagrams: mermaidDiagrams,
      contentPreview: message.content.substring(0, 500)
    });
  }

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
            {message.metadata && (
              <div className="flex items-center gap-3 text-white font-medium opacity-90" style={{ fontSize: '16px' }}>
                {message.metadata.model && (
                  <span style={{ color: 'rgba(255, 255, 255, 0.95)', fontWeight: 600 }}>
                    {message.metadata.model}
                  </span>
                )}
                {message.metadata.inputTokens && (
                  <span>📥 {message.metadata.inputTokens}</span>
                )}
                {message.metadata.outputTokens && (
                  <span>📤 {message.metadata.outputTokens}</span>
                )}
                {message.metadata.elapsedTime && (
                  <span>⏱️ {message.metadata.elapsedTime.toFixed(2)}s</span>
                )}
              </div>
            )}
            
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

              {/* Render Mermaid Button/Dropdown */}
              {mermaidDiagrams.length > 0 && onRenderMermaid && (
                mermaidDiagrams.length === 1 ? (
                  <Tooltip title="Render Mermaid Diagram">
                    <Button
                      type="text"
                      icon={<DownloadOutlined />}
                      onClick={() => onRenderMermaid?.(mermaidDiagrams[0])}
                      size="small"
                      style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                    />
                  </Tooltip>
                ) : (
                  <Dropdown
                    menu={{
                      items: createMermaidMenuItems()
                    }}
                    trigger={['click']}
                    placement="bottomRight"
                  >
                    <Tooltip title={`Choose from ${mermaidDiagrams.length} diagrams`}>
                      <Button
                        type="text"
                        icon={<DownloadOutlined />}
                        size="small"
                        style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                      />
                    </Tooltip>
                  </Dropdown>
                )
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

              {/* Extract Code Button */}
              {hasCodeFragments(message.content) && onExtractCode && (
                <Tooltip title={`Extract ${codeBlocks.length} code block(s)`}>
                  <Button
                    type="text"
                    icon={<CodeOutlined />}
                    onClick={() => onExtractCode(message.id)}
                    size="small"
                    style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                  />
                </Tooltip>
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
              // HTML View - Render HTML content directly
              <div 
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: displayContent }}
                style={{
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  padding: '20px',
                  backgroundColor: '#f8fafc',
                  lineHeight: '1.6',
                  fontSize: '15px',
                  color: '#1e293b'
                }}
              />
            ) : (
              // Markdown View - Use ReactMarkdown (default)
              <div 
                className="prose prose-slate max-w-none" 
                style={{ 
                  lineHeight: '1.6', 
                  fontSize: '15px',
                  color: '#1e293b'
                }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code(props: React.ComponentProps<'code'> & { inline?: boolean }) {
                      const { inline, className, children, ...rest } = props;
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <pre
                          className={`${className || ''} bg-gray-50 border border-gray-200 p-4 rounded-lg overflow-x-auto`}
                          style={{ 
                            fontSize: '14px', 
                            lineHeight: '1.6',
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
                    },
                    // Style other markdown elements for dark text
                    h1: (props) => <h1 style={{ color: '#1e293b', fontWeight: 700 }} {...props} />,
                    h2: (props) => <h2 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h3: (props) => <h3 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h4: (props) => <h4 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h5: (props) => <h5 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    h6: (props) => <h6 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                    p: (props) => <p style={{ color: '#374151', lineHeight: '1.7' }} {...props} />,
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
        }}
        size="default"
        bodyStyle={{ 
          padding: '0',
          background: 'transparent',
          borderRadius: message.role === 'user' 
            ? '20px 20px 4px 20px' 
            : '20px 20px 20px 4px',
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
            {message.metadata && (
              <div className="flex items-center gap-3 text-white font-medium opacity-90" style={{ fontSize: '16px' }}>
                {message.metadata.model && (
                  <span style={{ color: 'rgba(255, 255, 255, 0.95)', fontWeight: 600 }}>
                    {message.metadata.model}
                  </span>
                )}
                {message.metadata.inputTokens && (
                  <span>📥 {message.metadata.inputTokens}</span>
                )}
                {message.metadata.outputTokens && (
                  <span>📤 {message.metadata.outputTokens}</span>
                )}
                {message.metadata.elapsedTime && (
                  <span>⏱️ {message.metadata.elapsedTime.toFixed(2)}s</span>
                )}
              </div>
            )}
            
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

              {/* Render Mermaid Button/Dropdown */}
              {mermaidDiagrams.length > 0 && onRenderMermaid && (
                mermaidDiagrams.length === 1 ? (
                  <Tooltip title="Render Mermaid Diagram">
                    <Button
                      type="text"
                      icon={<DownloadOutlined />}
                      onClick={() => onRenderMermaid?.(mermaidDiagrams[0])}
                      size="small"
                      style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                    />
                  </Tooltip>
                ) : (
                  <Dropdown
                    menu={{
                      items: createMermaidMenuItems()
                    }}
                    trigger={['click']}
                    placement="bottomRight"
                  >
                    <Tooltip title={`Choose from ${mermaidDiagrams.length} diagrams`}>
                      <Button
                        type="text"
                        icon={<DownloadOutlined />}
                        size="small"
                        style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                      />
                    </Tooltip>
                  </Dropdown>
                )
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

              {/* Extract Code Button */}
              {hasCodeFragments(message.content) && onExtractCode && (
                <Tooltip title={`Extract ${codeBlocks.length} code block(s)`}>
                  <Button
                    type="text"
                    icon={<CodeOutlined />}
                    onClick={() => onExtractCode(message.id)}
                    size="small"
                    style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                  />
                </Tooltip>
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
            background: 'white',
            padding: '14px',
            borderRadius: message.role === 'user' 
              ? '0 0 4px 20px' 
              : '0 0 20px 4px',
          }}
        >
          
          {/* Message Content */}
          {isExpanded && (
            <div className="message-content">
              {viewMode === 'html' && hasHtmlContent ? (
                // HTML View - Render HTML content directly
                <div 
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: displayContent }}
                  style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '12px',
                    backgroundColor: '#f8fafc',
                    maxHeight: '500px',
                    overflowY: 'auto',
                    lineHeight: '1.6',
                    fontSize: '14px',
                    color: '#1e293b'
                  }}
                />
              ) : (
                // Markdown View - Use ReactMarkdown (default)
                <div 
                  className="prose prose-slate max-w-none" 
                  style={{ 
                    lineHeight: '1.6', 
                    fontSize: '14px',
                    color: '#1e293b'
                  }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code(props: React.ComponentProps<'code'> & { inline?: boolean }) {
                        const { inline, className, children, ...rest } = props;
                        const match = /language-(\w+)/.exec(className || '');
                        return !inline && match ? (
                          <pre
                            className={`${className || ''} bg-gray-50 border border-gray-200 p-4 rounded-lg overflow-x-auto`}
                            style={{ 
                              fontSize: '14px', 
                              lineHeight: '1.6',
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
                      },
                      // Style other markdown elements for dark text
                      h1: (props) => <h1 style={{ color: '#1e293b', fontWeight: 700 }} {...props} />,
                      h2: (props) => <h2 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h3: (props) => <h3 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h4: (props) => <h4 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h5: (props) => <h5 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      h6: (props) => <h6 style={{ color: '#1e293b', fontWeight: 600 }} {...props} />,
                      p: (props) => <p style={{ color: '#374151', lineHeight: '1.7' }} {...props} />,
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
  onExtractCode?: (messageId: string) => void;
  onRenderMermaid?: (code: string) => void;
  onShowCode?: (code: string, language: string, title?: string) => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  loading = false,
  onExtractCode,
  onRenderMermaid,
  onShowCode,
}) => {
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

  return (
    <div className="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
      <div className="w-full px-0">
        {messages.map((message) => (
          <MessageItem
            key={message.id}
            message={message}
            onExtractCode={onExtractCode}
            onRenderMermaid={onRenderMermaid}
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
              bodyStyle={{ 
                padding: '14px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                borderRadius: '20px 20px 20px 4px',
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