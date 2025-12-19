// @ts-nocheck
/**
 * Header Component
 *
 * This module exports the Header component for the application.
 */
import {
  BookOutlined,
  CodeOutlined,
  DeploymentUnitOutlined,
  DownOutlined,
  FileTextOutlined,
  MenuOutlined,
  MessageOutlined,
  PlayCircleOutlined,
  FormOutlined,
} from '@ant-design/icons'
import { Button, Dropdown, Layout, Select, theme as antdTheme, Tooltip, Typography } from 'antd'
import { Brand, BrandColors } from 'branding'
import React from 'react'

import { useTheme } from '../../themes'
import type { AgentPrompt } from '../../types'

const { Header: AntHeader } = Layout
const { Title, Text } = Typography
const { Option } = Select

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
 * @property {Function} onHome - Callback to return to landing page
 * @property {string} [currentSystem] - Currently selected system prompt
 * @property {Function} onSystemChange - Callback when system prompt changes
 * @property {Function} onRunSystemPrompt - Callback to execute system prompt
 * @property {AgentPrompt[]} [agentPrompts] - List of available agent prompts
 */
interface HeaderProps {
  onSetContext: () => void
  onNewConversation: () => void
  onNewSession: () => void
  onEditFile: () => void
  onOpenSettings: () => void
  onToggleTheme: () => void
  onOpenThemePicker: () => void
  onSystemMessage: () => void
  onAbout: () => void
  onCodeFragments: () => void
  onGenerateDocumentation: () => void
  onHelp: () => void
  onMermaidTester: () => void
  onD2Tester: () => void
  onDiagramWizard: () => void
  onNewFormSystemTab?: () => void
  onHome: () => void
  currentSystem?: string
  onSystemChange: (system: string) => void
  onRunSystemPrompt: (systemName: string) => void
  agentPrompts?: AgentPrompt[]
  activeTabType?: 'chat' | 'file' | 'documentation' | 'diagramWizard' | 'formSystem'
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
  onOpenSettings,
  onHome,
  onNewConversation,
  onSetContext,
  onEditFile,
  onGenerateDocumentation,
  onDiagramWizard,
  onNewFormSystemTab,
  currentSystem = 'default',
  onSystemChange,
  onRunSystemPrompt,
  agentPrompts = [],
  activeTabType,
}) => {
  useTheme()
  const { token } = antdTheme.useToken()
  const brandTokens = token as unknown as Record<string, string>

  // Use agent prompts instead of hardcoded system options
  const systemOptions =
    agentPrompts.length > 0
      ? agentPrompts.map((prompt) => prompt.name)
      : ['default', 'coding', 'documentation', 'refactoring', 'debugging']

  const headerBg = brandTokens.colorBrandHeaderBg ?? BrandColors.primary
  const headerBorder =
    brandTokens.colorBrandHeaderBorder ?? BrandColors.secondary ?? BrandColors.primary
  const headerText = brandTokens.colorBrandHeaderText ?? '#ffffff'

  // Tools dropdown menu items
  const handleToolsMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'ai-chat':
        onNewConversation()
        break
      case 'set-context':
        onSetContext()
        break
      case 'file-editor':
        onEditFile()
        break
      case 'documentation':
        onGenerateDocumentation()
        break
      case 'diagram-wizard':
        onDiagramWizard()
        break
      case 'form-system':
        onNewFormSystemTab?.()
        break
    }
  }

  const toolsMenu = {
    items: [
      {
        key: 'ai-chat',
        label: 'AI Chat',
        icon: <MessageOutlined />,
      },
      {
        key: 'set-context',
        label: 'Set Context',
        icon: <FileTextOutlined />,
      },
      {
        key: 'file-editor',
        label: 'File Editor',
        icon: <CodeOutlined />,
      },
      {
        key: 'documentation',
        label: 'Documentation',
        icon: <BookOutlined />,
      },
      {
        key: 'diagram-wizard',
        label: 'Diagram Wizard',
        icon: <DeploymentUnitOutlined />,
      },
      {
        key: 'form-system',
        label: 'Form System',
        icon: <FormOutlined />,
      },
    ],
    onClick: handleToolsMenuClick,
  }

  const mastheadActions = [
    { label: 'Home', handler: onHome, tooltip: 'Return to landing page' },
    { label: 'Settings', handler: onOpenSettings, tooltip: 'Configure application settings' },
  ]
  const actionSurface = brandTokens.colorBgContainer ?? BrandColors.brand?.white ?? '#ffffff'
  const actionText = brandTokens.colorText ?? (BrandColors as any).text?.primary ?? '#231f20'
  const actionSubtleText =
    brandTokens.colorTextSecondary ?? (BrandColors as any).text?.secondary ?? '#5d5550'
  const neutralBorder = brandTokens.colorBorder ?? (BrandColors as any).neutral?.stroke ?? '#d9d9d9'
  const containerPadding = 'clamp(16px, 4vw, 48px)'

  const renderBrandLogo = () => {
    if (Brand.logo?.type === 'image' && Brand.logo.src) {
      return (
        <img
          src={Brand.logo.src}
          alt={Brand.logo.alt || Brand.name}
          style={{ height: 24, width: 'auto', display: 'block' }}
        />
      )
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
    )
  }

  const renderAgentSelector = (labelColor: string, labelOpacity = 0.9) => (
    <div className="flex w-full flex-col">
      <span
        className="mb-2 text-xs tracking-wide"
        style={{
          color: labelColor,
          fontWeight: 600,
          letterSpacing: '0.5px',
          opacity: labelOpacity,
        }}
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
            <div className="border-b-2 border-gray-300 bg-gray-50 px-4 py-3 dark:border-gray-500 dark:bg-gray-700">
              <div className="grid grid-cols-12 gap-4 text-sm font-semibold text-gray-700 dark:text-gray-300">
                <div className="col-span-3 border-r border-gray-300 pr-4 dark:border-gray-500">
                  Agent Name
                </div>
                <div className="col-span-6 border-r border-gray-300 pr-4 dark:border-gray-500">
                  Description
                </div>
                <div className="col-span-3">Categories & File</div>
              </div>
            </div>
            {menu}
          </div>
        )}
      >
        {systemOptions.map((system) => {
          const prompt = agentPrompts.find((p) => p.name === system)
          const displayName = prompt
            ? prompt.title
            : system.charAt(0).toUpperCase() + system.slice(1)
          const shortName =
            displayName.length > 80 ? `${displayName.substring(0, 80)}...` : displayName
          const description = prompt?.description || ''
          const categories = prompt?.category || []

          return (
            <Option key={system} value={system} label={shortName}>
              <div className="min-h-[80px] border-b border-gray-200 px-4 py-5 last:border-b-0 hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700">
                <div className="grid grid-cols-12 items-start gap-4">
                  {/* Agent Name & Title */}
                  <div className="col-span-3 border-r border-gray-200 pr-4 dark:border-gray-600">
                    <div className="break-words text-sm font-semibold leading-tight text-gray-900 dark:text-white">
                      {displayName}
                    </div>
                    <div className="mt-1 break-words text-xs font-medium text-blue-600 dark:text-blue-400">
                      {system}
                    </div>
                  </div>

                  {/* Description */}
                  <div className="col-span-6 border-r border-gray-200 pr-4 dark:border-gray-600">
                    <div className="whitespace-pre-wrap break-words text-sm leading-relaxed text-gray-600 dark:text-gray-300">
                      {description || 'No description available'}
                    </div>
                  </div>

                  {/* Categories & File */}
                  <div className="col-span-3">
                    {categories.length > 0 && (
                      <div className="mb-2 flex flex-wrap gap-1">
                        {categories.slice(0, 4).map((cat, idx) => (
                          <span
                            key={idx}
                            className="inline-block break-words rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-800 dark:text-green-200"
                          >
                            {cat}
                          </span>
                        ))}
                        {categories.length > 4 && (
                          <span className="px-1 text-xs text-gray-500">
                            +{categories.length - 4} more
                          </span>
                        )}
                      </div>
                    )}
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <div className="flex-1 break-words rounded bg-gray-100 px-2 py-1 text-xs text-gray-500 dark:bg-gray-600 dark:text-gray-400">
                        📄 {prompt?.filename || `${system}.md`}
                      </div>
                      <Tooltip title={`Run ${displayName} system prompt`}>
                        <Button
                          type="primary"
                          size="small"
                          icon={<PlayCircleOutlined />}
                          className="!border-green-600 !bg-green-600 hover:!bg-green-700"
                          onClick={(e) => {
                            e.stopPropagation()
                            onRunSystemPrompt(system)
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
          )
        })}
      </Select>
    </div>
  )

  return (
    <AntHeader
      className="border-b !p-0"
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

          {/* Agent selector - moved to chat tab (top fixed row) */}

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
              <ul
                style={{
                  listStyle: 'none',
                  margin: 0,
                  padding: 0,
                  display: 'flex',
                  gap: 16,
                  flexWrap: 'wrap',
                  alignItems: 'center',
                }}
              >
                <li key="tools">
                  <Dropdown menu={toolsMenu} trigger={['click']}>
                    <button
                      type="button"
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
                        display: 'flex',
                        alignItems: 'center',
                        gap: 4,
                      }}
                      onClick={(e) => e.preventDefault()}
                    >
                      Tools <DownOutlined style={{ fontSize: 10 }} />
                    </button>
                  </Dropdown>
                </li>
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
          <div className="flex min-w-[220px] flex-1 flex-col gap-1">
            <Title level={4} className="!mb-0" style={{ color: actionText, fontWeight: 600 }}>
              {Brand.name}
            </Title>
            <Text style={{ color: actionSubtleText, fontSize: '13px', fontWeight: 500 }}>
              {Brand.description}
            </Text>
          </div>

          {/* Agent selector moved to chat tab (top fixed row) */}

          {/* Right Section placeholder to maintain spacing */}
          <div className="flex min-w-[160px] flex-1 items-center justify-end" />
        </div>
      </div>
    </AntHeader>
  )
}

export default Header
