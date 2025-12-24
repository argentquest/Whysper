import { EditOutlined, EyeOutlined } from '@ant-design/icons';
import { Button, Col,DatePicker, Input, message, Row, Select, Space, Table } from 'antd';
import React, { useEffect,useState } from 'react';

import ApiService from '../../services/api';

interface SubmittedFormsGridProps {
  onEdit: (submission: any) => void;
  onView: (submission: any) => void;
}

const SubmittedFormsGrid: React.FC<SubmittedFormsGridProps> = ({ onEdit, onView }) => {
  const [submissions, setSubmissions] = useState([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    formName: '',
    formType: '',
  });

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

    setFilteredSubmissions(result);
  }, [filters, submissions]);

  const uniqueFormTypes = Array.from(new Set(submissions.map((s: any) => s.form_type)));

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
        </Space>
      )
    }
  ];

  return (
    <div>
      {/* Filter Controls */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={8}>
          <Input
            placeholder="Filter by form name"
            value={filters.formName}
            onChange={(e) => setFilters({...filters, formName: e.target.value})}
          />
        </Col>
        <Col span={8}>
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
        <Col span={8}>
            <Button onClick={loadSubmissions}>Refresh</Button>
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
    </div>
  );
};

export default SubmittedFormsGrid;
