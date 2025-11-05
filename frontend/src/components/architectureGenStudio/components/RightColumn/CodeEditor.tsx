/**
 * Code Editor Component
 * Displays and edits diagram code
 */

import React, { useCallback } from 'react';
import { Input } from 'antd';
import type { DiagramType } from '../../types';

interface CodeEditorProps {
  code: string;
  onChange: (code: string) => void;
  diagramType: DiagramType;
  isReadOnly: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
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
