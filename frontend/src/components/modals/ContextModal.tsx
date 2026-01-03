/**
 * ContextModal Component
 *
 * This module exports the ContextModal component for the application.
 * Provides GitHub repository import and uploaded file selection for AI conversation context.
 */
import {
  ApartmentOutlined,
  CloudUploadOutlined,
  FileOutlined,
  FolderOutlined,
  ReloadOutlined,
  UnorderedListOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import { Button, Checkbox, Dropdown, Input, Menu, message, Segmented, Space, Spin, Typography } from 'antd'
import React, { useEffect, useRef, useState } from 'react'

import ApiService from '../../services/api'
import type { FileItem, UploadedFile } from '../../types'
import { Modal } from '../common/Modal'
import FileTreeModal from './FileTreeModal'
import type { ProgressEvent } from '../../services/sseClient'
import { getApiBaseUrl } from '../../utils/apiBase'

const { Search } = Input
const { Text } = Typography

/**
 * Props interface for the ContextModal component
 *
 * @interface ContextModalProps
 * @property {boolean} open - Controls modal visibility state
 * @property {() => void} onCancel - Callback triggered when modal is cancelled
 * @property {(selectedFiles: FileItem[]) => void} onApply - Callback triggered when files are selected and applied
 * @property {FileItem[]} [initialFiles] - Pre-selected files to initialize the modal with
 */
/**
 * ContextModalProps type definition
 *
 * Describes the structure and properties of ContextModalProps
 */
interface ContextModalProps {
  open: boolean
  onCancel: () => void
  onApply: (selectedFiles: FileItem[]) => void
  initialFiles?: FileItem[]
}

/**
 * ContextModal Component
 *
 * A file selection modal for AI conversation context that supports:
 * - GitHub repository import: Import code from public GitHub repositories
 * - Uploaded files view: Files uploaded in the current session
 *
 * Features:
 * - GitHub repository import with branch/tag and subpath support
 * - File upload functionality with session-based organization
 * - Batch file selection with select all/none options
 * - File size formatting and type detection
 * - Real-time file selection tracking
 * - Session-based file organization using GUIDs
 *
 * @param {ContextModalProps} props - Component props
 * @returns {JSX.Element} Rendered context selection modal
 */
/**
 * ContextModal component
 */
export const ContextModal: React.FC<ContextModalProps> = ({
  open,
  onCancel,
  onApply,
  initialFiles = [],
}) => {
  // View mode state: 'github', 'tree', or 'uploaded'
  const [viewMode, setViewMode] = useState<'github' | 'tree' | 'uploaded'>('github')
  const [loading, setLoading] = useState(false)
  const [files, setFiles] = useState<FileItem[]>([])
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([])
  const [uploadLoading, setUploadLoading] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [githubRepo, setGithubRepo] = useState('')
  const [githubRef, setGithubRef] = useState('main')
  const [githubSubpath, setGithubSubpath] = useState('')
  const [lastImportedPath, setLastImportedPath] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string>('')
  const [githubProgress, setGithubProgress] = useState<ProgressEvent | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all')
  const [sizeFilter, setSizeFilter] = useState<'all' | 'small' | 'medium' | 'large'>('all')
  const fileInputRef = useRef<HTMLInputElement>(null)

  /**
   * Initialize selected files from props when component mounts or initialFiles changes
   * Converts FileItem array to Set of file paths for efficient lookup
   *
   * @param {FileItem[]} initialFiles - Array of pre-selected files
   */
  useEffect(() => {
    if (initialFiles.length > 0) {
      setSelectedFiles(new Set(initialFiles.map((f) => f.path)))
    }
  }, [initialFiles])

  /**
   * Generate unique session ID when modal opens for the first time
   * Used for organizing session-specific data like uploads
   * Format: YYYY-MM-DD-xxxxxxxxxxxx
   */
  useEffect(() => {
    if (open && !sessionId) {
      const generateGUID = () => {
        const today = new Date()
        const datePrefix = today.toISOString().split('T')[0] // YYYY-MM-DD
        const guid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
          const r = Math.random() * 16 | 0
          const v = c === 'x' ? r : (r & 0x3 | 0x8)
          return v.toString(16)
        })
        return `${datePrefix}-${guid}`
      }
      setSessionId(generateGUID())
    }
  }, [open, sessionId])

  /**
   * Load files from backend when modal opens
   * Fetches file list from the configured code path
   */
  useEffect(() => {
    if (open) {
      loadFiles()
    }
  }, [open])

  /**
   * Load uploaded files when modal opens
   * Retrieves files uploaded in the current session
   */
  useEffect(() => {
    if (open) {
      loadUploadedFiles()
    }
  }, [open])

  /**
   * Loads files from the backend API
   * Updates files state and handles loading states
   *
   * @async
   * @returns {Promise<void>}
   */
  // Normalize backend items (including GitHub import results) into the UI FileItem shape
  const normalizeFileItems = (items: any[]): FileItem[] =>
    items.map((item) => ({
      path: item.path,
      name: item.name || item.relativePath || item.path?.split(/[\\/]/).pop() || item.path,
      size: item.size ?? 0,
      isSelected: Boolean(item.isSelected),
      type: item.type === 'directory' ? 'directory' : 'file',
      is_uploaded: item.is_uploaded,
      content: item.content,
      date: item.modifiedTime || item.date, // Use modifiedTime from backend or fallback to date field
    }))

  const loadFiles = async () => {
    setLoading(true)
    try {
      const response = await ApiService.getFiles()
      if (response.success && response.data) {
        setFiles(normalizeFileItems(response.data))
      } else {
        message.error(response.error || 'Failed to load files')
      }
    } catch (error) {
      message.error('Error loading files')
      console.error('Error loading files:', error)
    } finally {
      setLoading(false)
    }
  }

  /**
   * Loads uploaded files from the backend
   * Retrieves files that were uploaded in the current session
   *
   * @async
   * @returns {Promise<void>}
   */
  const loadUploadedFiles = async () => {
    try {
      const response = await ApiService.getUploadedFiles()
      if (response.success && response.data) {
        setUploadedFiles(normalizeFileItems(response.data))
      }
    } catch (error) {
      console.error('Error loading uploaded files:', error)
    }
  }


  /**
   * Handles file upload functionality
   * Reads selected files, uploads them to backend, and updates uploaded files list
   *
   * @param {File[]} fileList - Array of files to upload
   * @async
   * @returns {Promise<void>}
   */
  const handleFileUpload = async (fileList: File[]) => {
    if (fileList.length === 0) return

    setUploadLoading(true)

    try {
      const uploadedFiles: UploadedFile[] = []

      // Process each file: read content and create UploadedFile objects
      for (const file of fileList) {
        const content = await readFileAsText(file)
        uploadedFiles.push({
          name: file.name,
          content,
          size: file.size,
          type: file.type || 'text/plain',
        })
      }

      // Upload files to backend using session-specific subfolder
      const response = await ApiService.uploadFiles({
        files: uploadedFiles,
        target_directory: `uploads/${sessionId}`,
      })

      if (response.success && response.data) {
        message.success(`Successfully uploaded ${uploadedFiles.length} file(s)`)

        // Refresh uploaded files list
        await loadUploadedFiles()

        // Switch to uploaded files view
        setViewMode('uploaded')

        // Auto-select uploaded files
        const newPaths = response.data.data.files.map((f: FileItem) => f.path)
        setSelectedFiles(new Set([...selectedFiles, ...newPaths]))
      } else {
        message.error(response.error || 'Failed to upload files')
      }
    } catch (error) {
      console.error('Error uploading files:', error)
      message.error('Error uploading files')
    } finally {
      setUploadLoading(false)
    }
  }

  /**
   * Reads a File object as text content
   * Utility function for file upload processing
   *
   * @param {File} file - File object to read
   * @returns {Promise<string>} File content as string
   */
  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  /**
   * Triggers file input click for upload functionality
   */
  const handleUploadButtonClick = () => {
    fileInputRef.current?.click()
  }

  /**
   * Performs fuzzy search on text
   * Returns true if search term matches with some tolerance for typos
   *
   * @param {string} text - Text to search in
   * @param {string} searchTerm - Term to search for
   * @returns {boolean} Whether the search term fuzzy matches the text
   */
  const fuzzyMatch = (text: string, searchTerm: string): boolean => {
    if (!searchTerm) return true
    const textLower = text.toLowerCase()
    const termLower = searchTerm.toLowerCase()

    // Exact match
    if (textLower.includes(termLower)) return true

    // Fuzzy match: check if all characters of search term appear in order
    let textIndex = 0
    for (let i = 0; i < termLower.length; i++) {
      const char = termLower[i]
      const foundIndex = textLower.indexOf(char, textIndex)
      if (foundIndex === -1) return false
      textIndex = foundIndex + 1
    }
    return true
  }

  /**
   * Gets file extension from file name
   *
   * @param {string} fileName - Name of the file
   * @returns {string} File extension (lowercase)
   */
  const getFileExtension = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase() || ''
    return ext
  }

  /**
   * Checks if file size matches the size filter
   *
   * @param {number} size - File size in bytes
   * @param {'all' | 'small' | 'medium' | 'large'} filter - Size filter
   * @returns {boolean} Whether file size matches filter
   */
  const matchesSizeFilter = (size: number, filter: 'all' | 'small' | 'medium' | 'large'): boolean => {
    if (filter === 'all') return true
    const kb = size / 1024
    switch (filter) {
      case 'small': return kb < 10
      case 'medium': return kb >= 10 && kb < 100
      case 'large': return kb >= 100
      default: return true
    }
  }

  /**
   * Filters files based on search term, file type, and size
   * Uses fuzzy matching for search and applies multiple filters
   *
   * @param {FileItem[]} files - Array of files to filter
   * @returns {FileItem[]} Filtered array of files
   */
  const filteredFiles = files.filter((file) => {
    // Search filter with fuzzy matching
    const matchesSearch = fuzzyMatch(file.name, searchTerm) || fuzzyMatch(file.path, searchTerm)

    // File type filter
    const extension = getFileExtension(file.name)
    const matchesType = fileTypeFilter === 'all' ||
      (fileTypeFilter === 'code' && ['js', 'ts', 'jsx', 'tsx', 'py', 'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'go', 'rs'].includes(extension)) ||
      (fileTypeFilter === 'config' && ['json', 'yml', 'yaml', 'xml', 'ini', 'cfg', 'conf', 'toml', 'env'].includes(extension)) ||
      (fileTypeFilter === 'text' && ['txt', 'md', 'rst', 'adoc'].includes(extension)) ||
      (fileTypeFilter === 'image' && ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'].includes(extension)) ||
      extension === fileTypeFilter

    // Size filter
    const matchesSize = matchesSizeFilter(file.size, sizeFilter)

    return matchesSearch && matchesType && matchesSize
  })

  /**
   * Handles individual file selection/deselection
   * Updates selected files set
   *
   * @param {string} filePath - Path of the file to toggle
   * @param {boolean} checked - Whether the file should be selected
   */
  const handleFileToggle = (filePath: string, checked: boolean) => {
    const newSelected = new Set(selectedFiles)
    if (checked) {
      newSelected.add(filePath)
    } else {
      newSelected.delete(filePath)
    }
    setSelectedFiles(newSelected)
  }

  /**
   * Selects all currently filtered files
   */
  const handleSelectAll = () => {
    const allFilePaths = filteredFiles.map((f) => f.path)
    setSelectedFiles(new Set([...selectedFiles, ...allFilePaths]))
  }

  /**
   * Deselects all currently selected files
   */
  const handleSelectNone = () => {
    setSelectedFiles(new Set())
  }

  /**
   * Formats file size in human-readable format
   * Converts bytes to appropriate unit (B, KB, MB, GB)
   *
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size string
   */
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  /**
   * Formats date string for display
   * Shows relative time for recent dates, absolute date for older ones
   *
   * @param {string} dateString - ISO date string
   * @returns {string} Formatted date string
   */
  const formatFileDate = (dateString: string) => {
    if (!dateString) return '-'

    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

      if (diffDays === 0) {
        return 'Today'
      } else if (diffDays === 1) {
        return 'Yesterday'
      } else if (diffDays < 7) {
        return `${diffDays} days ago`
      } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7)
        return `${weeks} week${weeks !== 1 ? 's' : ''} ago`
      } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30)
        return `${months} month${months !== 1 ? 's' : ''} ago`
      } else {
        return date.toLocaleDateString()
      }
    } catch {
      return dateString
    }
  }

  /**
   * Returns appropriate icon component for file type
   *
   * @param {FileItem} file - File item to get icon for
   * @returns {JSX.Element} Icon component
   */
  const getFileIcon = (file: FileItem) => {
    if (file.is_uploaded) {
      return <CloudUploadOutlined className="text-green-500" />
    }
    return file.type === 'directory' ? (
      <FolderOutlined className="text-blue-500" />
    ) : (
      <FileOutlined className="text-gray-500" />
    )
  }

  /**
   * Handles apply action with selected files
   * Combines regular files and uploaded files, applies selection, and closes modal
   */
  const handleApply = () => {
    // Combine regular files and uploaded files
    const allFiles = [...files, ...uploadedFiles]
    const selectedFileItems = allFiles.filter((file) => selectedFiles.has(file.path))

    onApply(selectedFileItems)
    onCancel()
  }

  /**
   * Handles importing a public GitHub repository with progress feedback
   * Uses SSE to provide real-time progress updates during file download and caching
   *
   * @async
   * @returns {Promise<void>}
   */
  const handleGitHubImport = async () => {
    if (!githubRepo.trim()) {
      message.warning('Enter a repository in owner/repo or GitHub URL form')
      return
    }

    setImportLoading(true)
    setGithubProgress(null)

    try {
      const API_BASE_URL = getApiBaseUrl()
      const controller = new AbortController()
      const signal = controller.signal

      // Start SSE connection for progress updates
      const sseResponse = await fetch(`${API_BASE_URL}/stream/github-import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository: githubRepo.trim(),
          ref: githubRef.trim() || 'main',
          subpath: githubSubpath.trim() || undefined,
          session_id: sessionId,
        }),
        signal,
      })

      if (!sseResponse.ok) {
        throw new Error(`HTTP ${sseResponse.status}: ${sseResponse.statusText}`)
      }

      if (!sseResponse.body) {
        throw new Error('Response body is null')
      }

      const reader = sseResponse.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const eventText of events) {
          if (!eventText.trim()) continue

          try {
            const lines = eventText.split('\n')
            let eventType = 'message'
            let eventData = ''

            for (const line of lines) {
              if (line.startsWith('event:')) {
                eventType = line.substring(6).trim()
              } else if (line.startsWith('data:')) {
                eventData = line.substring(5).trim()
              }
            }

            const data = JSON.parse(eventData)

            if (eventType === 'progress') {
              setGithubProgress(data as ProgressEvent)
            } else if (eventType === 'complete') {
              const normalized = normalizeFileItems(data.files || [])
              setFiles(normalized)
              setLastImportedPath(data.scanPath || data.rootPath || null)
              setSelectedFiles(new Set())
              message.success(data.message || 'Repository imported successfully')
              setGithubProgress(null)
              break
            } else if (eventType === 'error') {
              message.error(data.error || 'Failed to import repository')
              setGithubProgress(null)
              break
            }
          } catch (error) {
            console.error('Failed to parse GitHub import event:', eventText, error)
          }
        }
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        console.error('Error importing GitHub repo:', error)
        message.error('Error importing GitHub repository')
        setGithubProgress(null)
      }
    } finally {
      setImportLoading(false)
    }
  }


  // If tree view mode is selected, render the FileTreeModal
  if (viewMode === 'tree') {
    return (
      <FileTreeModal
        open={open}
        onCancel={onCancel}
        onApply={onApply}
        initialFiles={initialFiles}
        externalFiles={files}
      />
    )
  }

  // Use appropriate files based on view mode
  const displayFiles = viewMode === 'uploaded' ? uploadedFiles : files

  // Otherwise render the list view
  return (
    <Modal
      title="Conversation Context"
      open={open}
      onCancel={onCancel}
      onOk={handleApply}
      width={800}
      okText="Apply Context"
      cancelText="Cancel"
    >
      <div className="space-y-4">
        {/* View Mode Toggle */}
        <div className="flex items-center justify-between">
          <Segmented
            value={viewMode}
            onChange={(value) => setViewMode(value as 'github' | 'tree' | 'uploaded')}
            options={[
              {
                label: 'GitHub Import',
                value: 'github',
                icon: <ApartmentOutlined />,
              },
              {
                label: 'Tree View',
                value: 'tree',
                icon: <ApartmentOutlined />,
              },
              {
                label: 'Uploaded Files',
                value: 'uploaded',
                icon: <CloudUploadOutlined />,
              },
            ]}
          />
        </div>

        {/* GitHub import controls */}
        {viewMode === 'github' && (
          <div className="space-y-3">
            <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
              <Text className="mb-2 block text-sm font-medium">Import public GitHub repository</Text>
              <div className="grid grid-cols-12 gap-2">
                <Input
                  className="col-span-6"
                  placeholder="owner/repo or GitHub URL"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                  aria-label="GitHub repository"
                />
                <Input
                  className="col-span-2"
                  placeholder="ref (main)"
                  value={githubRef}
                  onChange={(e) => setGithubRef(e.target.value)}
                  aria-label="Git reference"
                />
                <Input
                  className="col-span-3"
                  placeholder="subpath (optional)"
                  value={githubSubpath}
                  onChange={(e) => setGithubSubpath(e.target.value)}
                  aria-label="GitHub subpath"
                />
                <Button
                  type="primary"
                  loading={importLoading}
                  onClick={handleGitHubImport}
                  className="col-span-1"
                >
                  Fetch
                </Button>
              </div>
              {lastImportedPath && (
                <Text className="mt-2 block text-xs text-gray-500">
                  Loaded: {lastImportedPath}
                </Text>
              )}
            </div>

            {/* Progress Display */}
            {githubProgress && (
              <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <Spin size="small" />
                  <Text className="text-sm font-medium text-blue-800 dark:text-blue-200">
                    {githubProgress.stage}
                  </Text>
                </div>
                <Text className="text-sm text-blue-700 dark:text-blue-300">
                  {githubProgress.message}
                </Text>
              </div>
            )}

            <div className="flex items-center gap-4">
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={handleUploadButtonClick}
                loading={uploadLoading}
                className="mb-4"
              >
                Upload Files
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".txt,.py,.js,.ts,.jsx,.tsx,.html,.css,.json,.md,.yml,.yaml,.xml,.csv,.sql,.sh,.bat,.ps1,.go,.rs,.java,.cpp,.c,.h,.hpp,.php,.rb,.swift,.kt,.scala,.clj,.hs,.ml,.fs,.dart,.lua,.r,.m,.nim,.v,.zig,.cr,.ex,.exs,.elm,.purs,.tsv,.ini,.cfg,.conf,.toml,.env,.gitignore,.dockerfile,.makefile,.cmake"
                style={{ display: 'none' }}
                aria-label="Upload files for context"
                title="Upload files to use as context in conversations"
                onChange={(e) => {
                  const files = e.target.files
                  if (files) {
                    handleFileUpload(Array.from(files))
                  }
                  // Reset input value to allow uploading the same file again
                  e.target.value = ''
                }}
              />
            </div>
          </div>
        )}

        {/* Upload controls for uploaded view */}
        {viewMode === 'uploaded' && (
          <div className="flex items-center gap-4">
            <Button
              icon={<ReloadOutlined />}
              onClick={loadUploadedFiles}
              loading={loading}
              className="mb-4"
            >
              Refresh
            </Button>
          </div>
        )}


        {/* File Selection Status */}
        <div className="flex items-center justify-between border-b border-gray-200 py-2 dark:border-gray-700">
          <Text className="text-sm text-gray-600">
            {selectedFiles.size > 0
              ? `${selectedFiles.size} file${selectedFiles.size !== 1 ? 's' : ''} selected`
              : 'No files selected'}
          </Text>

          <Text className="text-sm text-gray-600">
            {viewMode === 'uploaded'
              ? `${uploadedFiles.length} uploaded file${uploadedFiles.length !== 1 ? 's' : ''}`
              : 'Directory scanned successfully'}
          </Text>
        </div>

        {/* File Actions */}
        <div className="flex items-center justify-between">
          <Space>
            <Button onClick={handleSelectAll} size="small" disabled={displayFiles.length === 0}>
              Select All ({displayFiles.length})
            </Button>
            <Button onClick={handleSelectNone} size="small" disabled={selectedFiles.size === 0}>
              Select None
            </Button>
          </Space>

          {(viewMode === 'github' && (
            <Space>
              <Search
                placeholder="Filter files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-48"
                size="small"
              />
              <Dropdown
                overlay={
                  <Menu>
                    <Menu.SubMenu title="File Type">
                      <Menu.Item onClick={() => setFileTypeFilter('all')}>All Files</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('code')}>Code Files</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('config')}>Config Files</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('text')}>Text Files</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('image')}>Images</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('js')}>JavaScript</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('ts')}>TypeScript</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('py')}>Python</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('json')}>JSON</Menu.Item>
                      <Menu.Item onClick={() => setFileTypeFilter('md')}>Markdown</Menu.Item>
                    </Menu.SubMenu>
                    <Menu.SubMenu title="File Size">
                      <Menu.Item onClick={() => setSizeFilter('all')}>All Sizes</Menu.Item>
                      <Menu.Item onClick={() => setSizeFilter('small')}>Small Less 10KB</Menu.Item>
                      <Menu.Item onClick={() => setSizeFilter('medium')}>Medium 10KB - 100KB</Menu.Item>
                      <Menu.Item onClick={() => setSizeFilter('large')}>Large More 100KB</Menu.Item>
                    </Menu.SubMenu>
                  </Menu>
                }
                trigger={['click']}
              >
                <Button size="small" icon={<UnorderedListOutlined />}>
                  Filters {(fileTypeFilter !== 'all' || sizeFilter !== 'all') && '•'}
                </Button>
              </Dropdown>
            </Space>
          ))}
        </div>

        {/* File List */}
        <div className="rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="border-b border-gray-200 bg-gray-50 px-4 py-2 dark:border-gray-700 dark:bg-gray-800">
            <div className="grid grid-cols-12 gap-4 text-xs font-medium text-gray-600 dark:text-gray-400">
              <div className="col-span-5">
                {viewMode === 'uploaded' ? 'File Name' : 'File Path'}
              </div>
              <div className="col-span-2">Size</div>
              <div className="col-span-3">Date</div>
              <div className="col-span-2 text-right">Type</div>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {loading || uploadLoading ? (
              <div className="flex items-center justify-center py-8">
                <Spin size="large" />
              </div>
            ) : displayFiles.length === 0 ? (
              <div className="py-8 text-center text-gray-500">
                {viewMode === 'uploaded' ? 'No uploaded files found' : 'No files found'}
              </div>
            ) : (
              displayFiles.map((file) => (
                <div
                  key={file.path}
                  className="grid grid-cols-12 gap-4 border-b border-gray-100 px-4 py-1.5 last:border-b-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800"
                >
                  <div className="col-span-5 flex items-center gap-2">
                    <Checkbox
                      checked={selectedFiles.has(file.path)}
                      onChange={(e) => handleFileToggle(file.path, e.target.checked)}
                    />
                    {getFileIcon(file)}
                    <Text className="truncate text-sm">
                      {viewMode === 'uploaded' ? file.name : file.path}
                    </Text>
                    {file.is_uploaded && (
                      <span className="rounded bg-green-100 px-2 py-1 text-xs text-green-800 dark:bg-green-900 dark:text-green-200">
                        Uploaded
                      </span>
                    )}
                  </div>

                  <div className="col-span-2 flex items-center">
                    <Text className="text-xs text-gray-500">{formatFileSize(file.size)}</Text>
                  </div>

                  <div className="col-span-3 flex items-center">
                    <Text className="text-xs text-gray-500">{formatFileDate(file.date || '')}</Text>
                  </div>

                  <div className="col-span-2 flex items-center justify-end">
                    {file.is_uploaded ? (
                      <Text className="text-xs text-green-600 dark:text-green-400">Upload</Text>
                    ) : (
                      <Text className="text-xs text-gray-400">Local</Text>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Selection Summary */}
        <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
          <Text className="text-sm">
            <strong>{selectedFiles.size}</strong> files selected
            {selectedFiles.size > 0 && (
              <span className="ml-2 text-gray-600 dark:text-gray-400">
                Total size:{' '}
                {formatFileSize(
                  [...files, ...uploadedFiles]
                    .filter((f) => selectedFiles.has(f.path))
                    .reduce((sum, f) => sum + f.size, 0)
                )}
              </span>
            )}
          </Text>
        </div>
      </div>
    </Modal>
  )
}

export default ContextModal
