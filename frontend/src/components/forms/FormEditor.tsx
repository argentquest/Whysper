import { CloseOutlined,SaveOutlined } from '@ant-design/icons';
import Editor from '@monaco-editor/react';
import { Theme as AntDTheme } from '@rjsf/antd';
import { withTheme } from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { Button, message,Space, Tabs } from 'antd';
import React, { useEffect,useState } from 'react';

import ApiService from '../../services/api';

const AntDForm = withTheme(AntDTheme);

interface FormEditorProps {
  mode: 'new' | 'edit' | 'view';
  selectedForm: any;
  editingSubmission?: any;
  onSave: () => void;
  onCancel: () => void;
  sessionId: string;
}

const FormEditor: React.FC<FormEditorProps> = ({
  mode,
  selectedForm,
  editingSubmission,
  onSave,
  onCancel,
  sessionId
}) => {
  const [formData, setFormData] = useState({});
  const [formDataText, setFormDataText] = useState('{}');
  const [metadata, setMetadata] = useState({});
  const [activeTab, setActiveTab] = useState('form');
  const [formSchema, setFormSchema] = useState<any>(null);
  const [formUiSchema, setFormUiSchema] = useState<any>(null);

  useEffect(() => {
    if (mode === 'edit' || mode === 'view') {
        // Load submission data (includes schema if stored)
        const loadSubmission = async () => {
            if (editingSubmission?.submission_id) {
                try {
                    const response = await ApiService.get(`/forms/submissions/${editingSubmission.submission_id}`);
                    if (response.data) {
                        setFormData(response.data.form_data);
                        setFormDataText(JSON.stringify(response.data.form_data, null, 2));
                        setMetadata(response.data.metadata);

                        // Use stored schema if available (for edit resilience)
                        if (response.data.schema) {
                            setFormSchema(response.data.schema);
                        }
                        if (response.data.ui_schema) {
                            setFormUiSchema(response.data.ui_schema);
                        }
                    }
                } catch (e) {
                    message.error("Failed to load submission data");
                }
            }
        };
        loadSubmission();
    } else if (mode === 'new') {
        // Initialize with default form data if available
        if (selectedForm?.form_data) {
             setFormData(selectedForm.form_data);
             setFormDataText(JSON.stringify(selectedForm.form_data, null, 2));
        }
        // Set schema from selected form
        if (selectedForm?.schema) {
            setFormSchema(selectedForm.schema);
        }
        if (selectedForm?.ui_schema) {
            setFormUiSchema(selectedForm.ui_schema);
        }
    }
  }, [mode, editingSubmission, selectedForm]);

  const handleSave = async () => {
    try {
      // Validate JSON
      const parsedData = JSON.parse(formDataText);

      const payload = {
          form_id: selectedForm?.form_id || editingSubmission?.form_id,
          form_data: parsedData,
          session_id: sessionId
      };

      if (mode === 'edit') {
           await ApiService.put(`/forms/edit/${editingSubmission.submission_id}`, payload);
      } else {
           await ApiService.post('/forms/submit', payload);
      }

      message.success('Form saved successfully');
      onSave();
    } catch (error: any) {
      console.error(error);
      message.error('Error saving form: ' + (error.message || 'Unknown error'));
    }
  };

  const tabItems = [
    {
      key: 'form',
      label: 'Form',
      children: (
        <div style={{ padding: '16px', maxWidth: '100%', overflow: 'auto' }}>
          {(formSchema || selectedForm) ? (
            <div style={{ maxWidth: '100%' }}>
              <AntDForm
                schema={formSchema || selectedForm?.schema || {}}
                uiSchema={formUiSchema || selectedForm?.ui_schema || {}}
                formData={formData}
                validator={validator}
                onChange={({ formData: newData }) => {
                  setFormData(newData || {});
                  setFormDataText(JSON.stringify(newData || {}, null, 2));
                }}
                disabled={mode === 'view'}
                liveValidate
              >
                <div /> {/* Remove default submit button */}
              </AntDForm>
            </div>
          ) : <div>Loading form definition...</div>}
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
              if (value && mode !== 'view') {
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
              readOnly: mode === 'view',
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
          <pre style={{
            background: '#f5f5f5',
            padding: '16px',
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            {JSON.stringify(metadata, null, 2)}
          </pre>
        </div>
      )
    }
  ];

  return (
    <div style={{ maxWidth: '100%', overflow: 'hidden' }}>
      {/* Header with actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        padding: '16px',
        background: '#fafafa',
        borderRadius: '4px',
        flexWrap: 'wrap',
        gap: '8px'
      }}>
        <h3>{mode === 'new' ? 'Fill New Form' : mode === 'edit' ? 'Edit Form' : 'View Form'}</h3>
        <Space>
          {mode !== 'view' && (
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
            >
              Save
            </Button>
          )}
          <Button
            icon={<CloseOutlined />}
            onClick={onCancel}
          >
            Close
          </Button>
        </Space>
      </div>

      {/* Three-tab interface */}
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={tabItems}
        size="large"
      />
    </div>
  );
};

export default FormEditor;
