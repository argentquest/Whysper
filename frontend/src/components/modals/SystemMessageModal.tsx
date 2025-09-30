import React, { useState, useEffect } from 'react';
import { Form, Input, Select, Button, Space, Typography, message, Tabs } from 'antd';
import { ReloadOutlined, CopyOutlined } from '@ant-design/icons';
import { Modal } from '../common/Modal';
import ApiService from '../../services/api';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface Agent {
  name: string;
  title: string;
  description: string;
  category: string[];
  filename: string;
}

interface SystemMessageModalProps {
  open: boolean;
  onCancel: () => void;
  onSave: (systemMessage: string) => void;
  currentSystemMessage?: string;
  currentAgent?: string;
}

export const SystemMessageModal: React.FC<SystemMessageModalProps> = ({
  open,
  onCancel,
  onSave,
  currentSystemMessage = '',
  currentAgent = '',
}) => {
  const [form] = Form.useForm();
  const [activeTemplate, setActiveTemplate] = useState<string>(currentAgent);
  const [customMessage, setCustomMessage] = useState(currentSystemMessage);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(false);

  // Load agents from backend
  useEffect(() => {
    const loadAgents = async () => {
      try {
        setLoading(true);
        const response = await ApiService.getAgents();
        if (response.success && response.data) {
          setAgents(response.data);
        }
      } catch (error) {
        console.error('Failed to load agents:', error);
        message.error('Failed to load agent prompts');
      } finally {
        setLoading(false);
      }
    };

    if (open) {
      loadAgents();
      setCustomMessage(currentSystemMessage);
      setActiveTemplate(currentAgent);
      form.setFieldValue('systemMessage', currentSystemMessage);
    }
  }, [open, currentSystemMessage, currentAgent, form]);

  const handleTemplateChange = async (agentName: string) => {
    const agent = agents.find(a => a.name === agentName);
    if (agent) {
      setActiveTemplate(agentName);
      setLoading(true);
      try {
        const response = await ApiService.getAgentPrompt(agent.filename);
        if (response.success && response.data) {
          setCustomMessage(response.data.content);
          form.setFieldValue('systemMessage', response.data.content);
        }
      } catch (error) {
        console.error('Failed to load agent content:', error);
        message.error('Failed to load agent content');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSave = () => {
    const messageContent = customMessage.trim();
    if (messageContent) {
      onSave(messageContent);
      onCancel();
    } else {
      message.warning('Please enter a system message');
    }
  };

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      message.success('Copied to clipboard');
    } catch {
      message.error('Failed to copy');
    }
  };

  const handleReset = () => {
    if (agents.length > 0) {
      const defaultAgent = agents[0];
      handleTemplateChange(defaultAgent.name);
    }
  };

  return (
    <Modal
      title="Agent Prompt Configuration"
      open={open}
      onCancel={onCancel}
      onOk={handleSave}
      width={800}
      okText="Save Agent Prompt"
      cancelText="Cancel"
      confirmLoading={loading}
    >
      <Tabs defaultActiveKey="agents">
        <TabPane tab="Agent Prompts" key="agents">
          <div className="space-y-4">
            <div>
              <Text className="block mb-2 font-medium">Choose an Agent:</Text>
              <Select
                value={activeTemplate}
                onChange={handleTemplateChange}
                placeholder="Select an agent prompt"
                className="w-full"
                loading={loading}
              >
                {agents.map(agent => (
                  <Option key={agent.name} value={agent.name}>
                    <div>
                      <div className="font-medium">{agent.title}</div>
                      <div className="text-xs text-gray-500">{agent.description}</div>
                      <div className="text-xs text-blue-500">
                        {agent.category.length > 0 && `Categories: ${agent.category.join(', ')}`}
                      </div>
                    </div>
                  </Option>
                ))}
              </Select>
            </div>

            {activeTemplate && (
              <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <Text strong>Preview:</Text>
                  <Button
                    type="link"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => handleCopy(customMessage)}
                  >
                    Copy
                  </Button>
                </div>
                <div className="text-sm whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {customMessage}
                </div>
              </div>
            )}
          </div>
        </TabPane>

        <TabPane tab="Custom" key="custom">
          <Form form={form} layout="vertical">
            <Form.Item
              label="System Message"
              name="systemMessage"
              help="This message defines how the AI assistant should behave and respond."
            >
              <TextArea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                rows={12}
                placeholder="Enter a custom system message..."
                className="font-mono text-sm"
              />
            </Form.Item>

            <div className="flex justify-between items-center">
              <Space>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={handleReset}
                >
                  Reset to Default
                </Button>
                <Text type="secondary" className="text-sm">
                  Characters: {customMessage.length}
                </Text>
              </Space>

              <Button
                type="link"
                icon={<CopyOutlined />}
                onClick={() => handleCopy(customMessage)}
              >
                Copy Message
              </Button>
            </div>
          </Form>
        </TabPane>

        <TabPane tab="Available Agents" key="examples">
          <div className="space-y-4">
            <Title level={5}>Available Agent Prompts</Title>
            
            {agents.map((agent) => (
              <div key={agent.name} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <Text strong>{agent.title}</Text>
                    <Text type="secondary" className="block text-sm">{agent.description}</Text>
                    {agent.category.length > 0 && (
                      <Text type="secondary" className="block text-xs">
                        Categories: {agent.category.join(', ')}
                      </Text>
                    )}
                  </div>
                  <Space>
                    <Button
                      size="small"
                      onClick={() => handleTemplateChange(agent.name)}
                      loading={loading}
                    >
                      Use This
                    </Button>
                    <Button
                      type="link"
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={async () => {
                        try {
                          const response = await ApiService.getAgentPrompt(agent.filename);
                          if (response.success && response.data) {
                            await handleCopy(response.data.content);
                          }
                        } catch (error) {
                          message.error('Failed to copy agent content');
                        }
                      }}
                    />
                  </Space>
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded">
                  <Text type="secondary">File: {agent.filename}</Text>
                </div>
              </div>
            ))}
          </div>
        </TabPane>
      </Tabs>
    </Modal>
  );
};

export default SystemMessageModal;