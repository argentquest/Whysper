import React, { useState, useEffect, useRef } from 'react';
import { Select, Button, Checkbox, Input, Space, Typography, Spin, message, Segmented } from 'antd';
import {
  ReloadOutlined,
  FolderOutlined,
  FileOutlined,
  UnorderedListOutlined,
  ApartmentOutlined,
  UploadOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';
import { Modal } from '../common/Modal';
import type { FileItem, UploadedFile } from '../../types';
import ApiService from '../../services/api';
import FileTreeModal from './FileTreeModal';

const { Option } = Select;
const { Search } = Input;
const { Text } = Typography;

interface ContextModalProps {
  open: boolean;
  onCancel: () => void;
  onApply: (selectedFiles: FileItem[]) => void;
  initialFiles?: FileItem[];
}

export const ContextModal: React.FC<ContextModalProps> = ({
  open,
  onCancel,
  onApply,
  initialFiles = [],
}) => {
  const [viewMode, setViewMode] = useState<'list' | 'tree' | 'uploaded'>('list');
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [currentDirectory, setCurrentDirectory] = useState('Root (All Files)');
  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([]);
  const [uploadLoading, setUploadLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize selected files from props
  useEffect(() => {
    if (initialFiles.length > 0) {
      setSelectedFiles(new Set(initialFiles.map(f => f.path)));
    }
  }, [initialFiles]);

  // Load files when modal opens
  useEffect(() => {
    if (open) {
      loadFiles();
    }
  }, [open]);

  // Load uploaded files when modal opens
  useEffect(() => {
    if (open) {
      loadUploadedFiles();
    }
  }, [open]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await ApiService.getFiles();
      if (response.success && response.data) {
        setFiles(response.data);
      } else {
        message.error(response.error || 'Failed to load files');
      }
    } catch (error) {
      message.error('Error loading files');
      console.error('Error loading files:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUploadedFiles = async () => {
    try {
      const response = await ApiService.getUploadedFiles();
      if (response.success && response.data) {
        setUploadedFiles(response.data);
      }
    } catch (error) {
      console.error('Error loading uploaded files:', error);
    }
  };

  const loadDirectory = async (path?: string) => {
    setLoading(true);
    try {
      const response = await ApiService.getFiles(path === 'Root (All Files)' ? undefined : path);
      if (response.success && response.data) {
        setFiles(response.data);
        setCurrentDirectory(path || 'Root (All Files)');
        message.success('Directory loaded successfully');
      } else {
        message.error(response.error || 'Failed to load directory');
      }
    } catch (error) {
      message.error('Error loading directory');
      console.error('Error loading directory:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (fileList: File[]) => {
    if (fileList.length === 0) return;

    setUploadLoading(true);
    
    try {
      const uploadedFiles: UploadedFile[] = [];
      
      // Process each file
      for (const file of fileList) {
        const content = await readFileAsText(file);
        uploadedFiles.push({
          name: file.name,
          content,
          size: file.size,
          type: file.type || 'text/plain'
        });
      }

      // Upload files to backend
      const response = await ApiService.uploadFiles({
        files: uploadedFiles,
        target_directory: 'uploads'
      });

      if (response.success && response.data) {
        message.success(`Successfully uploaded ${uploadedFiles.length} file(s)`);
        
        // Refresh uploaded files list
        await loadUploadedFiles();
        
        // Switch to uploaded files view
        setViewMode('uploaded');
        
        // Auto-select uploaded files
        const newPaths = response.data.data.files.map((f: FileItem) => f.path);
        setSelectedFiles(new Set([...selectedFiles, ...newPaths]));
      } else {
        message.error(response.error || 'Failed to upload files');
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      message.error('Error uploading files');
    } finally {
      setUploadLoading(false);
    }
  };

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  };

  const handleUploadButtonClick = () => {
    fileInputRef.current?.click();
  };

  const filteredFiles = files.filter(file =>
    file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    file.path.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleFileToggle = (filePath: string, checked: boolean) => {
    const newSelected = new Set(selectedFiles);
    if (checked) {
      newSelected.add(filePath);
    } else {
      newSelected.delete(filePath);
    }
    setSelectedFiles(newSelected);
  };

  const handleSelectAll = () => {
    const allFilePaths = filteredFiles.map(f => f.path);
    setSelectedFiles(new Set([...selectedFiles, ...allFilePaths]));
  };

  const handleSelectNone = () => {
    setSelectedFiles(new Set());
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const getFileIcon = (file: FileItem) => {
    if (file.is_uploaded) {
      return <CloudUploadOutlined className="text-green-500" />;
    }
    return file.type === 'directory' ? (
      <FolderOutlined className="text-blue-500" />
    ) : (
      <FileOutlined className="text-gray-500" />
    );
  };

  const handleApply = () => {
    // Combine regular files and uploaded files
    const allFiles = [...files, ...uploadedFiles];
    const selectedFileItems = allFiles.filter(file => selectedFiles.has(file.path));
    onApply(selectedFileItems);
    onCancel();
  };

  const directoryOptions = [
    'Root (All Files)',
    'backend/',
    'backend/app/',
    'backend/app/api/v1/endpoints/',
    'backend/app/services/',
    'backend/app/utils/',
    'backend/common/',
    'backend/tests/',
    'frontend/',
    'frontend/src/',
    'frontend/src/components/',
    'frontend/src/services/',
    'frontend/src/types/',
    'prompts/',
    'prompts/coding/agent/',
  ];

  // If tree view mode is selected, render the FileTreeModal
  if (viewMode === 'tree') {
    return (
      <FileTreeModal
        open={open}
        onCancel={onCancel}
        onApply={onApply}
        initialFiles={initialFiles}
      />
    );
  }

  // Use uploaded files for the uploaded view mode
  const displayFiles = viewMode === 'uploaded' ? uploadedFiles : files;

  // Otherwise render the list view
  return (
    <Modal
      title="Conversation Context"
      open={open}
      onCancel={onCancel}
      onOk={handleApply}
      width={800}
      okText="Apply Context"
      cancelText="Cancel"
    >
      <div className="space-y-4">
        {/* View Mode Toggle */}
        <div className="flex items-center justify-between">
          <Segmented
            value={viewMode}
            onChange={(value) => setViewMode(value as 'list' | 'tree' | 'uploaded')}
            options={[
              {
                label: 'List View',
                value: 'list',
                icon: <UnorderedListOutlined />,
              },
              {
                label: 'Tree View',
                value: 'tree',
                icon: <ApartmentOutlined />,
              },
              {
                label: 'Uploaded Files',
                value: 'uploaded',
                icon: <CloudUploadOutlined />,
              },
            ]}
          />
        </div>

        {/* File Upload Button - Show in all views except tree */}
                {String(viewMode) !== 'tree' && (
          <div className="flex items-center gap-4">
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={handleUploadButtonClick}
              loading={uploadLoading}
              className="mb-4"
            >
              Upload Files
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.py,.js,.ts,.jsx,.tsx,.html,.css,.json,.md,.yml,.yaml,.xml,.csv,.sql,.sh,.bat,.ps1,.go,.rs,.java,.cpp,.c,.h,.hpp,.php,.rb,.swift,.kt,.scala,.clj,.hs,.ml,.fs,.dart,.lua,.r,.m,.nim,.v,.zig,.cr,.ex,.exs,.elm,.purs,.tsv,.ini,.cfg,.conf,.toml,.env,.gitignore,.dockerfile,.makefile,.cmake"
              style={{ display: 'none' }}
              aria-label="Upload files for context"
              title="Upload files to use as context in conversations"
              onChange={(e) => {
                const files = e.target.files;
                if (files) {
                  handleFileUpload(Array.from(files));
                }
                // Reset input value to allow uploading the same file again
                e.target.value = '';
              }}
            />
            {viewMode === 'uploaded' && (
              <Button
                icon={<ReloadOutlined />}
                onClick={loadUploadedFiles}
                loading={loading}
                className="mb-4"
              >
                Refresh
              </Button>
            )}
          </div>
        )}

        {/* Directory Selection - Hide in uploaded view */}
        {viewMode !== 'uploaded' && (
          <div className="flex items-center gap-4">
          <div className="flex-1">
            <Text className="block mb-2 text-sm font-medium">Select Folder</Text>
            <Select
              value={currentDirectory}
              onChange={(value) => {
                setCurrentDirectory(value);
                loadDirectory(value);
              }}
              className="w-full"
              placeholder="Choose directory"
            >
              {directoryOptions.map(dir => (
                <Option key={dir} value={dir}>{dir}</Option>
              ))}
            </Select>
          </div>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={() => loadDirectory(currentDirectory)}
            loading={loading}
            className="mt-6"
          >
            Load Directory
          </Button>
          </div>
        )}

        {/* File Selection Status */}
        <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700">
          <Text className="text-sm text-gray-600">
            {selectedFiles.size > 0
              ? `${selectedFiles.size} file${selectedFiles.size !== 1 ? 's' : ''} selected`
              : 'No files selected'
            }
          </Text>
          
          <Text className="text-sm text-gray-600">
            {viewMode === 'uploaded'
              ? `${uploadedFiles.length} uploaded file${uploadedFiles.length !== 1 ? 's' : ''}`
              : 'Directory scanned successfully'
            }
          </Text>
        </div>

        {/* File Actions - Hide search in uploaded view */}
        <div className="flex items-center justify-between">
          <Space>
            <Button
              onClick={handleSelectAll}
              size="small"
              disabled={displayFiles.length === 0}
            >
              Select All ({displayFiles.length})
            </Button>
            <Button
              onClick={handleSelectNone}
              size="small"
              disabled={selectedFiles.size === 0}
            >
              Select None
            </Button>
          </Space>

          {viewMode !== 'uploaded' && (
            <Search
              placeholder="Filter files..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
              size="small"
            />
          )}
        </div>

        {/* File List */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 border-b border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-12 gap-4 text-xs font-medium text-gray-600 dark:text-gray-400">
              <div className="col-span-7">{viewMode === 'uploaded' ? 'File Name' : 'File Path'}</div>
              <div className="col-span-3">Size</div>
              <div className="col-span-2 text-right">Type</div>
            </div>
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {(loading || uploadLoading) ? (
              <div className="flex items-center justify-center py-8">
                <Spin size="large" />
              </div>
            ) : displayFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {viewMode === 'uploaded' ? 'No uploaded files found' : 'No files found'}
              </div>
            ) : (
              displayFiles.map((file) => (
                <div
                  key={file.path}
                  className="grid grid-cols-12 gap-4 px-4 py-1.5 border-b border-gray-100 dark:border-gray-800 last:border-b-0 hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <div className="col-span-7 flex items-center gap-2">
                    <Checkbox
                      checked={selectedFiles.has(file.path)}
                      onChange={(e) => handleFileToggle(file.path, e.target.checked)}
                    />
                    {getFileIcon(file)}
                    <Text className="text-sm truncate">
                      {viewMode === 'uploaded' ? file.name : file.path}
                    </Text>
                    {file.is_uploaded && (
                      <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
                        Uploaded
                      </span>
                    )}
                  </div>
                  
                  <div className="col-span-3 flex items-center">
                    <Text className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </Text>
                  </div>
                  
                  <div className="col-span-2 flex justify-end items-center">
                    {file.is_uploaded ? (
                      <Text className="text-xs text-green-600 dark:text-green-400">Upload</Text>
                    ) : (
                      <Text className="text-xs text-gray-400">Local</Text>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Selection Summary */}
        <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
          <Text className="text-sm">
            <strong>{selectedFiles.size}</strong> files selected
            {selectedFiles.size > 0 && (
              <span className="text-gray-600 dark:text-gray-400 ml-2">
                Total size: {formatFileSize(
                  [...files, ...uploadedFiles]
                    .filter(f => selectedFiles.has(f.path))
                    .reduce((sum, f) => sum + f.size, 0)
                )}
              </span>
            )}
          </Text>
        </div>
      </div>
    </Modal>
  );
};

export default ContextModal;