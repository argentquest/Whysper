import React, { useState, useEffect } from 'react';
import { Spin, Alert, Button, message } from 'antd';
import { FileOutlined, SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import MonacoEditor from './MonacoEditor';
import ApiService from '../../services/api';
import type { Tab } from '../../types';

interface FileEditorViewProps {
  tab: Tab;
  onContentChange: (tabId: string, content: string, isDirty: boolean) => void;
  onSave: (tabId: string) => Promise<void>;
  theme: 'light' | 'dark';
}

export const FileEditorView: React.FC<FileEditorViewProps> = ({
  tab,
  onContentChange,
  onSave,
  theme,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Load file content when tab is created or file path changes
  useEffect(() => {
    if (tab.filePath && !tab.fileContent) {
      loadFileContent();
    }
  }, [tab.filePath]);

  const loadFileContent = async () => {
    if (!tab.filePath) return;

    setLoading(true);
    setError(null);

    try {
      // Encode the path properly for URL while preserving path separators
      const encodedPath = tab.filePath.split('/').map(encodeURIComponent).join('/');
      const response = await ApiService.get(`/files/read/${encodedPath}`);
      
      if (response.data?.success && response.data?.data) {
        const content = response.data.data.content;
        // When loading file for the first time, both fileContent and originalContent should be set
        onContentChange(tab.id, content, false);
      } else {
        throw new Error('Failed to load file content');
      }
    } catch (error: any) {
      console.error('Error loading file:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load file';
      setError(errorMessage);
      message.error(`Failed to load file: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (newContent: string | undefined) => {
    if (newContent !== undefined && newContent !== tab.originalContent) {
      const isDirty = newContent !== tab.originalContent;
      onContentChange(tab.id, newContent, isDirty);
    }
  };

  const handleSave = async () => {
    if (!tab.filePath || !tab.fileContent) return;

    setSaving(true);
    try {
      await onSave(tab.id);
      message.success(`File saved: ${tab.filePath}`);
    } catch (error: any) {
      console.error('Error saving file:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save file';
      message.error(`Failed to save file: ${errorMessage}`);
    } finally {
      setSaving(false);
    }
  };

  const getLanguageFromPath = (filePath: string): string => {
    const extension = filePath.split('.').pop()?.toLowerCase() || '';
    
    const languageMap: { [key: string]: string } = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'json': 'json',
      'html': 'html',
      'htm': 'html',
      'css': 'css',
      'scss': 'scss',
      'sass': 'scss',
      'less': 'less',
      'md': 'markdown',
      'markdown': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'xml': 'xml',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'dockerfile': 'dockerfile',
      'vue': 'vue',
      'go': 'go',
      'rs': 'rust',
      'java': 'java',
      'c': 'c',
      'cpp': 'cpp',
      'cxx': 'cpp',
      'cc': 'cpp',
      'h': 'c',
      'hpp': 'cpp',
      'cs': 'csharp',
      'php': 'php',
      'rb': 'ruby',
      'swift': 'swift',
      'kt': 'kotlin',
      'scala': 'scala',
      'r': 'r',
      'lua': 'lua',
      'pl': 'perl',
      'toml': 'toml',
      'ini': 'ini',
      'cfg': 'ini',
      'conf': 'ini',
    };

    return languageMap[extension] || 'plaintext';
  };

  // If still loading
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Spin size="large" />
          <div className="mt-4 text-gray-600 dark:text-gray-400">
            Loading {tab.filePath}...
          </div>
        </div>
      </div>
    );
  }

  // If error occurred
  if (error) {
    return (
      <div className="p-6">
        <Alert
          message="Error Loading File"
          description={error}
          type="error"
          showIcon
          action={
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={loadFileContent}
            >
              Retry
            </Button>
          }
        />
      </div>
    );
  }

  // If no file content yet (shouldn't happen after loading)
  if (!tab.fileContent && tab.fileContent !== '') {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <FileOutlined className="text-4xl mb-4" />
          <div>No file content available</div>
          <Button
            className="mt-4"
            icon={<ReloadOutlined />}
            onClick={loadFileContent}
          >
            Load File
          </Button>
        </div>
      </div>
    );
  }

  const language = getLanguageFromPath(tab.filePath || '');

  return (
    <div className="h-full flex flex-col">
      {/* File Info Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <FileOutlined className="text-blue-600 dark:text-blue-400" />
          <span className="font-medium text-gray-900 dark:text-gray-100">
            {tab.filePath}
          </span>
          {tab.isDirty && (
            <span className="text-orange-500 font-bold">●</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">
            {language.toUpperCase()}
          </span>
          
          <Button
            type="primary"
            size="small"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
            disabled={!tab.isDirty}
          >
            Save
          </Button>
        </div>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1 overflow-hidden">
        <MonacoEditor
          value={tab.fileContent || ''}
          language={language}
          onChange={handleContentChange}
          onSave={handleSave}
          theme={theme}
          height="100%"
          showToolbar={false} // We have our own toolbar above
        />
      </div>
    </div>
  );
};

export default FileEditorView;