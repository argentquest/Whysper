/**
 * index Type Definitions
 *
 * TypeScript type definitions and interfaces for index.
 */
// Core application types
import type { ThemeKey } from '../themes/antd-themes'

/**
 * Conversation type definition
 *
 * Describes the structure and properties of Conversation
 */
export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

/**
 * Message type definition
 *
 * Describes the structure and properties of Message
 */
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: {
    model?: string
    provider?: string
    tokens?: number
    inputTokens?: number
    outputTokens?: number
    cachedTokens?: number
    elapsedTime?: number // in seconds
    codeBlocks?: CodeBlock[]
    mermaidDiagrams?: MermaidDiagram[]
    d2Diagrams?: D2Diagram[]
  }
}

/**
 * CodeBlock type definition
 *
 * Describes the structure and properties of CodeBlock
 */
export interface CodeBlock {
  id: string
  language: string
  code: string
  filename?: string
}

/**
 * MermaidDiagram type definition
 *
 * Describes the structure and properties of MermaidDiagram
 */
export interface MermaidDiagram {
  id: string
  code: string
  title?: string
}

/**
 * D2Diagram type definition
 *
 * Describes the structure and properties of D2Diagram
 */
export interface D2Diagram {
  id: string
  code: string
  title?: string
  svgContent?: string
}

/**
 * Tab type definition
 *
 * Describes the structure and properties of Tab
 */
export interface Tab {
  id: string
  conversationId: string
  title: string
  isActive: boolean
  isDirty: boolean
  type: 'chat' | 'file' | 'documentation' | 'diagramWizard'
  filePath?: string
  fileContent?: string
  originalContent?: string
  // Additional properties for new tab types
  sessionId?: string // For diagram wizard sessions
}

/**
 * AppSettings type definition
 *
 * Describes the structure and properties of AppSettings
 */
export interface AppSettings {
  theme: ThemeKey
  provider: string
  model: string
  systemPrompt: string
  contextFiles: string[]
  maxTokens: number
  temperature: number
  timeout?: number // Frontend timeout in seconds for API requests
  values?: { [key: string]: string }
  masked?: { [key: string]: boolean }
  agentPrompts?: AgentPrompt[]
  subagentCommands?: SubagentCommand[]
}

/**
 * FileItem type definition
 *
 * Describes the structure and properties of FileItem
 */
export interface FileItem {
  path: string
  name: string
  size: number
  isSelected: boolean
  type: 'file' | 'directory'
  is_uploaded?: boolean // Flag to indicate if this is an uploaded file
  content?: string // File content for uploaded files
}

/**
 * ApiResponse type definition
 *
 * Describes the structure and properties of ApiResponse
 */
export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

/**
 * Response from the GitHub repository import API endpoint.
 *
 * This interface defines the structure returned by POST /api/v1/github/import
 * after successfully fetching and scanning a public GitHub repository. The data
 * is compatible with the existing Set Context UI (ContextModal, FileTreeModal).
 *
 * @interface GitHubImportResponse
 * @property {string} repository - Repository identifier in "owner/name" format (e.g., "facebook/react")
 * @property {string} ref - Git reference that was fetched (branch, tag, or commit SHA)
 * @property {string} rootPath - Local filesystem path to the cached repository root
 * @property {string} scanPath - Local filesystem path that was scanned (may be a subdirectory)
 * @property {FileItem[]} files - Array of file metadata compatible with file selection UI
 * @property {Record<string, unknown>} tree - Hierarchical directory tree for tree view navigation
 * @property {string} message - User-friendly success message (e.g., "Loaded python/cpython@main from GitHub")
 *
 * @example
 * const response: GitHubImportResponse = {
 *   repository: "python/cpython",
 *   ref: "3.11",
 *   rootPath: "/cache/python/cpython/3.11",
 *   scanPath: "/cache/python/cpython/3.11/Lib",
 *   files: [
 *     { path: "Lib/os.py", name: "os.py", size: 12345, isSelected: false },
 *     { path: "Lib/sys.py", name: "sys.py", size: 6789, isSelected: false }
 *   ],
 *   tree: {
 *     name: "Lib",
 *     type: "directory",
 *     children: [...]
 *   },
 *   message: "Loaded python/cpython@3.11 from GitHub"
 * }
 */
export interface GitHubImportResponse {
  repository: string
  ref: string
  rootPath: string
  scanPath: string
  files: FileItem[]
  tree: Record<string, unknown>
  message: string
}

/**
 * ChatRequest type definition
 *
 * Describes the structure and properties of ChatRequest
 */
export interface ChatRequest {
  message: string
  conversationId?: string
  contextFiles?: string[]
  settings?: Partial<AppSettings>
}

/**
 * ChatResponse type definition
 *
 * Describes the structure and properties of ChatResponse
 */
export interface ChatResponse {
  message: Message
  conversationId: string
  usage?: {
    promptTokens: number
    completionTokens: number
    totalTokens: number
  }
}

/**
 * AgentPrompt type definition
 *
 * Describes the structure and properties of AgentPrompt
 */
export interface AgentPrompt {
  name: string
  title: string
  filename: string
  description?: string
  category?: string[]
}

/**
 * SubagentCommand type definition
 *
 * Describes the structure and properties of SubagentCommand
 */
export interface SubagentCommand {
  category: string
  title: string
  subcommand: string
}

/**
 * FileContent type definition
 *
 * Describes the structure and properties of FileContent
 */
export interface FileContent {
  path: string
  content: string
  size: number
}

/**
 * FileSaveRequest type definition
 *
 * Describes the structure and properties of FileSaveRequest
 */
export interface FileSaveRequest {
  path: string
  content: string
}

/**
 * FileSaveResponse type definition
 *
 * Describes the structure and properties of FileSaveResponse
 */
export interface FileSaveResponse {
  success: boolean
  message: string
  data: {
    path: string
    size: number
  }
}

/**
 * UploadedFile type definition
 *
 * Describes the structure and properties of UploadedFile
 */
export interface UploadedFile {
  name: string
  content: string
  size: number
  type: string
}

/**
 * FileUploadRequest type definition
 *
 * Describes the structure and properties of FileUploadRequest
 */
export interface FileUploadRequest {
  files: UploadedFile[]
  target_directory?: string
}

/**
 * FileUploadResponse type definition
 *
 * Describes the structure and properties of FileUploadResponse
 */
export interface FileUploadResponse {
  success: boolean
  message: string
  data: {
    files: FileItem[]
    total_files: number
    total_size: number
    upload_directory: string
  }
}
