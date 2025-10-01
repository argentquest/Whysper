import React, { useRef, useEffect, useState } from 'react';
import { Card, Button, Typography, Tag, Space, Tooltip } from 'antd';
import {
  ExpandOutlined,
  CompressOutlined,
  CopyOutlined,
  DownloadOutlined,
  CodeOutlined,
  FileTextOutlined,
  Html5Outlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../types';

const { Text } = Typography;

interface MessageItemProps {
  message: Message;
  onExtractCode?: (messageId: string) => void;
  onRenderMermaid?: (code: string) => void;
}

const MessageItem: React.FC<MessageItemProps> = ({ 
  message, 
  onExtractCode, 
  onRenderMermaid 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showFullContent, setShowFullContent] = useState(false);
  
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

  const getMessageStyle = () => {
    switch (message.role) {
      case 'system':
        return {
          backgroundColor: '#fff7e6',
          borderColor: '#ffd666',
          borderLeft: '4px solid #faad14',
        };
      case 'user':
        return {
          backgroundColor: '#e6f7ff',
          borderColor: '#91d5ff',
          borderLeft: '4px solid #1890ff',
        };
      case 'assistant':
        return {
          backgroundColor: '#ffffff',
          borderColor: '#d9d9d9',
          borderLeft: '4px solid #52c41a',
        };
      default:
        return {};
    }
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
    // Use exact same pattern as web1: /```(\w+)?\n([\s\S]*?)\n```/g
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)\n```/g;
    const matches = [];
    let match;
    
    while ((match = codeBlockRegex.exec(content)) !== null) {
      matches.push({
        language: match[1] || 'text',
        code: match[2],
        fullMatch: match[0],
      });
    }
    
    return matches;
  };
  
  const hasCodeFragments = (content: string): boolean => {
    // Use exact same detection as web1: /```[\s\S]*?```/.test(text)
    return /```[\s\S]*?```/.test(content);
  };

  const detectMermaidDiagrams = (content: string) => {
    const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
    const matches = [];
    let match;
    
    while ((match = mermaidRegex.exec(content)) !== null) {
      matches.push(match[1]);
    }
    
    return matches;
  };

  const codeBlocks = detectCodeBlocks(message.content);
  const mermaidDiagrams = detectMermaidDiagrams(message.content);

  return (
    <Card
      className="mb-6 message-card"
      style={{
        ...getMessageStyle(),
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
        borderRadius: '12px',
      }}
      size="default"
      bodyStyle={{ padding: '20px' }}
    >
      {/* Message Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Tag 
            color={
              message.role === 'system' ? 'orange' :
              message.role === 'user' ? 'blue' : 'green'
            }
            style={{ 
              fontWeight: 600,
              fontSize: '11px',
              padding: '2px 8px',
              borderRadius: '6px'
            }}
          >
            {message.role.toUpperCase()}
          </Tag>
          <Text type="secondary" className="text-sm font-medium">
            {formatTimestamp(message.timestamp)}
          </Text>
          {message.metadata?.model && (
            <Text type="secondary" className="text-sm font-medium">
              ({message.metadata.model})
            </Text>
          )}
          {/* Token Information */}
          {message.metadata && (
            <div className="flex items-center gap-3 text-sm text-gray-600 font-medium">
              {message.metadata.inputTokens && (
                <span>📥 {message.metadata.inputTokens}</span>
              )}
              {message.metadata.cachedTokens && (
                <span>💾 {message.metadata.cachedTokens}</span>
              )}
              {message.metadata.outputTokens && (
                <span>📤 {message.metadata.outputTokens}</span>
              )}
              {message.metadata.tokens && !message.metadata.inputTokens && !message.metadata.outputTokens && (
                <span>🔢 {message.metadata.tokens}</span>
              )}
              {message.metadata.elapsedTime && (
                <span>⏱️ {message.metadata.elapsedTime.toFixed(2)}s</span>
              )}
            </div>
          )}
        </div>
        
        <Space>
          {/* View Mode Toggle Buttons - Only show for assistant messages with HTML content */}
          {message.role === 'assistant' && hasHtmlContent && (
            <>
              <Tooltip title="Markdown View">
                <Button
                  type={viewMode === 'markdown' ? 'primary' : 'text'}
                  size="small"
                  icon={<FileTextOutlined />}
                  onClick={() => setViewMode('markdown')}
                />
              </Tooltip>
              
              <Tooltip title="HTML View">
                <Button
                  type={viewMode === 'html' ? 'primary' : 'text'}
                  size="small"
                  icon={<Html5Outlined />}
                  onClick={() => setViewMode('html')}
                />
              </Tooltip>
            </>
          )}
          
          {/* Extract Code Button */}
          {hasCodeFragments(message.content) && onExtractCode && (
            <Tooltip title={`Extract ${codeBlocks.length} code block(s)`}>
              <Button
                type="text"
                size="small"
                icon={<CodeOutlined />}
                onClick={() => onExtractCode(message.id)}
              />
            </Tooltip>
          )}
          
          {/* Render Mermaid Button */}
          {mermaidDiagrams.length > 0 && onRenderMermaid && (
            <Tooltip title={`Render ${mermaidDiagrams.length} diagram(s)`}>
              <Button
                type="text"
                size="small"
                icon={<DownloadOutlined />}
                onClick={() => mermaidDiagrams.forEach(diagram => onRenderMermaid?.(diagram))}
              />
            </Tooltip>
          )}
          
          {/* Copy Button */}
          <Tooltip title="Copy content">
            <Button
              type="text"
              size="small"
              icon={<CopyOutlined />}
              onClick={handleCopyContent}
            />
          </Tooltip>
          
          {/* Expand/Collapse Button */}
          <Tooltip title={isExpanded ? "Collapse" : "Expand"}>
            <Button
              type="text"
              size="small"
              icon={isExpanded ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setIsExpanded(!isExpanded)}
            />
          </Tooltip>
        </Space>
      </div>

      {/* Message Content */}
      {isExpanded && (
        <div className="message-content">
          {viewMode === 'html' && hasHtmlContent ? (
            // HTML View - Render HTML content directly
            <div 
              className="prose dark:prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: displayContent }}
              style={{
                border: '1px solid #e1e5e9',
                borderRadius: '8px',
                padding: '20px',
                backgroundColor: '#fafbfc',
                maxHeight: '500px',
                overflowY: 'auto',
                lineHeight: '1.2',
                fontSize: '15px'
              }}
            />
          ) : (
            // Markdown View - Use ReactMarkdown (default)
            <div className="prose dark:prose-invert max-w-none" style={{ lineHeight: '1.7', fontSize: '15px' }}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code(props: React.ComponentProps<'code'> & { inline?: boolean }) {
                    const { inline, className, children, ...rest } = props;
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <pre
                        className={`${className || ''} bg-gray-50 dark:bg-gray-800 p-5 rounded-lg overflow-x-auto`}
                        style={{ fontSize: '14px', lineHeight: '1.6' }}
                      >
                        <code className={className} {...rest}>
                          {children}
                        </code>
                      </pre>
                    ) : (
                      <code className={`${className || ''} bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded`} style={{ fontSize: '14px' }} {...rest}>
                        {children}
                      </code>
                    );
                  },
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
              >
                {showFullContent ? 'Show Less' : 'Show More'}
              </Button>
            </div>
          )}
        </div>
      )}
    </Card>
  );
};

interface ChatViewProps {
  messages: Message[];
  loading?: boolean;
  onExtractCode?: (messageId: string) => void;
  onRenderMermaid?: (code: string) => void;
}

export const ChatView: React.FC<ChatViewProps> = ({
  messages,
  loading = false,
  onExtractCode,
  onRenderMermaid,
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
          />
        ))}
        
        {loading && (
          <Card 
            className="mb-6" 
            style={{
              backgroundColor: '#ffffff',
              borderColor: '#d9d9d9',
              borderLeft: '4px solid #52c41a',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
              borderRadius: '12px',
            }}
            bodyStyle={{ padding: '20px' }}
          >
            <div className="flex items-center gap-3">
              <Tag 
                color="green"
                style={{ 
                  fontWeight: 600,
                  fontSize: '11px',
                  padding: '2px 8px',
                  borderRadius: '6px'
                }}
              >
                ASSISTANT
              </Tag>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.15s'}}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.3s'}}></div>
              </div>
              <Text type="secondary" className="text-sm font-medium">Thinking...</Text>
            </div>
          </Card>
        )}
        
        <div ref={chatEndRef} />
      </div>
    </div>
  );
};

export default ChatView;