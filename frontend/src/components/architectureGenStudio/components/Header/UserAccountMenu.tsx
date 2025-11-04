/**
 * User Account Menu Component
 * User profile and logout actions
 */

import React from 'react';
import { Dropdown, Avatar, Menu } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';

interface UserAccountMenuProps {
  onLogout: () => void;
}

export const UserAccountMenu: React.FC<UserAccountMenuProps> = ({ onLogout }) => {
  const items = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: onLogout,
    },
  ];

  return (
    <Dropdown menu={{ items }} trigger={['click']} placement="bottomRight">
      <Avatar
        size={32}
        icon={<UserOutlined />}
        style={{ cursor: 'pointer', backgroundColor: 'var(--ant-color-primary)' }}
      />
    </Dropdown>
  );
};

export default UserAccountMenu;
