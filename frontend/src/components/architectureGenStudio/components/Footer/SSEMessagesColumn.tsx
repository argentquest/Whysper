/**
 * SSE Messages Column Component
 * Displays real-time SSE messages from backend
 */

import React, { useEffect, useRef } from 'react';
import { Badge, Button, Space, Modal, Tag, theme } from 'antd';
import type { SSEMessage } from '../../types';

interface SSEMessagesColumnProps {
  messages: SSEMessage[];
  isConnected: boolean;
  unreadCount: number;
}

export const SSEMessagesColumn: React.FC<SSEMessagesColumnProps> = ({
  messages,
  isConnected,
  unreadCount,
}) => {
  const { token } = theme.useToken();
  const brandTokens = token as Record<string, string>;
  const badgeBg = brandTokens.colorBrandBadgeBg ?? token.colorPrimary ?? '#d71e28';
  const badgeText = brandTokens.colorBrandBadgeText ?? '#ffffff';
  const linkColor = brandTokens.colorBrandLink ?? token.colorLink ?? '#004c97';
  const successBg = brandTokens.colorBrandStatusSuccessBg ?? '#e6f3ec';
  const successBorder = brandTokens.colorBrandStatusSuccessBorder ?? '#8abf9b';
  const successText = brandTokens.colorBrandStatusSuccessText ?? '#1f4f2f';
  const errorBg = brandTokens.colorBrandStatusErrorBg ?? '#fbeaea';
  const errorBorder = brandTokens.colorBrandStatusErrorBorder ?? '#d71e28';
  const errorText = brandTokens.colorBrandStatusErrorText ?? '#8b0d16';

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleViewMessages = () => {
    Modal.info({
      title: 'Processing Messages',
      width: 600,
      content: (
        <div
          ref={scrollRef}
          style={{
            maxHeight: '400px',
            overflow: 'auto',
            fontFamily: 'monospace',
            fontSize: '12px',
          }}
        >
          {messages.length === 0 ? (
            <p>No messages yet</p>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} style={{ marginBottom: '8px', paddingBottom: '8px', borderBottom: '1px solid #f0f0f0' }}>
                <Tag color={msg.type === 'error' ? 'red' : 'blue'}>{msg.type}</Tag>
                <span style={{ fontSize: '11px', color: '#999', marginLeft: '8px' }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
                <div style={{ marginTop: '4px' }}>{msg.message}</div>
              </div>
            ))
          )}
        </div>
      ),
    });
  };

  return (
    <Space size={8}>
      <Badge
        count={unreadCount}
        color={badgeBg}
        style={{ color: badgeText }}
        offset={[-4, 4]}
      >
        <Button
          type="text"
          size="small"
          onClick={handleViewMessages}
          title={`${messages.length} messages`}
          style={{ color: linkColor, fontWeight: 600 }}
        >
          Messages ({messages.length})
        </Button>
      </Badge>
      <Tag
        style={{
          borderRadius: 999,
          border: `1px solid ${isConnected ? successBorder : errorBorder}`,
          backgroundColor: isConnected ? successBg : errorBg,
          color: isConnected ? successText : errorText,
          padding: '2px 12px',
        }}
      >
        {isConnected ? 'Connected' : 'Disconnected'}
      </Tag>
    </Space>
  );
};

export default SSEMessagesColumn;
