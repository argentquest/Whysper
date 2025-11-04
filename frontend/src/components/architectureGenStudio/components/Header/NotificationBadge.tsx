/**
 * Notification Badge Component
 * Displays notification count
 */

import React from 'react';
import { Badge, Button } from 'antd';
import { BellOutlined } from '@ant-design/icons';

interface NotificationBadgeProps {
  count: number;
}

export const NotificationBadge: React.FC<NotificationBadgeProps> = ({ count }) => {
  return (
    <Badge count={count} offset={[-8, 8]}>
      <Button
        type="text"
        icon={<BellOutlined style={{ fontSize: '18px' }} />}
        size="large"
      />
    </Badge>
  );
};

export default NotificationBadge;
