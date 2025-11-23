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

import React from 'react';
import { message as antMessage } from 'antd';
import diagramProviderService, {
  type DiagramType,
  type OutputFormat,
  type DiagramRenderResponse,
  type DiagramValidationResponse,
  type ProviderInfo
} from '../../services/diagramProviderService';

// ===================================================================
// Type Definitions
// ===================================================================

/**
 * State for diagram rendering
 * @interface DiagramState
 * @property {boolean} isRendering - Whether the diagram is currently being rendered
 * @property {boolean} isValidating - Whether the diagram code is currently being validated
 * @property {string | null} error - Error message if rendering or validation fails
 * @property {string | null} svg - Rendered SVG content
 * @property {string | null} png - Rendered PNG content (base64)
 * @property {DiagramValidationResponse | null} validation - Validation result details
 * @property {ProviderInfo | null} providerInfo - Information about the diagram provider
 * @property {DiagramRenderResponse | null} renderResult - Full render response details
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
 * @interface BaseDiagramRendererProps
 * @property {string} code - The diagram source code to render
 * @property {string} [title] - Optional title for the diagram
 * @property {boolean} [showCode] - Whether to show source code by default
 * @property {Function} [onRenderComplete] - Callback when rendering completes
 * @property {Function} [onValidationComplete] - Callback when validation completes
 * @property {string} [className] - CSS class name
 * @property {React.CSSProperties} [style] - CSS styles
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
export abstract class BaseDiagramRenderer<_Props extends BaseDiagramRendererProps = BaseDiagramRendererProps> {
  /**
   * Get the diagram type this renderer handles
   * Must be implemented by subclasses
   * @returns {DiagramType} The type of diagram (mermaid, d2, etc.)
   */
  abstract getDiagramType(): DiagramType;

  /**
   * Render the diagram content to the DOM
   * Must be implemented by subclasses
   * @param {HTMLDivElement} container - The DOM element to render into
   * @param {string} svg - The SVG content to render
   */
  abstract renderToDOM(container: HTMLDivElement, svg: string): void;

  /**
   * Validate diagram code
   * Can be overridden by subclasses for custom validation
   * @param {string} code - The diagram source code
   * @param {boolean} [autoFix=true] - Whether to attempt automatic fixes
   * @returns {Promise<DiagramValidationResponse>} The validation result
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
   * @param {string} code - The diagram source code
   * @param {OutputFormat} [format='svg'] - The desired output format
   * @returns {Promise<DiagramRenderResponse>} The render result
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
   * @returns {Promise<ProviderInfo>} Information about the diagram provider
   */
  protected async getProviderInfo(): Promise<ProviderInfo> {
    return diagramProviderService.getProviderInfo(this.getDiagramType());
  }

  /**
   * Export diagram as SVG
   * @param {string} svgContent - The SVG content to export
   * @param {string} [filename] - The filename to save as
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
   * @param {string} svgContent - The SVG content to export
   * @param {string} [filename] - The filename to save as
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
   * @param {string} code - The code to copy
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
   * @param {Object} event - The event details
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
   * @param {DiagramRenderResponse} result - The render response
   * @returns {Object} Extracted metadata
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
   * @param {any} error - The error object
   * @returns {string} Formatted error message
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
   * @param {OutputFormat} format - The format to check
   * @returns {Promise<boolean>} True if supported
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
   * @returns {Promise<boolean>} True if supported
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
   * @returns {Promise<boolean>} True if supported
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
 * @param {DiagramType} diagramType - The type of diagram to manage
 * @returns {Object} Hook state and methods
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
   * @param {Partial<DiagramState>} updates - State updates to merge
   */
  const updateState = (updates: Partial<DiagramState>): void => {
    setState(prev => ({ ...prev, ...updates }));
  };

  /**
   * Render diagram
   * @param {string} code - The code to render
   * @param {OutputFormat} [format='svg'] - The output format
   * @returns {Promise<boolean>} Success status
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
   * @param {string} code - The code to validate
   * @param {boolean} [autoFix=true] - Whether to auto-fix errors
   * @returns {Promise<boolean>} Validity status
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
   * @returns {Promise<ProviderInfo | null>} Provider information
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
 * @param {string} type - The raw diagram type string
 * @returns {DiagramType} The normalized diagram type
 */
export function normalizeDiagramType(type: string): DiagramType {
  const normalized = type.toLowerCase();
  if (normalized.includes('mermaid')) return 'mermaid';
  if (normalized.includes('d2')) return 'd2';
  if (normalized.includes('c4')) return 'c4';
  return normalized as DiagramType;
}
