import React from 'react';
import type { AgentPrompt } from '../../types';
import { Layout, Button, Select, Typography, Tooltip, Dropdown } from 'antd';
import {
  MoonOutlined,
  SunOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  MessageOutlined,
  FileTextOutlined,
  BookOutlined,
  PlayCircleOutlined,
  CodeOutlined,
  BgColorsOutlined,
  MoreOutlined,
  DownOutlined,
  EditOutlined,
  FileSearchOutlined,
} from '@ant-design/icons';
import { useTheme } from '../../themes';

const { Header: AntHeader } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

interface HeaderProps {
  onSetContext: () => void;
  onNewConversation: () => void;
  onEditFile: () => void;
  onOpenSettings: () => void;
  onToggleTheme: () => void;
  onOpenThemePicker: () => void;
  onSystemMessage: () => void;
  onAbout: () => void;
  onCodeFragments: () => void;
  onGenerateDocumentation: () => void;
  currentSystem?: string;
  onSystemChange: (system: string) => void;
  onRunSystemPrompt: (systemName: string) => void;
  agentPrompts?: AgentPrompt[];
}

export const Header: React.FC<HeaderProps> = ({
  onSetContext,
  onNewConversation,
  onEditFile,
  onOpenSettings,
  onToggleTheme,
  onOpenThemePicker,
  onSystemMessage,
  onAbout,
  onCodeFragments,
  onGenerateDocumentation,
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
    <AntHeader 
      className="!px-8 !h-20 flex items-center justify-between border-b"
      style={{
        background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        borderColor: '#e2e8f0',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
      }}
    >
      {/* Left Section - Branding */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3">
          <div 
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: '12px',
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.25)',
            }}
          >
            <span style={{ fontSize: '24px' }}>🧠</span>
          </div>
          <div>
            <Title level={3} className="!mb-0" style={{ color: '#1e293b', fontWeight: 700 }}>
              Whysper
            </Title>
            <Text style={{ color: '#64748b', fontSize: '12px', fontWeight: 500 }}>
              AI Code Assistant
            </Text>
          </div>
        </div>
      </div>

      {/* Center Section - System Selection */}
      <div className="flex items-center flex-1 justify-center max-w-2xl mx-8">
        {/* System Selection */}
        <div className="flex flex-col w-full">
          <span 
            className="text-xs mb-2"
            style={{ color: '#64748b', fontWeight: 600, letterSpacing: '0.5px' }}
          >
            ACTIVE AGENT
          </span>
          <Select
            value={currentSystem}
            onChange={onSystemChange}
            className="w-full"
            size="large"
            placeholder="Select agent prompt"
            dropdownStyle={{ width: '80vw', maxWidth: '1200px' }}
            optionLabelProp="label"
            style={{
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
            }}
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
              const shortName = displayName.length > 80 ? displayName.substring(0, 80) + '...' : displayName;
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
      <div className="flex items-center gap-3">
        {/* Primary Actions */}
        <div className="flex items-center gap-2">
          <Tooltip title="Set Context Files">
            <Button
              type="primary"
              icon={<FileTextOutlined />}
              onClick={onSetContext}
              size="large"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                borderRadius: '12px',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.25)',
                padding: '0 20px',
                height: '44px',
              }}
            >
              Set Context
            </Button>
          </Tooltip>
          
          <Tooltip title="Generate Documentation">
            <Button
              type="primary"
              icon={<FileSearchOutlined />}
              onClick={onGenerateDocumentation}
              size="large"
              style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: 'none',
                borderRadius: '12px',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.25)',
                padding: '0 20px',
                height: '44px',
              }}
            >
              Generate Docs
            </Button>
          </Tooltip>
          
          <Tooltip title="New Conversation">
            <Button
              icon={<MessageOutlined />}
              onClick={onNewConversation}
              size="large"
              style={{
                borderRadius: '12px',
                fontWeight: 500,
                height: '44px',
                padding: '0 20px',
                borderColor: '#e2e8f0',
                color: '#64748b',
              }}
            >
              New Chat
            </Button>
          </Tooltip>
          
          <Tooltip title="Edit File">
            <Button
              icon={<EditOutlined />}
              onClick={onEditFile}
              size="large"
              style={{
                borderRadius: '12px',
                fontWeight: 500,
                height: '44px',
                padding: '0 20px',
                borderColor: '#e2e8f0',
                color: '#64748b',
              }}
            >
              Edit File
            </Button>
          </Tooltip>
          
        </div>

        {/* Secondary Actions */}
        <div className="flex items-center gap-1">
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
                size="large"
                style={{
                  borderRadius: '10px',
                  color: '#64748b',
                  width: '44px',
                  height: '44px',
                }}
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
