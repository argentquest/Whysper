import React, { useState } from 'react';
import { Form, Input, Button, message, Typography } from 'antd';
import ApiService from '../../services/api';

const { Title, Paragraph } = Typography;

interface WelcomeScreenProps {
  onSuccess: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: { access_key: string }) => {
    setLoading(true);
    try {
      const response = await ApiService.verifyAccessKey(values.access_key);
      if (response.success) {
        message.success('Access granted!');
        localStorage.setItem('access_key', values.access_key);
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
      <div style={{ width: 400, padding: 40, background: 'white', borderRadius: 8, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)' }}>
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
          <Form.Item>
            <Button type="default" style={{ width: '100%' }} onClick={() => window.open('/static/QUICKGUIDE.MD', '_blank')}>
              Quick Start Guide
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};
