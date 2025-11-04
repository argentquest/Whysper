/**
 * Agent Option List Component
 * Displays available agent options as a simple list
 */

import React from 'react';
import { Menu, Spin, Empty } from 'antd';
import { AgentOption } from '../../types';

interface AgentOptionListProps {
  options: AgentOption[];
  selectedOptionId: string | null;
  onOptionSelect: (option: AgentOption) => void;
  isLoading: boolean;
  error: string | null;
}

export const AgentOptionList: React.FC<AgentOptionListProps> = ({
  options,
  selectedOptionId,
  onOptionSelect,
  isLoading,
  error,
}) => {
  if (isLoading) {
    return <Spin />;
  }

  if (error) {
    return <Empty description={`Error: ${error}`} />;
  }

  if (options.length === 0) {
    return <Empty description="No agent options available" />;
  }

  const items = options.map((option) => ({
    key: option.id,
    label: option.name,
    title: option.description,
  }));

  return (
    <Menu
      items={items}
      selectedKeys={selectedOptionId ? [selectedOptionId] : []}
      onClick={(e) => {
        const option = options.find((o) => o.id === e.key);
        if (option) {
          onOptionSelect(option);
        }
      }}
      style={{ border: '1px solid var(--ant-color-border)', borderRadius: '4px' }}
    />
  );
};

export default AgentOptionList;
