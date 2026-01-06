import { SaveOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { Theme as AntDTheme } from '@rjsf/antd';
import { withTheme } from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { Button, message, Modal, Select, Space, Tabs } from 'antd';
import React, { useEffect, useState } from 'react';

import ApiService from '../../services/api';
import DiagramApi from '../../services/diagram/diagramApi';

const AntDForm = withTheme(AntDTheme);

interface FormRendererProps {
  visible: boolean;
  onClose: () => void;
  onSubmit: (formData: any, formMetadata: any, submissionId?: string) => void;
  sessionId: string;
  title?: string;
  formId?: string | null; // Pre-selected form ID
}

const FormRenderer: React.FC<FormRendererProps> = ({
  visible,
  onClose,
  onSubmit,
  sessionId,
  title = 'Fill Form',
  formId = null
}) => {
  const [publishedForms, setPublishedForms] = useState<any[]>([]);
  const [selectedFormId, setSelectedFormId] = useState<string | null>(null);
  const [selectedForm, setSelectedForm] = useState<any>(null);
  const [formData, setFormData] = useState({});
  const [formDataText, setFormDataText] = useState('{}');
  const [activeTab, setActiveTab] = useState('form');
  const [saving, setSaving] = useState(false);

  // Load published forms when modal opens
  useEffect(() => {
    if (visible) {
      loadPublishedForms();
    }
  }, [visible]);

  // Auto-select form when formId prop is provided
  useEffect(() => {
    if (visible && formId && publishedForms.length > 0) {
      const form = publishedForms.find(f => f.form_id === formId);
      if (form) {
        setSelectedFormId(formId);
        setSelectedForm(form);
      }
    }
  }, [visible, formId, publishedForms]);

  // Reset form when selected form changes
  useEffect(() => {
    if (selectedForm) {
      const initialData = selectedForm.form_data || {};
      setFormData(initialData);
      setFormDataText(JSON.stringify(initialData, null, 2));
      setActiveTab('form'); // Reset to form tab
    }
  }, [selectedForm]);

  const loadPublishedForms = async () => {
    try {
      const response = await ApiService.get('/forms/published');
      if (response.data) {
        setPublishedForms(response.data);
      }
    } catch (error) {
      console.error('Failed to load published forms:', error);
      message.error('Failed to load published forms');
    }
  };

  const handleFormSelect = (formId: string) => {
    setSelectedFormId(formId);
    const form = publishedForms.find(f => f.form_id === formId);
    setSelectedForm(form);
  };

  const handleSave = async () => {
    if (!selectedForm) {
      message.error('Please select a form');
      return;
    }

    try {
      setSaving(true);

      // Validate JSON
      const parsedData = JSON.parse(formDataText);

      const payload = {
        form_id: selectedForm.form_id,
        form_data: parsedData,
        session_id: sessionId
      };

      // Save to backend
      const submitResponse = await ApiService.post('/forms/submit', payload);
      const submissionId = submitResponse.data.submission_id;

      message.success('Form saved successfully');

      // If being used in diagram wizard (not temp session), add form data to diagram session
      const isInDiagramWizard = sessionId && sessionId !== 'temp-session';
      if (isInDiagramWizard) {
        try {
          await DiagramApi.addFormDataToSession(sessionId, submissionId);
          message.success('Form data added to diagram session');
        } catch (err) {
          console.error('Failed to add form data to diagram session:', err);
          message.warning('Form saved but could not add to diagram session');
        }
      }

      // Prepare metadata for callback
      const formMetadata = {
        form_name: selectedForm.form_name,
        form_type: selectedForm.form_type,
        version: selectedForm.version,
        form_description: selectedForm.form_description
      };

      // Call parent callback with form data, metadata, and submission ID
      onSubmit(parsedData, formMetadata, submissionId);

      // Reset and close
      handleClose();
    } catch (error: any) {
      console.error(error);
      message.error('Error saving form: ' + (error.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    // Reset state
    setSelectedFormId(null);
    setSelectedForm(null);
    setFormData({});
    setFormDataText('{}');
    setActiveTab('form');
    onClose();
  };

  const tabItems = [
    {
      key: 'form',
      label: 'Form',
      children: (
        <div style={{ padding: '16px 24px 16px 16px', width: '100%', overflowY: 'auto', overflowX: 'hidden', minHeight: '400px' }}>
          {selectedForm ? (
            <div className="rjsf" style={{ width: '100%', maxWidth: '100%', wordWrap: 'break-word' }}>
              <AntDForm
                schema={selectedForm.schema || {}}
                uiSchema={(selectedForm.ui_schema || {}) as any}
                formData={formData}
                validator={validator as any}
                onChange={({ formData: newData }) => {
                  setFormData(newData || {});
                  setFormDataText(JSON.stringify(newData || {}, null, 2));
                }}
                liveValidate
              >
                <div /> {/* Remove default submit button */}
              </AntDForm>
            </div>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#999'
            }}>
              Please select a form from the dropdown above
            </div>
          )}
        </div>
      )
    },
    {
      key: 'json',
      label: 'Form JSON',
      children: (
        <div style={{ padding: '16px' }}>
          <Editor
            height="500px"
            language="json"
            value={formDataText}
            onChange={(value) => {
              if (value) {
                setFormDataText(value);
                try {
                  const parsed = JSON.parse(value);
                  setFormData(parsed);
                } catch (error) {
                  // Invalid JSON, don't update formData
                }
              }
            }}
            options={{
              minimap: { enabled: false },
              fontSize: 14
            }}
          />
        </div>
      )
    },
    {
      key: 'metadata',
      label: 'Metadata',
      children: (
        <div style={{ padding: '16px' }}>
          {selectedForm ? (
            <pre style={{
              background: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              fontSize: '14px'
            }}>
              {JSON.stringify({
                form_name: selectedForm.form_name,
                form_type: selectedForm.form_type,
                form_description: selectedForm.form_description,
                version: selectedForm.version
              }, null, 2)}
            </pre>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#999'
            }}>
              No form selected
            </div>
          )}
        </div>
      )
    }
  ];

  return (
    <Modal
      title={title}
      open={visible}
      onCancel={handleClose}
      width="80vw"
      style={{ top: '10vh' }}
      bodyStyle={{ height: '70vh', overflowY: 'auto', overflowX: 'hidden' }}
      footer={
        <Space>
          <Button onClick={handleClose}>
            Cancel
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={saving}
            disabled={!selectedForm}
          >
            Save
          </Button>
        </Space>
      }
    >
      {/* Form Selector Dropdown - Only show if no formId provided */}
      {!formId && (
        <div style={{ marginBottom: '16px' }}>
          <Select
            placeholder="Select a form to fill"
            style={{ width: '100%' }}
            size="large"
            value={selectedFormId}
            onChange={handleFormSelect}
            allowClear
            onClear={() => {
              setSelectedFormId(null);
              setSelectedForm(null);
            }}
          >
            {publishedForms.map(form => (
              <Select.Option key={form.form_id} value={form.form_id}>
                {form.form_name} ({form.form_type}) - v{form.version || '1.0'}
              </Select.Option>
            ))}
          </Select>
        </div>
      )}

      {/* Three-tab interface */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        size="large"
      />
    </Modal>
  );
};

export default FormRenderer;