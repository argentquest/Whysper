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

export interface Tab {
  id: string;
  conversationId: string;
  title: string;
  isActive: boolean;
  isDirty: boolean;
  type: 'chat' | 'file' | 'shell';
  filePath?: string;
  fileContent?: string;
  originalContent?: string;
  shellSessionId?: string;
  shellType?: string;
}

export interface AppSettings {
  theme: ThemeKey;
  provider: string;
  model: string;
  systemPrompt: string;
  contextFiles: string[];
  maxTokens: number;
  temperature: number;
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