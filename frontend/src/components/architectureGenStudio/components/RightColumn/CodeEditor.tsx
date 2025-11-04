/**
 * Code Editor Component
 * Displays and edits diagram code
 */

import React, { useCallback } from 'antd';
import { Input, Select } from 'antd';
import { DiagramType } from '../../types';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  diagramType: DiagramType;
  isReadOnly: boolean;
}

const getLanguageMode = (type: DiagramType): string => {
  const modes: Record<DiagramType, string> = {
    mermaid: 'mermaid',
    d2: 'plaintext',
    structurizr: 'plaintext',
    plantuml: 'plaintext',
  };
  return modes[type];
};

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  diagramType,
  isReadOnly,
}) => {
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onChange(e.target.value);
    },
    [onChange]
  );

  return (
    <Input.TextArea
      value={code}
      onChange={handleChange}
      disabled={isReadOnly}
      placeholder="Diagram code will appear here..."
      style={{
        fontFamily: 'monospace',
        fontSize: '12px',
        height: '100%',
        minHeight: '300px',
        borderRadius: 0,
      }}
      rows={20}
    />
  );
};

export default CodeEditor;
