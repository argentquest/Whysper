import { ClockCircleOutlined, EditOutlined, FileAddOutlined } from '@ant-design/icons';
import { Button, Divider,Modal, Space, Timeline, Typography } from 'antd';
import React from 'react';

const { Text, Title } = Typography;

interface VersionHistoryModalProps {
  visible: boolean;
  onClose: () => void;
  versions: any[];
  onViewVersion: (version: any) => void;
}

const VersionHistoryModal: React.FC<VersionHistoryModalProps> = ({
  visible,
  onClose,
  versions,
  onViewVersion
}) => {
  return (
    <Modal
      title="Version History"
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose}>
          Close
        </Button>
      ]}
      width={700}
    >
      <div style={{ padding: '16px 0' }}>
        {versions.length === 0 ? (
          <Text type="secondary">No version history available</Text>
        ) : (
          <>
            <Title level={5}>
              Total Versions: {versions.length}
            </Title>
            <Divider />
            <Timeline>
              {versions.map((version, index) => (
                <Timeline.Item
                  key={version.submission_id}
                  dot={
                    index === 0 ? (
                      <FileAddOutlined style={{ fontSize: '16px' }} />
                    ) : (
                      <EditOutlined style={{ fontSize: '16px' }} />
                    )
                  }
                  color={index === versions.length - 1 ? 'green' : 'blue'}
                >
                  <div style={{ marginBottom: '16px' }}>
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div>
                        <Text strong>
                          {index === 0 ? 'Original Submission' : `Edit ${index}`}
                        </Text>
                        {index === versions.length - 1 && (
                          <Text type="success" style={{ marginLeft: '8px' }}>
                            (Current)
                          </Text>
                        )}
                      </div>
                      <div>
                        <ClockCircleOutlined style={{ marginRight: '8px' }} />
                        <Text type="secondary">
                          {new Date(version.submission_timestamp).toLocaleString()}
                        </Text>
                      </div>
                      <div>
                        <Text type="secondary">
                          Submission ID: {version.submission_id}
                        </Text>
                      </div>
                      <div>
                        <Text type="secondary">
                          Session: {version.session_id}
                        </Text>
                      </div>
                      <div>
                        <Button
                          size="small"
                          type="link"
                          onClick={() => {
                            onViewVersion(version);
                            onClose();
                          }}
                        >
                          View This Version
                        </Button>
                      </div>
                    </Space>
                  </div>
                </Timeline.Item>
              ))}
            </Timeline>
          </>
        )}
      </div>
    </Modal>
  );
};

export default VersionHistoryModal;
