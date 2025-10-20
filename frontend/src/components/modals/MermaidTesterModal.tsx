import React, { useState, useEffect } from 'react';
import { Button, message, Tabs, Typography } from 'antd';
import { PlayCircleOutlined, CheckCircleOutlined, EditOutlined, ReloadOutlined } from '@ant-design/icons';
import { Modal } from '../common/Modal';
import { MonacoEditor } from '../editor/MonacoEditor';
import { useTheme } from '../../themes';
import ApiService from '../../services/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface MermaidTesterModalProps {
  open: boolean;
  onCancel: () => void;
}

interface ValidationResult {
  is_valid: boolean;
  error: string | null;
  code_length: number;
  auto_fixed: boolean;
  fixed_code: string | null;
  fix_message: string | null;
}

interface RenderResult {
  success: boolean;
  svg_content: string | null;
  validation: {
    is_valid: boolean;
    error: string | null;
    auto_fixed?: boolean;
  };
  metadata: {
    render_time: number;
    timestamp: string;
  };
  error: string | null;
}

const TEST_CASES = {
  valid1: {
    name: 'Valid Flowchart',
    code: `flowchart TD
    A[Start] --> B{Is it valid?}
    B -->|Yes| C[Render]
    B -->|No| D[Fix Syntax]
    D --> B
    C --> E[End]`,
    description: 'Basic flowchart with decision nodes',
    isValid: true,
  },
  valid2: {
    name: 'Valid Sequence Diagram',
    code: `sequenceDiagram
    participant User
    participant API
    participant Database

    User->>API: Request data
    API->>Database: Query
    Database-->>API: Results
    API-->>User: Response`,
    description: 'Simple sequence diagram with participants',
    isValid: true,
  },
  invalid1: {
    name: 'Missing Diagram Type',
    code: `A[Start] --> B{Decision}
    B -->|Yes| C[Success]
    B -->|No| D[Failure]`,
    description: 'Should be auto-fixed by adding "flowchart TD"',
    isValid: false,
  },
  invalid2: {
    name: 'Reserved Keyword Error',
    code: `flowchart TD
    A[Start] --> B[Process]
    B --> end
    end --> C[Done]`,
    description: 'Using "end" as a node ID (reserved word)',
    isValid: false,
  },
  complex1: {
    name: 'Complex Architecture',
    code: `flowchart TB
    subgraph "Frontend"
        UI[User Interface]
        Router[React Router]
    end

    subgraph "Backend"
        API[FastAPI Server]
        Auth[Authentication]
        DB[Database]
    end

    UI --> Router
    Router --> API
    API --> Auth
    API --> DB
    Auth --> DB`,
    description: 'Multi-tier system architecture',
    isValid: true,
  },
};

export const MermaidTesterModal: React.FC<MermaidTesterModalProps> = ({
  open,
  onCancel,
}) => {
  const { theme } = useTheme();
  const [mermaidCode, setMermaidCode] = useState<string>(TEST_CASES.valid1.code);
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
      const response = await fetch('http://localhost:8003/api/v1/mermaid/health');
      const data = await response.json();
      setServerStatus({ status: data.status, available: data.mermaid_available });
    } catch (error) {
      setServerStatus({ status: 'offline', available: false });
    }
  };

  const loadTestCase = (caseKey: keyof typeof TEST_CASES) => {
    const testCase = TEST_CASES[caseKey];
    setMermaidCode(testCase.code);
    setValidationResult(null);
    setRenderResult(null);
    message.info(`Loaded: ${testCase.name}`);
  };

  const validateMermaid = async (autoFix: boolean = false) => {
    if (!mermaidCode.trim()) {
      message.error('Please enter some Mermaid code');
      return;
    }

    setValidating(true);
    setValidationResult(null);

    try {
      const response = await fetch('http://localhost:8003/api/v1/mermaid/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: mermaidCode, auto_fix: autoFix }),
      });

      const data: ValidationResult = await response.json();
      setValidationResult(data);

      if (data.is_valid) {
        message.success(data.auto_fixed ? 'Auto-fix successful!' : 'Valid Mermaid syntax!');
      } else {
        message.error('Invalid Mermaid syntax');
      }
    } catch (error) {
      message.error('Validation request failed');
      console.error(error);
    } finally {
      setValidating(false);
    }
  };

  const renderMermaid = async () => {
    if (!mermaidCode.trim()) {
      message.error('Please enter some Mermaid code');
      return;
    }

    setRendering(true);
    setRenderResult(null);

    try {
      const response = await fetch('http://localhost:8003/api/v1/mermaid/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: mermaidCode,
          return_svg: true,
          output_format: 'svg',
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

  const applyFixedCode = () => {
    if (validationResult?.fixed_code) {
      setMermaidCode(validationResult.fixed_code);
      setValidationResult(null);
      message.success('Applied fixed code');
    }
  };

  return (
    <Modal
      title={
        <div className="flex items-center justify-between">
          <span>Mermaid Diagram Tester</span>
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
            <Title level={5}>Mermaid Code Editor</Title>
            <div style={{ height: '450px', border: '1px solid #d9d9d9', borderRadius: '4px', overflow: 'hidden' }}>
              <MonacoEditor
                value={mermaidCode}
                language="markdown"
                onChange={(value) => setMermaidCode(value || '')}
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
              onClick={() => validateMermaid(false)}
              loading={validating}
            >
              Validate Only
            </Button>
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => validateMermaid(true)}
              loading={validating}
            >
              Validate & Auto-Fix
            </Button>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={renderMermaid}
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
                {validationResult.auto_fixed && (
                  <Button size="small" type="primary" onClick={applyFixedCode}>
                    Apply Fixed Code
                  </Button>
                )}
              </div>

              {validationResult.auto_fixed && (
                <div className="mb-2">
                  <Text type="success">{validationResult.fix_message}</Text>
                </div>
              )}

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

              {validationResult.fixed_code && (
                <details style={{ marginTop: '8px' }}>
                  <summary style={{ cursor: 'pointer', color: '#1890ff' }}>
                    View Fixed Code
                  </summary>
                  <pre
                    style={{
                      backgroundColor: '#fff',
                      padding: '8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      marginTop: '8px',
                    }}
                  >
                    {validationResult.fixed_code}
                  </pre>
                </details>
              )}
            </div>
          )}
        </div>

        {/* Right Panel - Test Cases & Preview */}
        <div className="flex flex-col gap-4">
          <div>
            <Title level={5}>Test Cases</Title>
            <div className="flex flex-col gap-2">
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
                {renderResult.validation.auto_fixed && (
                  <div style={{ color: '#52c41a' }}>✓ Code was auto-fixed before rendering</div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default MermaidTesterModal;
