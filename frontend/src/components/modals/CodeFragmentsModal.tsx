/**
 * CodeFragmentsModal Component
 *
 * This module exports the CodeFragmentsModal component for the application.
 */
import { CodeOutlined,CopyOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons'
import { Button, Input, message,Space, Tag, Tooltip, Typography } from 'antd'
import React, { useState } from 'react'

import type { CodeBlock } from '../../types'
import { Modal } from '../common/Modal'

const { Text } = Typography
const { Search } = Input

/**
 * CodeFragmentsModalProps type definition
 *
 * Describes the structure and properties of CodeFragmentsModalProps
 */
interface CodeFragmentsModalProps {
  open: boolean
  onCancel: () => void
  codeBlocks: CodeBlock[]
  onDeleteBlock?: (blockId: string) => void
  onDownloadBlock?: (block: CodeBlock) => void
}

/**
 * CodeFragmentsModal component
 */
export const CodeFragmentsModal: React.FC<CodeFragmentsModalProps> = ({
  open,
  onCancel,
  codeBlocks,
  onDeleteBlock,
  onDownloadBlock,
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState<string>('')

  const filteredBlocks = codeBlocks.filter((block) => {
    const matchesSearch =
      block.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      block.filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      block.language.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesLanguage = !selectedLanguage || block.language === selectedLanguage

    return matchesSearch && matchesLanguage
  })

  const languages = [...new Set(codeBlocks.map((block) => block.language))].sort()

  const handleCopyCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code)
      message.success('Code copied to clipboard')
    } catch {
      message.error('Failed to copy code')
    }
  }

  const handleDownload = (block: CodeBlock) => {
    const element = document.createElement('a')
    const file = new Blob([block.code], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = block.filename || `code-block.${getFileExtension(block.language)}`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)

    if (onDownloadBlock) {
      onDownloadBlock(block)
    }
  }

  const getFileExtension = (language: string): string => {
    const extensions: { [key: string]: string } = {
      javascript: 'js',
      typescript: 'ts',
      python: 'py',
      java: 'java',
      cpp: 'cpp',
      c: 'c',
      csharp: 'cs',
      html: 'html',
      css: 'css',
      sql: 'sql',
      bash: 'sh',
      shell: 'sh',
      json: 'json',
      xml: 'xml',
      yaml: 'yml',
      markdown: 'md',
      rust: 'rs',
      go: 'go',
      php: 'php',
      ruby: 'rb',
      swift: 'swift',
      kotlin: 'kt',
    }
    return extensions[language.toLowerCase()] || 'txt'
  }

  const getLanguageColor = (language: string): string => {
    const colors: { [key: string]: string } = {
      javascript: 'gold',
      typescript: 'blue',
      python: 'green',
      java: 'orange',
      cpp: 'purple',
      c: 'purple',
      csharp: 'purple',
      html: 'red',
      css: 'cyan',
      sql: 'geekblue',
      bash: 'lime',
      shell: 'lime',
      json: 'orange',
      xml: 'magenta',
      yaml: 'volcano',
      markdown: 'default',
      rust: 'orange',
      go: 'blue',
      php: 'purple',
      ruby: 'red',
      swift: 'orange',
      kotlin: 'purple',
    }
    return colors[language.toLowerCase()] || 'default'
  }

  const formatCode = (code: string, maxLines: number = 10): string => {
    const lines = code.split('\n')
    if (lines.length <= maxLines) {
      return code
    }
    return lines.slice(0, maxLines).join('\n') + '\n...'
  }

  return (
    <Modal
      title={
        <div className="flex items-center gap-2">
          <CodeOutlined />
          <span>Code Fragments</span>
          <Tag color="blue">{codeBlocks.length} blocks</Tag>
        </div>
      }
      open={open}
      onCancel={onCancel}
      width={1000}
      footer={
        <div className="flex justify-between">
          <Text type="secondary" className="text-sm">
            {filteredBlocks.length} of {codeBlocks.length} code blocks shown
          </Text>
          <Button onClick={onCancel}>Close</Button>
        </div>
      }
    >
      <div className="space-y-4">
        {/* Filters */}
        <div className="flex items-center gap-4">
          <Search
            placeholder="Search code, filename, or language..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
            allowClear
          />

          <div className="flex items-center gap-2">
            <Text className="whitespace-nowrap">Language:</Text>
            <div className="flex flex-wrap gap-1">
              <Tag
                className="cursor-pointer"
                color={!selectedLanguage ? 'blue' : 'default'}
                onClick={() => setSelectedLanguage('')}
              >
                All
              </Tag>
              {languages.map((language) => (
                <Tag
                  key={language}
                  className="cursor-pointer"
                  color={selectedLanguage === language ? 'blue' : 'default'}
                  onClick={() => setSelectedLanguage(language === selectedLanguage ? '' : language)}
                >
                  {language}
                </Tag>
              ))}
            </div>
          </div>
        </div>

        {/* Code Blocks */}
        <div className="max-h-96 space-y-4 overflow-y-auto">
          {filteredBlocks.length === 0 ? (
            <div className="py-8 text-center text-gray-500">
              {codeBlocks.length === 0 ? (
                <>
                  <CodeOutlined className="mb-2 text-4xl" />
                  <div>No code blocks extracted yet</div>
                  <div className="text-sm">
                    Code blocks will appear here when extracted from AI responses
                  </div>
                </>
              ) : (
                <>No code blocks match your search criteria</>
              )}
            </div>
          ) : (
            filteredBlocks.map((block) => (
              <div
                key={block.id}
                className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-700"
              >
                {/* Header */}
                <div className="flex items-center justify-between bg-gray-50 px-4 py-2 dark:bg-gray-800">
                  <div className="flex items-center gap-2">
                    <Tag color={getLanguageColor(block.language)}>{block.language}</Tag>
                    {block.filename && <Text className="font-mono text-sm">{block.filename}</Text>}
                    <Text type="secondary" className="text-xs">
                      {block.code.split('\n').length} lines
                    </Text>
                  </div>

                  <Space>
                    <Tooltip title="Copy Code">
                      <Button
                        type="text"
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => handleCopyCode(block.code)}
                      />
                    </Tooltip>

                    <Tooltip title="Download File">
                      <Button
                        type="text"
                        size="small"
                        icon={<DownloadOutlined />}
                        onClick={() => handleDownload(block)}
                      />
                    </Tooltip>

                    {onDeleteBlock && (
                      <Tooltip title="Delete Block">
                        <Button
                          type="text"
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={() => onDeleteBlock(block.id)}
                          danger
                        />
                      </Tooltip>
                    )}
                  </Space>
                </div>

                {/* Code Content */}
                <div className="relative">
                  <pre className="max-h-60 overflow-auto bg-gray-900 p-4 font-mono text-sm text-gray-100">
                    <code>{formatCode(block.code)}</code>
                  </pre>

                  {block.code.split('\n').length > 10 && (
                    <div className="absolute bottom-2 right-2">
                      <Button
                        size="small"
                        type="link"
                        onClick={() => handleCopyCode(block.code)}
                        className="!text-gray-300 hover:!text-white"
                      >
                        View Full Code
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Summary */}
        {codeBlocks.length > 0 && (
          <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
            <div className="flex items-center justify-between text-sm">
              <div>
                <Text strong>Total: {codeBlocks.length} code blocks</Text>
                <Text type="secondary" className="ml-4">
                  Languages: {languages.join(', ')}
                </Text>
              </div>
              <Space>
                <Button
                  size="small"
                  onClick={() => {
                    const allCode = codeBlocks
                      .map(
                        (block) =>
                          `// ${block.filename || 'Code Block'} (${block.language})\n${block.code}`
                      )
                      .join('\n\n---\n\n')
                    handleCopyCode(allCode)
                  }}
                >
                  Copy All
                </Button>
              </Space>
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}

export default CodeFragmentsModal
