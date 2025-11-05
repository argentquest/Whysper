/**
 * Agent Selector Component
 * Dropdown for selecting AI agents
 */

import React, { useMemo } from 'react';
import { Select, Modal, Spin } from 'antd';
import type { Agent } from '../../types';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgent: Agent | null;
  onAgentSelect: (agent: Agent) => void;
  hasUnsavedPrompt: boolean;
  isLoading?: boolean;
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onAgentSelect,
  hasUnsavedPrompt,
  isLoading = false,
}) => {
  const options = useMemo(
    () =>
      agents.map((agent) => ({
        label: agent.name,
        value: agent.id,
        agent,
      })),
    [agents]
  );

  const handleChange = (agentId: string) => {
    if (hasUnsavedPrompt) {
      Modal.confirm({
        title: 'Unsaved Changes',
        content: 'You have an unsaved prompt. Switching agents will discard it. Continue?',
        okText: 'Yes',
        cancelText: 'No',
        onOk() {
          const agent = agents.find((a) => a.id === agentId);
          if (agent) {
            onAgentSelect(agent);
          }
        },
      });
    } else {
      const agent = agents.find((a) => a.id === agentId);
      if (agent) {
        onAgentSelect(agent);
      }
    }
  };

  return (
    <Spin spinning={isLoading}>
      <Select
        placeholder="Select an agent..."
        value={selectedAgent?.id || undefined}
        onChange={handleChange}
        options={options}
        style={{ minWidth: '200px' }}
        disabled={isLoading}
        allowClear
      />
    </Spin>
  );
};

export default AgentSelector;
