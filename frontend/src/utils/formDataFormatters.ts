export interface FormMetadata {
  form_name: string;
  form_type: string;
  version?: string;
  form_description?: string;
}

/**
 * Format form data for system description (initial prompt)
 * Provides clear context with form name, JSON code block for syntax highlighting,
 * and space for user to add additional text
 */
export const formatFormDataForPrompt = (
  formData: any,
  metadata: FormMetadata
): string => {
  const description = metadata.form_description
    ? `${metadata.form_description}\n\n`
    : '';

  return `${description}# System Description from Form: ${metadata.form_name}

\`\`\`json
${JSON.stringify(formData, null, 2)}
\`\`\`

Additional Context:
[Add more details here if needed]`;
};

/**
 * Format form data for clarification response
 * Provides form context and JSON data in code block format
 */
export const formatFormDataForClarification = (
  formData: any,
  metadata: FormMetadata
): string => {
  const description = metadata.form_description
    ? `${metadata.form_description}\n\n`
    : '';

  return `${description}# Response using ${metadata.form_name}:

\`\`\`json
${JSON.stringify(formData, null, 2)}
\`\`\``;
};