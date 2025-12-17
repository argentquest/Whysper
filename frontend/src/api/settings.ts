// Define backend connection details using environment variables or default port
import { getApiBaseUrl } from '../utils/apiBase'

const BACKEND_URL = getApiBaseUrl()

// Define interface for backend settings to ensure type safety
export interface BackendSettings {
  values: Record<string, string>
  masked: Record<string, string>
  descriptions: Record<string, string>
  theme: string
  availableThemes: string[]
  timeout: number
  activeBrand: string // Active brand from backend
}

// Fetch application settings from backend with error handling
export async function fetchSettings(): Promise<BackendSettings> {
  try {
    // Attempt to retrieve settings from backend API endpoint
    const response = await fetch(`${BACKEND_URL}/settings`)

    // Throw error if response is not successful
    if (!response.ok) {
      throw new Error(`Failed to fetch settings: ${response.statusText}`)
    }

    // Parse and return JSON response if successful
    return await response.json()
  } catch (error) {
    // Log error and return default settings if backend is unavailable
    console.error('Error fetching settings from backend:', error)

    // Provide fallback settings to prevent application from breaking
    return {
      values: {},
      masked: {},
      descriptions: {},
      theme: 'light',
      availableThemes: ['light', 'dark'],
      timeout: 120,
      activeBrand: 'WF', // Default fallback
    }
  }
}

// Retrieve active brand from backend settings with fallback mechanism
export async function getActiveBrand(): Promise<string> {
  try {
    // Fetch settings and extract active brand
    const settings = await fetchSettings()

    // Return active brand or default to 'WF'
    return settings.activeBrand || 'WF'
  } catch (error) {
    // Log warning and return default brand if retrieval fails
    console.warn('Failed to get active brand from backend, using default WF')
    return 'WF'
  }
}
