import React, { useState } from 'react'
import Form from '@rjsf/antd'
import validator from '@rjsf/validator-ajv8'
import type { RJSFSchema } from '@rjsf/utils'
import Editor from '@monaco-editor/react'
import { Alert, Tabs } from 'antd'

const defaultSchema: RJSFSchema = {
    title: 'A registration form',
    description: 'A simple form example using RJSF and Ant Design.',
    type: 'object',
    required: [
        'firstName',
        'lastName'
    ],
    properties: {
        firstName: {
            type: 'string',
            title: 'First name',
            default: 'Chuck'
        },
        lastName: {
            type: 'string',
            title: 'Last name'
        },
        telephone: {
            type: 'string',
            title: 'Telephone',
            minLength: 10
        }
    }
}

const log = (type: string) => console.log.bind(console, type)

export const FormSystemView: React.FC = () => {
    const [schemaCode, setSchemaCode] = useState<string>(JSON.stringify(defaultSchema, null, 2))
    const [parsedSchema, setParsedSchema] = useState<RJSFSchema>(defaultSchema)
    const [parseError, setParseError] = useState<string | null>(null)
    const editorRef = React.useRef<any>(null)

    const handleEditorChange = (value: string | undefined) => {
        if (!value) return
        setSchemaCode(value)
        try {
            const parsed = JSON.parse(value)
            setParsedSchema(parsed)
            setParseError(null)
        } catch (error: any) {
            setParseError(error.message)
        }
    }

    const handleEditorDidMount = (editor: any, monaco: any) => {
        editorRef.current = editor
        // Focus immediately on mount
        editor.focus()
    }

    const handleTabChange = (key: string) => {
        if (key === 'schema') {
            // Slight delay to ensure tab content is visible before focusing
            setTimeout(() => {
                editorRef.current?.focus()
            }, 100)
        }
    }

    const items = [
        {
            key: 'form',
            label: 'Form',
            children: (
                <div className="flex-1 p-8 overflow-auto h-full bg-gray-50/30">
                    <div className="max-w-2xl mx-auto w-full bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        {parsedSchema ? (
                            <Form
                                schema={parsedSchema}
                                validator={validator}
                                onChange={log('changed')}
                                onSubmit={log('submitted')}
                                onError={log('errors')}
                            />
                        ) : (
                            <div className="text-gray-400 text-center mt-10">Invalid Schema</div>
                        )}
                    </div>
                </div>
            )
        },
        {
            key: 'schema',
            label: 'JSON Schema',
            children: (
                <div className="flex flex-col h-full">
                    <div className="relative border-b border-gray-200" style={{ height: 'calc(100vh - 150px)' }}>
                        <Editor
                            height="100%"
                            defaultLanguage="json"
                            value={schemaCode}
                            onChange={handleEditorChange}
                            onMount={handleEditorDidMount}
                            options={{
                                minimap: { enabled: false },
                                fontSize: 14,
                                scrollBeyondLastLine: false,
                                wordWrap: 'on',
                            }}
                        />
                    </div>
                    {parseError && (
                        <div className="p-2 bg-white">
                            <Alert message="Invalid JSON" description={parseError} type="error" showIcon />
                        </div>
                    )}
                </div>
            )
        },
        {
            key: 'designer',
            label: 'Designer',
            children: (
                <div className="flex items-center justify-center h-full bg-white">
                    <h1 className="text-3xl font-bold text-gray-300">Hello World</h1>
                </div>
            )
        }
    ]

    return (
        <div className="h-full bg-white flex flex-col">
            <Tabs
                defaultActiveKey="form"
                items={items}
                onChange={handleTabChange}
                className="flex-1 overflow-hidden"
                style={{ height: '100%' }}
                renderTabBar={(props, DefaultTabBar) => (
                    <div className="px-4 pt-2 bg-gray-50 border-b border-gray-200">
                        <DefaultTabBar {...props} style={{ marginBottom: 0 }} />
                    </div>
                )}
            />
        </div>
    )
}
