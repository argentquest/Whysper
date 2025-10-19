/**
 * D2 API Service
 * Handles communication with the backend D2 rendering API
 */

import ApiService from './api';

export interface D2RenderRequest {
  code: string;
  metadata?: Record<string, any>;
  return_svg?: boolean;
  save_to_file?: boolean;
}

export interface D2RenderResponse {
  success: boolean;
  svg_content?: string;
  validation: {
    is_valid: boolean;
    error?: string;
  };
  metadata: {
    render_time?: number;
    code_length: number;
    timestamp: string;
  };
  error?: string;
  file_path?: string;
}

export interface D2ValidationRequest {
  code: string;
}

export interface D2ValidationResponse {
  is_valid: boolean;
  error?: string;
  code_length: number;
}

export interface D2BatchRenderRequest {
  codes: string[];
  metadata?: Record<string, any>;
}

export interface D2BatchRenderResponse {
  results: D2RenderResponse[];
  summary: {
    total_diagrams: number;
    successful: number;
    failed: number;
    success_rate: number;
    total_time: number;
    average_time_per_diagram: number;
  };
  batch_id: string;
}

export interface D2InfoResponse {
  available: boolean;
  executable?: string;
  version?: string;
  error?: string;
}

export class D2ApiService {
  private static instance: D2ApiService;

  private constructor() {
    // ApiService is a static class, no initialization needed
  }

  static getInstance(): D2ApiService {
    if (!D2ApiService.instance) {
      D2ApiService.instance = new D2ApiService();
    }
    return D2ApiService.instance;
  }

  /**
   * Render a D2 diagram to SVG
   */
  async renderD2(request: D2RenderRequest): Promise<D2RenderResponse> {
    try {
      console.log('[D2 API] Rendering D2 diagram via backend API');
      const response = await ApiService.post('/d2/render', request);
      return response.data;
    } catch (error) {
      console.error('[D2 API] Render failed:', error);
      throw error;
    }
  }

  /**
   * Validate D2 code without rendering
   */
  async validateD2(request: D2ValidationRequest): Promise<D2ValidationResponse> {
    try {
      console.log('[D2 API] Validating D2 code via backend API');
      const response = await ApiService.post('/d2/validate', request);
      return response.data;
    } catch (error) {
      console.error('[D2 API] Validation failed:', error);
      throw error;
    }
  }

  /**
   * Render multiple D2 diagrams in a batch
   */
  async renderD2Batch(request: D2BatchRenderRequest): Promise<D2BatchRenderResponse> {
    try {
      console.log(`[D2 API] Rendering batch of ${request.codes.length} diagrams`);
      const response = await ApiService.post('/d2/render/batch', request);
      return response.data;
    } catch (error) {
      console.error('[D2 API] Batch render failed:', error);
      throw error;
    }
  }

  /**
   * Get D2 CLI information
   */
  async getD2Info(): Promise<D2InfoResponse> {
    try {
      console.log('[D2 API] Getting D2 CLI info');
      const response = await ApiService.get('/d2/info');
      return response.data;
    } catch (error) {
      console.error('[D2 API] Get info failed:', error);
      throw error;
    }
  }

  /**
   * Check D2 service health
   */
  async checkD2Health(): Promise<{ status: string; d2_available: boolean; timestamp: string; error?: string }> {
    try {
      console.log('[D2 API] Checking D2 service health');
      const response = await ApiService.get('/d2/health');
      return response.data;
    } catch (error) {
      console.error('[D2 API] Health check failed:', error);
      throw error;
    }
  }

  /**
   * Quick render with common defaults
   */
  async quickRender(code: string): Promise<D2RenderResponse> {
    return this.renderD2({
      code,
      return_svg: true,
      save_to_file: false,
      metadata: {
        source: 'frontend_quick_render',
        timestamp: new Date().toISOString()
      }
    });
  }

  /**
   * Quick validation
   */
  async quickValidate(code: string): Promise<D2ValidationResponse> {
    return this.validateD2({ code });
  }

  /**
   * Basic check if D2 code is not empty - backend handles actual validation
   */
  basicCheck(code: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!code || code.trim().length === 0) {
      errors.push('D2 code is empty');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}

// Export singleton instance as default
const d2Api = D2ApiService.getInstance();
export default d2Api;