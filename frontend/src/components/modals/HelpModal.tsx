import React, { useState, useEffect } from 'react';
import { Modal } from 'antd';
import ReactMarkdown from 'react-markdown';

interface HelpModalProps {
  open: boolean;
  onCancel: () => void;
}

export const HelpModal: React.FC<HelpModalProps> = ({ open, onCancel }) => {
  const [guideContent, setGuideContent] = useState('');

  useEffect(() => {
    if (open) {
      const backendPort = import.meta.env.VITE_BACKEND_PORT || '8003';
      const guideUrl = import.meta.env.DEV ? `http://localhost:${backendPort}/static/QUICKGUIDE.MD` : '/static/QUICKGUIDE.MD';
      fetch(guideUrl)
        .then(response => response.text())
        .then(text => setGuideContent(text));
    }
  }, [open]);

  return (
    <Modal
      title="Quick Start Guide"
      open={open}
      onCancel={onCancel}
      footer={null}
      width={800}
    >
      <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
        <ReactMarkdown>{guideContent}</ReactMarkdown>
      </div>
    </Modal>
  );
};
