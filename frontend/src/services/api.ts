/**
 * API Service for WhisperCode Web2 Frontend
 * 
 * This service handles all HTTP communication with the WhisperCode Web2 Backend.
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
 * - Mermaid rendering: diagram generation from markdown
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
  CodeBlock      // Code block structure
} from '../types';

// Backend API base URL - matches the FastAPI server port
const API_BASE_URL = 'http://localhost:8001/api/v1';

/**
 * Axios HTTP client configuration
 * 
 * Configured with:
 * - 30-second timeout for AI operations (some AI calls can be slow)
 * - JSON content type for all requests
 * - Base URL pointing to FastAPI backend
 */
const api = axios.create({
  baseURL: API_BASE_URL,                    // FastAPI backend URL
  timeout: 30000,                           // 30 second timeout for AI operations
  headers: {
    'Content-Type': 'application/json',     // JSON API communication
  },
});

// ==================== Request Interceptor ====================
// Logs all outgoing API requests for debugging and monitoring
api.interceptors.request.use(
  (config) => {
    // Log request details in development mode
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    // Log request setup errors
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// ==================== Response Interceptor ====================
// Handles errors and provides consistent error logging
api.interceptors.response.use(
  (response) => {
    // Successful responses pass through unchanged
    return response;
  },
  (error) => {
    // Log all API errors for debugging
    console.error('API Response Error:', error);
    
    // Handle specific HTTP status codes
    if (error.response?.status === 401) {
      // Authentication/authorization errors
      console.warn('Authentication required');
    } else if (error.response?.status >= 500) {
      // Server-side errors (backend issues)
      console.error('Server error:', error.response.status);
    }
    
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
      const response = await api.post('/chat', request);
      return response.data;
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

  // File context endpoints
  static async getFiles(directory?: string): Promise<ApiResponse<FileItem[]>> {
    try {
      const params = directory ? { directory } : {};
      const response = await api.get('/files', { params });
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
      return response.data;
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

  // NEW: Mermaid diagram rendering endpoint
  static async renderMermaid(code: string, title?: string): Promise<ApiResponse<string>> {
    try {
      const response = await api.post('/mermaid/render', { code, title });
      return response.data;
    } catch (error: unknown) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to render mermaid diagram',
      };
    }
  }
}

export default ApiService;
