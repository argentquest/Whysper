Here's the TypeScript code with inline comments:

```typescript
import React from 'react';
import { Modal as AntModal, Button } from 'antd';
import { CloseOutlined } from '@ant-design/icons';

// Define props structure for flexible modal component configuration
interface ModalProps {
  title: string | React.ReactNode;
  open: boolean;
  onCancel: () => void;
  onOk?: () => void;
  children: React.ReactNode;
  width?: number | string;
  footer?: React.ReactNode | null;
  okText?: string;
  cancelText?: string;
  confirmLoading?: boolean;
  destroyOnClose?: boolean;
  maskClosable?: boolean;
  centered?: boolean;
  className?: string;
}

// Create a reusable modal component with default and customizable behaviors
export const Modal: React.FC<ModalProps> = ({
  title,
  open,
  onCancel,
  onOk,
  children,
  width = 520,
  footer,
  okText = 'OK',
  cancelText = 'Cancel',
  confirmLoading = false,
  destroyOnClose = true,
  maskClosable = true,
  centered = true,
  className = '',
}) => {
  // Generate footer based on custom or default configuration
  // Allows for complete footer customization or automatic button generation
  const defaultFooter = footer === null ? null : footer || (
    <div className="flex justify-end gap-2">
      // Render cancel button with configurable text
      <Button onClick={onCancel}>{cancelText}</Button>
      // Conditionally render OK button with optional loading state
      {onOk && (
        <Button 
          type="primary" 
          onClick={onOk}
          loading={confirmLoading}
        >
          {okText}
        </Button>
      )}
    </div>
  );

  return (
    // Use Ant Design Modal with enhanced customization
    <AntModal
      // Create a custom title layout with dynamic content and close button
      title={
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold">{title}</div>
          // Inline close button using CloseOutlined icon
          <Button
            type="text"
            icon={<CloseOutlined />}
            onClick={onCancel}
            className="!p-1"
          />
        </div>
      }
      open={open}
      onCancel={onCancel}
      footer={defaultFooter}
      width={width}
      // Configure modal behavior and appearance through props
      destroyOnHidden={destroyOnClose}
      maskClosable={maskClosable}
      centered={centered}
      className={`Whysper-modal ${className}`}
      closable={false} // Manual close button management in custom title
    >
      // Wrap modal content with consistent padding
      <div className="py-4">
        {children}
      </div>
    </AntModal>
  );
};

export default Modal;