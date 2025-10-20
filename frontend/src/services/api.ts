/**
 * API Service for Whysper Web2 Frontend
 * 
 * This service handles all HTTP communication with the Whysper Web2 Backend.
 * It provides a clean interface for frontend components to interact with the
 * FastAPI backend without directly dealing with HTTP requests.
 * 
 * Features:
 * - Axios-based HTTP client with interceptors
 * - Automatic error handling and logging
 * - Type-safe request/response handling
 * - Timeout configuration for long-running operations
 * - Development-friendly request/response logging
 * 
 * API Structure:
 * - Chat operations: sending messages, managing conversations
 * - Code extraction: parsing code blocks from AI responses
 * - Settings management: user preferences and AI configuration
 * - File operations: context file handling
 */

// HTTP client library
import axios from 'axios';

// TypeScript type definitions for API communication
import type {
  ApiResponse,   // Standard API response wrapper
  ChatRequest,   // Chat message request structure
  ChatResponse,  // Chat message response structure
  Conversation,  // Conversation data structure
  AppSettings,   // Application settings structure
  FileItem,      // File attachment structure
  CodeBlock,     // Code block structure
  FileUploadRequest,  // File upload request structure
  FileUploadResponse, // File upload response structure
  UploadedFile   // Uploaded file structure
} from '../types';

// Backend API base URL - development mode uses separate ports
// You can override the backend port by setting VITE_BACKEND_PORT in frontend/.env
const BACKEND_PORT = import.meta.env.VITE_BACKEND_PORT || '8003';
const API_BASE_URL = import.meta.env.DEV ? `http://localhost:${BACKEND_PORT}/api/v1` : '/api/v1';

/**
 * Axios HTTP client configuration
 *
 * Configured with:
 * - 60-second timeout for AI operations (D2 rendering can take time)
 * - JSON content type for all requests
 * - Base URL pointing to FastAPI backend
 * - Increased max content length for large diagram responses
 */
const api = axios.create({
  baseURL: API_BASE_URL,                    // FastAPI backend URL
  timeout: 60000,                           // 60 second timeout for AI operations (was 30000)
  maxContentLength: 50 * 1024 * 1024,       // 50 MB max response size
  maxBodyLength: 50 * 1024 * 1024,          // 50 MB max request size
  headers: {
    'Content-Type': 'application/json',     // JSON API communication
  },
});

// ==================== Request Interceptor ====================
// Logs all outgoing API requests for debugging and monitoring
api.interceptors.request.use(
  (config) => {
    // Enhanced debug logging in development mode
    console.group(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log('Base URL:', config.baseURL);
    console.log('Full URL:', `${config.baseURL}${config.url}`);
    console.log('Headers:', config.headers);
    if (config.data) {
      console.log('Request Data:', config.data);
    }
    if (config.params) {
      console.log('Query Params:', config.params);
    }
    console.groupEnd();
    return config;
  },
  (error) => {
    // Log request setup errors
    console.error('❌ API Request Setup Error:', error);
    return Promise.reject(error);
  }
);

// ==================== Response Interceptor ====================
// Handles errors and provides consistent error logging
api.interceptors.response.use(
  (response) => {
    // Enhanced success logging
    console.group(`✅ API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    console.log('Response Data:', response.data);
    console.log('Response Headers:', response.headers);
    console.groupEnd();
    return response;
  },
  (error) => {
    // Enhanced error logging for debugging
    console.group(`❌ API Response Error: ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
    console.error('Error Details:', error);
    console.log('Error Code:', error.code);
    console.log('Error Message:', error.message);
    
    if (error.response) {
      // Server responded with error status
      console.log('Response Status:', error.response.status);
      console.log('Response Data:', error.response.data);
      console.log('Response Headers:', error.response.headers);
      
      // Handle specific HTTP status codes
      if (error.response.status === 401) {
        console.warn('🔒 Authentication required');
      } else if (error.response.status >= 500) {
        console.error('🚨 Server error:', error.response.status);
      }
    } else if (error.request) {
      // Network error - no response received
      console.error('🌐 Network Error - No response received');
      console.log('Request Details:', error.request);
    } else {
      // Something else happened
      console.error('⚠️ Request Setup Error:', error.message);
    }
    console.groupEnd();
    
    return Promise.reject(error);
  }
);

/**
 * API Service Class
 * 
 * Provides static methods for all backend API operations.
 * Each method handles a specific API endpoint and provides
 * type-safe interfaces for frontend components.
 */
export class ApiService {
  // Chat endpoints
  static async sendMessage(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    try {
      const accessKey = sessionStorage.getItem('access_key');
      const requestData = { ...request, settings: { ...request.settings, access_key: accessKey } };
      const response = await api.post('/chat', requestData);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to send message',
      };
    }
  }

  // Conversation endpoints
  static async getConversations(): Promise<ApiResponse<Conversation[]>> {
    try {
      const response = await api.get('/conversations');
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch conversations',
      };
    }
  }

  static async getConversation(id: string): Promise<ApiResponse<Conversation>> {
    try {
      const response = await api.get(`/conversations/${id}`);
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch conversation',
      };
    }
  }

  static async saveConversation(conversation: Conversation): Promise<ApiResponse<Conversation>> {
    try {
      const response = await api.post('/conversations', conversation);
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to save conversation',
      };
    }
  }

  static async deleteConversation(id: string): Promise<ApiResponse<void>> {
    try {
      const response = await api.delete(`/conversations/${id}`);
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete conversation',
      };
    }
  }

  static async clearConversation(conversationId: string): Promise<ApiResponse<{message: string, conversationId: string}>> {
    try {
      const response = await api.post(`/chat/conversations/${conversationId}/clear`);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to clear conversation',
      };
    }
  }

  // File context endpoints
  static async getFiles(directory?: string): Promise<ApiResponse<FileItem[]>> {
    try {
      const params = directory ? { directory } : {};
      const response = await api.get('/files/', { params });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch files',
      };
    }
  }

  static async loadDirectory(path: string): Promise<ApiResponse<FileItem[]>> {
    try {
      const response = await api.post('/files/load', { path });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to load directory',
      };
    }
  }

  // Settings endpoints
  static async getSettings(): Promise<ApiResponse<AppSettings>> {
    try {
      const response = await api.get('/settings');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch settings',
      };
    }
  }

  static async updateSettings(settings: Partial<AppSettings>): Promise<ApiResponse<AppSettings>> {
    try {
      const response = await api.put('/settings', settings);
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update settings',
      };
    }
  }

  static async updateEnvSettings(envUpdates: {[key: string]: string}): Promise<ApiResponse<Record<string, boolean>>> {
    try {
      const response = await api.put('/settings/env', { updates: envUpdates });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update environment settings',
      };
    }
  }

  static async restartServer(): Promise<ApiResponse<{message: string}>> {
    try {
      const response = await api.post('/settings/restart');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to restart server',
      };
    }
  }

  // System endpoints
  static async getSystemInfo(): Promise<ApiResponse<Record<string, unknown>>> {
    try {
      const response = await api.get('/system/info');
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch system info',
      };
    }
  }

  static async executeSystemPrompt(prompt: string): Promise<ApiResponse<ChatResponse>> {
    try {
      const response = await api.post('/system/execute', { prompt });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute system prompt',
      };
    }
  }

  // NEW: Code extraction endpoint
  static async extractCode(messageId: string): Promise<ApiResponse<CodeBlock[]>> {
    try {
      const response = await api.post('/code/extract', { messageId });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to extract code',
      };
    }
  }

  // Agent prompts endpoints
  static async getAgents(): Promise<ApiResponse<any[]>> {
    try {
      const response = await api.get('/settings/agents');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get agents',
      };
    }
  }

  static async getSubagents(): Promise<ApiResponse<any[]>> {
    try {
      const response = await api.get('/settings/subagents');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get subagents',
      };
    }
  }

  static async getAgentPrompt(filename: string): Promise<ApiResponse<{filename: string, content: string}>> {
    try {
      const response = await api.get(`/settings/agent-prompts/${filename}`);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get agent prompt',
      };
    }
  }

  // Diagram event logging
  static async logDiagramEvent(event: {
    event_type: 'detection' | 'render_start' | 'render_success' | 'render_error';
    diagram_type: 'mermaid' | 'd2';
    code_preview?: string;
    code_length?: number;
    error_message?: string;
    detection_method?: string;
    conversation_id?: string;
  }): Promise<ApiResponse<any>> {
    try {
      const response = await api.post('/diagrams/log-diagram-event', event);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      // Silently fail - logging errors shouldn't break the UI
      console.warn('Failed to log diagram event to backend:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to log diagram event',
      };
    }
  }

  // Generic HTTP methods for file operations
  static async get(url: string): Promise<any> {
    try {
      const response = await api.get(url);
      return response;
    } catch (error: unknown) {
      throw error;
    }
  }

  static async post(url: string, data: any): Promise<any> {
    try {
      const response = await api.post(url, data);
      return response;
    } catch (error: unknown) {
      throw error;
    }
  }

  static async delete(url: string): Promise<any> {
    try {
      const response = await api.delete(url);
      return response;
    } catch (error: unknown) {
      throw error;
    }
  }
  // File upload endpoints
  static async uploadFiles(request: FileUploadRequest): Promise<ApiResponse<FileUploadResponse>> {
    try {
      const response = await api.post('/files/upload', request);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to upload files',
      };
    }
  }

  static async getUploadedFiles(): Promise<ApiResponse<FileItem[]>> {
    try {
      const response = await api.get('/files/uploaded');
      return {
        success: true,
        data: response.data.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch uploaded files',
      };
    }
  }

  // Documentation endpoints
  static async generateDocumentation(request: {
    file_paths: string[];
    documentation_type: string;
    output_format?: string;
    include_examples?: boolean;
    include_diagrams?: boolean;
    target_audience?: string;
    language?: string;
  }): Promise<ApiResponse<{
    id: string;
    content: string;
    metadata: Record<string, any>;
    diagrams: Array<Record<string, any>>;
    examples: Array<Record<string, any>>;
    references: string[];
    generated_at: string;
    processing_time: number;
    token_usage: Record<string, number>;
  }>> {
    try {
      const response = await api.post('/documentation/generate', request);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate documentation',
      };
    }
  }

  static async generateBulkDocumentation(request: {
    file_paths: string[];
    include_source_files?: boolean;
    documentation_types?: string[];
  }): Promise<Blob> {
    try {
      const response = await api.post('/documentation/generate-bulk', request, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error: unknown) {
      throw new Error(error instanceof Error ? error.message : 'Failed to generate bulk documentation');
    }
  }

  static async getDocumentationTemplates(): Promise<ApiResponse<{
    templates: Array<{
      name: string;
      title: string;
      description: string;
      supported_formats: string[];
      instructions: string;
    }>;
    count: number;
  }>> {
    try {
      const response = await api.get('/documentation/templates');
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch documentation templates',
      };
    }
  }

  static async exportDocumentation(request: {
    documentation_id: string;
    export_format: string;
    content: string;
    filename?: string;
    options?: Record<string, any>;
  }): Promise<ApiResponse<{
    content: string;
    format: string;
    filename: string;
    content_type: string;
  }>> {
    try {
      const response = await api.post('/documentation/export', request);
      return {
        success: true,
        data: response.data
      };
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to export documentation',
      };
    }
  }

  static async verifyAccessKey(accessKey: string): Promise<ApiResponse<{success: boolean}>> {
    try {
      const response = await api.post('/auth/verify', { access_key: accessKey });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Invalid access key.',
      };
    }
  }
}

export default ApiService;
