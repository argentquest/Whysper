// Core application types
import type { ThemeKey } from '../themes/antd-themes';

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    provider?: string;
    tokens?: number;
    inputTokens?: number;
    outputTokens?: number;
    cachedTokens?: number;
    elapsedTime?: number; // in seconds
    codeBlocks?: CodeBlock[];
    mermaidDiagrams?: MermaidDiagram[];
    d2Diagrams?: D2Diagram[];
  };
}

export interface CodeBlock {
  id: string;
  language: string;
  code: string;
  filename?: string;
}

export interface MermaidDiagram {
  id: string;
  code: string;
  title?: string;
}

export interface D2Diagram {
  id: string;
  code: string;
  title?: string;
  svgContent?: string;
}

export interface Tab {
  id: string;
  conversationId: string;
  title: string;
  isActive: boolean;
  isDirty: boolean;
  type: 'chat' | 'file' | 'documentation';
  filePath?: string;
  fileContent?: string;
  originalContent?: string;
}

export interface AppSettings {
  theme: ThemeKey;
  provider: string;
  model: string;
  systemPrompt: string;
  contextFiles: string[];
  maxTokens: number;
  temperature: number;
  timeout?: number; // Frontend timeout in seconds for API requests
  values?: {[key: string]: string};
  masked?: {[key: string]: boolean};
  agentPrompts?: AgentPrompt[];
  subagentCommands?: SubagentCommand[];
}

export interface FileItem {
  path: string;
  name: string;
  size: number;
  isSelected: boolean;
  type: 'file' | 'directory';
  is_uploaded?: boolean; // Flag to indicate if this is an uploaded file
  content?: string; // File content for uploaded files
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  contextFiles?: string[];
  settings?: Partial<AppSettings>;
}

export interface ChatResponse {
  message: Message;
  conversationId: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
}

export interface AgentPrompt {
  name: string;
  title: string;
  filename: string;
  description?: string;
  category?: string[];
}

export interface SubagentCommand {
  category: string;
  title: string;
  subcommand: string;
}

export interface FileContent {
  path: string;
  content: string;
  size: number;
}

export interface FileSaveRequest {
  path: string;
  content: string;
}

export interface FileSaveResponse {
  success: boolean;
  message: string;
  data: {
    path: string;
    size: number;
  };
}

export interface UploadedFile {
  name: string;
  content: string;
  size: number;
  type: string;
}

export interface FileUploadRequest {
  files: UploadedFile[];
  target_directory?: string;
}

export interface FileUploadResponse {
  success: boolean;
  message: string;
  data: {
    files: FileItem[];
    total_files: number;
    total_size: number;
    upload_directory: string;
  };
}