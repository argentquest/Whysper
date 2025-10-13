import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Slider, Switch, Tabs, Typography, message, InputNumber, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { Modal } from '../common/Modal';
import type { AppSettings } from '../../types';
import { useTheme } from '../../themes';
import ApiService from '../../services/api';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface SettingsModalProps {
  open: boolean;
  onCancel: () => void;
  onSave: (settings: AppSettings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  open,
  onCancel,
  onSave,
}) => {
  const [form] = Form.useForm();
  const [saving, setSaving] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const { theme, setTheme } = useTheme();
  const providersListValue = Form.useWatch('providersList', form);
  const modelsListValue = Form.useWatch('modelsList', form);

  useEffect(() => {
    if (providersListValue !== undefined) {
      const providers = providersListValue
        ? providersListValue.split(',').map((provider: string) => provider.trim()).filter(Boolean)
        : [];
      setAvailableProviders(providers);
    }
  }, [providersListValue]);

  useEffect(() => {
    if (modelsListValue !== undefined) {
      const models = modelsListValue
        ? modelsListValue.split(',').map((model: string) => model.trim()).filter(Boolean)
        : [];
      setAvailableModels(models);
    }
  }, [modelsListValue]);

  const providerValue = form.getFieldValue('provider') || 'openrouter';
  const providerOptions = availableProviders.length > 0
    ? Array.from(new Set([...availableProviders, providerValue]))
    : ['openrouter', 'custom'];
  const defaultModelValue = form.getFieldValue('defaultModel') || '';
  const modelOptions = availableModels.length > 0
    ? Array.from(new Set([...availableModels, defaultModelValue].filter(Boolean)))
    : (defaultModelValue ? [defaultModelValue] : []);

  const loadSettings = React.useCallback(async () => {
    try {
      const response = await ApiService.getSettings();
      if (response.success && response.data) {
        const settings = response.data;

        // Get sensitive values for form
        const apiKeyValue = settings.values?.API_KEY || '';
        const tokenPasswordValue = settings.values?.TOKEN_PASSWORD || '';

        // Map backend settings to form structure
        const formValues = {
          // API Configuration
          apiKey: apiKeyValue || '',
          provider: settings.values?.PROVIDER || 'openrouter',
          providersList: settings.values?.PROVIDERS || '',
          apiUrl: settings.values?.API_URL || '',
          tokenUrl: settings.values?.TOKEN_URL || '',
          tokenUseId: settings.values?.TOKEN_USE_ID || '',
          tokenPassword: tokenPasswordValue || '',
          validateSsl: settings.values?.VALIDATE_SSL === 'true',

          // Model Configuration
          defaultModel: settings.values?.DEFAULT_MODEL || '',
          maxTokens: parseInt(settings.values?.MAX_TOKENS || '4000'),
          temperature: parseFloat(settings.values?.TEMPERATURE || '0.7'),
          topP: parseFloat(settings.values?.TOP_P || '1.0'),
          frequencyPenalty: parseFloat(settings.values?.FREQUENCY_PENALTY || '0.0'),
          modelsList: settings.values?.MODELS || '',

          // UI Configuration
          theme: settings.values?.UI_THEME || theme,
          uiTheme: settings.values?.UI_THEME || 'light',
          language: settings.values?.LANGUAGE || 'en',

          // File System Configuration
          codePath: settings.values?.CODE_PATH || '',
          ignoreFolders: settings.values?.IGNORE_FOLDERS || '',
          supportedExtensions: settings.values?.SUPPORTED_EXTENSIONS || '',
          maxFileSize: parseInt(settings.values?.MAX_FILE_SIZE || '10485760'),

          // System Prompt
          currentSystemPrompt: settings.values?.CURRENT_SYSTEM_PROMPT || '',
          systemPrompt: settings.values?.SYSTEM_PROMPT || '',

          // Additional UI Settings
          baseUrl: settings.values?.BASE_URL || '',
          autoSaveConversations: settings.values?.AUTO_SAVE_CONVERSATIONS === 'true',
          showLineNumbers: settings.values?.SHOW_LINE_NUMBERS === 'true',
          enableStreaming: settings.values?.ENABLE_STREAMING === 'true',
          retryAttempts: parseInt(settings.values?.RETRY_ATTEMPTS || '3'),
          debugLogging: settings.values?.DEBUG_LOGGING === 'true',
          showTokenUsage: settings.values?.SHOW_TOKEN_USAGE === 'true',

          // Logging Configuration
          logLevel: settings.values?.LOG_LEVEL || 'INFO',
          logDir: settings.values?.LOG_DIR || 'logs',

          // Advanced Configuration
          cacheSize: parseInt(settings.values?.CACHE_SIZE || '100'),
          requestTimeout: parseInt(settings.values?.REQUEST_TIMEOUT || '60'),
          aiConnectTimeout: parseInt(settings.values?.AI_CONNECT_TIMEOUT || '30'),
          aiReadTimeout: parseInt(settings.values?.AI_READ_TIMEOUT || '120'),
          openrouterApiUrl: settings.values?.OPENROUTER_API_URL || '',
          openrouterHttpReferer: settings.values?.OPENROUTER_HTTP_REFERER || '',
          openrouterTitle: settings.values?.OPENROUTER_TITLE || '',
          openrouterTemperature: parseFloat(settings.values?.OPENROUTER_TEMPERATURE || '0.1'),
          customProviderApiUrl: settings.values?.CUSTOM_PROVIDER_API_URL || '',
          customProviderRequestTimeout: parseInt(settings.values?.CUSTOM_PROVIDER_REQUEST_TIMEOUT || '30'),

          // Server Configuration
          apiPort: parseInt(settings.values?.API_PORT || '8000'),
          apiHost: settings.values?.API_HOST || '0.0.0.0',
          fastapiUrl: settings.values?.FASTAPI_URL || 'http://localhost:8000',

          // CLI Memory
          lastUsedFolder: settings.values?.LAST_USED_FOLDER || '',
          lastUsedQuestion: settings.values?.LAST_USED_QUESTION || '',
          lastExcludePatterns: settings.values?.LAST_EXCLUDE_PATTERNS || '',
          lastOutputFormat: settings.values?.LAST_OUTPUT_FORMAT || 'markdown',
          dirSave: settings.values?.DIR_SAVE || 'results',
        };

        form.setFieldsValue(formValues);

        // Extract models and providers from backend settings
        if (settings.values?.MODELS) {
          const models = settings.values.MODELS.split(',').map((m: string) => m.trim()).filter(Boolean);
          setAvailableModels(models);
        } else {
          setAvailableModels([]);
        }

        if (settings.values?.PROVIDERS) {
          const providers = settings.values.PROVIDERS.split(',').map((p: string) => p.trim()).filter(Boolean);
          setAvailableProviders(providers);
        } else {
          setAvailableProviders([]);
        }
      } else {
        message.error(response.error || 'Failed to load settings');
      }
    } catch (error) {
      message.error('Error loading settings');
      console.error('Error loading settings:', error);
    }
  }, [form, theme]);

  useEffect(() => {
    if (open) {
      loadSettings();
    }
  }, [open, loadSettings]);

  const handleSave = async () => {
    try {
      setSaving(true);
      const values = await form.validateFields();

      const normalizedProviders = (values.providersList || '')
        .split(',')
        .map((provider: string) => provider.trim())
        .filter(Boolean)
        .join(',');

      const normalizedModels = (values.modelsList || '')
        .split(',')
        .map((model: string) => model.trim())
        .filter(Boolean)
        .join(',');

      values.providersList = normalizedProviders;
      values.modelsList = normalizedModels;

      // Map form values back to backend environment format
      const backendSettings = {
        // API Configuration
        API_KEY: values.apiKey || '',
        PROVIDER: values.provider || 'openrouter',
        PROVIDERS: normalizedProviders,
        API_URL: values.apiUrl || '',
        TOKEN_URL: values.tokenUrl || '',
        TOKEN_USE_ID: values.tokenUseId || '',
        TOKEN_PASSWORD: values.tokenPassword || '',
        VALIDATE_SSL: values.validateSsl ? 'true' : 'false',

        // Model Configuration
        DEFAULT_MODEL: values.defaultModel || '',
        MODELS: normalizedModels,
        MAX_TOKENS: (values.maxTokens ?? 4000).toString(),
        TEMPERATURE: (values.temperature ?? 0.7).toString(),
        TOP_P: (values.topP ?? 1.0).toString(),
        FREQUENCY_PENALTY: (values.frequencyPenalty ?? 0.0).toString(),

        // UI Configuration
        UI_THEME: values.uiTheme || 'light',
        LANGUAGE: values.language || 'en',

        // File System Configuration
        CODE_PATH: values.codePath || '',
        IGNORE_FOLDERS: values.ignoreFolders || '',
        SUPPORTED_EXTENSIONS: values.supportedExtensions || '',
        MAX_FILE_SIZE: (values.maxFileSize ?? 10485760).toString(),

        // System Prompt
        CURRENT_SYSTEM_PROMPT: values.currentSystemPrompt || '',
        SYSTEM_PROMPT: values.systemPrompt || '',

        // Additional UI Settings
        BASE_URL: values.baseUrl || '',
        AUTO_SAVE_CONVERSATIONS: values.autoSaveConversations ? 'true' : 'false',
        SHOW_LINE_NUMBERS: values.showLineNumbers ? 'true' : 'false',
        ENABLE_STREAMING: values.enableStreaming ? 'true' : 'false',
        RETRY_ATTEMPTS: (values.retryAttempts ?? 3).toString(),
        DEBUG_LOGGING: values.debugLogging ? 'true' : 'false',
        SHOW_TOKEN_USAGE: values.showTokenUsage ? 'true' : 'false',

        // Logging Configuration
        LOG_LEVEL: values.logLevel || 'INFO',
        LOG_DIR: values.logDir || 'logs',

        // Advanced Configuration
        CACHE_SIZE: (values.cacheSize ?? 100).toString(),
        REQUEST_TIMEOUT: (values.requestTimeout ?? 60).toString(),
        AI_CONNECT_TIMEOUT: (values.aiConnectTimeout ?? 30).toString(),
        AI_READ_TIMEOUT: (values.aiReadTimeout ?? 120).toString(),
        OPENROUTER_API_URL: values.openrouterApiUrl || '',
        OPENROUTER_HTTP_REFERER: values.openrouterHttpReferer || '',
        OPENROUTER_TITLE: values.openrouterTitle || '',
        OPENROUTER_TEMPERATURE: (values.openrouterTemperature ?? 0.1).toString(),
        CUSTOM_PROVIDER_API_URL: values.customProviderApiUrl || '',
        CUSTOM_PROVIDER_REQUEST_TIMEOUT: (values.customProviderRequestTimeout ?? 30).toString(),

        // Server Configuration
        API_PORT: (values.apiPort ?? 8000).toString(),
        API_HOST: values.apiHost || '0.0.0.0',
        FASTAPI_URL: values.fastapiUrl || 'http://localhost:8000',

        // CLI Memory
        LAST_USED_FOLDER: values.lastUsedFolder || '',
        LAST_USED_QUESTION: values.lastUsedQuestion || '',
        LAST_EXCLUDE_PATTERNS: values.lastExcludePatterns || '',
        LAST_OUTPUT_FORMAT: values.lastOutputFormat || 'markdown',
        DIR_SAVE: values.dirSave || 'results',
      };

      const response = await ApiService.updateEnvSettings(backendSettings);

      if (response.success) {
        onSave(values);
        message.success('Settings saved successfully');
        onCancel();
      } else {
        message.error(response.error || 'Failed to save settings');
      }
    } catch (error: unknown) {
      console.error('Error saving settings:', error);
      if (error && typeof error === 'object' && 'errorFields' in error) {
        message.error('Please correct the validation errors');
      } else {
        message.error('Error saving settings');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
    form.setFieldValue('theme', newTheme);
    form.setFieldValue('uiTheme', newTheme);
  };

  const handleRestartServer = async () => {
    try {
      setRestarting(true);
      const response = await ApiService.restartServer();

      if (response.success) {
        message.success('Server is restarting... The page will reload in 3 seconds.');

        // Wait for server to restart, then reload the page
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      } else {
        message.error(response.error || 'Failed to restart server');
        setRestarting(false);
      }
    } catch (error) {
      console.error('Error restarting server:', error);
      message.error('Error restarting server');
      setRestarting(false);
    }
  };

  return (
    <Modal
      title="Application Settings"
      open={open}
      onCancel={onCancel}
      onOk={handleSave}
      width={900}
      confirmLoading={saving}
      okText="Save Settings"
      cancelText="Cancel"
      footer={[
        <Button
          key="restart"
          icon={<ReloadOutlined />}
          onClick={handleRestartServer}
          loading={restarting}
          danger
        >
          Restart Server
        </Button>,
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button
          key="save"
          type="primary"
          onClick={handleSave}
          loading={saving}
        >
          Save Settings
        </Button>,
      ]}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          theme: theme,
          provider: 'openrouter',
          providersList: '',
          modelsList: '',
          maxTokens: 4000,
          temperature: 0.7,
          topP: 1.0,
          frequencyPenalty: 0.0,
          validateSsl: true,
          autoSaveConversations: true,
          showLineNumbers: true,
          enableStreaming: true,
          retryAttempts: 3,
          debugLogging: false,
          showTokenUsage: true,
          logLevel: 'INFO',
          cacheSize: 100,
          requestTimeout: 60,
          aiConnectTimeout: 30,
          aiReadTimeout: 120,
          openrouterTemperature: 0.1,
          customProviderRequestTimeout: 30,
          apiPort: 8000,
          apiHost: '0.0.0.0',
          fastapiUrl: 'http://localhost:8000',
          lastOutputFormat: 'markdown',
        }}
      >
        <Tabs
          defaultActiveKey="api"
          items={[
            {
              key: 'api',
              label: '🔑 API',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Provider Configuration</Title>

                  <Form.Item
                    label="API Provider"
                    name="provider"
                    rules={[{ required: true, message: 'Please select a provider' }]}
                    tooltip="AI service provider (openrouter, custom, etc.)"
                  >
                    <Select>
                      {providerOptions.map(provider => (
                        <Option key={provider} value={provider}>{provider}</Option>
                      ))}
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="Available Providers"
                    name="providersList"
                    tooltip="Comma-separated list of available providers"
                  >
                    <TextArea rows={2} placeholder="openrouter,custom" />
                  </Form.Item>

                  <Form.Item
                    label="API Key"
                    name="apiKey"
                    rules={[{ required: true, message: 'Please enter your API key' }]}
                    tooltip="Your API key for the selected provider"
                  >
                    <Input.Password placeholder="sk-or-v1-..." />
                  </Form.Item>

                  <Form.Item
                    label="API URL"
                    name="apiUrl"
                    tooltip="API endpoint URL for chat completions"
                  >
                    <Input placeholder="https://api.openrouter.ai/v1/chat/completions" />
                  </Form.Item>

                  <Form.Item
                    label="Token URL"
                    name="tokenUrl"
                    tooltip="URL for token authentication (if required)"
                  >
                    <Input placeholder="https://api.openrouter.ai/v1/token" />
                  </Form.Item>

                  <div className="grid grid-cols-2 gap-4">
                    <Form.Item
                      label="Token User ID"
                      name="tokenUseId"
                      tooltip="User ID for token authentication"
                    >
                      <Input placeholder="Optional" />
                    </Form.Item>

                    <Form.Item
                      label="Token Password"
                      name="tokenPassword"
                      tooltip="Password for token authentication"
                    >
                      <Input.Password placeholder="Optional" />
                    </Form.Item>
                  </div>

                <Title level={5}>OpenRouter Settings</Title>

                <Form.Item
                  label="OpenRouter API URL"
                  name="openrouterApiUrl"
                  tooltip="API endpoint for OpenRouter requests"
                >
                  <Input placeholder="https://openrouter.ai/api/v1/chat/completions" />
                </Form.Item>

                <Form.Item
                  label="HTTP Referer"
                  name="openrouterHttpReferer"
                  tooltip="Referer header required by OpenRouter"
                >
                  <Input placeholder="https://github.com/yourusername/code-chat-ai" />
                </Form.Item>

                <Form.Item
                  label="Request Title"
                  name="openrouterTitle"
                  tooltip="X-Title header describing your integration"
                >
                  <Input placeholder="Code Chat with AI" />
                </Form.Item>

                <Form.Item
                  label={`OpenRouter Temperature: ${form.getFieldValue('openrouterTemperature')?.toFixed(1) ?? '0.1'}`}
                  name="openrouterTemperature"
                  tooltip="Default temperature for OpenRouter requests"
                >
                  <Slider
                    min={0}
                    max={2}
                    step={0.1}
                    marks={{
                      0: '0',
                      0.5: '0.5',
                      1: '1',
                      2: '2',
                    }}
                  />
                </Form.Item>

                <Title level={5}>Custom Provider Settings</Title>

                <Form.Item
                  label="Custom Provider API URL"
                  name="customProviderApiUrl"
                  tooltip="API endpoint for the custom provider"
                >
                  <Input placeholder="https://your-api.com/v1/chat" />
                </Form.Item>

                <Form.Item
                  label="Custom Provider Timeout (seconds)"
                  name="customProviderRequestTimeout"
                  tooltip="Request timeout for custom provider calls"
                >
                  <InputNumber min={1} max={600} className="w-full" />
                </Form.Item>

                <Form.Item
                  label="Validate SSL"
                  name="validateSsl"
                  tooltip="Enable SSL certificate validation"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
                </div>
              ),
            },
            {
              key: 'model',
              label: '🤖 Model',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Model Selection</Title>

                  <Form.Item
                    label="Available Models"
                    name="modelsList"
                    tooltip="Comma-separated list of available models"
                  >
                    <TextArea rows={3} placeholder="model-a,model-b" />
                  </Form.Item>

                  <Form.Item
                    label="Default Model"
                    name="defaultModel"
                    rules={[{ required: true, message: 'Please select a model' }]}
                    tooltip="AI model to use for responses"
                  >
                    <Select showSearch placeholder="Select a model">
                      {modelOptions.length === 0 && (
                        <Option value="" disabled>No models configured</Option>
                      )}
                      {modelOptions.map(model => (
                        <Option key={model} value={model}>{model}</Option>
                      ))}
                    </Select>
                  </Form.Item>

                  <Title level={5}>Model Parameters</Title>

                  <Form.Item
                    label={`Max Tokens: ${form.getFieldValue('maxTokens') || 4000}`}
                    name="maxTokens"
                    tooltip="Maximum number of tokens in the response (1-16000)"
                  >
                    <Slider
                      min={100}
                      max={16000}
                      step={100}
                      marks={{
                        100: '100',
                        4000: '4K',
                        8000: '8K',
                        16000: '16K',
                      }}
                    />
                  </Form.Item>

                  <Form.Item
                    label={`Temperature: ${form.getFieldValue('temperature')?.toFixed(1) || '0.7'}`}
                    name="temperature"
                    tooltip="Controls creativity/randomness (0.0 = deterministic, 2.0 = very creative)"
                  >
                    <Slider
                      min={0}
                      max={2}
                      step={0.1}
                      marks={{
                        0: '0',
                        0.7: '0.7',
                        1: '1',
                        2: '2',
                      }}
                    />
                  </Form.Item>

                  <Form.Item
                    label={`Top P: ${form.getFieldValue('topP')?.toFixed(1) || '1.0'}`}
                    name="topP"
                    tooltip="Nucleus sampling parameter (0.0-1.0)"
                  >
                    <Slider
                      min={0}
                      max={1}
                      step={0.1}
                      marks={{
                        0: '0',
                        0.5: '0.5',
                        1: '1',
                      }}
                    />
                  </Form.Item>

                  <Form.Item
                    label={`Frequency Penalty: ${form.getFieldValue('frequencyPenalty')?.toFixed(1) || '0.0'}`}
                    name="frequencyPenalty"
                    tooltip="Penalize repeated tokens (-2.0 to 2.0)"
                  >
                    <Slider
                      min={-2}
                      max={2}
                      step={0.1}
                      marks={{
                        '-2': '-2',
                        0: '0',
                        2: '2',
                      }}
                    />
                  </Form.Item>
                </div>
              ),
            },
            {
              key: 'interface',
              label: '🎨 Interface',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Theme & Display</Title>

                  <Form.Item
                    label="Theme"
                    name="theme"
                    tooltip="Choose between light and dark theme"
                  >
                    <Select onChange={handleThemeChange}>
                      <Option value="light">Light</Option>
                      <Option value="dark">Dark</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="Language"
                    name="language"
                    tooltip="Interface language"
                  >
                    <Select>
                      <Option value="en">English</Option>
                      <Option value="es">Spanish</Option>
                      <Option value="fr">French</Option>
                      <Option value="de">German</Option>
                    </Select>
                  </Form.Item>

                  <Title level={5}>Display Options</Title>

                  <Form.Item
                    label="Auto-save conversations"
                    name="autoSaveConversations"
                    tooltip="Automatically save conversations"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>

                  <Form.Item
                    label="Show line numbers in code"
                    name="showLineNumbers"
                    tooltip="Display line numbers in code blocks"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>

                  <Form.Item
                    label="Enable streaming responses"
                    name="enableStreaming"
                    tooltip="Stream responses as they're generated"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>

                  <Form.Item
                    label="Show token usage"
                    name="showTokenUsage"
                    tooltip="Display token consumption information"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </div>
              ),
            },
            {
              key: 'files',
              label: '📁 Files',
              children: (
                <div className="space-y-4">
                  <Title level={5}>File System Configuration</Title>

                  <Form.Item
                    label="Code Path"
                    name="codePath"
                    tooltip="Root directory for your codebase"
                  >
                    <Input placeholder="C:\Code2025\Whysper" />
                  </Form.Item>

                  <Form.Item
                    label="Ignore Folders"
                    name="ignoreFolders"
                    tooltip="Comma-separated list of folders to ignore"
                  >
                    <Input placeholder="node_modules,__pycache__,.git" />
                  </Form.Item>

                  <Form.Item
                    label="Supported Extensions"
                    name="supportedExtensions"
                    tooltip="Comma-separated list of file extensions to process"
                  >
                    <TextArea
                      rows={3}
                      placeholder=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.h,.cs"
                    />
                  </Form.Item>

                  <Form.Item
                    label="Max File Size (bytes)"
                    name="maxFileSize"
                    tooltip="Maximum file size to process (default: 10MB)"
                  >
                    <InputNumber
                      min={1024}
                      max={104857600}
                      step={1048576}
                      className="w-full"
                      formatter={(value) => {
                        const mb = (value || 0) / 1048576;
                        return `${mb.toFixed(1)} MB`;
                      }}
                    />
                  </Form.Item>

                  <Form.Item
                    label="Output Directory"
                    name="dirSave"
                    tooltip="Directory for saving results"
                  >
                    <Input placeholder="results" />
                  </Form.Item>
                </div>
              ),
            },
            {
              key: 'prompts',
              label: '💬 Prompts',
              children: (
                <div className="space-y-4">
                  <Title level={5}>System Message Configuration</Title>

                  <Form.Item
                    label="Current System Prompt File"
                    name="currentSystemPrompt"
                    tooltip="System message file to use"
                  >
                    <Input placeholder="systemmessage_documentation.txt" />
                  </Form.Item>

                  <Form.Item
                    label="Custom System Prompt"
                    name="systemPrompt"
                    tooltip="Override system prompt with custom text"
                  >
                    <TextArea
                      rows={6}
                      placeholder="Enter custom system prompt here..."
                    />
                  </Form.Item>

                  <Text type="secondary" className="text-xs">
                    💡 Leave custom prompt empty to use the file specified above
                  </Text>
                </div>
              ),
            },
            {
              key: 'server',
              label: '🌐 Server',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Backend Server</Title>

                  <div className="grid grid-cols-2 gap-4">
                    <Form.Item
                      label="API Host"
                      name="apiHost"
                      tooltip="Host address for the API server"
                    >
                      <Input placeholder="0.0.0.0" />
                    </Form.Item>

                    <Form.Item
                      label="API Port"
                      name="apiPort"
                      tooltip="Port for the FastAPI server"
                    >
                      <InputNumber min={1} max={65535} className="w-full" />
                    </Form.Item>
                  </div>

                  <Title level={5}>Frontend Configuration</Title>

                  <Form.Item
                    label="FastAPI URL"
                    name="fastapiUrl"
                    tooltip="Backend URL for frontend to connect to"
                  >
                    <Input placeholder="http://localhost:8000" />
                  </Form.Item>

                  <Form.Item
                    label="Base URL"
                    name="baseUrl"
                    tooltip="Custom API base URL (optional)"
                  >
                    <Input placeholder="Optional custom base URL" />
                  </Form.Item>
                </div>
              ),
            },
            {
              key: 'advanced',
              label: '🔧 Advanced',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Performance</Title>

                  <Form.Item
                    label={`Request Timeout: ${form.getFieldValue('requestTimeout') || 60}s`}
                    name="requestTimeout"
                    tooltip="How long to wait for AI responses (1-300 seconds)"
                  >
                    <Slider
                      min={1}
                      max={300}
                      step={5}
                      marks={{
                        1: '1s',
                        60: '1m',
                        180: '3m',
                        300: '5m',
                      }}
                    />
                  </Form.Item>

                  <Form.Item
                    label="Connect Timeout (seconds)"
                    name="aiConnectTimeout"
                    tooltip="Timeout for establishing connections to AI providers"
                  >
                    <InputNumber min={1} max={300} className="w-full" />
                  </Form.Item>

                  <Form.Item
                    label="Read Timeout (seconds)"
                    name="aiReadTimeout"
                    tooltip="Timeout for reading responses from AI providers"
                  >
                    <InputNumber min={1} max={600} className="w-full" />
                  </Form.Item>

                  <Form.Item
                    label="Retry Attempts"
                    name="retryAttempts"
                    tooltip="Number of retry attempts for failed requests"
                  >
                    <Select>
                      <Option value={1}>1</Option>
                      <Option value={2}>2</Option>
                      <Option value={3}>3</Option>
                      <Option value={5}>5</Option>
                      <Option value={10}>10</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="Cache Size"
                    name="cacheSize"
                    tooltip="Number of files to cache in memory (1-1000)"
                  >
                    <InputNumber min={1} max={1000} className="w-full" />
                  </Form.Item>

                  <Title level={5}>Logging</Title>

                  <Form.Item
                    label="Log Level"
                    name="logLevel"
                    tooltip="Logging verbosity level"
                  >
                    <Select>
                      <Option value="DEBUG">Debug</Option>
                      <Option value="INFO">Info</Option>
                      <Option value="WARNING">Warning</Option>
                      <Option value="ERROR">Error</Option>
                      <Option value="CRITICAL">Critical</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    label="Log Directory"
                    name="logDir"
                    tooltip="Directory for log files"
                  >
                    <Input placeholder="logs" />
                  </Form.Item>

                  <Form.Item
                    label="Enable debug logging"
                    name="debugLogging"
                    tooltip="Log detailed information for troubleshooting"
                    valuePropName="checked"
                  >
                    <Switch />
                  </Form.Item>
                </div>
              ),
            },
            {
              key: 'cli',
              label: '💾 CLI Memory',
              children: (
                <div className="space-y-4">
                  <Title level={5}>Interactive CLI Settings</Title>
                  <Text type="secondary" className="block mb-4">
                    These settings store the last used values for CLI interactive mode
                  </Text>

                  <Form.Item
                    label="Last Used Folder"
                    name="lastUsedFolder"
                    tooltip="Last folder processed in CLI mode"
                  >
                    <Input placeholder="Automatically updated" />
                  </Form.Item>

                  <Form.Item
                    label="Last Used Question"
                    name="lastUsedQuestion"
                    tooltip="Last question asked in CLI mode"
                  >
                    <TextArea rows={2} placeholder="Automatically updated" />
                  </Form.Item>

                  <Form.Item
                    label="Last Exclude Patterns"
                    name="lastExcludePatterns"
                    tooltip="Last exclude patterns used"
                  >
                    <Input placeholder="Automatically updated" />
                  </Form.Item>

                  <Form.Item
                    label="Last Output Format"
                    name="lastOutputFormat"
                    tooltip="Last output format used"
                  >
                    <Select>
                      <Option value="markdown">Markdown</Option>
                      <Option value="json">JSON</Option>
                      <Option value="text">Text</Option>
                      <Option value="html">HTML</Option>
                    </Select>
                  </Form.Item>
                </div>
              ),
            },
          ]}
        />
      </Form>
    </Modal>
  );
};

export default SettingsModal;
