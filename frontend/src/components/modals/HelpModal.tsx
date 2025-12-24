/**
 * HelpModal Components
 *
 * This module contains component definitions and exports for HelpModal.
 */
import { Modal } from 'antd'
import React, { useEffect,useState } from 'react'
import ReactMarkdown from 'react-markdown'

import { getBackendBaseUrl } from '../../utils/apiBase'

/**
 * HelpModalProps type definition
 *
 * Describes the structure and properties of HelpModalProps
 */
interface HelpModalProps {
  open: boolean
  onCancel: () => void
}

/**
 * HelpModal component
 */
export const HelpModal: React.FC<HelpModalProps> = ({ open, onCancel }) => {
  // State to store the markdown content for the guide
  const [guideContent, setGuideContent] = useState('')

  useEffect(() => {
    // Fetch guide content only when modal is opened
    if (open) {
      const guideUrl = `${getBackendBaseUrl()}/static/QUICKGUIDE.MD`

      // Fetch markdown guide content from server
      fetch(guideUrl)
        .then((response) => response.text())
        .then((text) => setGuideContent(text))
    }
  }, [open]) // Re-run effect when 'open' state changes

  return (
    // Antd Modal component to display help guide
    <Modal title="Quick Start Guide" open={open} onCancel={onCancel} footer={null} width={800}>
      {/* Scrollable container for markdown content */}
      <div style={{ maxHeight: '70vh', overflowY: 'auto' }}>
        {/* Render markdown content using ReactMarkdown */}
        <ReactMarkdown>{guideContent}</ReactMarkdown>
      </div>
    </Modal>
  )
}
