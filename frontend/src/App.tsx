/**
 * WhysperCode Web2 - Main Application Component
 * 
 * This is the root component of the WhysperCode Web2 React application.
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
import { Layout, message } from 'antd';

// Layout components
import { Header } from './components/layout/Header';
import { TabManager } from './components/layout/TabManager';
import { ChatView } from './components/chat/ChatView';
import { InputPanel } from './components/chat/InputPanel';
import { StatusBar } from './components/layout/StatusBar';

// Modal components for secondary interfaces
import {
  ContextModal,      // File selection and context management
  SettingsModal,     // Application settings and AI configuration
  AboutModal,        // Application information and version details
  SystemMessageModal,// System prompt customization
  CodeFragmentsModal,// Extracted code blocks management
} from './components/modals';

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
  
  // ==================== Data State Management ====================
  
  // Files selected for AI context inclusion
  const [selectedFiles, setSelectedFiles] = useState<FileItem[]>([]);
  
  // Code blocks extracted from AI responses for download/management
  const [extractedCodeBlocks, setExtractedCodeBlocks] = useState<CodeBlock[]>([]);
  
  // Agent prompts loaded from backend
  const [agentPrompts, setAgentPrompts] = useState<AgentPrompt[]>([]);

  // ==================== Application Initialization ====================
  
  /**
   * Initialize the application with default state
   * 
   * Creates the first tab and conversation, then loads user settings from backend.
   * This ensures the app always has a usable conversation interface ready.
   */
  const initializeApp = useCallback(async () => {
    // Create the initial tab for the first conversation
    const initialTab: Tab = {
      id: 'tab-1',                    // Unique tab identifier
      conversationId: 'conv-1',       // Associated conversation ID
      title: 'Chat 1',               // Display name in tab bar
      isActive: true,                 // This tab is currently active
      isDirty: false,                 // No unsaved changes yet
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
  }, []);

  // Initialize the application when component mounts
  useEffect(() => {
    initializeApp();
  }, [initializeApp]);

  const loadSettings = async () => {
    try {
      const response = await ApiService.getSettings();
      if (response.success && response.data) {
        const backendSettings = response.data;
        
        // Map backend settings to frontend settings structure
        const mappedSettings: AppSettings = {
          theme: theme,
          provider: backendSettings.values?.PROVIDER || 'openrouter',
          model: backendSettings.values?.DEFAULT_MODEL || backendSettings.values?.MODELS?.split(',')[0]?.trim() || '',
          systemPrompt: backendSettings.values?.SYSTEM_PROMPT || 'You are a helpful AI assistant specialized in code analysis and development.',
          contextFiles: [],
          maxTokens: parseInt(backendSettings.values?.MAX_TOKENS) || 4000,
          temperature: parseFloat(backendSettings.values?.TEMPERATURE) || 0.7,
        };
        
        setSettings(mappedSettings);
        
        // Load agent prompts and subagent commands
        if (backendSettings.agentPrompts) {
          setAgentPrompts(backendSettings.agentPrompts);
        }
      }
    } catch (error) {
      console.warn('Could not load settings:', error);
      // Set fallback defaults if backend is not available
      setSettings(prev => ({
        ...prev,
        provider: 'openrouter',
        model: 'x-ai/grok-code-fast-1',
        systemPrompt: 'You are a helpful AI assistant specialized in code analysis and development.',
      }));
    }
  };

  // Chat functions
  const handleSendMessage = async (messageText: string, command?: string) => {
    const activeTab = tabs.find(tab => tab.id === activeTabId);
    if (!activeTab) return;

    const conversation = conversations[activeTab.conversationId];
    if (!conversation) return;

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
      // Send to API
      const response = await ApiService.sendMessage({
        message: messageText,
        conversationId: conversation.id,
        contextFiles: selectedFiles.map(f => f.path),
        settings,
      });

      if (response.success && response.data) {
        const assistantMessage = response.data.message;
        
        // Update conversation with assistant response
        const finalConversation = {
          ...updatedConversation,
          messages: [...updatedConversation.messages, assistantMessage],
          updatedAt: new Date().toISOString(),
        };

        setConversations(prev => ({
          ...prev,
          [conversation.id]: finalConversation,
        }));

        // Extract code blocks if any
        await extractCodeFromMessage(assistantMessage);
      } else {
        message.error(response.error || 'Failed to send message');
      }
    } catch (error) {
      message.error('Error sending message');
      console.error('Send message error:', error);
    } finally {
      setLoading(false);
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
        // response.data should be a URL to the generated PNG
        const link = document.createElement('a');
        link.href = response.data;
        link.download = 'mermaid-diagram.png';
        link.click();
        message.success('Mermaid diagram downloaded');
      } else {
        message.error(response.error || 'Failed to render mermaid diagram');
      }
    } catch (error) {
      message.error('Error rendering mermaid diagram');
      console.error('Mermaid render error:', error);
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

    const conversation = conversations[tab.conversationId];
    if (!conversation) return;

    try {
      const response = await ApiService.saveConversation(conversation);
      if (response.success) {
        setTabs(prev => prev.map(t => 
          t.id === tabId ? { ...t, isDirty: false } : t
        ));
        message.success('Conversation saved');
      } else {
        message.error(response.error || 'Failed to save conversation');
      }
    } catch (error) {
      message.error('Error saving conversation');
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
          setTabs(prev => prev.filter(t => t.id === tabId));
          setActiveTabId(tabId);
          message.success('Other tabs closed');
        }
        break;
        
      case 'close-all': {
        // Keep only one tab
        const firstTab = tabs[0];
        if (firstTab) {
          setTabs([firstTab]);
          setActiveTabId(firstTab.id);
          message.success('All tabs closed except current');
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
    <Layout className="h-screen flex flex-col">
      {/* Header */}
      <Header
        onSetContext={() => setContextModalOpen(true)}
        onExecuteSystemPrompt={() => setSystemMessageModalOpen(true)}
        onNewConversation={handleNewTab}
        onSaveHistory={() => handleTabSave(activeTabId)}
        onLoadHistory={handleLoadHistory}
        onOpenSettings={() => setSettingsModalOpen(true)}
        onToggleTheme={toggleTheme}
        onSystemMessage={() => setSystemMessageModalOpen(true)}
        onAbout={() => setAboutModalOpen(true)}
        onCodeFragments={() => setCodeFragmentsModalOpen(true)}
        currentModel={settings.model}
        onModelChange={(model) => setSettings(prev => ({ ...prev, model }))}
        currentSystem="default"
        onSystemChange={handleSystemChange}
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
      <Content className="flex-1 flex flex-col overflow-hidden">
        <ChatView
          messages={currentMessages}
          loading={loading}
          onExtractCode={(messageId: string) => {
            const message = currentMessages.find(m => m.id === messageId);
            if (message) extractCodeFromMessage(message);
          }}
          onRenderMermaid={handleRenderMermaid}
        />
        
        <InputPanel
          onSendMessage={handleSendMessage}
          onClear={handleClearInput}
          loading={loading}
        />
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
          message.success('System message updated');
        }}
        currentSystemMessage={settings.systemPrompt}
      />

      <CodeFragmentsModal
        open={codeFragmentsModalOpen}
        onCancel={() => setCodeFragmentsModalOpen(false)}
        codeBlocks={extractedCodeBlocks}
        onDeleteBlock={(blockId) => {
          setExtractedCodeBlocks(prev => prev.filter(block => block.id !== blockId));
        }}
      />
    </Layout>
  );
}

export default App;
