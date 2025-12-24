import { Button, Col, Layout, message,Row, Select } from 'antd';
import React, { useEffect,useState } from 'react';

import ApiService from '../../services/api';
import type { Tab } from '../../types';
import FormEditor from './FormEditor';
import SubmittedFormsGrid from './SubmittedFormsGrid';

interface FormSystemViewProps {
  tab: Tab;
  onFormChange?: (formData: any) => void;
}

export const FormSystemView: React.FC<FormSystemViewProps> = ({ tab, onFormChange }) => {
  const [publishedForms, setPublishedForms] = useState<any[]>([]);
  const [selectedForm, setSelectedForm] = useState<any>(null);
  const [editingSubmission, setEditingSubmission] = useState<any>(null);
  const [mode, setMode] = useState<'list' | 'new' | 'edit' | 'view'>('list');

  useEffect(() => {
    loadPublishedForms();
  }, []);

  const loadPublishedForms = async () => {
    try {
        const response = await ApiService.get('/forms/published');
        if (response.data) {
            setPublishedForms(response.data);
        }
    } catch (e) {
        message.error("Failed to load published forms");
    }
  };

  const handleEdit = async (submission: any) => {
      // Need to find the original form definition to pass schema/uischema
      const form = publishedForms.find(f => f.form_id === submission.form_id);
      if (!form) {
          // Attempt to reload forms if missing, or handle error
           message.warning("Form definition not found for this submission");
           // Proceed anyway? The editor might fail to render the form tab but JSON works.
      }
      setSelectedForm(form);
      setEditingSubmission(submission);
      setMode('edit');
  };

  const handleView = (submission: any) => {
      const form = publishedForms.find(f => f.form_id === submission.form_id);
      setSelectedForm(form);
      setEditingSubmission(submission);
      setMode('view');
  }

  return (
    <Layout style={{ padding: '24px', background: '#fff', height: '100%', overflow: 'auto' }}>
      {mode === 'list' && (
        <>
          {/* New Form Section */}
          <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
            <Col span={18}>
              <Select
                placeholder="Select a published form to fill"
                style={{ width: '100%' }}
                size="large"
                value={selectedForm?.form_id}
                onChange={(formId) => {
                  const form = publishedForms.find(f => f.form_id === formId);
                  setSelectedForm(form);
                }}
              >
                {publishedForms.map(form => (
                  <Select.Option key={form.form_id} value={form.form_id}>
                    {form.form_name} ({form.form_type})
                  </Select.Option>
                ))}
              </Select>
            </Col>
            <Col span={6}>
              <Button
                type="primary"
                size="large"
                disabled={!selectedForm}
                onClick={() => setMode('new')}
                block
              >
                Fill New Form
              </Button>
            </Col>
          </Row>

          {/* Submitted Forms Grid */}
          <SubmittedFormsGrid
            onEdit={handleEdit}
            onView={handleView}
          />
        </>
      )}

      {(mode === 'new' || mode === 'edit' || mode === 'view') && (
        <FormEditor
          mode={mode}
          selectedForm={selectedForm}
          editingSubmission={editingSubmission}
          sessionId={tab.sessionId || 'unknown-session'}
          onSave={() => {
            setMode('list');
            setEditingSubmission(null);
            setSelectedForm(null);
          }}
          onCancel={() => {
            setMode('list');
            setEditingSubmission(null);
            setSelectedForm(null);
          }}
        />
      )}
    </Layout>
  );
};
