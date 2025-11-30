/**
 * WelcomeScreen Components
 * 
 * This module contains component definitions and exports for WelcomeScreen.
 */
import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import ReactMarkdown from 'react-markdown';
import ApiService from '../../services/api';
import { Brand } from 'branding';

const { Title, Paragraph } = Typography;

// Define interface for component props to ensure type safety
interface WelcomeScreenProps {
  onSuccess: () => void;
}

// Main welcome screen component for access key verification
export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSuccess }) => {
  // State management for loading indicator and guide content
  const [loading, setLoading] = useState(false);
  const [guideContent, setGuideContent] = useState('');

  // Fetch quick guide content on component mount, using different URL based on environment
  useEffect(() => {
    // Determine backend port from environment variables
    const backendPort = import.meta.env.VITE_BACKEND_PORT || '8003';
    // Select appropriate URL based on development/production environment
    const guideUrl = import.meta.env.DEV ? `http://localhost:${backendPort}/static/QUICKGUIDE.MD` : '/static/QUICKGUIDE.MD';
    fetch(guideUrl)
      .then(response => response.text())
      .then(text => setGuideContent(text));
  }, []);

  // Handle form submission and access key verification
  const onFinish = async (values: { access_key: string }) => {
    // Start loading state to prevent multiple submissions
    setLoading(true);
    try {
      // Call API service to verify access key
      const response = await ApiService.verifyAccessKey(values.access_key);
      
      // Check verification result and handle accordingly
      if (response.success) {
        message.success('Access granted!');
        // Store access key in session storage for persistence
        sessionStorage.setItem('access_key', values.access_key);
        // Trigger success callback to proceed to next screen
        onSuccess();
      } else {
        // Show error message if verification fails
        message.error(response.error || 'Invalid access key.');
      }
    } catch (error) {
      // Handle any unexpected errors during verification
      message.error('An error occurred while verifying the access key.');
    } finally {
      // Reset loading state regardless of success or failure
      setLoading(false);
    }
  };

  // Render welcome screen with access key form and guide content
  const brandTagline = Brand.tagline || Brand.name || 'AI Assistant';

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <div style={{ width: 800, padding: 40, background: 'white', borderRadius: 8, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)', display: 'flex' }}>
        {/* Access key input section */}
        <div style={{ flex: 1, paddingRight: 40 }}>
          <Title level={2} style={{ textAlign: 'center' }}>Welcome to {brandTagline}</Title>
          <Paragraph style={{ textAlign: 'center', marginBottom: 24 }}>
            Please enter the access key to continue.
          </Paragraph>
          {/* Form for access key input with validation */}
          <Form onFinish={onFinish}>
            <Form.Item
              name="access_key"
              rules={[{ required: true, message: 'Please input the access key!' }]}
            >
              <Input.Password placeholder="Access Key" />
            </Form.Item>
            <Form.Item>
              {/* Submit button with loading state */}
              <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
                Enter
              </Button>
            </Form.Item>
          </Form>
        </div>
        {/* Quick guide section rendered using markdown */}
        <div style={{ flex: 1, borderLeft: '1px solid #f0f0f0', paddingLeft: 40, maxHeight: '80vh', overflowY: 'auto' }}>
          <ReactMarkdown>{guideContent}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
