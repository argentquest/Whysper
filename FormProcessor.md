# Form Processor System - Implementation Plan

## Feature Overview
Complete form system with admin publishing capabilities and end-user form management including a tabbed form editor with version control.

## System Architecture

### Admin Functions (Playground Framework)
- Create/design forms using JSON Schema + UI Schema
- Publish forms to backend `forms/` folder
- Manage form definitions and versions

### End User Functions (Tab System)
- Select published forms from dropdown
- Fill out forms using three-tab editor interface
- Submit and edit forms with version control
- Browse all submitted form data
- All data saves to `UserFormData/` folder

## Phase 1: Admin Form Publishing (Playground Extension) - 1-2 days

### 1.1 Extend RJSFPlayground Component
**File**: `frontend/src/pages/RJSFPlayground.tsx`

**New Features to Add**:
- Form metadata input section:
  - Form Name (string)
  - Form Description (text area)
  - Form Type (string)
  - Version (string, default "1.0")
- "Publish Form" button with validation
- Success/error messaging for publish operations
- Maintain existing schema/UI schema/form data editors

**UI Layout Enhancement**:
```tsx
// Add metadata section above existing editors
<div>
  <Title level={4}>Form Information</Title>
  <Form layout="vertical">
    <Form.Item label="Form Name" required>
      <Input placeholder="Contact Form" />
    </Form.Item>
    <Form.Item label="Form Description">
      <TextArea placeholder="Basic contact information collection" />
    </Form.Item>
    <Form.Item label="Form Type" required>
      <Input placeholder="contact" />
    </Form.Item>
    <Form.Item label="Version">
      <Input placeholder="1.0" defaultValue="1.0" />
    </Form.Item>
  </Form>
  <Button type="primary" size="large" onClick={handlePublishForm}>
    Publish Form
  </Button>
</div>
```

### 1.2 Backend Form Publishing API
**File**: `backend/app/routers/forms.py` (new)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/forms", tags=["forms"])

class PublishFormRequest(BaseModel):
    form_name: str
    form_description: str
    form_type: str
    version: str
    schema: Dict[str, Any]
    ui_schema: Dict[str, Any]
    form_data: Dict[str, Any]  # Sample data

@router.post("/publish")
async def publish_form(request: PublishFormRequest):
    """Publish a new form definition"""
    # Implementation details in service layer

@router.get("/published")
async def get_published_forms():
    """List all published forms with metadata"""
    # Return list of forms for dropdown selection
```

**File**: `backend/app/services/form_service.py` (new)

```python
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class FormService:
    def __init__(self):
        self.forms_directory = "forms"
        os.makedirs(self.forms_directory, exist_ok=True)

    def publish_form(self, form_data: Dict[str, Any]) -> str:
        """
        Publish a form and return the form_id
        Creates folder structure: forms/{form_id}/
        """
        form_id = f"{form_data['form_type']}-{uuid.uuid4().hex[:8]}"
        form_folder = os.path.join(self.forms_directory, form_id)
        os.makedirs(form_folder, exist_ok=True)

        # Save all form files
        self._save_form_files(form_folder, form_id, form_data)
        return form_id

    def _save_form_files(self, folder: str, form_id: str, data: Dict[str, Any]):
        """Save schema, ui_schema, form_data, and metadata files"""
        # Save schema.json
        with open(os.path.join(folder, "schema.json"), "w") as f:
            json.dump(data["schema"], f, indent=2)

        # Save ui_schema.json
        with open(os.path.join(folder, "ui_schema.json"), "w") as f:
            json.dump(data["ui_schema"], f, indent=2)

        # Save form_data.json (sample)
        with open(os.path.join(folder, "form_data.json"), "w") as f:
            json.dump(data["form_data"], f, indent=2)

        # Save metadata.json
        metadata = {
            "form_id": form_id,
            "form_name": data["form_name"],
            "form_description": data["form_description"],
            "form_type": data["form_type"],
            "version": data["version"],
            "created_timestamp": datetime.now().isoformat(),
            "created_by": "admin",
            "status": "published"
        }
        with open(os.path.join(folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
```

## Phase 2: End User Form Tab Interface - 3-4 days

### 2.1 Form System Tab Main View
**File**: `frontend/src/components/forms/FormSystemView.tsx` (new)

```tsx
import React, { useState, useEffect } from 'react';
import { Layout, Row, Col, Select, Button, message } from 'antd';
import SubmittedFormsGrid from './SubmittedFormsGrid';
import FormEditor from './FormEditor';

interface FormSystemViewProps {
  tab: Tab;
  onFormChange?: (formData: any) => void;
}

export const FormSystemView: React.FC<FormSystemViewProps> = ({ tab, onFormChange }) => {
  const [publishedForms, setPublishedForms] = useState([]);
  const [selectedForm, setSelectedForm] = useState(null);
  const [editingSubmission, setEditingSubmission] = useState(null);
  const [mode, setMode] = useState<'list' | 'new' | 'edit'>('list');

  // Two main sections:
  // 1. New Form Section: Dropdown + Fill Form button
  // 2. Submitted Forms Grid: Filterable table

  return (
    <Layout style={{ padding: '24px', background: '#fff' }}>
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
              >
                Fill New Form
              </Button>
            </Col>
          </Row>

          {/* Submitted Forms Grid */}
          <SubmittedFormsGrid
            onEdit={(submission) => {
              setEditingSubmission(submission);
              setMode('edit');
            }}
            onView={(submission) => {
              setEditingSubmission(submission);
              setMode('view');
            }}
          />
        </>
      )}

      {(mode === 'new' || mode === 'edit') && (
        <FormEditor
          mode={mode}
          selectedForm={selectedForm}
          editingSubmission={editingSubmission}
          onSave={() => {
            setMode('list');
            setEditingSubmission(null);
          }}
          onCancel={() => {
            setMode('list');
            setEditingSubmission(null);
          }}
        />
      )}
    </Layout>
  );
};
```

### 2.2 Submitted Forms Grid Component
**File**: `frontend/src/components/forms/SubmittedFormsGrid.tsx` (new)

```tsx
import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Input, Select, DatePicker } from 'antd';
import { EditOutlined, EyeOutlined } from '@ant-design/icons';

interface SubmittedFormsGridProps {
  onEdit: (submission: any) => void;
  onView: (submission: any) => void;
}

export const SubmittedFormsGrid: React.FC<SubmittedFormsGridProps> = ({ onEdit, onView }) => {
  const [submissions, setSubmissions] = useState([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState([]);
  const [filters, setFilters] = useState({
    formName: '',
    formType: '',
    dateRange: null
  });

  const columns = [
    {
      title: 'Form Name',
      dataIndex: 'form_name',
      key: 'form_name',
      sorter: (a, b) => a.form_name.localeCompare(b.form_name),
      filterable: true
    },
    {
      title: 'Form Type',
      dataIndex: 'form_type',
      key: 'form_type',
      sorter: (a, b) => a.form_type.localeCompare(b.form_type),
      filterable: true
    },
    {
      title: 'Submission Date',
      dataIndex: 'submission_timestamp',
      key: 'submission_date',
      sorter: (a, b) => new Date(a.submission_timestamp) - new Date(b.submission_timestamp),
      render: (text) => new Date(text).toLocaleString()
    },
    {
      title: 'Version',
      dataIndex: 'version',
      key: 'version'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
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

  // Grid with filtering capabilities
  // Load submissions from API
  // Handle filtering logic

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
            value={filters.formType}
            onChange={(value) => setFilters({...filters, formType: value})}
          >
            {/* Populate with unique form types */}
          </Select>
        </Col>
        <Col span={6}>
          <DatePicker.RangePicker
            style={{ width: '100%' }}
            onChange={(dates) => setFilters({...filters, dateRange: dates})}
          />
        </Col>
      </Row>

      {/* Data Table */}
      <Table
        columns={columns}
        dataSource={filteredSubmissions}
        rowKey="submission_id"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />
    </div>
  );
};
```

### 2.3 Three-Tab Form Editor Component
**File**: `frontend/src/components/forms/FormEditor.tsx` (new)

```tsx
import React, { useState, useEffect } from 'react';
import { Tabs, Button, Space, message } from 'antd';
import { SaveOutlined, CloseOutlined } from '@ant-design/icons';
import { withTheme } from '@rjsf/core';
import { Theme as AntDTheme } from '@rjsf/antd';
import validator from '@rjsf/validator-ajv8';
import Editor from '@monaco-editor/react';

const AntDForm = withTheme(AntDTheme);

interface FormEditorProps {
  mode: 'new' | 'edit' | 'view';
  selectedForm: any;
  editingSubmission?: any;
  onSave: () => void;
  onCancel: () => void;
}

export const FormEditor: React.FC<FormEditorProps> = ({
  mode,
  selectedForm,
  editingSubmission,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState({});
  const [formDataText, setFormDataText] = useState('{}');
  const [metadata, setMetadata] = useState({});
  const [activeTab, setActiveTab] = useState('form');

  // Three tabs with specific functionality
  const tabItems = [
    {
      key: 'form',
      label: 'Form',
      children: (
        <div style={{ padding: '16px' }}>
          {selectedForm && (
            <AntDForm
              schema={selectedForm.schema}
              uiSchema={selectedForm.ui_schema}
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

  const handleSave = async () => {
    try {
      // Validate JSON
      JSON.parse(formDataText);

      // Call API to save/submit form
      const apiCall = mode === 'edit'
        ? '/api/forms/edit/' + editingSubmission.submission_id
        : '/api/forms/submit';

      // Implementation for save operation
      message.success('Form saved successfully');
      onSave();
    } catch (error) {
      message.error('Error saving form: ' + error.message);
    }
  };

  return (
    <div>
      {/* Header with actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '16px',
        padding: '16px',
        background: '#fafafa',
        borderRadius: '4px'
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
```

### 2.4 Tab System Integration
**File**: `frontend/src/App.tsx` - Add missing function

```tsx
// Add this function to handle Form System tab creation
const handleNewFormSystemTab = () => {
  const newTabId = `form-system-tab-${Date.now()}`;
  const newSessionId = `form-session-${Date.now()}`;

  const newTab: Tab = {
    id: newTabId,
    conversationId: '', // Not needed for form system
    title: `Form System ${tabs.filter((t) => t.type === 'formSystem').length + 1}`,
    isActive: true,
    isDirty: false,
    type: 'formSystem',
    sessionId: newSessionId,
  };

  setTabs((prev) => [...prev.map((tab) => ({ ...tab, isActive: false })), newTab]);
  setActiveTabId(newTabId);
  message.success('New Form System tab created');
};

// Add to the main content area around line 1395
) : activeTab?.type === 'formSystem' ? (
  // Form System View
  <FormSystemView
    tab={activeTab}
    onFormChange={(formData) => {
      // Handle form data changes if needed
    }}
  />
```

**File**: `frontend/src/components/layout/TabManager.tsx` - Add Form System option

```tsx
// Add Form System option to the dropdown in TabManager
{label: 'Form System', key: 'formSystem', onClick: () => onNewFormSystemTab?.()}
```

## Phase 3: Backend Form Submission APIs - 1-2 days

### 3.1 Form Submission Router
**File**: `backend/app/routers/form_submissions.py` (new)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import os
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/forms", tags=["form_submissions"])

class SubmitFormRequest(BaseModel):
    form_id: str
    form_data: Dict[str, Any]
    session_id: str

@router.post("/submit")
async def submit_form(request: SubmitFormRequest):
    """Submit a new filled form"""
    service = FormSubmissionService()
    submission_id = service.submit_form(request.dict())
    return {"submission_id": submission_id, "message": "Form submitted successfully"}

@router.put("/edit/{submission_id}")
async def edit_form_submission(submission_id: str, request: SubmitFormRequest):
    """Edit an existing form submission (creates new version)"""
    service = FormSubmissionService()
    new_submission_id = service.edit_form_submission(submission_id, request.dict())
    return {"submission_id": new_submission_id, "message": "Form updated successfully"}

@router.get("/submissions")
async def get_form_submissions():
    """List all form submissions with metadata"""
    service = FormSubmissionService()
    return service.get_all_submissions()

@router.get("/submissions/{submission_id}")
async def get_form_submission(submission_id: str):
    """Get specific form submission"""
    service = FormSubmissionService()
    return service.get_submission(submission_id)

@router.get("/published")
async def get_published_forms():
    """List published forms for selection"""
    service = FormService()
    return service.get_published_forms()
```

### 3.2 Form Submission Service
**File**: `backend/app/services/form_submission_service.py` (new)

```python
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

class FormSubmissionService:
    def __init__(self):
        self.submissions_directory = "UserFormData"
        self.forms_directory = "forms"
        os.makedirs(self.submissions_directory, exist_ok=True)

    def submit_form(self, submission_data: Dict[str, Any]) -> str:
        """Submit a new form and return submission_id"""
        submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata
        form_metadata = self._get_form_metadata(submission_data["form_id"])

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

        # Save submission metadata
        metadata = {
            "submission_id": submission_id,
            "form_id": submission_data["form_id"],
            "form_name": form_metadata["form_name"],
            "form_type": form_metadata["form_type"],
            "version": form_metadata["version"],
            "session_id": submission_data["session_id"],
            "submission_timestamp": datetime.now().isoformat(),
            "submission_date": datetime.now().date().isoformat(),
            "is_edited": False,
            "original_submission_id": None
        }

        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return submission_id

    def edit_form_submission(self, original_submission_id: str, submission_data: Dict[str, Any]) -> str:
        """Edit existing form submission, creates new version"""
        # Create new submission
        new_submission_id = f"submission-{uuid.uuid4().hex[:8]}"
        submission_folder = os.path.join(self.submissions_directory, new_submission_id)
        os.makedirs(submission_folder, exist_ok=True)

        # Get form metadata
        form_metadata = self._get_form_metadata(submission_data["form_id"])

        # Save form data
        with open(os.path.join(submission_folder, "form_data.json"), "w") as f:
            json.dump(submission_data["form_data"], f, indent=2)

        # Save submission metadata with edit reference
        metadata = {
            "submission_id": new_submission_id,
            "form_id": submission_data["form_id"],
            "form_name": form_metadata["form_name"],
            "form_type": form_metadata["form_type"],
            "version": form_metadata["version"],
            "session_id": submission_data["session_id"],
            "submission_timestamp": datetime.now().isoformat(),
            "submission_date": datetime.now().date().isoformat(),
            "is_edited": True,
            "original_submission_id": original_submission_id
        }

        with open(os.path.join(submission_folder, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return new_submission_id

    def get_all_submissions(self) -> List[Dict[str, Any]]:
        """Get all form submissions with metadata"""
        submissions = []

        for submission_folder in os.listdir(self.submissions_directory):
            metadata_path = os.path.join(
                self.submissions_directory,
                submission_folder,
                "metadata.json"
            )

            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    submissions.append(metadata)

        # Sort by submission timestamp (newest first)
        submissions.sort(key=lambda x: x["submission_timestamp"], reverse=True)
        return submissions

    def get_submission(self, submission_id: str) -> Dict[str, Any]:
        """Get specific form submission with data and metadata"""
        submission_folder = os.path.join(self.submissions_directory, submission_id)

        if not os.path.exists(submission_folder):
            raise HTTPException(status_code=404, detail="Submission not found")

        # Load metadata
        with open(os.path.join(submission_folder, "metadata.json"), "r") as f:
            metadata = json.load(f)

        # Load form data
        with open(os.path.join(submission_folder, "form_data.json"), "r") as f:
            form_data = json.load(f)

        return {
            "metadata": metadata,
            "form_data": form_data
        }

    def _get_form_metadata(self, form_id: str) -> Dict[str, Any]:
        """Get metadata for a published form"""
        metadata_path = os.path.join(self.forms_directory, form_id, "metadata.json")

        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail=f"Form {form_id} not found")

        with open(metadata_path, "r") as f:
            return json.load(f)
```

## Phase 4: Data Structures & Storage - 1 day

### 4.1 Published Forms Directory Structure
```
forms/
├── contact-form-12ab34cd/
│   ├── schema.json                 # JSON Schema definition
│   ├── ui_schema.json             # UI Schema for rendering
│   ├── form_data.json             # Sample form data
│   └── metadata.json              # Form metadata
├── survey-form-56ef78gh/
│   ├── schema.json
│   ├── ui_schema.json
│   ├── form_data.json
│   └── metadata.json
└── registration-form-90ij12kl/
    ├── schema.json
    ├── ui_schema.json
    ├── form_data.json
    └── metadata.json
```

### 4.2 Published Form Metadata Structure
**File**: `forms/{form_id}/metadata.json`
```json
{
  "form_id": "contact-form-12ab34cd",
  "form_name": "Contact Information Form",
  "form_description": "Basic contact details collection for customer inquiries",
  "form_type": "contact",
  "version": "1.0",
  "created_timestamp": "2025-12-23T10:00:00Z",
  "created_by": "admin",
  "status": "published"
}
```

### 4.3 User Submissions Directory Structure
```
UserFormData/
├── submission-ab12cd34/           # Original submission
│   ├── form_data.json            # User's filled form data
│   └── metadata.json             # Submission metadata
├── submission-ef56gh78/           # New form submission
│   ├── form_data.json
│   └── metadata.json
├── submission-ij90kl12/           # Edited version of ab12cd34
│   ├── form_data.json            # Modified data
│   └── metadata.json             # New metadata with edit reference
└── submission-mn34op56/           # Another independent submission
    ├── form_data.json
    └── metadata.json
```

### 4.4 User Submission Metadata Structures

**Original Submission Metadata**:
```json
{
  "submission_id": "submission-ab12cd34",
  "form_id": "contact-form-12ab34cd",
  "form_name": "Contact Information Form",
  "form_type": "contact",
  "version": "1.0",
  "session_id": "tab-12345-67890",
  "submission_timestamp": "2025-12-23T15:30:00Z",
  "submission_date": "2025-12-23",
  "is_edited": false,
  "original_submission_id": null
}
```

**Edited Version Metadata**:
```json
{
  "submission_id": "submission-ij90kl12",
  "form_id": "contact-form-12ab34cd",
  "form_name": "Contact Information Form",
  "form_type": "contact",
  "version": "1.0",
  "session_id": "tab-67890-12345",
  "submission_timestamp": "2025-12-23T16:45:00Z",
  "submission_date": "2025-12-23",
  "is_edited": true,
  "original_submission_id": "submission-ab12cd34"
}
```

### 4.5 Form Data Examples

**Sample JSON Schema** (`forms/{form_id}/schema.json`):
```json
{
  "title": "Contact Information Form",
  "description": "Please fill out your contact details",
  "type": "object",
  "required": ["firstName", "lastName", "email"],
  "properties": {
    "firstName": {
      "type": "string",
      "title": "First Name"
    },
    "lastName": {
      "type": "string",
      "title": "Last Name"
    },
    "email": {
      "type": "string",
      "format": "email",
      "title": "Email Address"
    },
    "phone": {
      "type": "string",
      "title": "Phone Number"
    },
    "message": {
      "type": "string",
      "title": "Message"
    }
  }
}
```

**Sample UI Schema** (`forms/{form_id}/ui_schema.json`):
```json
{
  "firstName": {
    "ui:placeholder": "Enter your first name"
  },
  "lastName": {
    "ui:placeholder": "Enter your last name"
  },
  "email": {
    "ui:placeholder": "your.email@example.com"
  },
  "phone": {
    "ui:placeholder": "(555) 123-4567"
  },
  "message": {
    "ui:widget": "textarea",
    "ui:placeholder": "Your message here...",
    "ui:options": {
      "rows": 4
    }
  }
}
```

**Sample Filled Form Data** (`UserFormData/{submission_id}/form_data.json`):
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "(555) 123-4567",
  "message": "I would like to inquire about your services. Please contact me at your earliest convenience."
}
```

## Phase 5: Integration & Testing - 1 day

### 5.1 Frontend Integration Tasks
1. **API Service Integration**
   - Add form-related API calls to existing ApiService
   - Handle error responses and loading states
   - Implement proper TypeScript interfaces

2. **Tab System Integration**
   - Ensure FormSystemView integrates with existing tab system
   - Test tab switching and state management
   - Verify session ID capture from tab system

3. **State Management**
   - Sync between Form tab and JSON tab in FormEditor
   - Handle form validation across tabs
   - Manage dirty state for save operations

### 5.2 Backend Integration Tasks
1. **Router Registration**
   - Register new routers in main.py
   - Ensure proper API documentation
   - Add CORS configuration if needed

2. **File System Setup**
   - Create required directories on startup
   - Handle file permissions
   - Implement error handling for file operations

3. **Error Handling**
   - Consistent error responses
   - Proper HTTP status codes
   - Logging for debugging

### 5.3 Testing Checklist
1. **Admin Form Publishing**
   - ✅ Can create forms in RJSFPlayground
   - ✅ Can add form metadata
   - ✅ Publish button works and saves to backend
   - ✅ All required files are created correctly

2. **End User Form System**
   - ✅ Form System tab can be created
   - ✅ Published forms appear in dropdown
   - ✅ Can fill new forms
   - ✅ Three-tab editor works correctly
   - ✅ Form and JSON tabs sync bidirectionally
   - ✅ Metadata tab shows correct information

3. **Form Submission**
   - ✅ Forms can be submitted successfully
   - ✅ Data saves to UserFormData with proper structure
   - ✅ Metadata is generated correctly
   - ✅ Session ID is captured from tab system

4. **Form Editing**
   - ✅ Submitted forms appear in grid
   - ✅ Grid filtering works correctly
   - ✅ Can edit existing forms
   - ✅ Edit creates new version (preserves original)
   - ✅ Edit metadata references original submission

5. **Version Control**
   - ✅ Original submissions remain unchanged
   - ✅ Edited versions have proper metadata
   - ✅ Version tracking works correctly

## Implementation Timeline

### Week 1
- **Day 1**: Admin form publishing (Playground extension + backend APIs)
- **Day 2**: FormSystemView component and grid implementation
- **Day 3**: Three-tab FormEditor component (Form + JSON sync)

### Week 2
- **Day 4**: Metadata tab and form editing backend APIs
- **Day 5**: Version control implementation and testing
- **Day 6**: Integration testing and bug fixes
- **Day 7**: Documentation and final polish

## Dependencies and Prerequisites

### Frontend Dependencies (Already Available)
- React 18 with TypeScript
- Ant Design components
- Monaco Editor
- RJSF libraries (@rjsf/core, @rjsf/antd, @rjsf/validator-ajv8)
- Existing tab management system

### Backend Dependencies
- FastAPI framework
- File system access permissions
- JSON handling capabilities

### Infrastructure Requirements
- Directory write permissions for:
  - `forms/` folder creation
  - `UserFormData/` folder creation
- API endpoint registration in main.py

## Success Criteria

### Functional Requirements ✅
1. **Admin can design and publish forms** using enhanced RJSFPlayground
2. **Published forms are stored** with proper structure and metadata
3. **Users can access Form System tab** from tab manager
4. **Users can select and fill published forms** using three-tab editor
5. **Forms render correctly** using stored schemas
6. **Form and JSON tabs sync bidirectionally** in real-time
7. **Metadata tab displays correct information** for submissions
8. **Form submissions save properly** to UserFormData with metadata
9. **Users can view all submissions** in filterable grid
10. **Users can edit existing forms** creating new versions
11. **Version control preserves original submissions**
12. **Session IDs are captured** from tab system

### Technical Requirements ✅
1. **Proper error handling** throughout the system
2. **TypeScript interfaces** for all data structures
3. **API documentation** for all endpoints
4. **File system organization** matches specification
5. **Integration with existing codebase** patterns

### User Experience ✅
1. **Intuitive workflow** from form creation to submission
2. **Clear visual feedback** for all operations
3. **Responsive design** that works on different screen sizes
4. **Proper loading states** and error messages
5. **Seamless integration** with existing tab system

This implementation plan provides a complete form processing system that leverages the existing RJSF infrastructure while adding powerful publishing, submission, and editing capabilities with full version control.