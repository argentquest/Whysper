/**
 * Whysper Web2 - Main Application Component
 * 
 * This is the root component of the Whysper Web2 React application.
 * It provides a modern AI chat interface with multi-tab support, real-time
 * AI integration, and comprehensive conversation management.
 * 
 * Key Features:
 * - Multi-tab conversation management
 * - Real AI integration with multiple providers (OpenRouter, Anthropic, OpenAI)
 * - Code extraction and Mermaid diagram rendering
 * - Context file attachment support
 * - Theme switching (light/dark mode)
 * - Conversation persistence and history
 * - Settings management and system prompt configuration
 * 
 * Architecture:
 * - State management using React hooks (useState, useEffect)
 * - Ant Design components for UI consistency
 * - TypeScript for type safety
 * - Service layer for API communication
 * - Modal-based secondary interfaces
 */

// React core and hooks
import { useState, useEffect, useCallback } from 'react';

// Ant Design UI components
import { Layout, message, Modal, Button } from 'antd';
import { CopyOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';

// Layout components
import { Header } from './components/layout/Header';
import { TabManager } from './components/layout/TabManager';
import { ChatView } from './components/chat/ChatView';
import { InputPanel } from './components/chat/InputPanel';
import { StatusBar } from './components/layout/StatusBar';

// Helper function to convert theme key to editor theme mode
const getEditorTheme = (themeKey: string): 'light' | 'dark' => {
  const darkThemes = ['dark', 'proDark'];
  return darkThemes.includes(themeKey) ? 'dark' : 'light';
};

// Modal components for secondary interfaces
import {
  ContextModal,      // File selection and context management
  SettingsModal,     // Application settings and AI configuration
  AboutModal,        // Application information and version details
  SystemMessageModal,// System prompt customization
  CodeFragmentsModal,// Extracted code blocks management
  FileSelectionModal, // File selection for editing
  NewFileModal,       // New file creation modal
} from './components/modals';
import ThemePickerModal from './components/modals/ThemePickerModal';

// File editor components
import { FileEditorView } from './components/editor/FileEditorView';

// Terminal components  
import { ShellView } from './components/terminal/ShellView';

// Theme management
import { useTheme } from './themes';

// API service for backend communication
import ApiService from './services/api';

// TypeScript type definitions
import type { 
  Conversation,  // Conversation data structure
  Message,       // Individual chat message
  Tab,          // Tab management structure
  AppSettings,  // Application configuration
  FileItem,     // File attachment structure
  CodeBlock,    // Extracted code block structure
  AgentPrompt,  // Agent prompt structure
} from './types';

// Extract Layout.Content for cleaner JSX
const { Content } = Layout;

/**
 * Main App Component
 * 
 * Manages the entire application state and provides the main UI layout.
 * Orchestrates communication between all child components and the backend API.
 */
function App() {
  // Theme management hook for light/dark mode switching
  const { theme, toggleTheme } = useTheme();
  
  // ==================== Core Application State ====================
  
  // Conversation management: stores all conversations by ID
  const [conversations, setConversations] = useState<{ [key: string]: Conversation }>({});
  
  // Tab management: supports multiple conversation tabs like a modern IDE
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string>('');
  
  // Global loading state for API operations
  const [loading, setLoading] = useState(false);
  
  // Application settings: AI provider, model, system prompt, etc.
  const [settings, setSettings] = useState<AppSettings>({
    theme: theme,                    // Current theme (light/dark)
    provider: '',                    // AI provider - will be loaded from backend
    model: '',                       // AI model - will be loaded from backend
    systemPrompt: '',                // System prompt - will be loaded from backend
    contextFiles: [],               // Files to include in AI context
    maxTokens: 4000,                // Maximum tokens for AI responses
    temperature: 0.7,               // AI creativity/randomness (0.0-1.0)
  });
  
  // ==================== Modal State Management ====================
  // Controls visibility of various modal dialogs
  
  const [contextModalOpen, setContextModalOpen] = useState(false);           // File selection modal
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);        // Settings configuration modal
  const [aboutModalOpen, setAboutModalOpen] = useState(false);              // About/version information modal
  const [systemMessageModalOpen, setSystemMessageModalOpen] = useState(false); // System prompt editor modal
  const [codeFragmentsModalOpen, setCodeFragmentsModalOpen] = useState(false);  // Code extraction results modal
  const [themePickerModalOpen, setThemePickerModalOpen] = useState(false);  // Theme selection modal
  const [mermaidModalOpen, setMermaidModalOpen] = useState(false);          // Mermaid diagram display modal
  const [fileSelectionModalOpen, setFileSelectionModalOpen] = useState(false); // File editor selection modal
  const [newFileModalOpen, setNewFileModalOpen] = useState(false);         // New file creation modal
  const [mermaidImageData, setMermaidImageData] = useState<string>('');     // Rendered mermaid diagram data
  const [codeModalOpen, setCodeModalOpen] = useState(false);               // Code fragment display modal
  const [codeModalData, setCodeModalData] = useState<{code: string, language: string, title?: string}>({code: '', language: ''});
  
  // ==================== Data State Management ====================
  
  // Files selected for AI context inclusion
  const [selectedFiles, setSelectedFiles] = useState<FileItem[]>([]);
  
  // Code blocks extracted from AI responses for download/management
  const [extractedCodeBlocks, setExtractedCodeBlocks] = useState<CodeBlock[]>([]);
  
  // Agent prompts loaded from backend
  const [agentPrompts, setAgentPrompts] = useState<AgentPrompt[]>([]);

  // Subagent commands loaded from backend
  const [subagentCommands, setSubagentCommands] = useState<any[]>([]);

  // ==================== Application Initialization ====================

  const loadSettings = useCallback(async () => {
    console.log('🔧 Loading application settings...');
    try {
      const response = await ApiService.getSettings();
      console.log('📡 Settings API response:', response);
      if (response.success && response.data) {
        const backendSettings = response.data;

        // Map backend settings to frontend settings structure
        const mappedSettings: AppSettings = {
          theme: theme,
          provider: backendSettings.values?.PROVIDER || 'openrouter',
          model: backendSettings.values?.DEFAULT_MODEL || backendSettings.values?.MODELS?.split(',')[0]?.trim() || '',
          systemPrompt: backendSettings.values?.SYSTEM_PROMPT || 'You are a helpful AI assistant specialized in code analysis and development.',
          contextFiles: [],
          maxTokens: parseInt(backendSettings.values?.MAX_TOKENS || '4000', 10),
          temperature: parseFloat(backendSettings.values?.TEMPERATURE || '0.7'),
        };

        console.log('⚙️ Mapped settings:', mappedSettings);
        setSettings(mappedSettings);
      }
    } catch (error) {
      console.error('❌ Failed to load settings:', error);
      // Set fallback defaults if backend is not available
      setSettings(prev => ({
        ...prev,
        provider: 'openrouter',
        model: 'x-ai/grok-code-fast-1',
        systemPrompt: 'You are a helpful AI assistant specialized in code analysis and development.',
      }));
    }
  }, []);

  const loadAgentPrompts = useCallback(async () => {
    try {
      const response = await ApiService.getAgents();
      if (response.success && response.data) {
        setAgentPrompts(response.data);
      } else {
        console.warn('Could not load agent prompts:', response.error);
      }
    } catch (error) {
      console.warn('Could not load agent prompts:', error);
    }
  }, []);

  const loadSubagentCommands = useCallback(async () => {
    try {
      const response = await ApiService.getSubagents();
      if (response.success && response.data) {
        setSubagentCommands(response.data);
      } else {
        console.warn('Could not load subagent commands:', response.error);
      }
    } catch (error) {
      console.warn('Could not load subagent commands:', error);
    }
  }, []);

  // Initialize the application with default state
  // Creates the first tab and conversation, then loads user settings from backend.
  // This ensures the app always has a usable conversation interface ready.
  const initializeApp = useCallback(async () => {
    // Create the initial tab for the first conversation
    const initialTab: Tab = {
      id: 'tab-1',                    // Unique tab identifier
      conversationId: 'conv-1',       // Associated conversation ID
      title: 'Chat 1',               // Display name in tab bar
      isActive: true,                 // This tab is currently active
      isDirty: false,                 // No unsaved changes yet
      type: 'chat',                   // This is a chat tab
    };

    // Create the initial empty conversation
    const initialConversation: Conversation = {
      id: 'conv-1',                          // Unique conversation identifier
      title: 'New Conversation',            // Display title
      messages: [],                          // Start with empty message history
      createdAt: new Date().toISOString(),  // Creation timestamp
      updatedAt: new Date().toISOString(),  // Last update timestamp
    };

    // Set up initial application state
    setTabs([initialTab]);
    setActiveTabId(initialTab.id);
    setConversations({ [initialConversation.id]: initialConversation });

    // Load user settings from backend (API keys, preferences, etc.)
    await loadSettings();
    // Load agent prompts from separate endpoint
    await loadAgentPrompts();
    // Load subagent commands from separate endpoint
    await loadSubagentCommands();
  }, [loadSettings, loadAgentPrompts, loadSubagentCommands]);

  // Initialize the application when component mounts
  useEffect(() => {
    initializeApp();
  }, [initializeApp]);

  // Chat functions
  const handleSendMessage = async (messageText: string, command?: string) => {
    console.group('💬 Sending chat message');
    console.log('Message text:', messageText);
    console.log('Command:', command);
    console.log('Active tab ID:', activeTabId);
    
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    if (!activeTab) {
      console.error('❌ No active tab found');
      console.groupEnd();
      return;
    }

    const conversation = conversations[activeTab.conversationId];
    if (!conversation) {
      console.error('❌ No conversation found for tab');
      console.groupEnd();
      return;
    }
    
    console.log('Active conversation:', conversation.id);

    // Create user message
    const userMessage: Message = {
      id: `msg-${Date.now()}-user`,
      role: 'user',
      content: command ? `${command.toUpperCase()}: ${messageText}` : messageText,
      timestamp: new Date().toISOString(),
    };

    // Update conversation with user message
    const updatedConversation = {
      ...conversation,
      messages: [...conversation.messages, userMessage],
      updatedAt: new Date().toISOString(),
    };

    setConversations(prev => ({
      ...prev,
      [conversation.id]: updatedConversation,
    }));

    // Mark tab as dirty
    setTabs(prev => prev.map(tab => 
      tab.id === activeTabId ? { ...tab, isDirty: true } : tab
    ));

    setLoading(true);

    try {
      // Send to API with ALL selected files (no limit)
      const apiRequest = {
        message: messageText,
        conversationId: conversation.id,
        contextFiles: selectedFiles.map(f => f.path),
        settings,
      };
      
      console.log('📡 Sending API request:', apiRequest);
      console.log('🗂️ Selected files count:', selectedFiles.length);
      console.log('🗂️ Selected files:', selectedFiles.map(f => f.path));
      
      const response = await ApiService.sendMessage(apiRequest);
      console.log('📡 Chat API response:', response);

      if (response.success && response.data) {
        const assistantMessage = response.data.message;
        console.log('📨 Received assistant message:', assistantMessage);
        
        // Update conversation with assistant response
        const finalConversation = {
          ...updatedConversation,
          messages: [...updatedConversation.messages, assistantMessage],
          updatedAt: new Date().toISOString(),
        };

        console.log('💬 Final conversation state:', finalConversation);
        setConversations(prev => ({
          ...prev,
          [conversation.id]: finalConversation,
        }));

        // Extract code blocks if any
        await extractCodeFromMessage(assistantMessage);
        console.log('✅ Chat message sent successfully');
      } else {
        console.error('❌ API response failed:', response.error);
        message.error(response.error || 'Failed to send message');
      }
    } catch (error) {
      console.error('❌ Send message error:', error);
      message.error('Error sending message');
    } finally {
      setLoading(false);
      console.groupEnd();
    }
  };

  const extractCodeFromMessage = async (msg: Message) => {
    try {
      const response = await ApiService.extractCode(msg.id);
      if (response.success && response.data) {
        setExtractedCodeBlocks(prev => [...prev, ...(response.data || [])]);
      }
    } catch (error) {
      console.warn('Could not extract code:', error);
    }
  };

  const handleRenderMermaid = async (code: string) => {
    try {
      const response = await ApiService.renderMermaid(code);
      if (response.success && response.data) {
        // Store the diagram data and show modal
        setMermaidImageData(response.data);
        setMermaidModalOpen(true);
        message.success('Mermaid diagram rendered successfully');
      } else {
        message.error(response.error || 'Failed to render mermaid diagram');
      }
    } catch (error) {
      message.error('Error rendering mermaid diagram');
      console.error('Mermaid render error:', error);
    }
  };

  const handleDownloadMermaid = () => {
    if (mermaidImageData) {
      const link = document.createElement('a');
      link.href = mermaidImageData;
      link.download = 'mermaid-diagram.png';
      link.click();
      message.success('Mermaid diagram downloaded');
    }
  };

  const handleShowCode = (code: string, language: string, title?: string) => {
    setCodeModalData({ code, language, title });
    setCodeModalOpen(true);
  };

  const handleCopyCode = async () => {
    if (codeModalData.code) {
      try {
        await navigator.clipboard.writeText(codeModalData.code);
        message.success('Code copied to clipboard');
      } catch (error) {
        console.error('Failed to copy code:', error);
        message.error('Failed to copy code');
      }
    }
  };

  const handleClearInput = () => {
    // Clear any input state if needed
    // This will be passed to InputPanel to clear its internal state
    message.info('Input cleared');
  };

  const handleSystemChange = async (systemType: string) => {
    // Find the agent prompt for this system type
    const agentPrompt = agentPrompts.find(prompt => prompt.name === systemType);

    if (agentPrompt) {
      try {
        // Load the actual prompt content from the backend
        const response = await ApiService.getAgentPrompt(agentPrompt.filename);
        if (response.success && response.data) {
          setSettings(prev => ({
            ...prev,
            systemPrompt: response.data?.content || '',
          }));
          message.success(`System changed to: ${agentPrompt.title}`);
        } else {
          message.error('Failed to load agent prompt');
        }
      } catch (error) {
        console.error('Error loading agent prompt:', error);
        message.error('Error loading agent prompt');
      }
    } else {
      // Fallback to hardcoded prompts
      setSettings(prev => ({
        ...prev,
        systemPrompt: getSystemPromptByType(systemType),
      }));
      message.success(`System changed to: ${systemType}`);
    }
  };


  const handleRunSystemPrompt = async (systemName: string) => {
    // Find the agent prompt for this system
    const agentPrompt = agentPrompts.find(prompt => prompt.name === systemName);

    if (agentPrompt) {
      try {
        // Load the actual prompt content from the backend
        const response = await ApiService.getAgentPrompt(agentPrompt.filename);
        if (response.success && response.data) {
          const promptContent = response.data.content;
          // Send the system prompt as a regular message
          await handleSendMessage(`Execute this system prompt: ${promptContent}`);
          message.success(`Running system prompt: ${agentPrompt.title}`);
        } else {
          message.error('Failed to load agent prompt');
        }
      } catch (error) {
        console.error('Error loading agent prompt for execution:', error);
        message.error('Error loading agent prompt');
      }
    } else {
      // Fallback to hardcoded prompts
      const promptContent = getSystemPromptByType(systemName);
      await handleSendMessage(`Execute this system prompt: ${promptContent}`);
      message.success(`Running system prompt: ${systemName}`);
    }
  };

  const getSystemPromptByType = (systemType: string): string => {
    const systemPrompts: { [key: string]: string } = {
      default: 'You are a helpful AI assistant specialized in code analysis and development.',
      coding: 'You are an expert software developer and code reviewer. Analyze code thoroughly, suggest improvements, identify bugs, and provide best practices.',
      documentation: 'You are a technical documentation specialist. Create clear, comprehensive documentation that is easy to understand.',
      refactoring: 'You are a refactoring specialist. Help improve code by removing code smells, improving readability, and updating to modern standards.',
      debugging: 'You are a debugging expert. Help identify bugs, analyze error messages, and provide step-by-step troubleshooting.'
    };
    return systemPrompts[systemType] || systemPrompts.default;
  };

  // ==================== File Editor Functions ====================
  
  // Handle file selection for editing
  const handleFileSelect = async (file: FileItem) => {
    const fileTabId = `file-tab-${Date.now()}`;
    const fileName = file.name;
    
    const newFileTab: Tab = {
      id: fileTabId,
      conversationId: '', // File tabs don't need conversation IDs
      title: fileName,
      isActive: false,
      isDirty: false,
      type: 'file',
      filePath: file.path,
      fileContent: '', // Will be loaded by FileEditorView
      originalContent: '', // Will be set when content is loaded
    };

    setTabs(prev => [...prev, newFileTab]);
    setActiveTabId(fileTabId);
    message.success(`Opened ${fileName} for editing`);
  };

  // Handle file content change in editor
  const handleFileContentChange = (tabId: string, content: string, isDirty: boolean) => {
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { 
            ...tab, 
            fileContent: content, 
            isDirty,
            // If this is the first load (not dirty), set originalContent to the content
            originalContent: !isDirty && !tab.originalContent ? content : tab.originalContent
          } 
        : tab
    ));
  };

  // Handle file save
  const handleFileSave = async (tabId: string) => {
    const tab = tabs.find(t => t.id === tabId);
    if (!tab || tab.type !== 'file' || !tab.filePath || !tab.fileContent) {
      throw new Error('Invalid file tab or missing content');
    }

    try {
      const response = await ApiService.post('/files/save', {
        path: tab.filePath,
        content: tab.fileContent,
      });

      if (response.data?.success) {
        // Update tab to mark as saved and update original content
        setTabs(prev => prev.map(t => 
          t.id === tabId 
            ? { ...t, isDirty: false, originalContent: tab.fileContent } 
            : t
        ));
      } else {
        throw new Error(response.data?.message || 'Save failed');
      }
    } catch (error: any) {
      console.error('Error saving file:', error);
      throw error; // Re-throw to be handled by FileEditorView
    }
  };

  // Handle new file creation
  const handleCreateNewFile = async (filePath: string, initialContent: string = '') => {
    try {
      const response = await ApiService.post('/files/create', {
        path: filePath,
        content: initialContent,
      });

      if (response.data?.success) {
        // Create a new file tab
        const fileName = filePath.split('/').pop() || filePath;
        const fileTabId = `file-tab-${Date.now()}`;
        
        const newFileTab: Tab = {
          id: fileTabId,
          conversationId: '',
          title: fileName,
          isActive: false,
          isDirty: false,
          type: 'file',
          filePath: filePath,
          fileContent: initialContent,
          originalContent: initialContent,
        };

        setTabs(prev => [...prev, newFileTab]);
        setActiveTabId(fileTabId);
        message.success(`Created new file: ${filePath}`);
        
        return true;
      } else {
        throw new Error(response.data?.message || 'File creation failed');
      }
    } catch (error: any) {
      console.error('Error creating file:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create file';
      message.error(`Failed to create file: ${errorMessage}`);
      throw error;
    }
  };

  // ==================== Shell Functions ====================
  
  // Handle shell session creation and opening
  const handleNewShell = (shellType: string = 'auto') => {
    const shellTabId = `shell-tab-${Date.now()}`;
    const shellCount = tabs.filter(t => t.type === 'shell').length + 1;
    
    // Create descriptive title based on shell type
    let title = '';
    switch (shellType) {
      case 'cmd':
        title = `CMD ${shellCount}`;
        break;
      case 'powershell':
        title = `PowerShell ${shellCount}`;
        break;
      case 'bash':
        title = `Bash ${shellCount}`;
        break;
      default:
        title = `Shell ${shellCount}`;
    }
    
    const newShellTab: Tab = {
      id: shellTabId,
      conversationId: '', // Shell tabs don't need conversation IDs
      title: title,
      isActive: false,
      isDirty: false,
      type: 'shell',
      shellSessionId: undefined, // Will be set by ShellView
      shellType: shellType, // Store the shell type for the tab
    };

    setTabs(prev => [...prev, newShellTab]);
    setActiveTabId(shellTabId);
    message.success(`New ${title} session created`);
  };

  // Handle shell session ID assignment
  const handleShellSessionChange = (tabId: string, sessionId: string) => {
    setTabs(prev => prev.map(tab => 
      tab.id === tabId 
        ? { ...tab, shellSessionId: sessionId } 
        : tab
    ));
  };

  // Tab management
  const handleTabChange = (tabId: string) => {
    setActiveTabId(tabId);
  };

  const handleNewTab = () => {
    const newTabId = `tab-${Date.now()}`;
    const newConversationId = `conv-${Date.now()}`;
    
    const newTab: Tab = {
      id: newTabId,
      conversationId: newConversationId,
      title: `Chat ${tabs.length + 1}`,
      isActive: false,
      isDirty: false,
      type: 'chat',
    };

    const newConversation: Conversation = {
      id: newConversationId,
      title: 'New Conversation',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setTabs(prev => [...prev, newTab]);
    setConversations(prev => ({ ...prev, [newConversationId]: newConversation }));
    setActiveTabId(newTabId);
  };

  const handleTabClose = (tabId: string) => {
    if (tabs.length <= 1) return;

    const tab = tabs.find(t => t.id === tabId);
    if (!tab) return;

    // If tab is dirty (has unsaved changes), show confirmation dialog
    if (tab.isDirty) {
      const fileName = tab.type === 'file' ? tab.title : tab.title;
      
      Modal.confirm({
        title: 'Unsaved Changes',
        content: (
          <div>
            <p>The file <strong>{fileName}</strong> has unsaved changes.</p>
            <p>What would you like to do?</p>
          </div>
        ),
        okText: 'Save & Close',
        okType: 'primary',
        cancelText: 'Close Without Saving',
        width: 500,
        onOk: async () => {
          try {
            // Save the tab first, then close it
            await handleTabSave(tabId);
            performTabClose(tabId);
            message.success('File saved and closed');
          } catch (error) {
            // If save fails, don't close the tab
            console.error('Failed to save before closing:', error);
            message.error('Failed to save file. Tab not closed.');
          }
        },
        onCancel: () => {
          // Close without saving
          performTabClose(tabId);
          message.info('File closed without saving');
        },
        okButtonProps: {
          icon: <SaveOutlined />,
        },
        cancelButtonProps: {
          danger: true,
          icon: <CloseOutlined />,
        },
      });
    } else {
      // Tab is not dirty, close immediately
      performTabClose(tabId);
    }
  };

  // Helper function to perform the actual tab close operation
  const performTabClose = (tabId: string) => {
    const tabIndex = tabs.findIndex(tab => tab.id === tabId);
    const newTabs = tabs.filter(tab => tab.id !== tabId);
    
    // If closing active tab, switch to next available tab
    if (tabId === activeTabId) {
      const nextTab = newTabs[Math.min(tabIndex, newTabs.length - 1)];
      setActiveTabId(nextTab.id);
    }

    setTabs(newTabs);
  };

  const handleTabSave = async (tabId: string) => {
    const tab = tabs.find(t => t.id === tabId);
    if (!tab) return;

    try {
      if (tab.type === 'file') {
        // Handle file tab save
        await handleFileSave(tabId);
      } else {
        // Handle chat tab save
        const conversation = conversations[tab.conversationId];
        if (!conversation) return;

        const response = await ApiService.saveConversation(conversation);
        if (response.success) {
          setTabs(prev => prev.map(t => 
            t.id === tabId ? { ...t, isDirty: false } : t
          ));
          message.success('Conversation saved');
        } else {
          message.error(response.error || 'Failed to save conversation');
        }
      }
    } catch (error: any) {
      const errorMessage = tab.type === 'file' 
        ? 'Error saving file' 
        : 'Error saving conversation';
      message.error(errorMessage);
      console.error('Save error:', error);
    }
  };

  const handleTabsAction = (action: string, tabId?: string) => {
    switch (action) {
      case 'duplicate': {
        if (tabId) {
          const tab = tabs.find(t => t.id === tabId);
          const conversation = conversations[tab?.conversationId || ''];
          if (tab && conversation) {
            const newTabId = `tab-${Date.now()}`;
            const newConversationId = `conv-${Date.now()}`;
            
            const newTab: Tab = {
              ...tab,
              id: newTabId,
              conversationId: newConversationId,
              title: `${tab.title} (Copy)`,
              isDirty: false,
            };

            const newConversation: Conversation = {
              ...conversation,
              id: newConversationId,
              title: `${conversation.title} (Copy)`,
              createdAt: new Date().toISOString(),
            };

            setTabs(prev => [...prev, newTab]);
            setConversations(prev => ({ ...prev, [newConversationId]: newConversation }));
            setActiveTabId(newTabId);
            message.success('Tab duplicated');
          }
        }
        break;
      }
        
      case 'close-others':
        if (tabId) {
          const otherTabs = tabs.filter(t => t.id !== tabId);
          const dirtyOtherTabs = otherTabs.filter(t => t.isDirty);
          
          if (dirtyOtherTabs.length > 0) {
            const fileNames = dirtyOtherTabs.map(t => t.title).join(', ');
            Modal.confirm({
              title: 'Unsaved Changes in Other Tabs',
              content: (
                <div>
                  <p>The following tabs have unsaved changes:</p>
                  <p><strong>{fileNames}</strong></p>
                  <p>What would you like to do?</p>
                </div>
              ),
              okText: 'Save All & Close Others',
              cancelText: 'Close Others Without Saving',
              width: 600,
              onOk: async () => {
                try {
                  // Save all dirty tabs first
                  for (const tab of dirtyOtherTabs) {
                    await handleTabSave(tab.id);
                  }
                  setTabs(prev => prev.filter(t => t.id === tabId));
                  setActiveTabId(tabId);
                  message.success('Other tabs saved and closed');
                } catch (error) {
                  message.error('Failed to save some tabs. Operation cancelled.');
                }
              },
              onCancel: () => {
                setTabs(prev => prev.filter(t => t.id === tabId));
                setActiveTabId(tabId);
                message.info('Other tabs closed without saving');
              },
            });
          } else {
            setTabs(prev => prev.filter(t => t.id === tabId));
            setActiveTabId(tabId);
            message.success('Other tabs closed');
          }
        }
        break;
        
      case 'close-all': {
        const dirtyTabs = tabs.filter(t => t.isDirty);
        
        if (dirtyTabs.length > 0) {
          const fileNames = dirtyTabs.map(t => t.title).join(', ');
          Modal.confirm({
            title: 'Unsaved Changes in Multiple Tabs',
            content: (
              <div>
                <p>The following tabs have unsaved changes:</p>
                <p><strong>{fileNames}</strong></p>
                <p>What would you like to do?</p>
              </div>
            ),
            okText: 'Save All & Close All',
            cancelText: 'Close All Without Saving',
            width: 600,
            onOk: async () => {
              try {
                // Save all dirty tabs first
                for (const tab of dirtyTabs) {
                  await handleTabSave(tab.id);
                }
                // Keep only one tab
                const firstTab = tabs[0];
                if (firstTab) {
                  setTabs([{ ...firstTab, isDirty: false }]);
                  setActiveTabId(firstTab.id);
                  message.success('All tabs saved, all but current closed');
                }
              } catch (error) {
                message.error('Failed to save some tabs. Operation cancelled.');
              }
            },
            onCancel: () => {
              // Keep only one tab
              const firstTab = tabs[0];
              if (firstTab) {
                setTabs([firstTab]);
                setActiveTabId(firstTab.id);
                message.info('All tabs closed without saving except current');
              }
            },
          });
        } else {
          // Keep only one tab
          const firstTab = tabs[0];
          if (firstTab) {
            setTabs([firstTab]);
            setActiveTabId(firstTab.id);
            message.success('All tabs closed except current');
          }
        }
        break;
      }
        
      default:
        message.info(`Tab action: ${action}`);
    }
  };

  const handleLoadHistory = async () => {
    try {
      setLoading(true);
      const response = await ApiService.getConversations();
      
      if (response.success && response.data) {
        const conversations = response.data;
        
        if (conversations.length === 0) {
          message.info('No saved conversations found');
          return;
        }

        // Create tabs for loaded conversations
        const newTabs: Tab[] = conversations.map((conv, index) => ({
          id: `loaded-tab-${conv.id}`,
          conversationId: conv.id,
          title: conv.title || `Chat ${index + 1}`,
          isActive: index === 0,
          isDirty: false,
          type: 'chat',
        }));

        // Update conversations state
        const conversationsMap = conversations.reduce((acc, conv) => {
          acc[conv.id] = conv;
          return acc;
        }, {} as { [key: string]: Conversation });

        setTabs(newTabs);
        setConversations(conversationsMap);
        setActiveTabId(newTabs[0].id);
        
        message.success(`Loaded ${conversations.length} conversation(s)`);
      } else {
        message.error(response.error || 'Failed to load conversations');
      }
    } catch (error) {
      message.error('Error loading conversations');
      console.error('Load history error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get current conversation
  const activeTab = tabs.find(tab => tab.id === activeTabId);
  const currentConversation = activeTab ? conversations[activeTab.conversationId] : null;
  const currentMessages = currentConversation?.messages || [];

  return (
    <Layout className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <Header
        onSetContext={() => setContextModalOpen(true)}
        onNewConversation={handleNewTab}
        onEditFile={() => setFileSelectionModalOpen(true)}
        onNewShell={handleNewShell}
        onSaveHistory={() => handleTabSave(activeTabId)}
        onLoadHistory={handleLoadHistory}
        onOpenSettings={() => setSettingsModalOpen(true)}
        onToggleTheme={toggleTheme}
        onOpenThemePicker={() => setThemePickerModalOpen(true)}
        onSystemMessage={() => setSystemMessageModalOpen(true)}
        onAbout={() => setAboutModalOpen(true)}
        onCodeFragments={() => setCodeFragmentsModalOpen(true)}
        currentSystem={agentPrompts.find(prompt => prompt.title === settings.systemPrompt)?.name || 'default'}
        onSystemChange={handleSystemChange}
        onRunSystemPrompt={handleRunSystemPrompt}
        agentPrompts={agentPrompts}
      />

      {/* Tab Manager */}
      <TabManager
        tabs={tabs}
        activeTabId={activeTabId}
        onTabChange={handleTabChange}
        onTabClose={handleTabClose}
        onTabSave={handleTabSave}
        onNewTab={handleNewTab}
        onTabsAction={handleTabsAction}
      />

      {/* Main Content */}
      <Content className="flex-1 flex flex-col overflow-hidden" style={{ margin: '0', background: 'transparent' }}>
        {activeTab?.type === 'file' ? (
          // File Editor View
          <FileEditorView
            tab={activeTab}
            onContentChange={handleFileContentChange}
            onSave={handleFileSave}
            theme={getEditorTheme(theme)}
          />
        ) : activeTab?.type === 'shell' ? (
          // Shell View
          <ShellView
            tab={activeTab}
            onSessionChange={handleShellSessionChange}
            theme={getEditorTheme(theme)}
          />
        ) : (
          // Chat View
          <>
            <ChatView
              messages={currentMessages}
              loading={loading}
              onExtractCode={(messageId: string) => {
                const message = currentMessages.find(m => m.id === messageId);
                if (message) extractCodeFromMessage(message);
              }}
              onRenderMermaid={handleRenderMermaid}
              onShowCode={handleShowCode}
            />
            
            <div style={{ 
              background: 'white', 
              borderTop: '1px solid #f0f0f0',
              boxShadow: '0 -2px 8px rgba(0, 0, 0, 0.06)',
              padding: '16px 24px'
            }}>
              <InputPanel
                onSendMessage={handleSendMessage}
                onClear={handleClearInput}
                loading={loading}
                subagentCommands={subagentCommands}
              />
            </div>
          </>
        )}
      </Content>

      {/* Status Bar */}
      <StatusBar
        status={loading ? 'loading' : 'ready'}
        provider={settings.provider}
        model={settings.model}
        directory={selectedFiles.length > 0 ? 'Selected Files' : 'none'}
        fileCount={selectedFiles.length}
        tokenCount={currentMessages.reduce((sum, msg) => sum + (msg.metadata?.tokens || 0), 0)}
        onOpenDirectory={() => setContextModalOpen(true)}
      />

      {/* Modals */}
      <ContextModal
        open={contextModalOpen}
        onCancel={() => setContextModalOpen(false)}
        onApply={(files) => {
          setSelectedFiles(files);
          setContextModalOpen(false);
          message.success(`${files.length} files selected for context`);
        }}
        initialFiles={selectedFiles}
      />

      <SettingsModal
        open={settingsModalOpen}
        onCancel={() => setSettingsModalOpen(false)}
        onSave={(newSettings) => {
          setSettings(newSettings);
          message.success('Settings saved');
        }}
      />

      <AboutModal
        open={aboutModalOpen}
        onCancel={() => setAboutModalOpen(false)}
      />

      <SystemMessageModal
        open={systemMessageModalOpen}
        onCancel={() => setSystemMessageModalOpen(false)}
        onSave={(systemMessage) => {
          setSettings(prev => ({ ...prev, systemPrompt: systemMessage }));
          message.success('Agent prompt updated');
        }}
        currentSystemMessage={settings.systemPrompt}
        currentAgent={agentPrompts.find(prompt => prompt.title === settings.systemPrompt)?.name || ''}
      />

      <CodeFragmentsModal
        open={codeFragmentsModalOpen}
        onCancel={() => setCodeFragmentsModalOpen(false)}
        codeBlocks={extractedCodeBlocks}
        onDeleteBlock={(blockId) => {
          setExtractedCodeBlocks(prev => prev.filter(block => block.id !== blockId));
        }}
      />

      <ThemePickerModal
        open={themePickerModalOpen}
        onCancel={() => setThemePickerModalOpen(false)}
      />

      {/* Mermaid Diagram Display Modal */}
      <Modal
        title="Mermaid Diagram"
        open={mermaidModalOpen}
        onCancel={() => setMermaidModalOpen(false)}
        width={800}
        centered
        footer={[
          <Button key="download" type="primary" onClick={handleDownloadMermaid}>
            Download PNG
          </Button>,
          <Button key="close" onClick={() => setMermaidModalOpen(false)}>
            Close
          </Button>
        ]}
      >
        <div style={{ textAlign: 'center', padding: '20px' }}>
          {mermaidImageData && (
            <img 
              src={mermaidImageData} 
              alt="Mermaid Diagram" 
              style={{ 
                maxWidth: '100%', 
                maxHeight: '70vh', 
                border: '1px solid #f0f0f0',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
              }} 
            />
          )}
        </div>
      </Modal>

      {/* Code Fragment Display Modal */}
      <Modal
        title={codeModalData.title || `Code Fragment${codeModalData.language ? ` (${codeModalData.language})` : ''}`}
        open={codeModalOpen}
        onCancel={() => setCodeModalOpen(false)}
        width={900}
        centered
        footer={[
          <Button key="copy" type="primary" icon={<CopyOutlined />} onClick={handleCopyCode}>
            Copy Code
          </Button>,
          <Button key="close" onClick={() => setCodeModalOpen(false)}>
            Close
          </Button>
        ]}
      >
        <div style={{ maxHeight: '70vh', overflow: 'auto' }}>
          <pre
            style={{
              background: '#f8f9fa',
              border: '1px solid #e9ecef',
              borderRadius: '8px',
              padding: '16px',
              fontSize: '14px',
              lineHeight: '1.5',
              margin: 0,
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              color: '#212529',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}
          >
            <code>{codeModalData.code}</code>
          </pre>
        </div>
      </Modal>

      {/* File Selection Modal */}
      <FileSelectionModal
        open={fileSelectionModalOpen}
        onCancel={() => setFileSelectionModalOpen(false)}
        onSelectFile={handleFileSelect}
        onCreateNewFile={() => setNewFileModalOpen(true)}
      />

      {/* New File Creation Modal */}
      <NewFileModal
        open={newFileModalOpen}
        onCancel={() => setNewFileModalOpen(false)}
        onCreateFile={handleCreateNewFile}
      />
    </Layout>
  );
}

export default App;
