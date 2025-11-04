/**
 * SSE Messages Column Component
 * Displays real-time SSE messages from backend
 */

import React, { useEffect, useRef } from 'react';
import { Badge, Button, Space, Modal, Tag } from 'antd';
import { BgColorsOutlined } from '@ant-design/icons';
import { SSEMessage } from '../../types';

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
      <Badge count={unreadCount} offset={[-4, 4]}>
        <Button
          type="text"
          size="small"
          onClick={handleViewMessages}
          title={`${messages.length} messages`}
        >
          Messages ({messages.length})
        </Button>
      </Badge>
      <Tag color={isConnected ? 'green' : 'red'}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </Tag>
    </Space>
  );
};

export default SSEMessagesColumn;
