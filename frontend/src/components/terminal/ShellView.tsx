import React, { useState, useEffect } from 'react';
import { Spin, Alert, Button, message, Space, Select } from 'antd';
import {
  ConsoleSqlOutlined,
  ReloadOutlined,
  ClearOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import TerminalComponent from './TerminalComponent';
import ApiService from '../../services/api';
import type { Tab } from '../../types';

const { Option } = Select;

interface ShellViewProps {
  tab: Tab;
  onSessionChange?: (tabId: string, sessionId: string) => void;
  theme: 'light' | 'dark';
}

export const ShellView: React.FC<ShellViewProps> = ({
  tab,
  onSessionChange,
  theme,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [commandCount, setCommandCount] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(tab.shellSessionId || null);
  const [shellType, setShellType] = useState<string>(tab.shellType || 'auto');

  // Create shell session if none exists
  useEffect(() => {
    if (!sessionId) {
      createSession();
    } else {
      loadSessionInfo();
    }
  }, []);

  const createSession = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await ApiService.post('/shell/sessions', {
        working_directory: undefined, // Use default CODE_PATH
        shell_type: shellType
      });

      if (response.data?.success) {
        const newSessionId = response.data.data.session_id;
        setSessionId(newSessionId);
        setSessionInfo(response.data.data.session_info);
        onSessionChange?.(tab.id, newSessionId);
        message.success('Shell session created');
      } else {
        throw new Error('Failed to create shell session');
      }
    } catch (error: any) {
      console.error('Error creating shell session:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create shell session';
      setError(errorMessage);
      message.error(`Failed to create shell session: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const loadSessionInfo = async () => {
    if (!sessionId) return;

    try {
      const response = await ApiService.get(`/shell/sessions/${sessionId}`);
      if (response.data?.success) {
        setSessionInfo(response.data.data);
      }
    } catch (error: any) {
      console.error('Error loading session info:', error);
      // Session might not exist, create a new one
      if (error.response?.status === 404) {
        await createSession();
      }
    }
  };

  const handleConnectionChange = (connected: boolean) => {
    setIsConnected(connected);
  };

  const handleCommand = () => {
    setCommandCount(prev => prev + 1);
  };

  const handleReconnect = () => {
    if (sessionId) {
      loadSessionInfo();
    } else {
      createSession();
    }
  };

  const handleCloseSession = async () => {
    if (!sessionId) return;

    try {
      await ApiService.delete(`/shell/sessions/${sessionId}`);
      setSessionId(null);
      setSessionInfo(null);
      setIsConnected(false);
      message.success('Shell session closed');
      
      // Create a new session
      await createSession();
    } catch (error: any) {
      console.error('Error closing session:', error);
      message.error('Failed to close session');
    }
  };

  // If still loading
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Spin size="large" />
          <div className="mt-4 text-gray-600 dark:text-gray-400">
            Creating shell session...
          </div>
        </div>
      </div>
    );
  }

  // If error occurred
  if (error) {
    return (
      <div className="p-6">
        <Alert
          message="Error Creating Shell Session"
          description={error}
          type="error"
          showIcon
          action={
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={createSession}
            >
              Retry
            </Button>
          }
        />
      </div>
    );
  }

  // If no session ID yet (shouldn't happen after loading)
  if (!sessionId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <ConsoleSqlOutlined className="text-4xl mb-4" />
          <div>No shell session available</div>
          <Button
            className="mt-4"
            icon={<ReloadOutlined />}
            onClick={createSession}
          >
            Create Session
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Shell Info Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <ConsoleSqlOutlined className="text-green-600 dark:text-green-400" />
          <span className="font-medium text-gray-900 dark:text-gray-100">
            Shell Session
          </span>
          <span className={`text-xs px-2 py-1 rounded ${
            isConnected 
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {sessionInfo && (
            <div className="text-xs text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded flex items-center gap-1">
              <InfoCircleOutlined />
              <span>🔧 {sessionInfo.shell_type}</span>
              <span>•</span>
              <span>📁 {sessionInfo.working_directory}</span>
              <span>•</span>
              <span>📊 {commandCount} commands</span>
            </div>
          )}
          
          <Space>
            {!sessionId && (
              <Select
                value={shellType}
                onChange={setShellType}
                size="small"
                style={{ width: 120 }}
              >
                <Option value="auto">Auto</Option>
                <Option value="cmd">CMD</Option>
                <Option value="powershell">PowerShell</Option>
                <Option value="bash">Bash</Option>
              </Select>
            )}
            
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleReconnect}
              title="Reconnect session"
            />
            
            <Button
              size="small"
              icon={<ClearOutlined />}
              onClick={handleCloseSession}
              title="Close & recreate session"
            />
          </Space>
        </div>
      </div>

      {/* Terminal Component */}
      <div className="flex-1 overflow-hidden">
        <TerminalComponent
          sessionId={sessionId}
          onCommand={handleCommand}
          onConnectionChange={handleConnectionChange}
          theme={theme}
          height="100%"
        />
      </div>
    </div>
  );
};

export default ShellView;