import React from 'react';
import { Modal, Row, Col, Card, Typography, Button, Space } from 'antd';
import { CheckOutlined } from '@ant-design/icons';
import { getThemeList, type ThemeKey } from '../../themes/antd-themes';
import { useTheme } from '../../themes/useTheme';

const { Title, Text } = Typography;

interface ThemePickerModalProps {
  open: boolean;
  onCancel: () => void;
}

export const ThemePickerModal: React.FC<ThemePickerModalProps> = ({
  open,
  onCancel,
}) => {
  const { theme: currentTheme, setTheme } = useTheme();
  const themes = getThemeList();

  const handleThemeSelect = (themeKey: ThemeKey) => {
    setTheme(themeKey);
  };

  return (
    <Modal
      title={
        <Space>
          <span>🎨</span>
          <Title level={4} style={{ margin: 0 }}>
            Choose Theme
          </Title>
        </Space>
      }
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="close" onClick={onCancel}>
          Close
        </Button>,
      ]}
      width={800}
      style={{ top: 20 }}
    >
      <div style={{ marginBottom: 16 }}>
        <Text type="secondary">
          Choose from our collection of professional themes inspired by Ant Design Pro
        </Text>
      </div>

      <Row gutter={[16, 16]}>
        {themes.map((themeItem) => (
          <Col xs={24} sm={12} md={8} key={themeItem.key}>
            <Card
              hoverable
              style={{
                border: currentTheme === themeItem.key ? `2px solid ${themeItem.primary}` : '1px solid #d9d9d9',
                position: 'relative',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: currentTheme === themeItem.key 
                  ? `0 4px 12px ${themeItem.primary}20` 
                  : undefined,
              }}
              onClick={() => handleThemeSelect(themeItem.key)}
              bodyStyle={{ padding: 16 }}
            >
              {/* Theme Preview */}
              <div style={{ marginBottom: 12 }}>
                <div
                  style={{
                    height: 60,
                    borderRadius: 6,
                    background: `linear-gradient(135deg, ${themeItem.primary} 0%, ${themeItem.primary}80 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: 18,
                    fontWeight: 'bold',
                  }}
                >
                  {themeItem.name.charAt(0)}
                </div>
              </div>

              {/* Theme Info */}
              <div style={{ textAlign: 'center' }}>
                <Title level={5} style={{ margin: '0 0 4px 0' }}>
                  {themeItem.name}
                </Title>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {themeItem.primary}
                </Text>
              </div>

              {/* Selected Indicator */}
              {currentTheme === themeItem.key && (
                <div
                  style={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    backgroundColor: themeItem.primary,
                    borderRadius: '50%',
                    width: 24,
                    height: 24,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CheckOutlined style={{ color: 'white', fontSize: 12 }} />
                </div>
              )}

              {/* Color Swatch */}
              <div style={{ marginTop: 8, textAlign: 'center' }}>
                <div
                  style={{
                    display: 'inline-block',
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    backgroundColor: themeItem.primary,
                    border: '2px solid #f0f0f0',
                  }}
                />
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <div style={{ marginTop: 24, padding: 16, backgroundColor: '#f9f9f9', borderRadius: 6 }}>
        <Text strong>💡 Pro Tip:</Text>
        <br />
        <Text type="secondary">
          Your theme preference is automatically saved and will persist across sessions. 
          Each theme includes carefully crafted color schemes and component styling optimized for the best user experience.
        </Text>
      </div>
    </Modal>
  );
};

export default ThemePickerModal;