import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Slider, Switch, Tabs, Typography, message } from 'antd';
import { Modal } from '../common/Modal';
import type { AppSettings } from '../../types';
import { useTheme } from '../../themes';
import ApiService from '../../services/api';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Title } = Typography;

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
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [availableProviders, setAvailableProviders] = useState<Array<{label: string, value: string}>>([]);
  const { theme, setTheme } = useTheme();

  const loadSettings = React.useCallback(async () => {
    try {
      const response = await ApiService.getSettings();
      if (response.success && response.data) {
        const settings = response.data;
        
        // Map backend settings to form structure
        const formValues = {
          theme: theme,
          language: settings.values?.LANGUAGE || 'en',
          autoSaveConversations: settings.values?.AUTO_SAVE_CONVERSATIONS === 'true',
          showLineNumbers: settings.values?.SHOW_LINE_NUMBERS === 'true',
          provider: settings.values?.PROVIDER || 'openrouter',
          model: settings.values?.DEFAULT_MODEL || '',
          apiKey: settings.masked?.API_KEY || '',
          baseUrl: settings.values?.BASE_URL || '',
          maxTokens: parseInt(settings.values?.MAX_TOKENS || '4000'),
          temperature: parseFloat(settings.values?.TEMPERATURE || '0.7'),
          systemPrompt: settings.values?.SYSTEM_PROMPT || '',
          enableStreaming: settings.values?.ENABLE_STREAMING === 'true',
          requestTimeout: parseInt(settings.values?.REQUEST_TIMEOUT || '30'),
          retryAttempts: parseInt(settings.values?.RETRY_ATTEMPTS || '3'),
          debugLogging: settings.values?.DEBUG_LOGGING === 'true',
          showTokenUsage: settings.values?.SHOW_TOKEN_USAGE === 'true',
        };
        
        form.setFieldsValue(formValues);
        
        // Extract models from backend settings
        if (settings.values && settings.values.MODELS) {
          const models = settings.values.MODELS.split(',').map((m: string) => m.trim());
          setAvailableModels(models);
        }
        
        // Set available providers based on backend config
        const providers = [
          { label: 'OpenRouter', value: 'openrouter' },
          { label: 'OpenAI', value: 'openai' },
          { label: 'Anthropic', value: 'anthropic' },
          { label: 'Google', value: 'google' },
          { label: 'Local', value: 'local' },
        ];
        setAvailableProviders(providers);
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
      
      console.log('💾 Raw form values:', values);
      
      // Map form values back to backend environment format with proper null checks
      const backendSettings = {
        LANGUAGE: values.language || 'en',
        AUTO_SAVE_CONVERSATIONS: values.autoSaveConversations ? 'true' : 'false',
        SHOW_LINE_NUMBERS: values.showLineNumbers ? 'true' : 'false',
        PROVIDER: values.provider || 'openrouter',
        DEFAULT_MODEL: values.model || '',
        API_KEY: values.apiKey || '',
        BASE_URL: values.baseUrl || '',
        MAX_TOKENS: (values.maxTokens ?? 4000).toString(),
        TEMPERATURE: (values.temperature ?? 0.7).toString(),
        SYSTEM_PROMPT: values.systemPrompt || '',
        ENABLE_STREAMING: values.enableStreaming ? 'true' : 'false',
        REQUEST_TIMEOUT: (values.requestTimeout ?? 30).toString(),
        RETRY_ATTEMPTS: (values.retryAttempts ?? 3).toString(),
        DEBUG_LOGGING: values.debugLogging ? 'true' : 'false',
        SHOW_TOKEN_USAGE: values.showTokenUsage ? 'true' : 'false',
      };
      
      console.log('📤 Backend settings to send:', backendSettings);
      
      const response = await ApiService.updateEnvSettings(backendSettings);
      console.log('📥 Backend response:', response);
      
      if (response.success) {
        onSave(values);
        message.success('Settings saved successfully');
        onCancel();
      } else {
        message.error(response.error || 'Failed to save settings');
      }
    } catch (error: unknown) {
      console.error('💥 Error saving settings:', error);
      if (error && typeof error === 'object' && 'errorFields' in error) {
        message.error('Please correct the validation errors');
      } else {
        message.error('Error saving settings');
        console.error('Error saving settings:', error);
      }
    } finally {
      setSaving(false);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
    form.setFieldValue('theme', newTheme);
  };


  return (
    <Modal
      title="Settings"
      open={open}
      onCancel={onCancel}
      onOk={handleSave}
      width={720}
      confirmLoading={saving}
      okText="Save Settings"
      cancelText="Cancel"
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          theme: theme,
          provider: 'openrouter',
          model: 'x-ai/grok-code-fast-1',
          maxTokens: 4000,
          temperature: 0.7,
          systemPrompt: 'You are a helpful AI assistant specialized in code analysis and development.',
        }}
      >
        <Tabs defaultActiveKey="general">
          <TabPane tab="General" key="general">
            <div className="space-y-4">
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
            </div>
          </TabPane>

          <TabPane tab="AI Provider" key="provider">
            <div className="space-y-4">
              <Form.Item
                label="Provider"
                name="provider"
                rules={[{ required: true, message: 'Please select a provider' }]}
                tooltip="AI service provider"
              >
                <Select>
                  {availableProviders.map(provider => (
                    <Option key={provider.value} value={provider.value}>
                      {provider.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                label="Model"
                name="model"
                rules={[{ required: true, message: 'Please select a model' }]}
                tooltip="AI model to use for responses"
              >
                <Select>
                  {availableModels.map(model => (
                    <Option key={model} value={model}>{model}</Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                label="API Key"
                name="apiKey"
                tooltip="Your API key for the selected provider"
              >
                <Input.Password placeholder="Enter your API key" />
              </Form.Item>

              <Form.Item
                label="Base URL"
                name="baseUrl"
                tooltip="Custom API base URL (optional)"
              >
                <Input placeholder="https://api.example.com" />
              </Form.Item>
            </div>
          </TabPane>

          <TabPane tab="Model Parameters" key="parameters">
            <div className="space-y-6">
              <Form.Item
                label="Max Tokens"
                name="maxTokens"
                tooltip="Maximum number of tokens in the response"
              >
                <Slider
                  min={100}
                  max={8000}
                  step={100}
                  marks={{
                    100: '100',
                    2000: '2K',
                    4000: '4K',
                    8000: '8K',
                  }}
                />
              </Form.Item>

              <Form.Item
                label="Temperature"
                name="temperature"
                tooltip="Controls randomness in responses (0 = deterministic, 1 = creative)"
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
                label="System Prompt"
                name="systemPrompt"
                tooltip="Default system message for AI behavior"
              >
                <TextArea
                  rows={4}
                  placeholder="Enter system prompt..."
                />
              </Form.Item>

              <Form.Item
                label="Enable streaming"
                name="enableStreaming"
                tooltip="Stream responses as they're generated"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </div>
          </TabPane>

          <TabPane tab="Advanced" key="advanced">
            <div className="space-y-4">
              <Title level={5}>Performance</Title>
              
              <Form.Item
                label="Request timeout (seconds)"
                name="requestTimeout"
                tooltip="How long to wait for AI responses"
              >
                <Slider
                  min={5}
                  max={120}
                  step={5}
                  marks={{
                    5: '5s',
                    30: '30s',
                    60: '1m',
                    120: '2m',
                  }}
                />
              </Form.Item>

              <Form.Item
                label="Retry attempts"
                name="retryAttempts"
                tooltip="Number of retry attempts for failed requests"
              >
                <Select>
                  <Option value={1}>1</Option>
                  <Option value={2}>2</Option>
                  <Option value={3}>3</Option>
                  <Option value={5}>5</Option>
                </Select>
              </Form.Item>

              <Title level={5}>Debug</Title>

              <Form.Item
                label="Enable debug logging"
                name="debugLogging"
                tooltip="Log detailed information for troubleshooting"
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
          </TabPane>
        </Tabs>
      </Form>
    </Modal>
  );
};

export default SettingsModal;