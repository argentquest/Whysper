/**
 * StatusBar Component
 *
 * This module exports the StatusBar component for the application.
 */
import {
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  HistoryOutlined,
  LoadingOutlined,
} from '@ant-design/icons'
import { Badge, Popover, Typography } from 'antd'
import { BrandColors } from 'branding'
import React, { useEffect, useRef,useState } from 'react'

import { getApiBaseUrl } from '../../utils/apiBase'

const { Text } = Typography

/**
 * LogEvent type definition
 *
 * Describes the structure and properties of LogEvent
 * @interface LogEvent
 * @property {string} timestamp - The timestamp of the log event
 * @property {string} level - The log level (INFO, WARNING, ERROR)
 * @property {string} message - The log message
 * @property {string} logger - The logger name
 */
interface LogEvent {
  timestamp: string
  level: string
  message: string
  logger: string
}

/**
 * StatusBarProps type definition
 *
 * Describes the structure and properties of StatusBarProps
 * @interface StatusBarProps
 * @property {'ready' | 'loading' | 'error'} status - The current status of the application
 * @property {boolean} [isProcessing] - Whether AI response is being processed
 * @property {string} [errorMessage] - Error message if status is error
 * @property {string} [conversationId] - The ID of the current conversation
 * @property {string} [model] - The current AI model name
 */
interface StatusBarProps {
  status: 'ready' | 'loading' | 'error'
  isProcessing?: boolean
  errorMessage?: string
  conversationId?: string // For session-specific log filtering
  model?: string
}

/**
 * StatusBar component
 *
 * Displays status information at the bottom of the application window.
 * Includes:
 * - Application status (Ready, Loading, Error)
 * - Active provider and model
 * - Token usage
 * - File context statistics
 * - Real-time log viewer
 *
 * @param {StatusBarProps} props - Component props
 * @returns {JSX.Element} Rendered status bar
 */
export const StatusBar: React.FC<StatusBarProps> = ({
  status,
  isProcessing = false,
  errorMessage,
  conversationId,
  model = 'Not configured',
}) => {
  // Real-time log streaming state
  const [currentLog, setCurrentLog] = useState<LogEvent | null>(null)
  const [logHistory, setLogHistory] = useState<LogEvent[]>([])
  const [isLogConnected, setIsLogConnected] = useState(false)
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  // Track detected states from logs
  const [detectedActivity, setDetectedActivity] = useState<string>('')

  // Debug: Log status changes
  useEffect(() => {
    console.log('🔵 [STATUS BAR] Status changed:', status)
  }, [status])

  // Detect activity patterns from log messages
  useEffect(() => {
    if (!currentLog) return

    const message = currentLog.message.toLowerCase()

    // Detect AI API calls
    if (
      message.includes('calling ai provider') ||
      message.includes('sending request to') ||
      message.includes('openrouter') ||
      message.includes('making api call')
    ) {
      setDetectedActivity('ai_call')
    }
    // Detect response processing
    else if (
      message.includes('received response') ||
      message.includes('processing response') ||
      message.includes('parsing ai response')
    ) {
      setDetectedActivity('processing')
    }
    // Detect errors
    else if (
      currentLog.level === 'ERROR' ||
      message.includes('error') ||
      message.includes('failed')
    ) {
      setDetectedActivity('error')
    }
    // Detect completion
    else if (
      message.includes('completed') ||
      message.includes('finished') ||
      message.includes('success')
    ) {
      setDetectedActivity('ready')
    }
  }, [currentLog])

  // Connect to SSE log stream on mount (reconnect when conversationId changes)
  useEffect(() => {
    const API_BASE_URL = getApiBaseUrl()

    // Add session_id parameter for session-specific log filtering
    const url = conversationId
      ? `${API_BASE_URL}/chat/logs/stream?session_id=${conversationId}`
      : `${API_BASE_URL}/chat/logs/stream`

    const eventSource = new EventSource(url)
    eventSourceRef.current = eventSource

    eventSource.addEventListener('connected', () => {
      setIsLogConnected(true)
    })

    eventSource.addEventListener('log', (event) => {
      try {
        const logEvent: LogEvent = JSON.parse(event.data)
        setCurrentLog(logEvent)

        // Add to history buffer (keep last 30)
        setLogHistory((prev) => {
          const newHistory = [...prev, logEvent]
          // Keep only last 30 logs
          return newHistory.slice(-30)
        })
      } catch (error) {
        console.error('❌ [STATUS BAR] Failed to parse log event:', error)
      }
    })

    eventSource.onerror = (error) => {
      console.error('❌ [STATUS BAR] Connection error:', error)
      setIsLogConnected(false)
    }

    return () => {
      eventSource.close()
      // Clear history when disconnecting
      setLogHistory([])
    }
  }, [conversationId]) // Reconnect when conversationId changes

  const getStatusIcon = () => {
    switch (status) {
      case 'ready':
        return <CheckCircleOutlined className="text-green-500" />
      case 'loading':
        return <LoadingOutlined className="text-blue-500" />
      case 'error':
        return <ExclamationCircleOutlined className="text-red-500" />
      default:
        return <CheckCircleOutlined className="text-gray-500" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'ready':
        return 'Ready'
      case 'loading':
        return 'Processing...'
      case 'error':
        return errorMessage || 'Error'
      default:
        return 'Unknown'
    }
  }

  const getWaitingStatus = () => {
    // Use detected activity from logs if available
    if (detectedActivity === 'ai_call') {
      return 'Calling AI Provider'
    } else if (detectedActivity === 'processing') {
      return 'Processing AI Response'
    } else if (detectedActivity === 'error') {
      return 'Error Detected'
    }

    // Fall back to prop-based status
    if (status === 'loading') {
      if (isProcessing) {
        return 'Processing AI Response'
      }
      return 'Waiting for AI Response'
    } else if (status === 'error') {
      return 'Error - Ready for Input'
    }
    return 'Ready for Input'
  }

  const getWaitingStatusColor = () => {
    // Use detected activity from logs if available
    if (detectedActivity === 'ai_call') {
      return '#1890ff' // Blue - waiting for AI
    } else if (detectedActivity === 'processing') {
      return '#faad14' // Orange - processing
    } else if (detectedActivity === 'error') {
      return '#ff4d4f' // Red - error
    } else if (detectedActivity === 'ready') {
      return '#52c41a' // Green - ready
    }

    // Fall back to prop-based status
    if (status === 'loading') {
      if (isProcessing) {
        return '#faad14' // Orange - processing
      }
      return '#1890ff' // Blue - waiting
    } else if (status === 'error') {
      return '#ff4d4f' // Red - error
    }
    return '#52c41a' // Green - ready
  }

  // Log history popover content (reversed to show newest first)
  const logHistoryContent = (
    <div style={{ width: '1000px', maxHeight: '600px', overflowY: 'auto' }}>
      {logHistory.length === 0 ? (
        <Text style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>No logs yet</Text>
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
  )

  return (
    <div
      className="flex h-12 items-center justify-between border-t border-gray-200 px-6 dark:border-gray-700"
      style={{
        backgroundColor: BrandColors.tertiary,
        boxShadow: '0 -1px 4px rgba(0, 0, 0, 0.04)',
        borderTop: `1px solid ${BrandColors.tertiary}`,
        fontSize: '14px',
      }}
    >
      {/* Left Section - Status */}
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <Text className="font-medium" style={{ fontSize: '14px' }}>
          {getStatusText()}
        </Text>
      </div>

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
            margin: '0 16px',
            overflow: 'hidden',
            cursor: logHistory.length > 0 ? 'pointer' : 'default',
          }}
        >
          {currentLog && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Badge status={isLogConnected ? 'processing' : 'default'} text="" />
              <Text style={{ fontSize: '13px', color: '#64748b', fontFamily: 'monospace' }}>
                {new Date(currentLog.timestamp).toLocaleTimeString()}
              </Text>
              <Text
                style={{
                  fontSize: '13px',
                  color:
                    currentLog.level === 'ERROR'
                      ? '#ef4444'
                      : currentLog.level === 'WARNING'
                        ? '#faad14'
                        : '#10b981',
                  fontWeight: 500,
                }}
              >
                {currentLog.level}
              </Text>
              <Text
                style={{
                  fontSize: '13px',
                  color: currentLog.level === 'ERROR' ? '#dc2626' : '#1e293b',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  fontFamily: 'monospace',
                  fontWeight: currentLog.level === 'ERROR' ? 600 : 400,
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
            <Text style={{ fontSize: '13px', color: '#94a3b8', fontStyle: 'italic' }}>
              Waiting for logs...
            </Text>
          )}
          {!isLogConnected && (
            <Text style={{ fontSize: '13px', color: '#94a3b8', fontStyle: 'italic' }}>
              Connecting to log stream...
            </Text>
          )}
        </div>
      </Popover>

      {/* Right Section - Waiting Status & Model */}
      <div className="flex items-center gap-4">
        <Text className="font-medium" style={{ color: getWaitingStatusColor(), fontSize: '14px' }}>
          {getWaitingStatus()}
        </Text>
        <div className="flex items-center gap-2">
          <ApiOutlined className="text-gray-500" />
          <Text className="font-medium" style={{ fontSize: '14px', color: '#64748b' }}>
            {model}
          </Text>
        </div>
      </div>
    </div>
  )
}

export default StatusBar
