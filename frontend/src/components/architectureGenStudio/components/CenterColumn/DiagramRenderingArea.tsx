/**
 * Diagram Rendering Area Component
 * Displays SVG diagrams
 */

import React from 'react';
import type { DiagramResponse } from '../../types';

interface DiagramRenderingAreaProps {
  diagram: DiagramResponse;
  zoom: number;
}

export const DiagramRenderingArea: React.FC<DiagramRenderingAreaProps> = ({ diagram, zoom }) => {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        height: '100%',
        overflow: 'auto',
      }}
    >
      <div
        dangerouslySetInnerHTML={{ __html: diagram.svg }}
        style={{
          transform: `scale(${zoom})`,
          transformOrigin: 'center top',
          transition: 'transform 0.2s ease',
        }}
      />
    </div>
  );
};

export default DiagramRenderingArea;
