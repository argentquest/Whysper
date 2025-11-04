/**
 * Prompt Editor Component
 * Monaco editor for prompt input
 */

import React, { useCallback } from 'antd';
import { Input } from 'antd';

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  isReadOnly: boolean;
  maxCharacters: number;
  placeholder?: string;
}

export const PromptEditor: React.FC<PromptEditorProps> = ({
  value,
  onChange,
  isReadOnly,
  maxCharacters,
  placeholder,
}) => {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      if (newValue.length <= maxCharacters) {
        onChange(newValue);
      }
    },
    [maxCharacters, onChange]
  );

  return (
    <Input.TextArea
      value={value}
      onChange={handleChange}
      disabled={isReadOnly}
      placeholder={placeholder || 'Enter your prompt here...'}
      rows={10}
      style={{ fontFamily: 'monospace', fontSize: '13px' }}
    />
  );
};

export default PromptEditor;
