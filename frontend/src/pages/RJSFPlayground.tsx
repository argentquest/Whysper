import { Button, Col, Layout, Row, Space, Typography, Alert } from 'antd'
import Editor from '@monaco-editor/react'
import React, { useMemo, useState } from 'react'
import type { RJSFSchema, UiSchema } from '@rjsf/utils'
import { withTheme } from '@rjsf/core'
import { Theme as AntDTheme } from '@rjsf/antd'
import validator from '@rjsf/validator-ajv8'

const { Header, Content } = Layout
const { Title, Paragraph, Text } = Typography

type FormData = Record<string, any>

const defaultSchema: RJSFSchema = {
  title: 'RJSF Playground',
  description: 'Edit the schema, UI schema, and form data to see the form update live.',
  type: 'object',
  properties: {
    firstName: { type: 'string', title: 'First name' },
    lastName: { type: 'string', title: 'Last name' },
    age: { type: 'integer', title: 'Age', minimum: 0 },
    bio: { type: 'string', title: 'Bio' },
    country: {
      type: 'string',
      title: 'Country',
      enum: ['USA', 'Canada', 'UK', 'Germany', 'Other'],
    },
    newsletter: { type: 'boolean', title: 'Subscribe to newsletter', default: true },
  },
}

const defaultUiSchema: UiSchema = {
  age: { 'ui:widget': 'updown' },
  bio: { 'ui:widget': 'textarea', 'ui:options': { rows: 4 } },
  country: { 'ui:placeholder': 'Select a country' },
}

const defaultFormData: FormData = {
  firstName: 'Ada',
  lastName: 'Lovelace',
  age: 28,
  bio: 'Mathematician and writer.',
  country: 'UK',
  newsletter: true,
}

type ParseResult<T> = { data: T; error?: string }

const parseJson = <T,>(value: string, fallback: T): ParseResult<T> => {
  try {
    return { data: JSON.parse(value) as T }
  } catch (error: any) {
    return { data: fallback, error: error?.message || 'Invalid JSON' }
  }
}

const AntDForm = withTheme<FormData, RJSFSchema, UiSchema>(AntDTheme)

export const RJSFPlayground: React.FC = () => {
  const [schemaText, setSchemaText] = useState(JSON.stringify(defaultSchema, null, 2))
  const [uiSchemaText, setUiSchemaText] = useState(JSON.stringify(defaultUiSchema, null, 2))
  const [formDataText, setFormDataText] = useState(JSON.stringify(defaultFormData, null, 2))

  const schemaResult = useMemo<ParseResult<RJSFSchema>>(
    () => parseJson<RJSFSchema>(schemaText, defaultSchema),
    [schemaText]
  )
  const uiSchemaResult = useMemo<ParseResult<UiSchema>>(
    () => parseJson<UiSchema>(uiSchemaText, defaultUiSchema),
    [uiSchemaText]
  )
  const formDataResult = useMemo<ParseResult<FormData>>(
    () => parseJson<FormData>(formDataText, defaultFormData),
    [formDataText]
  )

  const handleReset = () => {
    setSchemaText(JSON.stringify(defaultSchema, null, 2))
    setUiSchemaText(JSON.stringify(defaultUiSchema, null, 2))
    setFormDataText(JSON.stringify(defaultFormData, null, 2))
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f9fafb' }}>
      <Header
        style={{
          background: '#1f2937',
          borderBottom: '4px solid #10b981',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          height: 72,
        }}
      >
        <Space direction="vertical" size={0}>
          <Title level={3} style={{ margin: 0, color: 'white' }}>
            RJSF Playground
          </Title>
          <Text style={{ color: '#d1fae5' }}>Interactive demo of react-jsonschema-form</Text>
        </Space>
        <Button onClick={handleReset} type="primary">
          Reset to defaults
        </Button>
      </Header>

      <Content style={{ padding: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  JSON Schema
                </Title>
                <Paragraph type="secondary">
                  Define the structure of the form (fields, types, validation).
                </Paragraph>
                <Editor
                  height="260px"
                  language="json"
                  value={schemaText}
                  onChange={(value) => setSchemaText(value ?? '')}
                  theme="light"
                  options={{ minimap: { enabled: false }, fontSize: 13 }}
                />
                {schemaResult.error && (
                  <Alert type="error" message="Schema JSON error" description={schemaResult.error} showIcon style={{ marginTop: 8 }} />
                )}
              </div>

              <div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  UI Schema
                </Title>
                <Paragraph type="secondary">
                  Control widgets, placeholders, and other UI customizations.
                </Paragraph>
                <Editor
                  height="220px"
                  language="json"
                  value={uiSchemaText}
                  onChange={(value) => setUiSchemaText(value ?? '')}
                  theme="light"
                  options={{ minimap: { enabled: false }, fontSize: 13 }}
                />
                {uiSchemaResult.error && (
                  <Alert type="error" message="UI Schema JSON error" description={uiSchemaResult.error} showIcon style={{ marginTop: 8 }} />
                )}
              </div>

              <div>
                <Title level={4} style={{ marginBottom: 8 }}>
                  Form Data
                </Title>
                <Paragraph type="secondary">Seed the form with initial values.</Paragraph>
                <Editor
                  height="200px"
                  language="json"
                  value={formDataText}
                  onChange={(value) => setFormDataText(value ?? '')}
                  theme="light"
                  options={{ minimap: { enabled: false }, fontSize: 13 }}
                />
                {formDataResult.error && (
                  <Alert type="error" message="Form data JSON error" description={formDataResult.error} showIcon style={{ marginTop: 8 }} />
                )}
              </div>
            </Space>
          </Col>

          <Col xs={24} lg={12}>
            <div
              style={{
                background: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: 12,
                padding: 16,
                boxShadow: '0 8px 24px rgba(0,0,0,0.04)',
              }}
            >
              <Title level={4} style={{ marginBottom: 4 }}>
                Live Form
              </Title>
              <Paragraph type="secondary" style={{ marginBottom: 16 }}>
                Powered by @rjsf/core with the Ant Design theme.
              </Paragraph>
              <AntDForm
                schema={schemaResult.data}
                uiSchema={uiSchemaResult.data}
                formData={formDataResult.data}
                validator={validator}
                onChange={(event) => {
                  setFormDataText(JSON.stringify(event.formData ?? {}, null, 2))
                }}
                onSubmit={({ formData }) => {
                  setFormDataText(JSON.stringify(formData ?? {}, null, 2))
                }}
                liveValidate
              />
            </div>
          </Col>
        </Row>
      </Content>
    </Layout>
  )
}

export default RJSFPlayground
