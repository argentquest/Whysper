/**
 * Header Component
 * 
 * This module exports the Header component for the application.
 */
// @ts-nocheck
import React from 'react';
import type { AgentPrompt } from '../../types';
import { Layout, Button, Select, Typography, Tooltip, Dropdown, theme as antdTheme } from 'antd';
import {
  MoonOutlined,
  SunOutlined,
  SettingOutlined,
  InfoCircleOutlined,
  BookOutlined,
  PlayCircleOutlined,
  CodeOutlined,
  BgColorsOutlined,
  QuestionCircleOutlined,
  MenuOutlined,
} from '@ant-design/icons';
import { useTheme } from '../../themes';
import { BrandColors, Brand } from 'branding';

const { Header: AntHeader } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;

/**
 * HeaderProps type definition
 * 
 * Describes the structure and properties of HeaderProps
 * @interface HeaderProps
 * @property {Function} onSetContext - Callback to open context modal
 * @property {Function} onNewConversation - Callback to start new conversation
 * @property {Function} onNewSession - Callback to start new session
 * @property {Function} onEditFile - Callback to edit file
 * @property {Function} onOpenSettings - Callback to open settings
 * @property {Function} onToggleTheme - Callback to toggle theme
 * @property {Function} onOpenThemePicker - Callback to open theme picker
 * @property {Function} onSystemMessage - Callback to open system message modal
 * @property {Function} onAbout - Callback to open about modal
 * @property {Function} onCodeFragments - Callback to open code fragments
 * @property {Function} onGenerateDocumentation - Callback to generate docs
 * @property {Function} onHelp - Callback to open help modal
 * @property {Function} onMermaidTester - Callback to open Mermaid tester
 * @property {Function} onD2Tester - Callback to open D2 tester
 * @property {Function} onDiagramWizard - Callback to open Diagram Wizard
 * @property {Function} onArchStudio - Callback to open Architecture Studio
 * @property {string} [currentSystem] - Currently selected system prompt
 * @property {Function} onSystemChange - Callback when system prompt changes
 * @property {Function} onRunSystemPrompt - Callback to execute system prompt
 * @property {AgentPrompt[]} [agentPrompts] - List of available agent prompts
 */
interface HeaderProps {
  onSetContext: () => void;
  onNewConversation: () => void;
  onNewSession: () => void;
  onEditFile: () => void;
  onOpenSettings: () => void;
  onToggleTheme: () => void;
  onOpenThemePicker: () => void;
  onSystemMessage: () => void;
  onAbout: () => void;
  onCodeFragments: () => void;
  onGenerateDocumentation: () => void;
  onHelp: () => void;
  onMermaidTester: () => void;
  onD2Tester: () => void;
  onDiagramWizard: () => void;
  onArchStudio: () => void;
  currentSystem?: string;
  onSystemChange: (system: string) => void;
  onRunSystemPrompt: (systemName: string) => void;
  agentPrompts?: AgentPrompt[];
}

/**
 * Header component
 *
 * Main application header containing:
 * - Branding/Logo
 * - Agent/System Prompt selector
 * - Quick actions toolbar
 * - Settings and tools menu
 *
 * @param {HeaderProps} props - Component props
 * @returns {JSX.Element} Rendered header
 */
export const Header: React.FC<HeaderProps> = ({
  onSetContext,
  onNewConversation,
  onNewSession,
  onEditFile,
  onOpenSettings,
  onToggleTheme,
  onOpenThemePicker,
  onSystemMessage,
  onAbout,
  onCodeFragments,
  onGenerateDocumentation,
  onHelp,
  onMermaidTester,
  onD2Tester,
  onDiagramWizard,
  onArchStudio,
  currentSystem = 'default',
  onSystemChange,
  onRunSystemPrompt,
  agentPrompts = [],
}) => {
  const { theme } = useTheme();
  const { token } = antdTheme.useToken();
  const brandTokens = token as Record<string, string>;

  // Use agent prompts instead of hardcoded system options
  const systemOptions = agentPrompts.length > 0
    ? agentPrompts.map(prompt => prompt.name)
    : ['default', 'coding', 'documentation', 'refactoring', 'debugging'];

  const headerBg = brandTokens.colorBrandHeaderBg ?? BrandColors.primary;
  const headerBorder = brandTokens.colorBrandHeaderBorder ?? BrandColors.secondary ?? BrandColors.primary;
  const headerText = brandTokens.colorBrandHeaderText ?? '#ffffff';
  const mastheadActions = [
    { label: 'Set Context', handler: onSetContext, tooltip: 'Select files to give the assistant context' },
    { label: 'New Session', handler: onNewSession, tooltip: 'Reset everything and start fresh' },
    { label: 'Generate Docs', handler: onGenerateDocumentation, tooltip: 'Create documentation from the current context' },
    { label: 'New Chat', handler: onNewConversation, tooltip: 'Open a new conversation tab' },
    { label: 'Edit File', handler: onEditFile, tooltip: 'Jump into edit mode for a file' },
    { label: 'ArchStudio', handler: onArchStudio, tooltip: 'Open Architecture Studio' },
    { label: 'DiagramWizard', handler: onDiagramWizard, tooltip: 'Launch Diagram Wizard' },
  ];
  const actionSurface = brandTokens.colorBgContainer ?? BrandColors.brand?.white ?? '#ffffff';
  const actionText = brandTokens.colorText ?? BrandColors.text?.primary ?? '#231f20';
  const actionSubtleText = brandTokens.colorTextSecondary ?? BrandColors.text?.secondary ?? '#5d5550';
  const neutralBorder = brandTokens.colorBorder ?? BrandColors.neutral?.stroke ?? '#d9d9d9';
  const containerPadding = 'clamp(16px, 4vw, 48px)';
  const toolMenuItems = [
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
      key: 'mermaid-tester',
      label: 'Mermaid Tester',
      icon: <PlayCircleOutlined />,
      onClick: onMermaidTester,
    },
    {
      key: 'd2-tester',
      label: 'D2 Tester',
      icon: <PlayCircleOutlined />,
      onClick: onD2Tester,
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
    {
      key: 'help',
      label: 'Help',
      icon: <QuestionCircleOutlined />,
      onClick: onHelp,
    },
  ];

  const renderBrandLogo = () => {
    if (Brand.logo?.type === 'image' && Brand.logo.src) {
      return (
        <img
          src={Brand.logo.src}
          alt={Brand.logo.alt || Brand.name}
          style={{ height: 24, width: 'auto', display: 'block' }}
        />
      );
    }
    return (
      <div
        style={{
          backgroundColor: Brand.logo?.backgroundColor ?? headerBorder,
          borderRadius: '12px',
          width: 48,
          height: 48,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: 24,
          boxShadow: `0 4px 12px ${BrandColors.primary}40`,
        }}
      >
        {Brand.logo?.emoji ?? 'WF'}
      </div>
    );
  };

  const renderAgentSelector = (labelColor: string, labelOpacity = 0.9) => (
    <div className="flex flex-col w-full">
      <span
        className="text-xs mb-2 tracking-wide"
        style={{ color: labelColor, fontWeight: 600, letterSpacing: '0.5px', opacity: labelOpacity }}
      >
        ACTIVE AGENT
      </span>
      <Select
        value={currentSystem}
        onChange={onSystemChange}
        className="w-full"
        size="large"
        placeholder="Select agent prompt"
        styles={{
          popup: {
            root: { width: '80vw', maxWidth: '1200px' },
          },
        }}
        optionLabelProp="label"
        style={{
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
          background: brandTokens.colorBgElevated ?? '#ffffff',
        }}
        popupRender={(menu) => (
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
          const shortName = displayName.length > 80 ? `${displayName.substring(0, 80)}...` : displayName;
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
  );


  return (
    <AntHeader
      className="!p-0 border-b"
      style={{
        background: 'transparent',
        borderColor: headerBorder,
        borderBottomWidth: 4,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
      }}
    >
      <div style={{ background: headerBg }}>
        <div
          style={{
            width: '100%',
            margin: 0,
            height: 75,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: `0 ${containerPadding}`,
            gap: '24px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, minWidth: 0 }}>
            {renderBrandLogo()}
            <div>
              <Title level={3} className="!mb-0" style={{ color: headerText, fontWeight: 700 }}>
                {Brand.tagline}
              </Title>
            </div>
          </div>

          <div className="hidden lg:flex flex-1 max-w-3xl px-6">
            {renderAgentSelector(headerText)}
          </div>

          <div className="flex items-center gap-3">
            <nav
              aria-label="Quick Actions"
              className="wf-header-actions"
              style={{
                alignItems: 'center',
                gap: 16,
                color: headerText,
                fontWeight: 600,
                flexWrap: 'wrap',
                justifyContent: 'flex-end',
                display: 'flex',
              }}
            >
              <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
                {mastheadActions.map((item) => (
                  <li key={item.label}>
                    <Tooltip title={item.tooltip}>
                      <button
                        type="button"
                        onClick={item.handler}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: headerText,
                          fontSize: 13,
                          letterSpacing: 0.5,
                          cursor: 'pointer',
                          padding: 0,
                          fontWeight: 600,
                          textDecoration: 'none',
                        }}
                      >
                        {item.label}
                      </button>
                    </Tooltip>
                  </li>
                ))}
                <li>
                  <Tooltip title="Open tools & settings">
                    <Dropdown
                      menu={{ items: toolMenuItems }}
                      trigger={['click']}
                    >
                      <button
                        type="button"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: headerText,
                          fontSize: 13,
                          letterSpacing: 0.5,
                          cursor: 'pointer',
                          fontWeight: 600,
                        }}
                      >
                        Setting
                      </button>
                    </Dropdown>
                  </Tooltip>
                </li>
              </ul>
            </nav>

            <Button
              className="lg:hidden"
              type="text"
              icon={<MenuOutlined />}
              aria-label="Open navigation menu"
              style={{
                color: headerText,
                borderRadius: 999,
                width: 44,
                height: 44,
              }}
            />
          </div>
        </div>
      </div>
      <div style={{ height: 4, background: headerBorder }} />

      <div style={{ background: actionSurface, borderBottom: `1px solid ${neutralBorder}` }}>
        <div
          style={{
            width: '100%',
            margin: 0,
            padding: `20px ${containerPadding}`,
            display: 'flex',
            flexWrap: 'wrap',
            gap: '24px',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* Left Section - Branding */}
          <div className="flex flex-col gap-1 flex-1 min-w-[220px]">
            <Title level={4} className="!mb-0" style={{ color: actionText, fontWeight: 600 }}>
              {Brand.name}
            </Title>
            <Text style={{ color: actionSubtleText, fontSize: '13px', fontWeight: 500 }}>
              {Brand.description}
            </Text>
          </div>

          {/* Center Section - System Selection (mobile / tablet) */}
          <div className="flex flex-col flex-1 min-w-[280px] max-w-2xl lg:hidden">
            {renderAgentSelector(actionSubtleText, 0.8)}
          </div>

          {/* Right Section placeholder to maintain spacing */}
          <div className="flex flex-1 justify-end items-center min-w-[160px]" />
        </div>
      </div>
    </AntHeader>
  );
};

export default Header;
