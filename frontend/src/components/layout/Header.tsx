import React from 'react';
import ApiService from '../../services/api';
import type { AgentPrompt } from '../../types';
import { Layout, Button, Select, Space, Typography, Tooltip, Dropdown, Menu } from 'antd';
import {
  MoonOutlined,
  SunOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  MessageOutlined,
  SaveOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  BookOutlined,
  PlayCircleOutlined,
  CodeOutlined,
  BgColorsOutlined,
  MoreOutlined,
  DownOutlined,
} from '@ant-design/icons';
import { useTheme } from '../../themes';

const { Header: AntHeader } = Layout;
const { Title } = Typography;
const { Option } = Select;

interface HeaderProps {
  onSetContext: () => void;
  onNewConversation: () => void;
  onSaveHistory: () => void;
  onLoadHistory: () => void;
  onOpenSettings: () => void;
  onToggleTheme: () => void;
  onOpenThemePicker: () => void;
  onSystemMessage: () => void;
  onAbout: () => void;
  onCodeFragments: () => void;
  currentSystem?: string;
  onSystemChange: (system: string) => void;
  onRunSystemPrompt: (systemName: string) => void;
  agentPrompts?: AgentPrompt[];
}

export const Header: React.FC<HeaderProps> = ({
  onSetContext,
  onNewConversation,
  onSaveHistory,
  onLoadHistory,
  onOpenSettings,
  onToggleTheme,
  onOpenThemePicker,
  onSystemMessage,
  onAbout,
  onCodeFragments,
  currentSystem = 'default',
  onSystemChange,
  onRunSystemPrompt,
  agentPrompts = [],
}) => {
  const { theme } = useTheme();

  // Use agent prompts instead of hardcoded system options
  const systemOptions = agentPrompts.length > 0
    ? agentPrompts.map(prompt => prompt.name)
    : ['default', 'coding', 'documentation', 'refactoring', 'debugging'];



  return (
    <AntHeader className="!px-6 !h-16 flex items-center justify-between bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      {/* Left Section - Branding */}
      <div className="flex items-center">
        <Title level={3} className="!mb-0 !text-gray-800 dark:!text-white">
          🧠 Whysper
        </Title>
      </div>

      {/* Center Section - System Selection */}
      <div className="flex items-center">
        {/* System Selection */}
        <div className="flex flex-col">
          <span className="text-xs text-gray-500 dark:text-gray-400 mb-1">Agent:</span>
          <Select
            value={currentSystem}
            onChange={onSystemChange}
            className="min-w-[400px]"
            size="small"
            placeholder="Select agent prompt"
            dropdownStyle={{ width: '80vw', maxWidth: '1200px' }}
            optionLabelProp="label"
            dropdownRender={(menu) => (
              <div>
                {/* Table Header */}
                <div className="py-3 px-4 bg-gray-50 dark:bg-gray-700 border-b-2 border-gray-300 dark:border-gray-500">
                  <div className="grid grid-cols-12 gap-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                    <div className="col-span-3 border-r border-gray-300 dark:border-gray-500 pr-4">Agent Name</div>
                    <div className="col-span-6 border-r border-gray-300 dark:border-gray-500 pr-4">Description</div>
                    <div className="col-span-3">Categories & File</div>
                  </div>
                </div>
                {menu}
              </div>
            )}
          >
            {systemOptions.map(system => {
              const prompt = agentPrompts.find(p => p.name === system);
              const displayName = prompt ? prompt.title : system.charAt(0).toUpperCase() + system.slice(1);
              const shortName = displayName.length > 35 ? displayName.substring(0, 35) + '...' : displayName;
              const description = prompt?.description || '';
              const categories = prompt?.category || [];
              
              return (
                <Option 
                  key={system} 
                  value={system}
                  label={shortName}
                >
                  <div className="py-5 px-4 border-b border-gray-200 dark:border-gray-600 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-700 min-h-[80px]">
                    <div className="grid grid-cols-12 gap-4 items-start">
                      {/* Agent Name & Title */}
                      <div className="col-span-3 border-r border-gray-200 dark:border-gray-600 pr-4">
                        <div className="font-semibold text-sm text-gray-900 dark:text-white leading-tight break-words">
                          {displayName}
                        </div>
                        <div className="text-xs text-blue-600 dark:text-blue-400 font-medium mt-1 break-words">
                          {system}
                        </div>
                      </div>
                      
                      {/* Description */}
                      <div className="col-span-6 border-r border-gray-200 dark:border-gray-600 pr-4">
                        <div className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed break-words whitespace-pre-wrap">
                          {description || 'No description available'}
                        </div>
                      </div>
                      
                      {/* Categories & File */}
                      <div className="col-span-3">
                        {categories.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-2">
                            {categories.slice(0, 4).map((cat, idx) => (
                              <span key={idx} className="inline-block px-2 py-1 bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200 text-xs rounded-md font-medium break-words">
                                {cat}
                              </span>
                            ))}
                            {categories.length > 4 && (
                              <span className="text-xs text-gray-500 px-1">+{categories.length - 4} more</span>
                            )}
                          </div>
                        )}
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-600 px-2 py-1 rounded break-words flex-1">
                            📄 {prompt?.filename || `${system}.md`}
                          </div>
                          <Tooltip title={`Run ${displayName} system prompt`}>
                            <Button
                              type="primary"
                              size="small"
                              icon={<PlayCircleOutlined />}
                              className="!bg-green-600 !border-green-600 hover:!bg-green-700"
                              onClick={(e) => {
                                e.stopPropagation();
                                onRunSystemPrompt(system);
                              }}
                            >
                              Run
                            </Button>
                          </Tooltip>
                        </div>
                      </div>
                    </div>
                  </div>
                </Option>
              );
            })}
          </Select>
        </div>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center">
        {/* Primary Actions */}
        <Space.Compact>
          <Tooltip title="Set Context">
            <Button
              type="primary"
              icon={<FileTextOutlined />}
              onClick={onSetContext}
              className="!bg-purple-600 !border-purple-600 hover:!bg-purple-700"
            >
              Set Context
            </Button>
          </Tooltip>
          
          
          <Tooltip title="New Conversation">
            <Button
              icon={<MessageOutlined />}
              onClick={onNewConversation}
              className="!ml-2"
            >
              New Conversation
            </Button>
          </Tooltip>
        </Space.Compact>

        {/* Secondary Actions */}
        <div className="flex items-center ml-4 gap-2">
          {/* File Actions Group */}
          <Dropdown
            menu={{
              items: [
                {
                  key: 'save-history',
                  label: 'Save History',
                  icon: <SaveOutlined />,
                  onClick: onSaveHistory,
                },
                {
                  key: 'load-history',
                  label: 'Load History',
                  icon: <FolderOpenOutlined />,
                  onClick: onLoadHistory,
                },
              ],
            }}
            trigger={['click']}
            placement="bottomRight"
          >
            <Tooltip title="File Actions">
              <Button
                type="text"
                icon={<SaveOutlined />}
                size="small"
              >
                <DownOutlined style={{ fontSize: '10px' }} />
              </Button>
            </Tooltip>
          </Dropdown>
          
          {/* Theme Actions Group */}
          <Dropdown
            menu={{
              items: [
                {
                  key: 'toggle-theme',
                  label: `Switch to ${theme === 'light' ? 'Dark' : 'Light'} Theme`,
                  icon: theme === 'light' ? <MoonOutlined /> : <SunOutlined />,
                  onClick: onToggleTheme,
                },
                {
                  key: 'theme-picker',
                  label: 'Choose Theme',
                  icon: <BgColorsOutlined />,
                  onClick: onOpenThemePicker,
                },
              ],
            }}
            trigger={['click']}
            placement="bottomRight"
          >
            <Tooltip title="Theme Options">
              <Button
                type="text"
                icon={<BgColorsOutlined />}
                size="small"
              >
                <DownOutlined style={{ fontSize: '10px' }} />
              </Button>
            </Tooltip>
          </Dropdown>
          
          {/* Tools Group */}
          <Dropdown
            menu={{
              items: [
                {
                  key: 'system-message',
                  label: 'System Message',
                  icon: <BookOutlined />,
                  onClick: onSystemMessage,
                },
                {
                  key: 'code-fragments',
                  label: 'Code Fragments',
                  icon: <CodeOutlined />,
                  onClick: onCodeFragments,
                },
                {
                  key: 'settings',
                  label: 'Settings',
                  icon: <SettingOutlined />,
                  onClick: onOpenSettings,
                },
                {
                  type: 'divider',
                },
                {
                  key: 'about',
                  label: 'About',
                  icon: <InfoCircleOutlined />,
                  onClick: onAbout,
                },
              ],
            }}
            trigger={['click']}
            placement="bottomRight"
          >
            <Tooltip title="More Options">
              <Button
                type="text"
                icon={<MoreOutlined />}
                size="small"
              >
                <DownOutlined style={{ fontSize: '10px' }} />
              </Button>
            </Tooltip>
          </Dropdown>
        </div>
      </div>
    </AntHeader>
  );
};

export default Header;