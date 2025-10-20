import React, { useState, useEffect } from 'react';
import { Button, message, Typography } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { Modal } from '../common/Modal';
import { MonacoEditor } from '../editor/MonacoEditor';
import { useTheme } from '../../themes';

const { Title, Text } = Typography;

interface D2TesterModalProps {
  open: boolean;
  onCancel: () => void;
}

interface ValidationResult {
  is_valid: boolean;
  error: string | null;
  code_length: number;
}

interface RenderResult {
  success: boolean;
  svg_content: string | null;
  validation: {
    is_valid: boolean;
    error: string | null;
  };
  metadata: {
    render_time: number;
    timestamp: string;
  };
  error: string | null;
}

const TEST_CASES = {
  valid1: {
    name: 'Valid Simple Diagram',
    code: `# Simple flowchart
User: {
  shape: person
}

API: {
  shape: rectangle
}

Database: {
  shape: cylinder
}

User -> API: Request
API -> Database: Query
Database -> API: Results
API -> User: Response`,
    description: 'Basic flowchart with different shapes',
    isValid: true,
  },
  valid2: {
    name: 'Valid Architecture Diagram',
    code: `# System Architecture
direction: right

Frontend: {
  UI: User Interface
  Router: React Router
}

Backend: {
  API: FastAPI Server
  Auth: Authentication
  DB: PostgreSQL {
    shape: cylinder
  }
}

Frontend.UI -> Frontend.Router
Frontend.Router -> Backend.API
Backend.API -> Backend.Auth
Backend.API -> Backend.DB
Backend.Auth -> Backend.DB`,
    description: 'Multi-tier system architecture',
    isValid: true,
  },
  valid3: {
    name: 'Valid Network Diagram',
    code: `# Network Topology
Internet: {
  shape: cloud
  label: "Internet"
}

Firewall: {
  shape: rectangle
}

LoadBalancer: {
  shape: rectangle
}

Server1: {
  shape: rectangle
}

Server2: {
  shape: rectangle
}

Internet -> Firewall
Firewall -> LoadBalancer
LoadBalancer -> Server1
LoadBalancer -> Server2`,
    description: 'Network infrastructure diagram',
    isValid: true,
  },
  invalid1: {
    name: 'Unclosed String',
    code: `# Invalid - unclosed quote
User: {
  label: "This is unclosed
}

API: {
  label: "API Server"
}

User -> API`,
    description: 'String not properly closed',
    isValid: false,
  },
  invalid2: {
    name: 'Invalid Shape',
    code: `# Invalid - unknown shape
User: {
  shape: human
}

API: {
  shape: rectangle
}

User -> API`,
    description: 'Using "human" instead of "person"',
    isValid: false,
  },
  complex1: {
    name: 'Complex Microservices',
    code: `# Microservices Architecture
direction: down

users: Users {
  shape: person
}

gateway: API Gateway {
  shape: rectangle
}

auth: Auth Service {
  shape: rectangle
}

user_service: User Service {
  shape: rectangle
}

order_service: Order Service {
  shape: rectangle
}

payment_service: Payment Service {
  shape: rectangle
}

user_db: User DB {
  shape: cylinder
}

order_db: Order DB {
  shape: cylinder
}

payment_db: Payment DB {
  shape: cylinder
}

cache: Redis Cache {
  shape: stored_data
}

queue: Message Queue {
  shape: queue
}

users -> gateway: HTTP Requests

gateway -> auth: Authenticate
gateway -> user_service: User Operations
gateway -> order_service: Order Operations
gateway -> payment_service: Payment Operations

auth -> cache: Session Cache

user_service -> user_db: CRUD
order_service -> order_db: CRUD
payment_service -> payment_db: CRUD

order_service -> queue: Order Events
payment_service -> queue: Payment Events`,
    description: 'Complete microservices architecture',
    isValid: true,
  },
};

export const D2TesterModal: React.FC<D2TesterModalProps> = ({
  open,
  onCancel,
}) => {
  const { theme } = useTheme();
  const [d2Code, setD2Code] = useState<string>(TEST_CASES.valid1.code);
  const [validating, setValidating] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [renderResult, setRenderResult] = useState<RenderResult | null>(null);
  const [serverStatus, setServerStatus] = useState<{ status: string; available: boolean } | null>(null);

  // Determine editor theme based on app theme
  const editorTheme = ['dark', 'proDark', 'modernGradientDark'].includes(theme) ? 'dark' : 'light';

  useEffect(() => {
    if (open) {
      checkServerStatus();
    }
  }, [open]);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('http://localhost:8003/api/v1/d2/health');
      const data = await response.json();
      setServerStatus({ status: data.status, available: data.d2_available });
    } catch (error) {
      setServerStatus({ status: 'offline', available: false });
    }
  };

  const loadTestCase = (caseKey: keyof typeof TEST_CASES) => {
    const testCase = TEST_CASES[caseKey];
    setD2Code(testCase.code);
    setValidationResult(null);
    setRenderResult(null);
    message.info(`Loaded: ${testCase.name}`);
  };

  const validateD2 = async () => {
    if (!d2Code.trim()) {
      message.error('Please enter some D2 code');
      return;
    }

    setValidating(true);
    setValidationResult(null);

    try {
      const response = await fetch('http://localhost:8003/api/v1/d2/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: d2Code }),
      });

      const data: ValidationResult = await response.json();
      setValidationResult(data);

      if (data.is_valid) {
        message.success('Valid D2 syntax!');
      } else {
        message.error('Invalid D2 syntax');
      }
    } catch (error) {
      message.error('Validation request failed');
      console.error(error);
    } finally {
      setValidating(false);
    }
  };

  const renderD2 = async () => {
    if (!d2Code.trim()) {
      message.error('Please enter some D2 code');
      return;
    }

    setRendering(true);
    setRenderResult(null);

    try {
      const response = await fetch('http://localhost:8003/api/v1/d2/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: d2Code,
          return_svg: true,
          save_to_file: false,
        }),
      });

      const data: RenderResult = await response.json();
      setRenderResult(data);

      if (data.success) {
        message.success(`Rendered in ${data.metadata.render_time.toFixed(2)}s`);
      } else {
        message.error('Rendering failed');
      }
    } catch (error) {
      message.error('Rendering request failed');
      console.error(error);
    } finally {
      setRendering(false);
    }
  };

  return (
    <Modal
      title={
        <div className="flex items-center justify-between">
          <span>D2 Diagram Tester</span>
          <div className="flex items-center gap-2">
            {serverStatus && (
              <div className="flex items-center gap-2 text-sm">
                <span
                  className="inline-block w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: serverStatus.status === 'healthy' ? '#52c41a' : '#ff4d4f',
                  }}
                />
                <span style={{ color: '#666' }}>
                  {serverStatus.status === 'healthy' ? 'Server Online' : 'Server Offline'}
                </span>
              </div>
            )}
            <Button size="small" icon={<ReloadOutlined />} onClick={checkServerStatus}>
              Refresh
            </Button>
          </div>
        </div>
      }
      open={open}
      onCancel={onCancel}
      width={1400}
      footer={null}
    >
      <div className="grid grid-cols-2 gap-4">
        {/* Left Panel - Code Editor */}
        <div className="flex flex-col gap-4">
          <div>
            <Title level={5}>D2 Code Editor</Title>
            <div style={{ height: '450px', border: '1px solid #d9d9d9', borderRadius: '4px', overflow: 'hidden' }}>
              <MonacoEditor
                value={d2Code}
                language="markdown"
                onChange={(value) => setD2Code(value || '')}
                height="100%"
                theme={editorTheme}
                showToolbar={false}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              type="default"
              icon={<CheckCircleOutlined />}
              onClick={validateD2}
              loading={validating}
            >
              Validate Only
            </Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={renderD2}
              loading={rendering}
              style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
            >
              Validate & Render
            </Button>
          </div>

          {/* Validation Result */}
          {validationResult && (
            <div
              className="p-4 rounded"
              style={{
                backgroundColor: validationResult.is_valid ? '#f6ffed' : '#fff2e8',
                border: `1px solid ${validationResult.is_valid ? '#b7eb8f' : '#ffbb96'}`,
              }}
            >
              <div className="flex items-center justify-between mb-2">
                <strong style={{ color: validationResult.is_valid ? '#52c41a' : '#fa8c16' }}>
                  {validationResult.is_valid ? '✅ Valid Syntax' : '❌ Invalid Syntax'}
                </strong>
              </div>

              {validationResult.error && (
                <pre
                  style={{
                    backgroundColor: '#fff',
                    padding: '8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    overflow: 'auto',
                    maxHeight: '150px',
                  }}
                >
                  {validationResult.error}
                </pre>
              )}

              {validationResult.is_valid && (
                <div className="mt-2">
                  <Text type="success">Code length: {validationResult.code_length} characters</Text>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Panel - Test Cases & Preview */}
        <div className="flex flex-col gap-4">
          <div>
            <Title level={5}>Test Cases</Title>
            <div className="flex flex-col gap-2" style={{ maxHeight: '250px', overflowY: 'auto' }}>
              {Object.entries(TEST_CASES).map(([key, testCase]) => (
                <div
                  key={key}
                  className="p-3 rounded cursor-pointer hover:bg-gray-50"
                  style={{
                    border: '1px solid #d9d9d9',
                    borderLeftWidth: '4px',
                    borderLeftColor: testCase.isValid ? '#52c41a' : '#ff4d4f',
                  }}
                  onClick={() => loadTestCase(key as keyof typeof TEST_CASES)}
                >
                  <div className="font-semibold">{testCase.isValid ? '✅' : '❌'} {testCase.name}</div>
                  <div className="text-sm text-gray-600">{testCase.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Rendered Diagram */}
          <div>
            <Title level={5}>Rendered Diagram</Title>
            <div
              className="p-4 rounded"
              style={{
                backgroundColor: '#fff',
                border: '1px solid #d9d9d9',
                minHeight: '300px',
                maxHeight: '500px',
                overflow: 'auto',
              }}
            >
              {renderResult?.success && renderResult.svg_content ? (
                <div
                  dangerouslySetInnerHTML={{ __html: renderResult.svg_content }}
                  style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}
                />
              ) : renderResult?.error ? (
                <div className="text-center text-gray-500">
                  <div className="mb-2" style={{ color: '#ff4d4f' }}>
                    ❌ Rendering failed
                  </div>
                  <pre
                    style={{
                      backgroundColor: '#fff2e8',
                      padding: '12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      textAlign: 'left',
                      overflow: 'auto',
                      maxHeight: '200px',
                    }}
                  >
                    {renderResult.error}
                  </pre>
                </div>
              ) : (
                <div className="text-center text-gray-400">
                  Click "Validate & Render" to see the diagram here
                </div>
              )}
            </div>

            {renderResult?.success && (
              <div className="mt-2 text-sm text-gray-600">
                <div>Render time: {renderResult.metadata.render_time.toFixed(2)}s</div>
                {renderResult.validation.is_valid && (
                  <div style={{ color: '#52c41a' }}>✓ Validation passed</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default D2TesterModal;
