import React, { useState, useEffect } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import ReactMarkdown from 'react-markdown';
import ApiService from '../../services/api';

const { Title, Paragraph } = Typography;

interface WelcomeScreenProps {
  onSuccess: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [guideContent, setGuideContent] = useState('');

  useEffect(() => {
    const backendPort = import.meta.env.VITE_BACKEND_PORT || '8003';
    const guideUrl = import.meta.env.DEV ? `http://localhost:${backendPort}/static/QUICKGUIDE.MD` : '/static/QUICKGUIDE.MD';
    fetch(guideUrl)
      .then(response => response.text())
      .then(text => setGuideContent(text));
  }, []);

  const onFinish = async (values: { access_key: string }) => {
    setLoading(true);
    try {
      const response = await ApiService.verifyAccessKey(values.access_key);
      if (response.success) {
        message.success('Access granted!');
        sessionStorage.setItem('access_key', values.access_key);
        onSuccess();
      } else {
        message.error(response.error || 'Invalid access key.');
      }
    } catch (error) {
      message.error('An error occurred while verifying the access key.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <div style={{ width: 800, padding: 40, background: 'white', borderRadius: 8, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)', display: 'flex' }}>
        <div style={{ flex: 1, paddingRight: 40 }}>
          <Title level={2} style={{ textAlign: 'center' }}>Welcome to Whysper</Title>
          <Paragraph style={{ textAlign: 'center', marginBottom: 24 }}>
            Please enter the access key to continue.
          </Paragraph>
          <Form onFinish={onFinish}>
            <Form.Item
              name="access_key"
              rules={[{ required: true, message: 'Please input the access key!' }]}
            >
              <Input.Password placeholder="Access Key" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} style={{ width: '100%' }}>
                Enter
              </Button>
            </Form.Item>
          </Form>
        </div>
        <div style={{ flex: 1, borderLeft: '1px solid #f0f0f0', paddingLeft: 40, maxHeight: '80vh', overflowY: 'auto' }}>
          <ReactMarkdown>{guideContent}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};
