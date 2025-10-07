import React, { useState, useEffect } from 'react';
import { Tree, Button, Input, Space, Typography, Spin, message, Checkbox } from 'antd';
import {
  ReloadOutlined,
  FolderOutlined,
  FolderOpenOutlined,
  FileOutlined,
  ExpandAltOutlined,
  ShrinkOutlined,
} from '@ant-design/icons';
import type { TreeProps, DataNode } from 'antd/es/tree';
import { Modal } from '../common/Modal';
import type { FileItem } from '../../types';
import ApiService from '../../services/api';

const { Search } = Input;
const { Text } = Typography;

interface FileTreeModalProps {
  open: boolean;
  onCancel: () => void;
  onApply: (selectedFiles: FileItem[]) => void;
  initialFiles?: FileItem[];
}

interface TreeNode extends DataNode {
  key: string;
  title: React.ReactNode;
  children?: TreeNode[];
  isLeaf?: boolean;
  path: string;
  size?: number;
  type: 'file' | 'directory';
}

export const FileTreeModal: React.FC<FileTreeModalProps> = ({
  open,
  onCancel,
  onApply,
  initialFiles = [],
}) => {
  const [loading, setLoading] = useState(false);
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [checkedKeys, setCheckedKeys] = useState<React.Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [autoExpandParent, setAutoExpandParent] = useState(true);
  const [searchValue, setSearchValue] = useState('');
  const [allFiles, setAllFiles] = useState<FileItem[]>([]);
  const [includeSubfolders, setIncludeSubfolders] = useState(true);

  // Initialize selected files from props
  useEffect(() => {
    if (initialFiles.length > 0) {
      setCheckedKeys(initialFiles.map(f => f.path));
    }
  }, [initialFiles]);

  // Load files when modal opens
  useEffect(() => {
    if (open) {
      loadFiles();
    }
  }, [open]);

  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await ApiService.getFiles();
      if (response.success && response.data) {
        setAllFiles(response.data);
        const tree = buildTreeFromFiles(response.data);
        setTreeData(tree);

        // Auto-expand first level
        const firstLevelKeys = tree.map(node => node.key);
        setExpandedKeys(firstLevelKeys);
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

  const buildTreeFromFiles = (files: FileItem[]): TreeNode[] => {
    const tree: { [key: string]: TreeNode } = {};
    const rootNodes: TreeNode[] = [];

    // Sort files: directories first, then by path
    const sortedFiles = [...files].sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'directory' ? -1 : 1;
      }
      return a.path.localeCompare(b.path);
    });

    sortedFiles.forEach(file => {
      const parts = file.path.split('/');
      let currentPath = '';

      parts.forEach((part, index) => {
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;

        if (!tree[currentPath]) {
          const isLeaf = index === parts.length - 1 && file.type === 'file';
          const nodeType = isLeaf ? 'file' : 'directory';

          tree[currentPath] = {
            key: currentPath,
            title: part,
            path: currentPath,
            isLeaf,
            type: nodeType,
            size: isLeaf ? file.size : undefined,
            children: [],
            icon: ({ expanded }: any) => {
              if (nodeType === 'file') {
                return <FileOutlined className="text-gray-500" />;
              }
              return expanded ?
                <FolderOpenOutlined className="text-blue-500" /> :
                <FolderOutlined className="text-blue-500" />;
            },
          };

          if (parentPath && tree[parentPath]) {
            tree[parentPath].children!.push(tree[currentPath]);
          } else if (index === 0) {
            rootNodes.push(tree[currentPath]);
          }
        }
      });
    });

    return rootNodes;
  };

  const onExpand: TreeProps['onExpand'] = (expandedKeysValue) => {
    setExpandedKeys(expandedKeysValue);
    setAutoExpandParent(false);
  };

  const onCheck: TreeProps['onCheck'] = (checkedKeysValue, info) => {
    const keys = Array.isArray(checkedKeysValue) ? checkedKeysValue : checkedKeysValue.checked;

    if (includeSubfolders) {
      // When a folder is checked, automatically check all its children
      const allKeys = new Set(keys);
      const checkedNodes = info.checkedNodes;

      const addChildKeys = (node: any) => {
        if (node.children) {
          node.children.forEach((child: any) => {
            allKeys.add(child.key);
            addChildKeys(child);
          });
        }
      };

      checkedNodes.forEach((node: any) => {
        if (node.type === 'directory') {
          addChildKeys(node);
        }
      });

      setCheckedKeys(Array.from(allKeys));
    } else {
      setCheckedKeys(keys);
    }
  };

  const onSelect: TreeProps['onSelect'] = (selectedKeysValue) => {
    setSelectedKeys(selectedKeysValue);
  };

  const expandAll = () => {
    const getAllKeys = (nodes: TreeNode[]): string[] => {
      let keys: string[] = [];
      nodes.forEach(node => {
        if (!node.isLeaf) {
          keys.push(node.key);
          if (node.children) {
            keys = keys.concat(getAllKeys(node.children));
          }
        }
      });
      return keys;
    };
    setExpandedKeys(getAllKeys(treeData));
  };

  const collapseAll = () => {
    setExpandedKeys([]);
  };

  const selectAll = () => {
    const getAllKeys = (nodes: TreeNode[]): string[] => {
      let keys: string[] = [];
      nodes.forEach(node => {
        keys.push(node.key);
        if (node.children) {
          keys = keys.concat(getAllKeys(node.children));
        }
      });
      return keys;
    };
    setCheckedKeys(getAllKeys(treeData));
  };

  const selectNone = () => {
    setCheckedKeys([]);
  };

  const handleApply = () => {
    // Filter files based on checked keys
    const selectedFileItems = allFiles.filter(file =>
      checkedKeys.includes(file.path) && file.type === 'file'
    );
    onApply(selectedFileItems);
    onCancel();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  // Get count of selected files (excluding directories)
  const selectedFileCount = allFiles.filter(file =>
    checkedKeys.includes(file.path) && file.type === 'file'
  ).length;

  const selectedTotalSize = allFiles
    .filter(file => checkedKeys.includes(file.path) && file.type === 'file')
    .reduce((sum, file) => sum + file.size, 0);

  // Enhanced tree node title with size for files
  const getTreeNodeTitle = (node: TreeNode) => {
    if (node.type === 'file' && node.size !== undefined) {
      return (
        <span className="flex items-center justify-between w-full">
          <span>{node.title}</span>
          <span className="text-xs text-gray-500 ml-2">
            {formatFileSize(node.size)}
          </span>
        </span>
      );
    }
    return node.title;
  };

  // Apply custom titles to tree nodes
  const enhanceTreeData = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.map(node => ({
      ...node,
      title: getTreeNodeTitle(node),
      children: node.children ? enhanceTreeData(node.children) : undefined,
    }));
  };

  const enhancedTreeData = enhanceTreeData(treeData);

  return (
    <Modal
      title="Select Files - Tree View"
      open={open}
      onCancel={onCancel}
      onOk={handleApply}
      width={900}
      okText="Apply Context"
      cancelText="Cancel"
    >
      <div className="space-y-4">
        {/* Action Bar */}
        <div className="flex items-center justify-between gap-4">
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadFiles}
              loading={loading}
              size="small"
            >
              Refresh
            </Button>
            <Button
              icon={<ExpandAltOutlined />}
              onClick={expandAll}
              size="small"
              disabled={loading}
            >
              Expand All
            </Button>
            <Button
              icon={<ShrinkOutlined />}
              onClick={collapseAll}
              size="small"
              disabled={loading}
            >
              Collapse All
            </Button>
          </Space>

          <Space>
            <Button
              onClick={selectAll}
              size="small"
              disabled={loading || treeData.length === 0}
            >
              Select All
            </Button>
            <Button
              onClick={selectNone}
              size="small"
              disabled={loading || checkedKeys.length === 0}
            >
              Deselect All
            </Button>
          </Space>
        </div>

        {/* Options */}
        <div className="flex items-center gap-4">
          <Checkbox
            checked={includeSubfolders}
            onChange={(e) => setIncludeSubfolders(e.target.checked)}
          >
            Auto-select files in subfolders when folder is checked
          </Checkbox>
        </div>

        {/* Selection Status */}
        <div className="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <Text className="text-sm">
            <strong>{selectedFileCount}</strong> file{selectedFileCount !== 1 ? 's' : ''} selected
            {selectedFileCount > 0 && (
              <span className="text-gray-600 dark:text-gray-400 ml-2">
                ({formatFileSize(selectedTotalSize)})
              </span>
            )}
          </Text>

          <Text className="text-xs text-gray-500">
            {checkedKeys.length} total items checked
          </Text>
        </div>

        {/* Search */}
        <Search
          placeholder="Search files and folders..."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          className="w-full"
          allowClear
        />

        {/* Tree View */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 bg-white dark:bg-gray-900">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Spin size="large" tip="Loading file tree..." />
            </div>
          ) : treeData.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileOutlined className="text-4xl mb-4" />
              <p>No files found</p>
            </div>
          ) : (
            <Tree
              checkable
              showIcon
              selectable
              expandedKeys={expandedKeys}
              checkedKeys={checkedKeys}
              selectedKeys={selectedKeys}
              onExpand={onExpand}
              onCheck={onCheck}
              onSelect={onSelect}
              treeData={enhancedTreeData}
              autoExpandParent={autoExpandParent}
              height={500}
              className="file-tree"
            />
          )}
        </div>

        {/* Help Text */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>💡 <strong>Tip:</strong> Check folders to select all files within them</p>
          <p>💡 <strong>Tip:</strong> Use search to quickly find specific files</p>
          <p>💡 <strong>Tip:</strong> Only files (not folders) are added to context</p>
        </div>
      </div>

      <style>{`
        .file-tree .ant-tree-treenode {
          padding: 0px 0;
        }

        .file-tree .ant-tree-node-content-wrapper {
          flex: 1;
          padding: 1px 0;
        }

        .file-tree .ant-tree-title {
          width: 100%;
        }
      `}</style>
    </Modal>
  );
};

export default FileTreeModal;
