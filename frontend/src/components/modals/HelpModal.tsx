```typescript
/**
 * HelpModal Components
 * 
 * This module contains component definitions and exports for HelpModal.
 */
import React, { useState, useEffect } from 'react';
import { Modal } from 'antd';
import ReactMarkdown from 'react-markdown';

/**
 * HelpModalProps type definition
 * 
 * Describes the structure and properties of HelpModalProps
 */
interface HelpModalProps {
  open: boolean;
  onCancel: () => void;
}

/**
 * HelpModal component
 */
export const HelpModal: React.FC<HelpModalProps> = ({ open, onCancel }) => {
  // State to store the markdown content for the guide
  const [guideContent, setGuideContent] = useState('');

  useEffect(() => {
    // Fetch guide content only when modal is opened
    if (open) {
      // Determine backend port from environment, default to 8003
      const backendPort = import.meta.env.VITE_BACKEND_PORT || '8003';
      
      // Set guide URL based on development or production environment
      const guideUrl = import.meta.env.DEV ? `http://localhost:${backendPort}/static/QUICKGUIDE.MD` : '/static/QUICKGUIDE.MD';
      
      // Fetch markdown guide content from server
      fetch(guideUrl)
        .then(response => response.text())
        .then(text => setGuideContent(text));
    }
  }, [open]); // Re-run effect when 'open' state changes

  return (
    // Antd Modal component to display help guide
    <Modal
      title="Quick Start Guide"
      open={open}
      onCancel={onCancel}
      footer={null}
      width={800}
    >
      {/* Scrollable container for markdown content */}
      <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
        {/* Render markdown content using ReactMarkdown */}
        <ReactMarkdown>{guideContent}</ReactMarkdown>
      </div>
    </Modal>
  );
};