/**
 * Unified Diagram Provider Service
 * Provides a single interface to interact with backend diagram providers (mermaidv1, d2v1, etc.)
 *
 * This service abstracts away the complexity of different diagram rendering backends
 * and provides consistent validation, rendering, and error handling across all diagram types.
 */

import ApiService from './api'

// ===================================================================
// Type Definitions
// ===================================================================

export type DiagramType = 'mermaid' | 'd2' | 'c4'
export type OutputFormat = 'svg' | 'png' | 'native'

/**
 * Request to render a diagram
 */
export interface DiagramRenderRequest {
  code: string
  diagram_type: DiagramType
  provider_id?: string // Optional: specify specific provider (e.g., 'mermaidv1', 'd2v1')
  output_format?: OutputFormat // Default: 'svg'
  metadata?: Record<string, unknown>
  save_to_file?: boolean
}

/**
 * Validation result from a diagram provider
 */
export interface ValidationResult {
  is_valid: boolean
  error?: string
  auto_fixed: boolean
  llm_corrected: boolean
  fixed_code?: string
  correction_method?: string
}

/**
 * Response from diagram rendering
 */
export interface DiagramRenderResponse {
  success: boolean
  content?: string // SVG, PNG data, or other format content
  output_format: string
  validation: ValidationResult
  metadata: {
    provider_id: string
    provider_name: string
    render_time: number // milliseconds
    timestamp: string
    code_length: number
    [key: string]: unknown
  }
  error?: string
  file_path?: string
}

/**
 * Request to validate diagram code
 */
export interface DiagramValidationRequest {
  code: string
  diagram_type: DiagramType
  provider_id?: string
  auto_fix?: boolean
  use_llm?: boolean
}

/**
 * Response from diagram validation
 */
export interface DiagramValidationResponse {
  is_valid: boolean
  error?: string
  code_length: number
  auto_fixed: boolean
  llm_corrected: boolean
  fixed_code?: string
  correction_method?: string
  provider_id: string
}

/**
 * Provider capabilities
 */
export interface ProviderCapability {
  validate: boolean
  render_svg: boolean
  render_png: boolean
  auto_fix: boolean
  llm_correction: boolean
  batch: boolean
}

/**
 * Provider metadata
 */
export interface ProviderInfo {
  provider_id: string
  provider_name: string
  diagram_type: DiagramType
  description?: string
  supported_output_formats: OutputFormat[]
  capabilities: string[]
  version?: string
  available: boolean
  requires_llm: boolean
}

/**
 * Provider list response
 */
export interface ProvidersListResponse {
  total_providers: number
  available_providers: number
  unavailable_providers: number
  providers: ProviderInfo[]
}

// ===================================================================
// Service Implementation
// ===================================================================

class DiagramProviderService {
  private static instance: DiagramProviderService
  private cachedProviders: Map<string, ProviderInfo> = new Map()
  private providersCacheExpiry: number = 0
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

  private constructor() {
    this.logDebug('DiagramProviderService initialized')
  }

  /**
   * Get singleton instance
   */
  static getInstance(): DiagramProviderService {
    if (!DiagramProviderService.instance) {
      DiagramProviderService.instance = new DiagramProviderService()
    }
    return DiagramProviderService.instance
  }

  /**
   * Log debug messages with prefix
   */
  private logDebug(message: string, data?: unknown): void {
    console.log(`[📊 DIAGRAM PROVIDER SERVICE] ${message}`, data || '')
  }

  /**
   * Log error messages with prefix
   */
  private logError(message: string, error?: unknown): void {
    console.error(`[❌ DIAGRAM PROVIDER SERVICE] ${message}`, error || '')
  }

  /**
   * Render a diagram using the appropriate provider
   *
   * @param request - Render request with code and diagram type
   * @returns Render response with SVG/PNG content and metadata
   */
  async render(request: DiagramRenderRequest): Promise<DiagramRenderResponse> {
    const startTime = performance.now()

    try {
      this.logDebug('Render request', {
        diagram_type: request.diagram_type,
        output_format: request.output_format || 'svg',
        code_length: request.code.length,
      })

      // Validate input
      if (!request.code || request.code.trim().length === 0) {
        throw new Error('Diagram code cannot be empty')
      }

      // Make API request to backend provider
      const response = await ApiService.post('/diagrams/v2/render', {
        code: request.code,
        diagram_type: request.diagram_type,
        provider_id: request.provider_id,
        output_format: request.output_format || 'svg',
        metadata: request.metadata,
        save_to_file: request.save_to_file || false,
      })

      const result = response.data as DiagramRenderResponse
      const duration = performance.now() - startTime

      this.logDebug('Render successful', {
        provider: result.metadata.provider_id,
        duration_ms: duration.toFixed(2),
        success: result.success,
      })

      return result
    } catch (error) {
      const duration = performance.now() - startTime
      this.logError(`Render failed (${duration.toFixed(2)}ms)`, error)
      throw error
    }
  }

  /**
   * Validate diagram code without rendering
   *
   * @param request - Validation request
   * @returns Validation result with potential fixes
   */
  async validate(request: DiagramValidationRequest): Promise<DiagramValidationResponse> {
    try {
      this.logDebug('Validation request', {
        diagram_type: request.diagram_type,
        auto_fix: request.auto_fix ?? true,
        code_length: request.code.length,
      })

      if (!request.code || request.code.trim().length === 0) {
        throw new Error('Diagram code cannot be empty')
      }

      const response = await ApiService.post('/diagrams/v2/validate', {
        code: request.code,
        diagram_type: request.diagram_type,
        provider_id: request.provider_id,
        auto_fix: request.auto_fix ?? true,
        use_llm: request.use_llm ?? false,
      })

      const result = response.data as DiagramValidationResponse

      this.logDebug('Validation complete', {
        is_valid: result.is_valid,
        auto_fixed: result.auto_fixed,
        provider: result.provider_id,
      })

      return result
    } catch (error) {
      this.logError('Validation failed', error)
      throw error
    }
  }

  /**
   * Get information about a specific provider
   *
   * @param diagramType - Type of diagram (mermaid, d2, c4)
   * @param providerId - Optional specific provider ID
   * @returns Provider metadata
   */
  async getProviderInfo(diagramType: DiagramType, providerId?: string): Promise<ProviderInfo> {
    try {
      this.logDebug('Getting provider info', { diagram_type: diagramType, provider_id: providerId })

      // Try cache first
      const cacheKey = providerId || diagramType
      if (this.cachedProviders.has(cacheKey) && Date.now() < this.providersCacheExpiry) {
        this.logDebug('Using cached provider info', { provider: cacheKey })
        return this.cachedProviders.get(cacheKey)!
      }

      // Fetch from backend
      const endpoint = providerId
        ? `/diagrams/v2/providers/${providerId}`
        : `/diagrams/v2/providers`
      const response = await ApiService.get(endpoint)

      let provider: ProviderInfo

      if (providerId) {
        // Single provider response
        provider = response.data as ProviderInfo
      } else {
        // List response - find matching provider
        const list = response.data as ProvidersListResponse
        const found = list.providers.find((p) => p.diagram_type === diagramType && p.available)

        if (!found) {
          throw new Error(`No available provider found for diagram type: ${diagramType}`)
        }

        provider = found
      }

      // Cache the result
      this.cachedProviders.set(cacheKey, provider)
      this.providersCacheExpiry = Date.now() + this.CACHE_DURATION

      this.logDebug('Provider info retrieved', {
        provider_id: provider.provider_id,
        name: provider.provider_name,
      })

      return provider
    } catch (error) {
      this.logError('Failed to get provider info', error)
      throw error
    }
  }

  /**
   * List all available diagram providers
   *
   * @returns List of all providers with metadata
   */
  async listProviders(): Promise<ProvidersListResponse> {
    try {
      this.logDebug('Listing all providers')

      const response = await ApiService.get('/diagrams/v2/providers')
      return response.data as ProvidersListResponse
    } catch (error) {
      this.logError('Failed to list providers', error)
      throw error
    }
  }

  /**
   * Get providers for a specific diagram type
   *
   * @param diagramType - Type of diagram (mermaid, d2, c4)
   * @returns List of providers for this diagram type
   */
  async getProvidersByType(diagramType: DiagramType): Promise<ProviderInfo[]> {
    try {
      const list = await this.listProviders()
      const matching = list.providers.filter((p) => p.diagram_type === diagramType)

      if (matching.length === 0) {
        throw new Error(`No providers found for diagram type: ${diagramType}`)
      }

      this.logDebug(`Found ${matching.length} providers for type: ${diagramType}`)
      return matching
    } catch (error) {
      this.logError('Failed to get providers by type', error)
      throw error
    }
  }

  /**
   * Check if a provider is available
   *
   * @param diagramType - Type of diagram
   * @param providerId - Optional specific provider ID
   * @returns true if provider is available
   */
  async isProviderAvailable(diagramType: DiagramType, providerId?: string): Promise<boolean> {
    try {
      const provider = await this.getProviderInfo(diagramType, providerId)
      return provider.available
    } catch {
      return false
    }
  }

  /**
   * Check health of the provider system
   *
   * @returns Health status including available providers
   */
  async checkHealth(): Promise<{
    status: string
    total_providers: number
    available_providers: number
    diagram_types: string[]
    timestamp: string
    error?: string
  }> {
    try {
      this.logDebug('Checking provider system health')

      const response = await ApiService.get('/diagrams/v2/health')
      return response.data
    } catch (error) {
      this.logError('Health check failed', error)
      throw error
    }
  }

  /**
   * Clear cached provider information
   */
  clearCache(): void {
    this.cachedProviders.clear()
    this.providersCacheExpiry = 0
    this.logDebug('Provider cache cleared')
  }

  /**
   * Map old diagram type names to provider diagram types
   * Useful for backwards compatibility
   *
   * @param oldType - Old diagram type name
   * @returns Normalized diagram type
   */
  static normalizeDiagramType(oldType: string): DiagramType {
    const normalized = oldType.toLowerCase()
    if (normalized === 'mermaid' || normalized === 'mermaidv1') return 'mermaid'
    if (normalized === 'd2' || normalized === 'd2v1') return 'd2'
    if (normalized === 'c4' || normalized === 'c4diagram') return 'c4'

    // Default to the provided type if not recognized
    return normalized as DiagramType
  }
}

// ===================================================================
// Exports
// ===================================================================

// Export singleton instance as default
const diagramProviderService = DiagramProviderService.getInstance()
export default diagramProviderService

// Export the class for testing
export { DiagramProviderService }
