import { DownloadOutlined, EditOutlined, EyeOutlined, HistoryOutlined } from '@ant-design/icons';
import { Button, Col, DatePicker, Dropdown, Input, Menu,message, Row, Select, Space, Table } from 'antd';
import type { Dayjs } from 'dayjs';
import React, { useEffect, useState } from 'react';

import ApiService from '../../services/api';
import VersionHistoryModal from './VersionHistoryModal';

const { RangePicker } = DatePicker;

interface SubmittedFormsGridProps {
  onEdit: (submission: any) => void;
  onView: (submission: any) => void;
}

const SubmittedFormsGrid: React.FC<SubmittedFormsGridProps> = ({ onEdit, onView }) => {
  const [submissions, setSubmissions] = useState([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<{
    formName: string;
    formType: string;
    dateRange: [Dayjs, Dayjs] | null;
  }>({
    formName: '',
    formType: '',
    dateRange: null,
  });
  const [versionHistoryVisible, setVersionHistoryVisible] = useState(false);
  const [versionHistory, setVersionHistory] = useState([]);

  const loadSubmissions = async () => {
    setLoading(true);
    try {
      const response = await ApiService.get('/forms/submissions');
      if (response.data) {
        setSubmissions(response.data);
        setFilteredSubmissions(response.data);
      }
    } catch (error) {
      console.error('Error loading submissions:', error);
      message.error('Failed to load submissions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, []);

  useEffect(() => {
    let result = submissions;

    if (filters.formName) {
      result = result.filter((s: any) =>
        s.form_name.toLowerCase().includes(filters.formName.toLowerCase())
      );
    }

    if (filters.formType) {
      result = result.filter((s: any) => s.form_type === filters.formType);
    }

    if (filters.dateRange) {
      const [startDate, endDate] = filters.dateRange;
      result = result.filter((s: any) => {
        const submissionDate = new Date(s.submission_timestamp);
        return submissionDate >= startDate.toDate() && submissionDate <= endDate.toDate();
      });
    }

    setFilteredSubmissions(result);
  }, [filters, submissions]);

  const uniqueFormTypes = Array.from(new Set(submissions.map((s: any) => s.form_type)));

  const handleShowVersionHistory = async (record: any) => {
    try {
      const response = await ApiService.get(`/forms/submissions/history/${record.original_submission_id || record.submission_id}`);
      if (response.data) {
        setVersionHistory(response.data);
        setVersionHistoryVisible(true);
      }
    } catch (error) {
      message.error('Failed to load version history');
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (filteredSubmissions.length === 0) {
      message.warning('No submissions to export');
      return;
    }

    try {
      if (format === 'json') {
        const dataStr = JSON.stringify(filteredSubmissions, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `form-submissions-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        message.success('Exported to JSON successfully');
      } else if (format === 'csv') {
        // Convert to CSV
        if (filteredSubmissions.length === 0) return;

        const headers = ['Submission ID', 'Form Name', 'Form Type', 'Version', 'Submission Date', 'Is Edited', 'Original Submission ID'];
        const rows = filteredSubmissions.map((s: any) => [
          s.submission_id,
          s.form_name,
          s.form_type,
          s.version,
          new Date(s.submission_timestamp).toLocaleString(),
          s.is_edited ? 'Yes' : 'No',
          s.original_submission_id || ''
        ]);

        const csvContent = [
          headers.join(','),
          ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');

        const dataBlob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `form-submissions-${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
        URL.revokeObjectURL(url);
        message.success('Exported to CSV successfully');
      }
    } catch (error) {
      message.error('Failed to export submissions');
    }
  };

  const exportMenu = (
    <Menu
      onClick={({ key }) => handleExport(key as 'json' | 'csv')}
      items={[
        { key: 'json', label: 'Export as JSON' },
        { key: 'csv', label: 'Export as CSV' }
      ]}
    />
  );

  const columns = [
    {
      title: 'Form Name',
      dataIndex: 'form_name',
      key: 'form_name',
      sorter: (a: any, b: any) => a.form_name.localeCompare(b.form_name),
    },
    {
      title: 'Form Type',
      dataIndex: 'form_type',
      key: 'form_type',
      sorter: (a: any, b: any) => a.form_type.localeCompare(b.form_type),
    },
    {
      title: 'Submission Date',
      dataIndex: 'submission_timestamp',
      key: 'submission_date',
      sorter: (a: any, b: any) => new Date(a.submission_timestamp).getTime() - new Date(b.submission_timestamp).getTime(),
      render: (text: string) => new Date(text).toLocaleString()
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version'
    },
    {
      title: 'Edited',
      dataIndex: 'is_edited',
      key: 'is_edited',
      render: (isEdited: boolean) => (isEdited ? 'Yes' : 'No')
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space>
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => onView(record)}
          >
            View
          </Button>
          <Button
            icon={<EditOutlined />}
            type="primary"
            size="small"
            onClick={() => onEdit(record)}
          >
            Edit
          </Button>
          {record.is_edited && (
            <Button
              icon={<HistoryOutlined />}
              size="small"
              onClick={() => handleShowVersionHistory(record)}
            >
              History
            </Button>
          )}
        </Space>
      )
    }
  ];

  return (
    <div>
      {/* Filter Controls */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={6}>
          <Input
            placeholder="Filter by form name"
            value={filters.formName}
            onChange={(e) => setFilters({...filters, formName: e.target.value})}
          />
        </Col>
        <Col span={6}>
          <Select
            placeholder="Filter by form type"
            style={{ width: '100%' }}
            value={filters.formType || undefined}
            onChange={(value) => setFilters({...filters, formType: value})}
            allowClear
          >
            {uniqueFormTypes.map((type: any) => (
               <Select.Option key={type} value={type}>{type}</Select.Option>
            ))}
          </Select>
        </Col>
        <Col span={6}>
          <RangePicker
            style={{ width: '100%' }}
            value={filters.dateRange}
            onChange={(dates) => setFilters({...filters, dateRange: dates as [Dayjs, Dayjs] | null})}
            placeholder={['Start Date', 'End Date']}
          />
        </Col>
        <Col span={6}>
          <Space>
            <Button onClick={loadSubmissions}>Refresh</Button>
            <Dropdown overlay={exportMenu} trigger={['click']}>
              <Button icon={<DownloadOutlined />}>
                Export
              </Button>
            </Dropdown>
          </Space>
        </Col>
      </Row>

      {/* Data Table */}
      <Table
        columns={columns}
        dataSource={filteredSubmissions}
        rowKey="submission_id"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
        loading={loading}
      />

      {/* Version History Modal */}
      <VersionHistoryModal
        visible={versionHistoryVisible}
        onClose={() => setVersionHistoryVisible(false)}
        versions={versionHistory}
        onViewVersion={onView}
      />
    </div>
  );
};

export default SubmittedFormsGrid;
