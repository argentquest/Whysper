import React, { useState, useRef, useEffect } from 'react';
import { Button, Input, Select, Tooltip } from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import type { TextAreaRef } from 'antd/es/input/TextArea';

const { TextArea } = Input;
const { Option } = Select;

interface SubagentCommand {
  category: string;
  title: string;
  subcommand: string;
}

interface InputPanelProps {
  onSendMessage: (message: string, command?: string) => void;
  onClear: () => void;
  loading?: boolean;
  placeholder?: string;
  disabled?: boolean;
  subagentCommands?: SubagentCommand[];
}

export const InputPanel: React.FC<InputPanelProps> = ({
  onSendMessage,
  onClear,
  loading = false,
  placeholder = "Type your next question. Press Enter to send, Shift+Enter for a new line.",
  disabled = false,
  subagentCommands = [],
}) => {
  const [message, setMessage] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCommand, setSelectedCommand] = useState<string>('');
  const textAreaRef = useRef<TextAreaRef>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textAreaRef.current?.resizableTextArea?.textArea;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [message]);

  // Get unique categories from subagent commands
  const categories = React.useMemo(() => {
    console.log('📊 Total subagent commands loaded:', subagentCommands.length, subagentCommands);
    const uniqueCategories = [...new Set(subagentCommands.map(cmd => cmd.category))];
    console.log('📊 Categories found:', uniqueCategories);
    return uniqueCategories.sort();
  }, [subagentCommands]);

  // Get subagents for selected category
  const subagentsForCategory = React.useMemo(() => {
    if (!selectedCategory) return [];
    const filtered = subagentCommands.filter(cmd => cmd.category === selectedCategory);
    console.log('🔍 Subagents for category:', selectedCategory, '→', filtered.length, 'items:', filtered);
    return filtered;
  }, [subagentCommands, selectedCategory]);

  const handleSend = () => {
    if (message.trim() && !loading) {
      onSendMessage(message.trim(), selectedCommand);
      setMessage('');
      setSelectedCategory('');
      setSelectedCommand('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessage('');
    setSelectedCategory('');
    setSelectedCommand('');
    onClear();
  };

  const injectSubagentCommand = (subcommand: string) => {
    const newMessage = message ? `${message}\n\n${subcommand}` : subcommand;
    setMessage(newMessage);
    
    // Focus textarea after inserting command
    setTimeout(() => {
      textAreaRef.current?.focus();
      const textarea = textAreaRef.current?.resizableTextArea?.textArea;
      if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
      }
    }, 0);
  };


  return (
    <div className="w-full px-6">
        {/* First Row: Subagent Commands + Submit/Clear Buttons */}
        <div className="flex items-center gap-3 mb-3">
          <span className="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
            Inject Command:
          </span>
          
          {/* Category Selection */}
          <Select
            placeholder="Select category"
            value={selectedCategory}
            onChange={(value) => {
              setSelectedCategory(value);
              setSelectedCommand(''); // Reset command when category changes
            }}
            className="min-w-[140px]"
            size="small"
            allowClear
          >
            {categories.map(category => (
              <Option key={category} value={category}>
                {category}
              </Option>
            ))}
          </Select>

          {/* Command Selection */}
          <Select
            placeholder="Select command"
            value={selectedCommand}
            onChange={setSelectedCommand}
            className="min-w-[180px]"
            size="small"
            allowClear
            disabled={!selectedCategory}
          >
            {subagentsForCategory.map((subagent, index) => (
              <Option key={`${subagent.category}-${subagent.title}-${index}`} value={subagent.title}>
                {subagent.title}
              </Option>
            ))}
          </Select>

          {/* Inject Button */}
          <Button 
            size="small" 
            icon={<PlusOutlined />}
            disabled={!selectedCommand}
            onClick={() => {
              const command = subagentsForCategory.find(cmd => cmd.title === selectedCommand);
              if (command) {
                injectSubagentCommand(command.subcommand);
              }
            }}
          >
            Inject
          </Button>

          <div className="flex-1" />

          {/* Submit and Clear Buttons */}
          <div className="flex gap-2">
            <Tooltip title="Submit Question">
              <Button
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={loading}
                disabled={!message.trim() || disabled}
                size="small"
              >
                Submit
              </Button>
            </Tooltip>

            <Tooltip title="Clear">
              <Button
                icon={<ClearOutlined />}
                onClick={handleClear}
                disabled={loading}
                size="small"
              >
                Clear
              </Button>
            </Tooltip>
          </div>
        </div>

        {/* Input Area */}
        <div className="relative">
          <TextArea
            ref={textAreaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || loading}
            autoSize={{ minRows: 4, maxRows: 12 }}
            className="resize-none"
            style={{
              borderRadius: '16px',
              fontSize: '15px',
              lineHeight: '1.6',
              padding: '20px 24px',
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              border: '2px solid #e2e8f0',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
              transition: 'all 0.3s ease',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#667eea';
              e.target.style.boxShadow = '0 4px 20px rgba(102, 126, 234, 0.15)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.05)';
            }}
          />
          
          {/* Floating action area */}
          {message.trim() && (
            <div 
              className="absolute bottom-3 right-3 flex items-center gap-2"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                borderRadius: '12px',
                padding: '8px 12px',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
              }}
            >
              <span 
                style={{ 
                  fontSize: '12px', 
                  color: '#64748b',
                  fontWeight: 500
                }}
              >
                Press Enter to send
              </span>
            </div>
          )}
        </div>
    </div>
  );
};

export default InputPanel;






