import React, { useRef, useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { Button, Tooltip, Space, message } from 'antd';
import { SaveOutlined, UndoOutlined, RedoOutlined, ExpandOutlined, CompressOutlined } from '@ant-design/icons';
import type { editor } from 'monaco-editor';

interface MonacoEditorProps {
  value: string;
  language: string;
  onChange: (value: string | undefined) => void;
  onSave?: () => void;
  readOnly?: boolean;
  height?: string | number;
  theme?: 'light' | 'dark';
  showToolbar?: boolean;
  className?: string;
}

// Type definitions for Monaco Editor handlers
type OnMount = (editor: editor.IStandaloneCodeEditor, monaco: any) => void;
type OnChange = (value: string | undefined, event: any) => void;

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  language,
  onChange,
  onSave,
  readOnly = false,
  height = '100%',
  theme = 'light',
  showToolbar = true,
  className = '',
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor>();
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Handle editor mount
  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Configure editor options
    editor.updateOptions({
      automaticLayout: true,
      fontSize: 14,
      lineHeight: 20,
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace",
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: true,
      folding: true,
      lineNumbers: 'on',
      renderWhitespace: 'boundary',
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true,
      },
      suggest: {
        enableIntelliSense: true,
        insertMode: 'replace',
        showInlineDetails: true,
      },
      quickSuggestions: {
        other: true,
        comments: true,
        strings: true,
      },
      parameterHints: { enabled: true },
      hover: { enabled: true },
      contextmenu: true,
      mouseWheelZoom: true,
      formatOnPaste: true,
      formatOnType: true,
    });

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      if (onSave) {
        onSave();
      }
    });

    // Set up language-specific features
    setupLanguageFeatures(monaco, language);
  };

  // Setup language-specific features like auto-completion
  const setupLanguageFeatures = (monaco: any, lang: string) => {
    switch (lang) {
      case 'typescript':
      case 'javascript':
        // Enable TypeScript/JavaScript IntelliSense
        monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
          target: monaco.languages.typescript.ScriptTarget.ES2020,
          allowNonTsExtensions: true,
          moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
          module: monaco.languages.typescript.ModuleKind.CommonJS,
          noEmit: true,
          esModuleInterop: true,
          jsx: monaco.languages.typescript.JsxEmit.React,
          reactNamespace: 'React',
          allowJs: true,
          typeRoots: ['node_modules/@types'],
        });

        monaco.languages.typescript.javascriptDefaults.setCompilerOptions({
          target: monaco.languages.typescript.ScriptTarget.ES2020,
          allowNonTsExtensions: true,
          allowJs: true,
        });
        break;

      case 'python':
        // Python-specific configuration
        break;

      case 'json':
        // JSON schema validation
        monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
          validate: true,
          allowComments: false,
          schemas: [],
        });
        break;

      default:
        break;
    }
  };

  // Handle content change
  const handleChange: OnChange = (newValue) => {
    onChange(newValue);
  };

  // Get Monaco theme based on app theme
  const getMonacoTheme = () => {
    return theme === 'dark' ? 'vs-dark' : 'vs';
  };

  // Detect language from file extension or content
  const getLanguageFromExtension = (lang: string): string => {
    const languageMap: { [key: string]: string } = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'json': 'json',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'dockerfile': 'dockerfile',
    };

    return languageMap[lang.toLowerCase()] || lang;
  };

  // Toolbar actions
  const handleUndo = () => {
    editorRef.current?.trigger('keyboard', 'undo', null);
  };

  const handleRedo = () => {
    editorRef.current?.trigger('keyboard', 'redo', null);
  };

  const handleFormat = () => {
    editorRef.current?.getAction('editor.action.formatDocument')?.run();
    message.success('Code formatted');
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const currentLanguage = getLanguageFromExtension(language);

  return (
    <div 
      className={`monaco-editor-container ${className} ${isFullscreen ? 'fullscreen' : ''}`}
      style={{
        height: isFullscreen ? '100vh' : height,
        position: isFullscreen ? 'fixed' : 'relative',
        top: isFullscreen ? 0 : 'auto',
        left: isFullscreen ? 0 : 'auto',
        right: isFullscreen ? 0 : 'auto',
        bottom: isFullscreen ? 0 : 'auto',
        zIndex: isFullscreen ? 1000 : 'auto',
        backgroundColor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
      }}
    >
      {/* Toolbar */}
      {showToolbar && (
        <div 
          className="editor-toolbar flex items-center justify-between p-2 border-b border-gray-200 dark:border-gray-600"
          style={{
            backgroundColor: theme === 'dark' ? '#2d2d30' : '#f8f9fa',
          }}
        >
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
              {currentLanguage.toUpperCase()}
            </span>
          </div>

          <Space>
            <Tooltip title="Undo (Ctrl+Z)">
              <Button
                type="text"
                size="small"
                icon={<UndoOutlined />}
                onClick={handleUndo}
              />
            </Tooltip>

            <Tooltip title="Redo (Ctrl+Y)">
              <Button
                type="text"
                size="small"
                icon={<RedoOutlined />}
                onClick={handleRedo}
              />
            </Tooltip>

            <Tooltip title="Format Code">
              <Button
                type="text"
                size="small"
                onClick={handleFormat}
              >
                Format
              </Button>
            </Tooltip>

            {onSave && (
              <Tooltip title="Save (Ctrl+S)">
                <Button
                  type="primary"
                  size="small"
                  icon={<SaveOutlined />}
                  onClick={onSave}
                >
                  Save
                </Button>
              </Tooltip>
            )}

            <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
              <Button
                type="text"
                size="small"
                icon={isFullscreen ? <CompressOutlined /> : <ExpandOutlined />}
                onClick={toggleFullscreen}
              />
            </Tooltip>
          </Space>
        </div>
      )}

      {/* Monaco Editor */}
      <div style={{ height: showToolbar ? 'calc(100% - 48px)' : '100%' }}>
        <Editor
          height="100%"
          language={currentLanguage}
          value={value}
          theme={getMonacoTheme()}
          onChange={handleChange}
          onMount={handleEditorDidMount}
          options={{
            readOnly,
            automaticLayout: true,
          }}
          loading={
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <div className="text-sm text-gray-500">Loading editor...</div>
              </div>
            </div>
          }
        />
      </div>
    </div>
  );
};

export default MonacoEditor;