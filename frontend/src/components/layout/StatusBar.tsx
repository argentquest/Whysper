import React, { useState, useEffect, useRef } from 'react';
import { Space, Tag, Typography, Tooltip, Button, Badge, Popover } from 'antd';
import {
  CheckCircleOutlined,
  LoadingOutlined,
  ExclamationCircleOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  CloudOutlined,
  ApiOutlined,
  HistoryOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

interface LogEvent {
  timestamp: string;
  level: string;
  message: string;
  logger: string;
}

interface StatusBarProps {
  status: 'ready' | 'loading' | 'error';
  provider?: string;
  model?: string;
  directory?: string;
  fileCount?: number;
  totalSize?: number;
  tokenCount?: number;
  onOpenDirectory?: () => void;
  errorMessage?: string;
  conversationId?: string;  // For session-specific log filtering
}

export const StatusBar: React.FC<StatusBarProps> = ({
  status,
  provider = 'openrouter',
  model = 'x-ai/grok-code-fast-1',
  directory = 'none',
  fileCount = 0,
  totalSize = 0,
  tokenCount = 0,
  onOpenDirectory,
  errorMessage,
  conversationId,
}) => {
  // Real-time log streaming state
  const [currentLog, setCurrentLog] = useState<LogEvent | null>(null);
  const [logHistory, setLogHistory] = useState<LogEvent[]>([]);
  const [isLogConnected, setIsLogConnected] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Connect to SSE log stream on mount (reconnect when conversationId changes)
  useEffect(() => {
    const BACKEND_PORT = import.meta.env.VITE_BACKEND_PORT || '8003';
    const API_BASE_URL = import.meta.env.DEV
      ? `http://localhost:${BACKEND_PORT}/api/v1`
      : '/api/v1';

    // Add session_id parameter for session-specific log filtering
    const url = conversationId
      ? `${API_BASE_URL}/chat/logs/stream?session_id=${conversationId}`
      : `${API_BASE_URL}/chat/logs/stream`;

    console.log('📡 [STATUS BAR] Connecting to log stream:', url);
    console.log('📡 [STATUS BAR] Session filter:', conversationId || 'ALL (no filter)');

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.addEventListener('connected', () => {
      console.log('✅ [STATUS BAR] Connected to log stream');
      setIsLogConnected(true);
    });

    eventSource.addEventListener('log', (event) => {
      try {
        const logEvent: LogEvent = JSON.parse(event.data);
        setCurrentLog(logEvent);

        // Add to history buffer (keep last 30)
        setLogHistory((prev) => {
          const newHistory = [...prev, logEvent];
          // Keep only last 30 logs
          return newHistory.slice(-30);
        });
      } catch (error) {
        console.error('❌ [STATUS BAR] Failed to parse log event:', error);
      }
    });

    eventSource.onerror = (error) => {
      console.error('❌ [STATUS BAR] Connection error:', error);
      setIsLogConnected(false);
    };

    return () => {
      console.log('🛑 [STATUS BAR] Disconnecting from log stream');
      eventSource.close();
      // Clear history when disconnecting
      setLogHistory([]);
    };
  }, [conversationId]); // Reconnect when conversationId changes

  const getStatusIcon = () => {
    switch (status) {
      case 'ready':
        return <CheckCircleOutlined className="text-green-500" />;
      case 'loading':
        return <LoadingOutlined className="text-blue-500" />;
      case 'error':
        return <ExclamationCircleOutlined className="text-red-500" />;
      default:
        return <CheckCircleOutlined className="text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'ready':
        return 'Ready';
      case 'loading':
        return 'Processing...';
      case 'error':
        return errorMessage || 'Error';
      default:
        return 'Unknown';
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    }
    return num.toString();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  // Log history popover content (reversed to show newest first)
  const logHistoryContent = (
    <div style={{ width: '500px', maxHeight: '300px', overflowY: 'auto' }}>
      {logHistory.length === 0 ? (
        <Text style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>
          No logs yet
        </Text>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[...logHistory].reverse().map((log, index) => (
            <div
              key={`${log.timestamp}-${index}`}
              style={{
                padding: '6px 8px',
                borderRadius: '4px',
                backgroundColor: index === 0 ? '#f0f9ff' : '#f8fafc',
                borderLeft: `3px solid ${log.level === 'INFO' ? '#10b981' : '#ef4444'}`,
              }}
            >
              <div style={{ display: 'flex', gap: '8px', marginBottom: '2px' }}>
                <Text style={{ fontSize: '10px', color: '#64748b', fontFamily: 'monospace' }}>
                  {new Date(log.timestamp).toLocaleTimeString()}
                </Text>
                <Text
                  style={{
                    fontSize: '10px',
                    color: log.level === 'INFO' ? '#10b981' : '#ef4444',
                    fontWeight: 600,
                  }}
                >
                  {log.level}
                </Text>
              </div>
              <Text
                style={{
                  fontSize: '11px',
                  color: '#1e293b',
                  fontFamily: 'monospace',
                  display: 'block',
                }}
              >
                {log.message}
              </Text>
              <Text
                style={{
                  fontSize: '9px',
                  color: '#94a3b8',
                  fontStyle: 'italic',
                  display: 'block',
                  marginTop: '2px',
                }}
              >
                {log.logger}
              </Text>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div 
      className="h-10 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between text-xs"
      style={{
        boxShadow: '0 -1px 4px rgba(0, 0, 0, 0.04)',
        borderTop: '1px solid #f0f0f0'
      }}
    >
      {/* Left Section - Status */}
      <Space size="large">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <Text className="text-xs font-medium">
            {getStatusText()}
          </Text>
        </div>

        {/* Provider Information */}
        <Tooltip title={`Provider: ${provider}`}>
          <div className="flex items-center gap-1">
            <CloudOutlined className="text-gray-500" />
            <Text className="text-xs text-gray-600 dark:text-gray-400">
              Provider: {provider}
            </Text>
          </div>
        </Tooltip>

        {/* Model Information */}
        <Tooltip title={`Active model: ${model}`}>
          <div className="flex items-center gap-1">
            <ApiOutlined className="text-gray-500" />
            <Text className="text-xs text-gray-600 dark:text-gray-400">
              Model: {model}
            </Text>
          </div>
        </Tooltip>
      </Space>

      {/* Center Section - Real-Time Logs */}
      <Popover
        content={logHistoryContent}
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HistoryOutlined />
            <span>Log History (Last {logHistory.length} of 30)</span>
          </div>
        }
        trigger="click"
        placement="topLeft"
        open={isHistoryOpen}
        onOpenChange={setIsHistoryOpen}
      >
        <div
          style={{
            flex: 1,
            maxWidth: '600px',
            margin: '0 16px',
            overflow: 'hidden',
            cursor: logHistory.length > 0 ? 'pointer' : 'default',
          }}
        >
          {currentLog && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Badge
                status={isLogConnected ? 'processing' : 'default'}
                text=""
              />
              <Text style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
                {new Date(currentLog.timestamp).toLocaleTimeString()}
              </Text>
              <Text
                style={{
                  fontSize: '11px',
                  color: currentLog.level === 'INFO' ? '#10b981' : '#ef4444',
                  fontWeight: 500,
                }}
              >
                {currentLog.level}
              </Text>
              <Text
                style={{
                  fontSize: '11px',
                  color: '#1e293b',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  fontFamily: 'monospace',
                }}
              >
                {currentLog.message}
              </Text>
              {logHistory.length > 0 && (
                <HistoryOutlined
                  style={{ fontSize: '12px', color: '#64748b', marginLeft: 'auto' }}
                />
              )}
            </div>
          )}
          {!currentLog && isLogConnected && (
            <Text style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>
              Waiting for logs...
            </Text>
          )}
          {!isLogConnected && (
            <Text style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>
              Connecting to log stream...
            </Text>
          )}
        </div>
      </Popover>

      {/* Right Section - Context & Stats */}
      <Space size="large">
        {/* Token Count */}
        {tokenCount > 0 && (
          <Tooltip title={`Total tokens in conversation: ${tokenCount.toLocaleString()}`}>
            <Tag className="text-xs">
              {formatNumber(tokenCount)} tokens
            </Tag>
          </Tooltip>
        )}

        {/* File Count, Total Size & Directory */}
        <div className="flex items-center gap-2">
          <Tooltip title={`${fileCount} files in context${totalSize > 0 ? `, total size: ${formatFileSize(totalSize)}` : ''}`}>
            <div className="flex items-center gap-1">
              <FileTextOutlined className="text-gray-500" />
              <Text className="text-xs text-gray-600 dark:text-gray-400">
                Files: {fileCount}
                {totalSize > 0 && (
                  <span className="ml-1 text-gray-500">
                    ({formatFileSize(totalSize)})
                  </span>
                )}
              </Text>
            </div>
          </Tooltip>

          <Tooltip title={`Current directory: ${directory}`}>
            <Button
              type="text"
              size="small"
              className="!p-0 !h-auto"
              onClick={onOpenDirectory}
            >
              <div className="flex items-center gap-1">
                <FolderOpenOutlined className="text-gray-500" />
                <Text className="text-xs text-gray-600 dark:text-gray-400 max-w-[200px] truncate">
                  Directory: {directory}
                </Text>
              </div>
            </Button>
          </Tooltip>
        </div>
      </Space>
    </div>
  );
};

export default StatusBar;