import React from 'react';
import { Tabs, Button, Space, Tooltip, Dropdown, Typography, theme as antdTheme } from 'antd';
import {
  PlusOutlined,
  SaveOutlined,
  CloseOutlined,
  MoreOutlined,
  MessageOutlined,
  ProjectOutlined,
  PartitionOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import type { Tab } from '../../types';
import { BrandColors } from 'branding';
const { Link } = Typography;

interface TabManagerProps {
  tabs: Tab[];
  activeTabId: string;
  onTabChange: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
  onTabSave: (tabId: string) => void;
  onNewTab: () => void;
  onNewDiagramWizardTab?: () => void;
  onNewArchStudioTab?: () => void;
  onTabsAction?: (action: string, tabId?: string) => void;
}

export const TabManager: React.FC<TabManagerProps> = ({
  tabs,
  activeTabId,
  onTabChange,
  onTabClose,
  onTabSave,
  onNewTab,
  onNewDiagramWizardTab,
  onNewArchStudioTab,
  onTabsAction,
}) => {
  const { token } = antdTheme.useToken();
  const brandTokens = token as Record<string, string>;
  const tabBackground = brandTokens.colorBrandHeaderBorder ?? BrandColors.secondary ?? '#f7b500';
  const tabBorderColor = brandTokens.colorBorder ?? 'rgba(0, 0, 0, 0.15)';
  const tabTextColor = brandTokens.colorText ?? BrandColors.text?.primary ?? '#231f20';
  const tabInactiveBg = brandTokens.colorBrandQuaternary ?? BrandColors.quaternary ?? '#fbd3a4';

  const handleTabEdit = (targetKey: React.MouseEvent | React.KeyboardEvent | string, action: 'add' | 'remove') => {
    if (action === 'add') {
      onNewTab();
    } else if (action === 'remove' && typeof targetKey === 'string') {
      onTabClose(targetKey);
    }
  };

  const getTabMenuItems = (tab: Tab): MenuProps['items'] => [
    {
      key: 'save',
      label: 'Save Tab',
      icon: <SaveOutlined />,
      onClick: () => onTabSave(tab.id),
    },
    {
      key: 'duplicate',
      label: 'Duplicate Tab',
      onClick: () => onTabsAction?.('duplicate', tab.id),
    },
    {
      type: 'divider',
    },
    {
      key: 'close',
      label: 'Close Tab',
      icon: <CloseOutlined />,
      onClick: () => onTabClose(tab.id),
      danger: true,
    },
    {
      key: 'close-others',
      label: 'Close Other Tabs',
      onClick: () => onTabsAction?.('close-others', tab.id),
    },
    {
      key: 'close-all',
      label: 'Close All Tabs',
      onClick: () => onTabsAction?.('close-all'),
      danger: true,
    },
  ];

  // New Tab Menu Items
  const newTabMenuItems: MenuProps['items'] = [
    {
      key: 'chat',
      label: 'New Chat',
      icon: <MessageOutlined />,
      onClick: () => onNewTab(),
    },
    {
      key: 'diagramWizard',
      label: 'Diagram Wizard',
      icon: <PartitionOutlined />,
      onClick: () => onNewDiagramWizardTab?.(),
      disabled: !onNewDiagramWizardTab,
    },
    {
      key: 'archStudio',
      label: 'Architecture Studio',
      icon: <ProjectOutlined />,
      onClick: () => onNewArchStudioTab?.(),
      disabled: !onNewArchStudioTab,
    },
  ];

  const tabItems = tabs.map((tab) => {
    const isDirty = tab.isDirty;
    
    return {
      key: tab.id,
      label: (
        <div className="flex items-center gap-2 min-w-0">
          <span className="truncate max-w-[120px]">
            {tab.title}
            {isDirty && <span className="text-orange-500">*</span>}
          </span>
          
          <div className="flex items-center gap-1 ml-auto">
            {isDirty && (
              <Tooltip title="Save Tab">
                <Button
                  type="text"
                  size="small"
                  icon={<SaveOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    onTabSave(tab.id);
                  }}
                  className="!p-0 !w-4 !h-4 !min-w-0 opacity-60 hover:opacity-100"
                />
              </Tooltip>
            )}
            
            <Dropdown
              menu={{ items: getTabMenuItems(tab) }}
              trigger={['click']}
              placement="bottomRight"
            >
              <Button
                type="text"
                size="small"
                icon={<MoreOutlined />}
                onClick={(e) => e.stopPropagation()}
                className="!p-0 !w-4 !h-4 !min-w-0 opacity-60 hover:opacity-100"
              />
            </Dropdown>
          </div>
        </div>
      ),
      children: null, // Content will be handled by parent component
    };
  });

  const containerStyle: React.CSSProperties & Record<string, string> = {
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.04)',
    borderBottom: `1px solid ${tabBorderColor}`,
    backgroundColor: tabBackground,
    '--wf-tab-inactive-bg': tabInactiveBg,
    '--wf-tab-text-color': tabTextColor,
  };

  return (
    <div 
      className="border-b border-gray-200 dark:border-gray-700"
      style={containerStyle}
    >
      <div className="flex items-center justify-between px-6 pt-3 pb-0">
        <Tabs
          type="editable-card"
          activeKey={activeTabId}
          onChange={onTabChange}
          onEdit={handleTabEdit}
          items={tabItems}
          className="flex-1 !mb-0"
          rootClassName="wf-tabs"
          size="small"
          hideAdd={true}
          tabBarStyle={{ margin: 0 }}
        />
        
        <Space className="ml-4" size={16}>
          <Tooltip title="Open a new tab">
            <Dropdown
              menu={{ items: newTabMenuItems }}
              trigger={['click']}
              placement="bottomLeft"
            >
              <Link
                onClick={(e) => e.preventDefault()}
                className="font-semibold"
                style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: tabTextColor }}
              >
                <PlusOutlined />
                New Tab
              </Link>
            </Dropdown>
          </Tooltip>
          
          <Tooltip title={tabs.length <= 1 ? 'At least one tab must remain open' : 'Close the current tab'}>
            <Link
              onClick={(e) => {
                e.preventDefault();
                if (tabs.length <= 1) return;
                onTabClose(activeTabId);
              }}
              aria-disabled={tabs.length <= 1}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                color: tabs.length <= 1 ? 'rgba(0,0,0,0.35)' : tabTextColor,
                pointerEvents: tabs.length <= 1 ? 'none' : 'auto',
                fontWeight: 600,
              }}
            >
              <CloseOutlined />
              Close Tab
            </Link>
          </Tooltip>
        </Space>
      </div>
    </div>
  );
};

export default TabManager;
