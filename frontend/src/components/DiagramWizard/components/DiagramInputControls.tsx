import { FormOutlined } from '@ant-design/icons'
import { Button, message, Select } from 'antd'
import React, { useEffect, useState } from 'react'

import ApiService from '../../../services/api'
import FormRenderer from '../../forms/FormRenderer'
import { formatFormDataForPrompt } from '../../../utils/formDataFormatters'
import { ImageAnalysisButton } from './ImageAnalysisButton'

interface DiagramInputControlsProps {
    onAppendText: (text: string) => void
    loading: boolean
    sessionId?: string
    onFormSubmissionId?: (submissionId: string) => void
}

/**
 * DiagramInputControls
 * 
 * A unified component that combines form usage and image analysis.
 * Features:
 * - Dropdown to select a published form
 * - "Use Form" button to open the form modal
 * - "Image Analysis" button to upload and analyze images
 */
export const DiagramInputControls: React.FC<DiagramInputControlsProps> = ({
    onAppendText,
    loading,
    sessionId,
    onFormSubmissionId
}) => {
    // Form integration state
    const [formModalVisible, setFormModalVisible] = useState(false)
    const [publishedForms, setPublishedForms] = useState<any[]>([])
    const [selectedFormId, setSelectedFormId] = useState<string | null>(null)

    // Load published forms on mount
    useEffect(() => {
        const loadForms = async () => {
            try {
                const response = await ApiService.get('/forms/published')
                if (response.data) {
                    setPublishedForms(response.data)
                }
            } catch (error) {
                console.error('Failed to load forms:', error)
            }
        }
        loadForms()
    }, [])

    // Handle form submission
    const handleFormSubmit = (formData: any, formMetadata: any, submissionId?: string) => {
        const formattedData = formatFormDataForPrompt(formData, formMetadata)

        // Prefix the formatted data with a header
        const textToAppend = `\n\n---\nForm Data:\n${formattedData}`
        onAppendText(textToAppend)

        if (submissionId && onFormSubmissionId) {
            onFormSubmissionId(submissionId)
        }

        setFormModalVisible(false)
        setSelectedFormId(null)
        message.success('Form data added to context')
    }

    return (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Select
                placeholder="Select a form template"
                style={{ width: 300, flex: 1 }}
                value={selectedFormId}
                onChange={setSelectedFormId}
                allowClear
                onClear={() => setSelectedFormId(null)}
                disabled={loading}
            >
                {publishedForms.map(form => (
                    <Select.Option key={form.form_id} value={form.form_id}>
                        {form.form_name} ({form.form_type})
                    </Select.Option>
                ))}
            </Select>
            <Button
                icon={<FormOutlined />}
                onClick={() => setFormModalVisible(true)}
                disabled={!selectedFormId || loading}
            >
                Use Form
            </Button>
            <ImageAnalysisButton
                onAnalysisComplete={(description) => {
                    const textToAppend = `\n\n---\nImage Context:\n${description}`
                    onAppendText(textToAppend)
                }}
                disabled={loading}
            />

            {/* Form Renderer Modal is now self-contained in this component */}
            <FormRenderer
                visible={formModalVisible}
                onClose={() => {
                    setFormModalVisible(false)
                    setSelectedFormId(null)
                }}
                onSubmit={handleFormSubmit}
                sessionId={sessionId || 'temp-session'}
                title="Fill Form Template"
                formId={selectedFormId}
            />
        </div>
    )
}
