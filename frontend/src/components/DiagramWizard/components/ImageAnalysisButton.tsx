import { UploadOutlined } from '@ant-design/icons'
import { Button, message, Spin, Upload } from 'antd'
import React, { useState } from 'react'

import ApiService from '../../../services/api'

interface ImageAnalysisButtonProps {
    onAnalysisComplete: (description: string) => void
    disabled?: boolean
    buttonText?: string
    buttonType?: 'primary' | 'default' | 'dashed' | 'text' | 'link'
}

/**
 * ImageAnalysisButton
 * 
 * Reusable component for uploading and analyzing architecture diagrams.
 * Handles the file upload, API call, and loading state.
 */
export const ImageAnalysisButton: React.FC<ImageAnalysisButtonProps> = ({
    onAnalysisComplete,
    disabled = false,
    buttonText = 'Upload Diagram',
    buttonType = 'default'
}) => {
    const [uploading, setUploading] = useState(false)

    const handleImageUpload = async (file: File) => {
        setUploading(true)
        try {
            const result = await ApiService.analyzeImage(file)
            if (result.success && result.data) {
                onAnalysisComplete(result.data.description)
                message.success('Image analyzed successfully!')
            } else {
                message.error(result.error || 'Failed to analyze image')
            }
        } catch (err) {
            console.error('Image upload error:', err)
            message.error('Error uploading image')
        } finally {
            setUploading(false)
        }
        return false // Prevent auto upload by antd
    }

    return (
        <Upload
            name="file"
            multiple={false}
            showUploadList={false}
            beforeUpload={handleImageUpload}
            accept="image/*,.svg"
            disabled={disabled || uploading}
        >
            <Button
                icon={uploading ? <Spin size="small" /> : <UploadOutlined />}
                disabled={disabled || uploading}
                type={buttonType}
            >
                {uploading ? 'Analyzing...' : buttonText}
            </Button>
        </Upload>
    )
}
