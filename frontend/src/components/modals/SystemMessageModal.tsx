/**
 * SystemMessageModal Component
 * 
 * This module exports the SystemMessageModal component for the application.
 */
import { CopyOutlined,ReloadOutlined } from '@ant-design/icons';
import { Button, Input, message, Modal as AntModal,Select, Space, Tabs, Typography } from 'antd';
import React, { useEffect,useState } from 'react';

import ApiService from '../../services/api';
import { Modal } from '../common/Modal';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

/**
 * Agent type definition
 * 
 * Describes the structure and properties of Agent
 */
interface Agent {
  name: string;
  title: string;
  description: string;
  category: string[];
  filename: string;
}

/**
 * SystemMessageModalProps type definition
 * 
 * Describes the structure and properties of SystemMessageModalProps
 */
interface SystemMessageModalProps {
  open: boolean;
  onCancel: () => void;
  onSave: (systemMessage: string) => void;
  currentSystemMessage?: string;
  currentAgent?: string;
  onClearConversation?: () => void;
  hasConversationHistory?: boolean;
}

/**
 * SystemMessageModal component
 */
export const SystemMessageModal: React.FC<SystemMessageModalProps> = ({
  open,
  onCancel,
  onSave,
  currentSystemMessage = '',
  currentAgent = '',
  onClearConversation,
  hasConversationHistory = false,
}) => {
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
          setAgents(response.data as Agent[]);
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
    }
  }, [open, currentSystemMessage, currentAgent]);

  const handleTemplateChange = async (agentName: string) => {
    const agent = agents.find(a => a.name === agentName);
    if (agent) {
      setActiveTemplate(agentName);
      setLoading(true);
      try {
        const response = await ApiService.getAgentPrompt(agent.filename);
        if (response.success && response.data) {
          setCustomMessage(response.data.content);
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
      // Check if system prompt actually changed
      const promptChanged = messageContent !== currentSystemMessage;
      
      if (promptChanged && hasConversationHistory && onClearConversation) {
        // Show confirmation dialog about starting new conversation
        AntModal.confirm({
          title: 'Start New Conversation?',
          content: 'Changing the system prompt will start a new conversation to ensure consistent AI behavior. Your current conversation will be saved to history.',
          okText: 'Start New Conversation',
          cancelText: 'Keep Current Conversation',
          onOk: () => {
            onSave(messageContent);
            onClearConversation();
            onCancel();
            message.success('Agent prompt updated and new conversation started');
          },
          onCancel: () => {
            onSave(messageContent);
            onCancel();
            message.warning('Agent prompt updated. Consider starting a new conversation for best results.');
          }
        });
      } else {
        // No conversation history or no change, just save
        onSave(messageContent);
        onCancel();
        message.success('Agent prompt updated');
      }
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
      <Tabs
        defaultActiveKey="agents"
        items={[
          {
            key: 'agents',
            label: 'Agent Prompts',
            children: (
              <div className="space-y-4">
                <div>
                  <Text className="mb-2 block font-medium">Choose an Agent:</Text>
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
                  <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
                    <div className="mb-2 flex items-center justify-between">
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
                    <div className="max-h-40 overflow-y-auto whitespace-pre-wrap text-sm">
                      {customMessage}
                    </div>
                  </div>
                )}
              </div>
            ),
          },
          {
            key: 'custom',
            label: 'Custom',
            children: (
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block font-medium">System Message</label>
                  <p className="mb-2 text-sm text-gray-500">
                    This message defines how the AI assistant should behave and respond.
                  </p>
                  <TextArea
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    rows={12}
                    placeholder="Enter a custom system message..."
                    className="font-mono text-sm"
                  />
                </div>

                <div className="flex items-center justify-between">
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
              </div>
            ),
          },
          {
            key: 'examples',
            label: 'Available Agents',
            children: (
              <div className="space-y-4">
                <Title level={5}>Available Agent Prompts</Title>
                
                {agents.map((agent) => (
                  <div key={agent.name} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
                    <div className="mb-2 flex items-center justify-between">
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
                    <div className="rounded bg-gray-50 p-3 text-sm text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                      <Text type="secondary">File: {agent.filename}</Text>
                    </div>
                  </div>
                ))}
              </div>
            ),
          },
        ]}
      />
    </Modal>
  );
};

export default SystemMessageModal;
