/**
 * InputPanel Component
 *
 * This module exports the InputPanel component for the application.
 */
import {
  ClearOutlined,
  CompressOutlined,
  CopyOutlined,
  ExpandOutlined,
  PlusOutlined,
  SendOutlined,
} from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { Button, message as antMessage,Select, Tooltip } from 'antd'
import { BrandColors } from 'branding'
import type * as Monaco from 'monaco-editor'
import React, { type ReactNode,useEffect, useRef, useState } from 'react'

const { Option } = Select
// @ts-expect-error - Brand color theme type mismatch
const linkColor = BrandColors.text?.link ?? '#5a469b'

const ActionLink: React.FC<{
  icon?: ReactNode
  onClick?: () => void
  disabled?: boolean
  loading?: boolean
  children: ReactNode
}> = ({ icon, onClick, disabled = false, loading = false, children }) => (
  <Tooltip title={typeof children === 'string' ? children : undefined}>
    <button
      type="button"
      onClick={() => {
        if (disabled || loading || !onClick) return
        onClick()
      }}
      aria-disabled={disabled || loading}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 6,
        fontWeight: 600,
        color: disabled ? '#94a3b8' : linkColor,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: loading ? 0.7 : 1,
        background: 'transparent',
        border: 'none',
        padding: 0,
        fontSize: 13,
      }}
    >
      {icon}
      {loading ? 'Sending…' : children}
    </button>
  </Tooltip>
)

/**
 * SubagentCommand type definition
 *
 * Describes the structure and properties of SubagentCommand
 */
interface SubagentCommand {
  category: string
  title: string
  subcommand: string
}

/**
 * InputPanelProps type definition
 *
 * Describes the structure and properties of InputPanelProps
 */
interface InputPanelProps {
  onSendMessage: (message: string, command?: string) => void
  onClear: () => void
  loading?: boolean
  disabled?: boolean
  subagentCommands?: SubagentCommand[]
}

/**
 * InputPanel component
 */
export const InputPanel: React.FC<InputPanelProps> = ({
  onSendMessage,
  onClear,
  loading = false,
  disabled = false,
  subagentCommands = [],
}) => {
  const [message, setMessage] = useState('')
  const [lastSentMessage, setLastSentMessage] = useState<string>('')

  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedCommand, setSelectedCommand] = useState<string>('')
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null)
  const [currentHeight, setCurrentHeight] = useState<number>(120) // Track current height in pixels
  const [previousHeight, setPreviousHeight] = useState<number>(120) // Store previous height for restoration

  // Refs to store current values for key binding
  const messageRef = useRef(message)
  const loadingRef = useRef(loading)
  const selectedCommandRef = useRef(selectedCommand)

  // Update refs when values change
  useEffect(() => {
    messageRef.current = message
  }, [message])

  useEffect(() => {
    loadingRef.current = loading
  }, [loading])

  useEffect(() => {
    selectedCommandRef.current = selectedCommand
  }, [selectedCommand])

  // Handle editor mount
  const handleEditorDidMount = (
    editor: Monaco.editor.IStandaloneCodeEditor,
    monaco: typeof Monaco
  ) => {
    editorRef.current = editor

    // Add custom key binding: Ctrl+Enter to submit
    editor.addAction({
      id: 'submit-message',
      label: 'Submit Message',
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => {
        // Use refs to get current values (avoid stale closure)
        const currentMessage = messageRef.current.trim()
        const currentSelectedCommand = selectedCommandRef.current
        const currentLoading = loadingRef.current

        if (currentMessage && !currentLoading) {
          const messageToSend = currentMessage
          const commandToSend = currentSelectedCommand || ''

          setLastSentMessage(messageToSend)
          onSendMessage(messageToSend, commandToSend)
          setMessage('')
          setSelectedCategory('')
          setSelectedCommand('')
        }
      },
    })
  }

  // Get unique categories from subagent commands
  const categories = React.useMemo(() => {
    const uniqueCategories = [...new Set(subagentCommands.map((cmd) => cmd.category))]
    return uniqueCategories.sort()
  }, [subagentCommands])

  // Get subagents for selected category
  const subagentsForCategory = React.useMemo(() => {
    if (!selectedCategory) return []
    const filtered = subagentCommands.filter((cmd) => cmd.category === selectedCategory)
    console.log(
      '🔍 Subagents for category:',
      selectedCategory,
      '→',
      filtered.length,
      'items:',
      filtered
    )
    return filtered
  }, [subagentCommands, selectedCategory])

  const handleSend = () => {
    if (message.trim() && !loading) {
      const messageToSend = message.trim()
      const commandToSend = selectedCommand || ''

      setLastSentMessage(messageToSend)
      onSendMessage(messageToSend, commandToSend)
      setMessage('')
      setSelectedCategory('')
      setSelectedCommand('')
    }
  }

  const handleCopyLastMessage = async () => {
    if (lastSentMessage) {
      try {
        await navigator.clipboard.writeText(lastSentMessage)
        antMessage.success('Last prompt copied to clipboard')
      } catch (error) {
        console.error('Failed to copy to clipboard:', error)
        antMessage.error('Failed to copy to clipboard')
      }
    }
  }

  const handleClear = () => {
    setMessage('')
    setSelectedCategory('')
    setSelectedCommand('')
    onClear()
  }

  const injectSubagentCommand = (subcommand: string) => {
    setMessage((prev) => (prev ? `${prev}\n\n${subcommand}` : subcommand))

    // Focus editor after inserting command
    setTimeout(() => {
      editorRef.current?.focus()
    }, 0)
  }

  // Handle editor changes
  const handleEditorChange = (value: string | undefined) => {
    setMessage(value || '')
  }

  const handleReduceHeight = () => {
    if (currentHeight > 60) {
      // Store current height before reducing
      setPreviousHeight(currentHeight)
      const newHeight = Math.max(60, Math.ceil(currentHeight * 0.25)) // Reduce by 75%, min 60px
      setCurrentHeight(newHeight)
    }
  }

  const handleRestoreHeight = () => {
    if (currentHeight < previousHeight) {
      setCurrentHeight(previousHeight)
    }
  }

  // @ts-expect-error - Brand color theme type mismatch
  const panelBackground = BrandColors.quaternary ?? '#fbd3a4'
  // @ts-expect-error - Brand color theme type mismatch
  const panelBorder = BrandColors.neutral?.stroke ?? '#e3ded8'

  return (
    <div
      className="w-full"
      style={{
        background: panelBackground,
        margin: 0,
        padding: 0,
      }}
    >
      <div
        className="shadow-sm"
        style={{
          background: panelBackground,
          borderTop: `1px solid ${panelBorder}`,
          borderBottom: `1px solid ${panelBorder}`,
          padding: 0,
          boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.04)',
        }}
      >
        {/* First Row: Subagent Commands + Submit/Clear Buttons */}
        <div className="mb-3 flex items-center gap-2">
          <span className="whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
            Inject Command:
          </span>

          {/* Category Selection */}
          <Select
            placeholder="Select category"
            value={selectedCategory}
            onChange={(value) => {
              setSelectedCategory(value)
              setSelectedCommand('') // Reset command when category changes
            }}
            className="min-w-[280px]"
            size="small"
            allowClear
          >
            {categories.map((category) => (
              <Option key={category} value={category}>
                {category}
              </Option>
            ))}
          </Select>

          {/* Command Selection */}
          <Select
            placeholder="Select command"
            value={selectedCommand}
            onChange={setSelectedCommand}
            className="min-w-[360px]"
            size="small"
            allowClear
            disabled={!selectedCategory}
          >
            {subagentsForCategory.map((subagent, index) => (
              <Option
                key={`${subagent.category}-${subagent.title}-${index}`}
                value={subagent.title}
              >
                {subagent.title}
              </Option>
            ))}
          </Select>

          {/* Inject Action Link */}
          <ActionLink
            icon={<PlusOutlined />}
            disabled={!selectedCommand}
            onClick={() => {
              const command = subagentsForCategory.find((cmd) => cmd.title === selectedCommand)
              if (command) {
                injectSubagentCommand(command.subcommand)
              }
            }}
          >
            Add Command
          </ActionLink>

          <div className="flex-1" />

          {/* Submit, Copy, and Clear Buttons */}
          <div className="flex gap-4">
            <Tooltip title="Submit Question">
              <ActionLink
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!message.trim() || disabled}
              >
                Submit
              </ActionLink>
            </Tooltip>

            <Tooltip title="Copy Last Prompt">
              <ActionLink
                icon={<CopyOutlined />}
                onClick={handleCopyLastMessage}
                disabled={!lastSentMessage || loading}
              >
                Copy
              </ActionLink>
            </Tooltip>

            <Tooltip title="Clear">
              <ActionLink icon={<ClearOutlined />} onClick={handleClear} disabled={loading}>
                Clear
              </ActionLink>
            </Tooltip>
          </div>
        </div>

        {/* Input Area */}
        <div className="relative">
          <div
            className="relative"
            style={{
              borderRadius: 0,
              border: `1px solid ${panelBorder}`,
              boxShadow: 'none',
              overflow: 'hidden',
              background: panelBackground,
              minHeight: `${currentHeight}px`,
              height: `${currentHeight}px`,
              maxHeight: '400px',
            }}
          >
            <Editor
              height={`${currentHeight}px`}
              defaultLanguage="markdown"
              value={message}
              onChange={handleEditorChange}
              onMount={handleEditorDidMount}
              theme="light"
              options={{
                minimap: { enabled: false },
                lineNumbers: 'off',
                glyphMargin: false,
                folding: false,
                lineDecorationsWidth: 0,
                lineNumbersMinChars: 0,
                renderLineHighlight: 'none',
                scrollBeyondLastLine: false,
                fontSize: 15,
                fontFamily: 'ui-sans-serif, system-ui, sans-serif',
                wordWrap: 'on',
                wrappingIndent: 'none',
                padding: { top: 10, bottom: 10 },
                overviewRulerBorder: false,
                overviewRulerLanes: 0,
                hideCursorInOverviewRuler: true,
                scrollbar: {
                  vertical: 'auto',
                  horizontal: 'hidden',
                  verticalScrollbarSize: 8,
                },
                readOnly: disabled || loading,
                suggest: {
                  showKeywords: false,
                  showSnippets: false,
                },
                quickSuggestions: false,
                parameterHints: { enabled: false },
                acceptSuggestionOnEnter: 'off',
              }}
            />

            {/* Resize buttons in top-right corner */}
            <div
              className="absolute right-2 top-2 flex gap-1"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                borderRadius: '6px',
                padding: '2px',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(226, 232, 240, 0.8)',
              }}
            >
              <Tooltip title="Reduce height by 75%">
                <Button
                  type="text"
                  size="small"
                  icon={<CompressOutlined />}
                  onClick={handleReduceHeight}
                  disabled={currentHeight <= 60}
                  style={{
                    fontSize: '10px',
                    height: '20px',
                    width: '20px',
                    minWidth: '20px',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                />
              </Tooltip>

              <Tooltip title="Restore to previous height">
                <Button
                  type="text"
                  size="small"
                  icon={<ExpandOutlined />}
                  onClick={handleRestoreHeight}
                  disabled={currentHeight >= previousHeight}
                  style={{
                    fontSize: '10px',
                    height: '20px',
                    width: '20px',
                    minWidth: '20px',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                />
              </Tooltip>
            </div>
          </div>

          {/* Floating action area */}
          {message.trim() && (
            <div
              className="absolute bottom-3 right-3 flex items-center gap-2"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                borderRadius: '12px',
                padding: '8px 12px',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
              }}
            >
              <span
                style={{
                  fontSize: '12px',
                  color: '#64748b',
                  fontWeight: 500,
                }}
              >
                Press Ctrl+Enter to send
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default InputPanel
