import React, { useState } from 'react';
import { Input, Button, Select, message, Form } from 'antd';
import {
  FileOutlined,
  FolderOutlined,
} from '@ant-design/icons';
import { Modal } from '../common/Modal';

const { Option } = Select;

interface NewFileModalProps {
  open: boolean;
  onCancel: () => void;
  onCreateFile: (filePath: string, initialContent?: string) => void;
}

// Common file templates
const FILE_TEMPLATES = {
  'javascript': {
    extension: '.js',
    content: `// New JavaScript file
console.log('Hello, World!');

function exampleFunction() {
    return 'This is a new JavaScript file';
}
`,
  },
  'typescript': {
    extension: '.ts',
    content: `// New TypeScript file
interface ExampleInterface {
    message: string;
}

function exampleFunction(): ExampleInterface {
    return { message: 'This is a new TypeScript file' };
}

console.log('Hello, World!');
`,
  },
  'python': {
    extension: '.py',
    content: `#!/usr/bin/env python3
"""
New Python file
"""

def example_function():
    """Example function"""
    return "This is a new Python file"

if __name__ == "__main__":
    print("Hello, World!")
    print(example_function())
`,
  },
  'react': {
    extension: '.tsx',
    content: `import React from 'react';

interface Props {
    // Add your props here
}

export const NewComponent: React.FC<Props> = () => {
    return (
        <div>
            <h1>New React Component</h1>
            <p>This is a new React component.</p>
        </div>
    );
};

export default NewComponent;
`,
  },
  'html': {
    extension: '.html',
    content: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New HTML File</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <p>This is a new HTML file.</p>
</body>
</html>
`,
  },
  'css': {
    extension: '.css',
    content: `/* New CSS file */

body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
`,
  },
  'json': {
    extension: '.json',
    content: `{
    "name": "new-file",
    "version": "1.0.0",
    "description": "A new JSON file",
    "main": "index.js",
    "scripts": {
        "start": "node index.js"
    },
    "keywords": [],
    "author": "",
    "license": "MIT"
}
`,
  },
  'markdown': {
    extension: '.md',
    content: `# New Markdown File

This is a new markdown file.

## Features

- **Bold text**
- *Italic text*
- \`Inline code\`

## Code Example

\`\`\`javascript
function hello() {
    console.log('Hello, World!');
}
\`\`\`

## Links

[Example Link](https://example.com)
`,
  },
  'plain': {
    extension: '.txt',
    content: `This is a new text file.

You can add any content here.
`,
  },
};

export const NewFileModal: React.FC<NewFileModalProps> = ({
  open,
  onCancel,
  onCreateFile,
}) => {
  const [form] = Form.useForm();
  const [fileName, setFileName] = useState('');
  const [fileTemplate, setFileTemplate] = useState<string>('plain');
  const [customPath, setCustomPath] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    try {
      await form.validateFields();
      
      if (!fileName.trim()) {
        message.error('Please enter a file name');
        return;
      }

      setLoading(true);

      // Build the file path
      let filePath = '';
      if (customPath.trim()) {
        // Normalize path separators
        const normalizedPath = customPath.trim().replace(/\\/g, '/');
        filePath = normalizedPath.endsWith('/') ? normalizedPath : normalizedPath + '/';
      }

      // Add filename with appropriate extension
      const template = FILE_TEMPLATES[fileTemplate as keyof typeof FILE_TEMPLATES];
      const baseFileName = fileName.trim();
      
      // Add extension if not already present
      if (!baseFileName.includes('.') && template) {
        filePath += baseFileName + template.extension;
      } else {
        filePath += baseFileName;
      }

      // Get initial content
      const initialContent = template?.content || '';

      // Create the file
      onCreateFile(filePath, initialContent);
      
      // Reset form
      form.resetFields();
      setFileName('');
      setCustomPath('');
      setFileTemplate('plain');
      
      onCancel();
      
    } catch (error) {
      console.error('Error creating file:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPreviewPath = () => {
    if (!fileName.trim()) return '';
    
    let path = customPath.trim() ? customPath.trim().replace(/\\/g, '/') : '';
    if (path && !path.endsWith('/')) path += '/';
    
    const template = FILE_TEMPLATES[fileTemplate as keyof typeof FILE_TEMPLATES];
    const baseFileName = fileName.trim();
    
    if (!baseFileName.includes('.') && template) {
      return path + baseFileName + template.extension;
    }
    return path + baseFileName;
  };

  return (
    <Modal
      title="Create New File"
      open={open}
      onCancel={() => {
        form.resetFields();
        setFileName('');
        setCustomPath('');
        setFileTemplate('plain');
        onCancel();
      }}
      footer={[
        <Button key="cancel" onClick={onCancel}>
          Cancel
        </Button>,
        <Button
          key="create"
          type="primary"
          loading={loading}
          onClick={handleCreate}
          disabled={!fileName.trim()}
        >
          Create File
        </Button>,
      ]}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          template: 'plain',
        }}
      >
        <Form.Item
          label="File Template"
          name="template"
        >
          <Select
            value={fileTemplate}
            onChange={setFileTemplate}
            size="large"
          >
            <Option value="plain">Plain Text (.txt)</Option>
            <Option value="javascript">JavaScript (.js)</Option>
            <Option value="typescript">TypeScript (.ts)</Option>
            <Option value="react">React Component (.tsx)</Option>
            <Option value="python">Python (.py)</Option>
            <Option value="html">HTML (.html)</Option>
            <Option value="css">CSS (.css)</Option>
            <Option value="json">JSON (.json)</Option>
            <Option value="markdown">Markdown (.md)</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="Directory Path (optional)"
          name="directory"
        >
          <Input
            prefix={<FolderOutlined />}
            placeholder="e.g., src/components or leave empty for root"
            value={customPath}
            onChange={(e) => setCustomPath(e.target.value)}
            size="large"
          />
        </Form.Item>

        <Form.Item
          label="File Name"
          name="filename"
          rules={[
            { required: true, message: 'Please enter a file name' },
            { 
              pattern: /^[^<>:"/\\|?*]+$/, 
              message: 'File name contains invalid characters' 
            },
          ]}
        >
          <Input
            prefix={<FileOutlined />}
            placeholder="Enter file name (extension will be added automatically)"
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            size="large"
            onPressEnter={handleCreate}
          />
        </Form.Item>

        {/* Preview */}
        {getPreviewPath() && (
          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              File will be created at:
            </div>
            <div className="font-mono text-sm text-blue-600 dark:text-blue-400">
              {getPreviewPath()}
            </div>
          </div>
        )}

        {/* Template Preview */}
        {fileTemplate !== 'plain' && (
          <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
            <strong>Template includes:</strong> Basic file structure with example code for {fileTemplate}
          </div>
        )}
      </Form>
    </Modal>
  );
};

export default NewFileModal;