import React, { useState, useRef, useEffect } from 'react';
import { Button, Select, Tooltip, message as antMessage, Checkbox } from 'antd';
import {
  SendOutlined,
  ClearOutlined,
  PlusOutlined,
  CopyOutlined,
  CompressOutlined,
  ExpandOutlined,
} from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import type * as Monaco from 'monaco-editor';

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
  disabled?: boolean;
  subagentCommands?: SubagentCommand[];
}

export const InputPanel: React.FC<InputPanelProps> = ({
  onSendMessage,
  onClear,
  loading = false,
  disabled = false,
  subagentCommands = [],
}) => {
  const [message, setMessage] = useState('');
  const [lastSentMessage, setLastSentMessage] = useState<string>('');
  const [showSubagentText, setShowSubagentText] = useState<boolean>(false); // Checkbox: when unchecked, send command separately (hidden)
  const [userMessage, setUserMessage] = useState<string>(''); // Store user's actual message separately from subagent text

  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCommand, setSelectedCommand] = useState<string>('');
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const [currentHeight, setCurrentHeight] = useState<number>(120); // Track current height in pixels
  const [previousHeight, setPreviousHeight] = useState<number>(120); // Store previous height for restoration

  // Refs to store current values for key binding
  const messageRef = useRef(message);
  const userMessageRef = useRef(userMessage);
  const loadingRef = useRef(loading);
  const selectedCommandRef = useRef(selectedCommand);
  const showSubagentTextRef = useRef(showSubagentText);

  // Update refs when values change
  useEffect(() => {
    messageRef.current = message;
  }, [message]);

  useEffect(() => {
    userMessageRef.current = userMessage;
  }, [userMessage]);

  useEffect(() => {
    loadingRef.current = loading;
  }, [loading]);

  useEffect(() => {
    selectedCommandRef.current = selectedCommand;
  }, [selectedCommand]);

  useEffect(() => {
    showSubagentTextRef.current = showSubagentText;
  }, [showSubagentText]);

  // Handle editor mount
  const handleEditorDidMount = (editor: Monaco.editor.IStandaloneCodeEditor, monaco: typeof Monaco) => {
    editorRef.current = editor;

    // Add custom key binding: Ctrl+Enter to submit
    editor.addAction({
      id: 'submit-message',
      label: 'Submit Message',
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => {
        // Use refs to get current values (avoid stale closure)
        const currentMessage = messageRef.current.trim();
        const currentUserMessage = userMessageRef.current.trim();
        const currentShowSubagent = showSubagentTextRef.current;
        const currentSelectedCommand = selectedCommandRef.current;
        const currentLoading = loadingRef.current;

        if (currentMessage && !currentLoading) {
          let messageToSend = currentMessage;
          let commandToSend = '';

          // Checkbox logic:
          // - Unchecked: Send user message only, pass subagent command separately (hidden from UI)
          // - Checked: Send full message including subagent text (visible in UI)
          if (!currentShowSubagent && currentSelectedCommand) {
            // Checkbox unchecked: send user message only, command goes separately
            messageToSend = currentUserMessage || currentMessage;
            commandToSend = currentSelectedCommand;
          }

          setLastSentMessage(messageToSend);
          onSendMessage(messageToSend, commandToSend);
          setMessage('');
          setUserMessage('');
          setSelectedCategory('');
          setSelectedCommand('');
        }
      }
    });
  };

  // Get unique categories from subagent commands
  const categories = React.useMemo(() => {
    const uniqueCategories = [...new Set(subagentCommands.map(cmd => cmd.category))];
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
      let messageToSend = message.trim();
      let commandToSend = '';

      // Checkbox logic:
      // - Unchecked: Send user message only, pass subagent command separately (hidden from UI)
      // - Checked: Send full message including subagent text (visible in UI)
      if (!showSubagentText && selectedCommand) {
        // Checkbox unchecked: send user message only, command goes separately
        messageToSend = userMessage.trim();
        commandToSend = selectedCommand;
      }
      // If checkbox is checked, messageToSend already includes subagent text

      setLastSentMessage(messageToSend);
      onSendMessage(messageToSend, commandToSend);
      setMessage('');
      setUserMessage('');
      setSelectedCategory('');
      setSelectedCommand('');
    }
  };

  const handleCopyLastMessage = async () => {
    if (lastSentMessage) {
      try {
        await navigator.clipboard.writeText(lastSentMessage);
        antMessage.success('Last prompt copied to clipboard');
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        antMessage.error('Failed to copy to clipboard');
      }
    }
  };

  const handleClear = () => {
    setMessage('');
    setUserMessage('');
    setSelectedCategory('');
    setSelectedCommand('');
    setShowSubagentText(false);
    onClear();
  };

  const injectSubagentCommand = (subcommand: string) => {
    // When injecting, add subcommand to current message
    const newMessage = userMessage ? `${userMessage}\n\n${subcommand}` : subcommand;
    setMessage(newMessage);
    setUserMessage(userMessage); // Keep user message separate

    // Auto-check the checkbox when injecting a command to show it
    handleCheckboxChange(true);

    // Focus editor after inserting command
    setTimeout(() => {
      editorRef.current?.focus();
    }, 0);
  };

  // Get the current subagent command text if one is selected
  const getCurrentSubagentText = () => {
    if (!selectedCommand) return '';
    const command = subagentsForCategory.find(cmd => cmd.title === selectedCommand);
    return command ? command.subcommand : '';
  };

  // Handle checkbox changes - update message to show/hide subagent text
  const handleCheckboxChange = (checked: boolean) => {
    setShowSubagentText(checked);

    if (checked && selectedCommand) {
      // Checkbox checked: show subagent text in editor
      const subagentText = getCurrentSubagentText();
      if (subagentText) {
        const newMessage = userMessage ? `${userMessage}\n\n${subagentText}` : subagentText;
        setMessage(newMessage);
      }
    } else {
      // Checkbox unchecked: hide subagent text, show only user message
      setMessage(userMessage);
    }
  };

  // Handle command selection changes
  useEffect(() => {
    if (showSubagentText && selectedCommand) {
      // If checkbox is checked and command is selected, update message to include subagent text
      const subagentText = getCurrentSubagentText();
      if (subagentText) {
        const newMessage = userMessage ? `${userMessage}\n\n${subagentText}` : subagentText;
        setMessage(newMessage);
      }
    } else if (!showSubagentText) {
      // Otherwise, show only user message
      setMessage(userMessage);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCommand, showSubagentText]); // Intentionally excluding userMessage to avoid loops

  // Handle editor changes - update userMessage state
  const handleEditorChange = (value: string | undefined) => {
    const newValue = value || '';
    setMessage(newValue);

    // If checkbox is unchecked, this is the user's actual message
    if (!showSubagentText) {
      setUserMessage(newValue);
    } else {
      // If checkbox is checked, extract user message (everything before subagent text)
      const subagentText = getCurrentSubagentText();
      if (subagentText && newValue.includes(subagentText)) {
        const parts = newValue.split(subagentText);
        setUserMessage(parts[0].trim());
      } else {
        setUserMessage(newValue);
      }
    }
  };

  const handleReduceHeight = () => {
    if (currentHeight > 60) {
      // Store current height before reducing
      setPreviousHeight(currentHeight);
      const newHeight = Math.max(60, Math.ceil(currentHeight * 0.25)); // Reduce by 75%, min 60px
      setCurrentHeight(newHeight);
    }
  };

  const handleRestoreHeight = () => {
    if (currentHeight < previousHeight) {
      setCurrentHeight(previousHeight);
    }
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
            className="min-w-[280px]"
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
            className="min-w-[360px]"
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

          {/* Show Subagent Text Checkbox */}
          <Checkbox
            checked={showSubagentText}
            onChange={(e) => handleCheckboxChange(e.target.checked)}
            className="ml-4"
          >
            Show Subagent Text
          </Checkbox>

          <div className="flex-1" />

          {/* Submit, Copy, and Clear Buttons */}
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

            <Tooltip title="Copy Last Prompt">
              <Button
                icon={<CopyOutlined />}
                onClick={handleCopyLastMessage}
                disabled={!lastSentMessage || loading}
                size="small"
              >
                Copy
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
          <div
            className="relative"
            style={{
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              border: '2px solid #e2e8f0',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
              overflow: 'hidden',
              minHeight: `${currentHeight}px`,
              height: `${currentHeight}px`,
              maxHeight: '400px',
            }}
          >
            <div style={{ padding: '0 10px' }}>
              <Editor
              height={`${currentHeight}px`}
              defaultLanguage="markdown"
              value={message}
              onChange={handleEditorChange}
              onMount={handleEditorDidMount}
              theme="light"
              options={{
                minimap: { enabled: false },
                lineNumbers: 'off',
                glyphMargin: false,
                folding: false,
                lineDecorationsWidth: 0,
                lineNumbersMinChars: 0,
                renderLineHighlight: 'none',
                scrollBeyondLastLine: false,
                fontSize: 15,
                fontFamily: 'ui-sans-serif, system-ui, sans-serif',
                wordWrap: 'on',
                wrappingIndent: 'none',
                padding: { top: 10, bottom: 10 },
                overviewRulerBorder: false,
                overviewRulerLanes: 0,
                hideCursorInOverviewRuler: true,
                scrollbar: {
                  vertical: 'auto',
                  horizontal: 'hidden',
                  verticalScrollbarSize: 8,
                },
                readOnly: disabled || loading,
                suggest: {
                  showKeywords: false,
                  showSnippets: false,
                },
                quickSuggestions: false,
                parameterHints: { enabled: false },
                acceptSuggestionOnEnter: 'off',
              }}
            />
            </div>

            {/* Resize buttons in top-right corner */}
            <div
              className="absolute top-2 right-2 flex gap-1"
              style={{
                background: 'rgba(255, 255, 255, 0.9)',
                borderRadius: '6px',
                padding: '2px',
                backdropFilter: 'blur(8px)',
                border: '1px solid rgba(226, 232, 240, 0.8)',
              }}
            >
              <Tooltip title="Reduce height by 75%">
                <Button
                  type="text"
                  size="small"
                  icon={<CompressOutlined />}
                  onClick={handleReduceHeight}
                  disabled={currentHeight <= 60}
                  style={{
                    fontSize: '10px',
                    height: '20px',
                    width: '20px',
                    minWidth: '20px',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                />
              </Tooltip>
              
              <Tooltip title="Restore to previous height">
                <Button
                  type="text"
                  size="small"
                  icon={<ExpandOutlined />}
                  onClick={handleRestoreHeight}
                  disabled={currentHeight >= previousHeight}
                  style={{
                    fontSize: '10px',
                    height: '20px',
                    width: '20px',
                    minWidth: '20px',
                    padding: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                />
              </Tooltip>
            </div>
          </div>
          
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
                Press Ctrl+Enter to send
              </span>
            </div>
          )}
        </div>
    </div>
  );
};

export default InputPanel;






