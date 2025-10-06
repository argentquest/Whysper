import React, { useState, useEffect } from 'react';
import { Button, Input, Space, Typography, Spin, message } from 'antd';
import {
  ReloadOutlined,
  FileOutlined,
  EditOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { Modal } from '../common/Modal';
import { useTheme } from '../../themes';
import type { FileItem } from '../../types';
import ApiService from '../../services/api';

const { Search } = Input;
const { Text } = Typography;

interface FileSelectionModalProps {
  open: boolean;
  onCancel: () => void;
  onSelectFile: (file: FileItem) => void;
  onCreateNewFile: () => void;
}

export const FileSelectionModal: React.FC<FileSelectionModalProps> = ({
  open,
  onCancel,
  onSelectFile,
  onCreateNewFile,
}) => {
  const { theme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Load files when modal opens
  useEffect(() => {
    if (open) {
      loadFiles();
    }
  }, [open]);

  // Filter files based on search term
  useEffect(() => {
    if (!searchTerm) {
      setFilteredFiles(files);
    } else {
      const filtered = files.filter(file => 
        file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        file.path.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredFiles(filtered);
    }
  }, [files, searchTerm]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await ApiService.get('/files/?recursive=true');
      
      if (response.data?.success && response.data?.data) {
        // Filter to only show actual files (not directories)
        const fileItems = response.data.data.filter((item: FileItem) => item.type === 'file');
        setFiles(fileItems);
      } else {
        message.error('No files found or invalid response format');
      }
    } catch (error) {
      console.error('Error loading files:', error);
      message.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (file: FileItem) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    // Return appropriate icons based on file type
    switch (extension) {
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
      case 'vue':
        return <FileOutlined style={{ color: '#f1e05a' }} />;
      case 'py':
        return <FileOutlined style={{ color: '#3776ab' }} />;
      case 'java':
        return <FileOutlined style={{ color: '#b07219' }} />;
      case 'html':
      case 'htm':
        return <FileOutlined style={{ color: '#e34c26' }} />;
      case 'css':
      case 'scss':
      case 'sass':
        return <FileOutlined style={{ color: '#563d7c' }} />;
      case 'json':
        return <FileOutlined style={{ color: '#293f58' }} />;
      case 'md':
      case 'markdown':
        return <FileOutlined style={{ color: '#083fa1' }} />;
      default:
        return <FileOutlined style={{ color: '#6b7280' }} />;
    }
  };

  const handleFileSelect = (file: FileItem) => {
    onSelectFile(file);
    onCancel();
  };

  const fileRows = filteredFiles.map((file) => (
    <div
      key={file.path}
      className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg border border-transparent hover:border-blue-200 dark:hover:border-blue-600 cursor-pointer transition-all duration-150"
      onClick={() => handleFileSelect(file)}
    >
      <div className="flex items-center gap-3 min-w-0 flex-1">
        {getFileIcon(file)}
        
        <div className="min-w-0 flex-1">
          <div className="font-medium text-gray-900 dark:text-gray-100 truncate">
            {file.name}
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400 truncate">
            {file.path}
          </div>
          <div className="text-xs text-gray-400 dark:text-gray-500">
            {(file.size / 1024).toFixed(1)} KB
          </div>
        </div>
      </div>
      
      <Button
        type="primary"
        size="small"
        icon={<EditOutlined />}
        onClick={(e) => {
          e.stopPropagation();
          handleFileSelect(file);
        }}
      >
        Edit
      </Button>
    </div>
  ));

  return (
    <Modal
      title="Select File to Edit"
      open={open}
      onCancel={onCancel}
      footer={null}
      width={800}
    >
      <div className="space-y-4">
        {/* Search and Controls */}
        <div className="flex items-center justify-between gap-4">
          <Search
            placeholder="Search files..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
            allowClear
          />
          
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={onCreateNewFile}
            >
              New File
            </Button>
            
            <Button
              icon={<ReloadOutlined />}
              onClick={loadFiles}
              loading={loading}
              title="Refresh file list"
            />
          </Space>
        </div>

        {/* File Count */}
        <div className="text-sm text-gray-600 dark:text-gray-400">
          {loading ? (
            <span>Loading files...</span>
          ) : (
            <span>
              {filteredFiles.length} of {files.length} files
              {searchTerm && ` matching "${searchTerm}"`}
            </span>
          )}
        </div>

        {/* File List */}
        <div 
          className="border border-gray-200 dark:border-gray-600 rounded-lg"
          style={{ 
            maxHeight: '400px', 
            overflowY: 'auto',
            backgroundColor: theme === 'dark' ? '#1f2937' : 'white',
          }}
        >
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Space>
                <Spin size="large" />
                <Text>Loading files...</Text>
              </Space>
            </div>
          ) : filteredFiles.length === 0 ? (
            <div className="flex items-center justify-center p-8">
              <div className="text-center">
                <FileOutlined className="text-4xl text-gray-400 mb-2" />
                <Text className="text-gray-500 dark:text-gray-400">
                  {searchTerm ? `No files found matching "${searchTerm}"` : 'No files found'}
                </Text>
              </div>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {fileRows}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
          💡 <strong>Tip:</strong> Click on any file or the "Edit" button to open it in a new editor tab.
          The file will be opened with syntax highlighting and full Monaco Editor features.
        </div>
      </div>
    </Modal>
  );
};

export default FileSelectionModal;