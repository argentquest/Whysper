/**
 * JsonPreview Component
 *
 * Renders JSON architecture data as a prettified, structured HTML display
 * similar to a rendered report - but using React components.
 */

import React from 'react';
import { Card, Tag, Descriptions, List, Typography, Divider } from 'antd';
import { DatabaseOutlined, LinkOutlined, InfoCircleOutlined, AppstoreOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface JsonPreviewProps {
  data: Record<string, any> | string;
}

const JsonPreview: React.FC<JsonPreviewProps> = ({ data }) => {
  // Parse data if it's a string
  let parsedData: Record<string, any> = {};

  if (typeof data === 'string') {
    try {
      parsedData = JSON.parse(data);
    } catch (e) {
      return (
        <div style={{ padding: '20px', textAlign: 'center', color: '#ff4d4f' }}>
          Invalid JSON format: {String(e)}
        </div>
      );
    }
  } else if (data && typeof data === 'object') {
    parsedData = data;
  }

  if (!parsedData || Object.keys(parsedData).length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
        No data to preview
      </div>
    );
  }

  // Render components section
  const renderComponents = (components: any[]) => {
    if (!components || components.length === 0) return null;

    return (
      <div style={{ marginBottom: '24px' }}>
        <Title level={5} style={{ color: '#1890ff', marginBottom: '12px' }}>
          <AppstoreOutlined /> Components ({components.length})
        </Title>
        <List
          grid={{ gutter: 12, xs: 1, sm: 1, md: 1, lg: 1, xl: 1, xxl: 1 }}
          dataSource={components}
          renderItem={(component: any, index: number) => (
            <List.Item>
              <Card
                size="small"
                style={{
                  backgroundColor: '#f0f5ff',
                  borderLeft: '4px solid #1890ff',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text strong style={{ fontSize: '14px' }}>
                    {component.name || component.id || `Component ${index + 1}`}
                  </Text>
                  {component.type && (
                    <Tag color="blue" style={{ fontSize: '11px' }}>
                      {component.type}
                    </Tag>
                  )}
                </div>
                {component.description && (
                  <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '8px' }}>
                    {component.description}
                  </Text>
                )}
                {component.properties && Object.keys(component.properties).length > 0 && (
                  <Descriptions
                    size="small"
                    column={1}
                    style={{ marginTop: '8px', fontSize: '11px' }}
                  >
                    {Object.entries(component.properties).map(([key, value]) => (
                      <Descriptions.Item key={key} label={key}>
                        {String(value)}
                      </Descriptions.Item>
                    ))}
                  </Descriptions>
                )}
              </Card>
            </List.Item>
          )}
        />
      </div>
    );
  };

  // Render connections section
  const renderConnections = (connections: any[]) => {
    if (!connections || connections.length === 0) return null;

    return (
      <div style={{ marginBottom: '24px' }}>
        <Title level={5} style={{ color: '#52c41a', marginBottom: '12px' }}>
          <LinkOutlined /> Connections ({connections.length})
        </Title>
        <List
          dataSource={connections}
          renderItem={(connection: any, index: number) => (
            <List.Item style={{ padding: '8px 0' }}>
              <Card
                size="small"
                style={{
                  width: '100%',
                  backgroundColor: '#f6ffed',
                  borderLeft: '4px solid #52c41a',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                  <Text code>{connection.from || connection.source || 'Source'}</Text>
                  <Text type="secondary">→</Text>
                  <Text code>{connection.to || connection.target || 'Target'}</Text>
                  {connection.label && (
                    <Tag color="green" style={{ fontSize: '10px', marginLeft: 'auto' }}>
                      {connection.label}
                    </Tag>
                  )}
                </div>
                {connection.description && (
                  <Text type="secondary" style={{ fontSize: '11px', display: 'block', marginTop: '4px' }}>
                    {connection.description}
                  </Text>
                )}
              </Card>
            </List.Item>
          )}
        />
      </div>
    );
  };

  // Render metadata section
  const renderMetadata = (metadata: Record<string, any>) => {
    if (!metadata || Object.keys(metadata).length === 0) return null;

    return (
      <div style={{ marginBottom: '24px' }}>
        <Title level={5} style={{ color: '#fa8c16', marginBottom: '12px' }}>
          <InfoCircleOutlined /> Metadata
        </Title>
        <Card size="small" style={{ backgroundColor: '#fff7e6', borderLeft: '4px solid #fa8c16' }}>
          <Descriptions size="small" column={1}>
            {Object.entries(metadata).map(([key, value]) => (
              <Descriptions.Item key={key} label={<Text strong>{key}</Text>}>
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </Descriptions.Item>
            ))}
          </Descriptions>
        </Card>
      </div>
    );
  };

  // Main render logic
  return (
    <div
      style={{
        height: '100%',
        overflow: 'auto',
        padding: '16px',
        backgroundColor: '#fafafa',
        border: '1px solid #d9d9d9',
        borderRadius: '4px',
      }}
    >
      <Title level={4} style={{ marginTop: 0, color: '#3c4043' }}>
        <DatabaseOutlined /> System Architecture
      </Title>
      <Divider style={{ margin: '12px 0' }} />

      {/* Render system name/title if available */}
      {(parsedData.name || parsedData.title || parsedData.system_name) && (
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ fontSize: '16px', color: '#1890ff' }}>
            {parsedData.name || parsedData.title || parsedData.system_name}
          </Text>
        </div>
      )}

      {/* Render description if available */}
      {parsedData.description && (
        <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#fff', borderRadius: '4px' }}>
          <Text type="secondary" style={{ fontSize: '13px', fontStyle: 'italic' }}>
            {parsedData.description}
          </Text>
        </div>
      )}

      {/* Render components */}
      {renderComponents(parsedData.components || parsedData.nodes || parsedData.elements)}

      {/* Render connections */}
      {renderConnections(parsedData.connections || parsedData.edges || parsedData.relationships || parsedData.links)}

      {/* Render metadata */}
      {renderMetadata(parsedData.metadata || parsedData.properties || parsedData.config)}

      {/* Render any other top-level properties */}
      {Object.entries(parsedData).map(([key, value]) => {
        // Skip already rendered properties
        if (['name', 'title', 'system_name', 'description', 'components', 'nodes', 'elements',
             'connections', 'edges', 'relationships', 'links', 'metadata', 'properties', 'config'].includes(key)) {
          return null;
        }

        // Render arrays as lists
        if (Array.isArray(value) && value.length > 0) {
          return (
            <div key={key} style={{ marginBottom: '24px' }}>
              <Title level={5} style={{ color: '#722ed1', marginBottom: '12px', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')} ({value.length})
              </Title>
              <List
                size="small"
                bordered
                dataSource={value}
                renderItem={(item: any, index: number) => (
                  <List.Item style={{ fontSize: '12px' }}>
                    {typeof item === 'object' ? JSON.stringify(item) : String(item)}
                  </List.Item>
                )}
              />
            </div>
          );
        }

        // Render objects as descriptions
        if (typeof value === 'object' && value !== null && Object.keys(value).length > 0) {
          return (
            <div key={key} style={{ marginBottom: '24px' }}>
              <Title level={5} style={{ color: '#722ed1', marginBottom: '12px', textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}
              </Title>
              <Card size="small" style={{ backgroundColor: '#f9f0ff', borderLeft: '4px solid #722ed1' }}>
                <Descriptions size="small" column={1}>
                  {Object.entries(value).map(([subKey, subValue]) => (
                    <Descriptions.Item key={subKey} label={<Text strong>{subKey}</Text>}>
                      {typeof subValue === 'object' ? JSON.stringify(subValue) : String(subValue)}
                    </Descriptions.Item>
                  ))}
                </Descriptions>
              </Card>
            </div>
          );
        }

        // Render primitives
        return (
          <div key={key} style={{ marginBottom: '12px' }}>
            <Text strong>{key.replace(/_/g, ' ')}: </Text>
            <Text>{String(value)}</Text>
          </div>
        );
      })}
    </div>
  );
};

export default JsonPreview;
