/**
 * Base Diagram Renderer Component
 * Abstract base class for all diagram rendering components
 *
 * Provides common functionality for:
 * - Diagram validation
 * - Error handling
 * - SVG/PNG export
 * - Copying code to clipboard
 * - Responsive rendering
 * - Provider integration
 */

import React, { ReactNode } from 'react';
import { message as antMessage } from 'antd';
import diagramProviderService, {
  DiagramType,
  OutputFormat,
  DiagramRenderResponse,
  DiagramValidationResponse,
  ProviderInfo
} from '../../services/diagramProviderService';

// ===================================================================
// Type Definitions
// ===================================================================

/**
 * State for diagram rendering
 */
export interface DiagramState {
  isRendering: boolean;
  isValidating: boolean;
  error: string | null;
  svg: string | null;
  png: string | null;
  validation: DiagramValidationResponse | null;
  providerInfo: ProviderInfo | null;
  renderResult: DiagramRenderResponse | null;
}

/**
 * Props for all diagram renderers
 */
export interface BaseDiagramRendererProps {
  code: string;
  title?: string;
  showCode?: boolean;
  onRenderComplete?: (success: boolean, svg?: string) => void;
  onValidationComplete?: (result: DiagramValidationResponse) => void;
  className?: string;
  style?: React.CSSProperties;
}

// ===================================================================
// Base Class Implementation
// ===================================================================

/**
 * Abstract base class for diagram renderers
 * All specific diagram components (Mermaid, D2, etc.) should extend this class
 */
export abstract class BaseDiagramRenderer<Props extends BaseDiagramRendererProps> {
  /**
   * Get the diagram type this renderer handles
   * Must be implemented by subclasses
   */
  abstract getDiagramType(): DiagramType;

  /**
   * Render the diagram content to the DOM
   * Must be implemented by subclasses
   */
  abstract renderToDOM(container: HTMLDivElement, svg: string): void;

  /**
   * Validate diagram code
   * Can be overridden by subclasses for custom validation
   */
  protected async validateDiagram(code: string, autoFix: boolean = true): Promise<DiagramValidationResponse> {
    return diagramProviderService.validate({
      code,
      diagram_type: this.getDiagramType(),
      auto_fix: autoFix
    });
  }

  /**
   * Render diagram using provider service
   * Can be overridden by subclasses for custom rendering
   */
  protected async renderDiagram(code: string, format: OutputFormat = 'svg'): Promise<DiagramRenderResponse> {
    return diagramProviderService.render({
      code,
      diagram_type: this.getDiagramType(),
      output_format: format
    });
  }

  /**
   * Get provider information
   */
  protected async getProviderInfo(): Promise<ProviderInfo> {
    return diagramProviderService.getProviderInfo(this.getDiagramType());
  }

  /**
   * Export diagram as SVG
   */
  protected exportAsSvg(svgContent: string, filename?: string): void {
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `${this.getDiagramType()}_diagram.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    antMessage.success(`${this.getDiagramType()} diagram exported as SVG`);
  }

  /**
   * Export diagram as PNG
   */
  protected async exportAsPng(svgContent: string, filename?: string): Promise<void> {
    try {
      // Render to PNG using provider if available
      const result = await this.renderDiagram(svgContent, 'png');

      if (result.content) {
        // Handle PNG data (usually base64 encoded)
        const blob = new Blob([Buffer.from(result.content, 'base64')], { type: 'image/png' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename || `${this.getDiagramType()}_diagram.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        antMessage.success(`${this.getDiagramType()} diagram exported as PNG`);
      }
    } catch (error) {
      console.error('Failed to export PNG:', error);
      antMessage.error('Failed to export diagram as PNG');
    }
  }

  /**
   * Copy code to clipboard
   */
  protected copyCodeToClipboard(code: string): void {
    navigator.clipboard
      .writeText(code)
      .then(() => {
        antMessage.success('Code copied to clipboard');
      })
      .catch((error) => {
        console.error('Failed to copy code:', error);
        antMessage.error('Failed to copy code to clipboard');
      });
  }

  /**
   * Log diagram event
   */
  protected logDiagramEvent(event: {
    event_type: 'detection' | 'render_start' | 'render_success' | 'render_error' | 'validation';
    diagram_type: string;
    code_length?: number;
    code_preview?: string;
    error?: string;
    provider_id?: string;
  }): void {
    console.log(`[${this.getDiagramType().toUpperCase()}] Event: ${event.event_type}`, event);

    // Could log to backend API if needed
    // ApiService.logDiagramEvent(event);
  }

  /**
   * Parse and extract provider metadata from render result
   */
  protected extractProviderMetadata(result: DiagramRenderResponse): {
    providerId: string;
    providerName: string;
    renderTime: number;
    version?: string;
  } {
    return {
      providerId: result.metadata.provider_id,
      providerName: result.metadata.provider_name,
      renderTime: result.metadata.render_time,
      version: undefined // Could be added to metadata
    };
  }

  /**
   * Format error message for display
   */
  protected formatErrorMessage(error: any): string {
    if (typeof error === 'string') {
      return error;
    }

    if (error?.response?.data?.error) {
      return error.response.data.error;
    }

    if (error?.response?.data?.detail) {
      return error.response.data.detail;
    }

    if (error?.message) {
      return error.message;
    }

    return 'An unknown error occurred while rendering the diagram';
  }

  /**
   * Check if provider supports output format
   */
  protected async supportsFormat(format: OutputFormat): Promise<boolean> {
    try {
      const provider = await this.getProviderInfo();
      return provider.supported_output_formats.includes(format);
    } catch {
      return false;
    }
  }

  /**
   * Check if provider supports auto-fix
   */
  protected async supportsAutoFix(): Promise<boolean> {
    try {
      const provider = await this.getProviderInfo();
      return provider.capabilities.includes('auto_fix');
    } catch {
      return false;
    }
  }

  /**
   * Check if provider supports LLM correction
   */
  protected async supportsLLMCorrection(): Promise<boolean> {
    try {
      const provider = await this.getProviderInfo();
      return provider.capabilities.includes('llm_correction');
    } catch {
      return false;
    }
  }
}

// ===================================================================
// React Hook for Using Base Renderer Functionality
// ===================================================================

/**
 * Custom React hook for diagram rendering
 * Provides common state and methods for diagram components
 */
export function useDiagramRenderer(diagramType: DiagramType) {
  const [state, setState] = React.useState<DiagramState>({
    isRendering: false,
    isValidating: false,
    error: null,
    svg: null,
    png: null,
    validation: null,
    providerInfo: null,
    renderResult: null
  });

  /**
   * Update state
   */
  const updateState = (updates: Partial<DiagramState>): void => {
    setState(prev => ({ ...prev, ...updates }));
  };

  /**
   * Render diagram
   */
  const render = async (code: string, format: OutputFormat = 'svg'): Promise<boolean> => {
    updateState({ isRendering: true, error: null });

    try {
      const result = await diagramProviderService.render({
        code,
        diagram_type: diagramType,
        output_format: format
      });

      if (result.success && result.content) {
        updateState({
          isRendering: false,
          svg: format === 'svg' ? result.content : state.svg,
          png: format === 'png' ? result.content : state.png,
          renderResult: result,
          error: null
        });
        return true;
      } else {
        const errorMsg = result.error || 'Unknown rendering error';
        updateState({
          isRendering: false,
          error: errorMsg
        });
        return false;
      }
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : 'Failed to render diagram';
      updateState({
        isRendering: false,
        error: errorMsg
      });
      return false;
    }
  };

  /**
   * Validate diagram
   */
  const validate = async (code: string, autoFix: boolean = true): Promise<boolean> => {
    updateState({ isValidating: true });

    try {
      const result = await diagramProviderService.validate({
        code,
        diagram_type: diagramType,
        auto_fix: autoFix
      });

      updateState({
        isValidating: false,
        validation: result,
        error: result.is_valid ? null : (result.error || 'Validation failed')
      });

      return result.is_valid;
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : 'Validation failed';
      updateState({
        isValidating: false,
        error: errorMsg
      });
      return false;
    }
  };

  /**
   * Get provider info
   */
  const getProviderInfo = async (): Promise<ProviderInfo | null> => {
    try {
      const info = await diagramProviderService.getProviderInfo(diagramType);
      updateState({ providerInfo: info });
      return info;
    } catch (error) {
      console.error('Failed to get provider info:', error);
      return null;
    }
  };

  return {
    state,
    updateState,
    render,
    validate,
    getProviderInfo
  };
}

// ===================================================================
// Utility Functions
// ===================================================================

/**
 * Normalize diagram type name
 */
export function normalizeDiagramType(type: string): DiagramType {
  const normalized = type.toLowerCase();
  if (normalized.includes('mermaid')) return 'mermaid';
  if (normalized.includes('d2')) return 'd2';
  if (normalized.includes('c4')) return 'c4';
  return normalized as DiagramType;
}
