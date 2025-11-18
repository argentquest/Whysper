Here's the code with inline comments explaining the logic:

import React from 'react';
import { Modal as AntModal, Button } from 'antd';
import { CloseOutlined } from '@ant-design/icons';

// Define the structure and properties for the Modal component
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

// Modal component with flexible configuration options
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
  // Determine footer content: custom, default, or null
  // Provides flexibility in modal footer rendering
  const defaultFooter = footer === null ? null : footer || (
    <div className="flex justify-end gap-2">
      {/* Cancel button with configurable text */}
      <Button onClick={onCancel}>{cancelText}</Button>
      {/* Conditional OK button with loading state */}
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
    // Ant Design Modal with customized title and behavior
    <AntModal
      // Custom title with dynamic content and close button
      title={
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold">{title}</div>
          {/* Inline close button using CloseOutlined icon */}
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
      // Configurable modal behavior and styling
      destroyOnHidden={destroyOnClose}
      maskClosable={maskClosable}
      centered={centered}
      className={`Whysper-modal ${className}`}
      closable={false} // We handle close button in custom title
    >
      {/* Modal content wrapper with padding */}
      <div className="py-4">
        {children}
      </div>
    </AntModal>
  );
};

export default Modal;