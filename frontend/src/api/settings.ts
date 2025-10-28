/**
 * Settings API - Fetch application settings from backend
 */

const BACKEND_PORT = import.meta.env.VITE_BACKEND_PORT || '8003';
const BACKEND_URL = `http://localhost:${BACKEND_PORT}/api/v1`;

export interface BackendSettings {
  values: Record<string, string>;
  masked: Record<string, string>;
  descriptions: Record<string, string>;
  theme: string;
  availableThemes: string[];
  timeout: number;
  activeBrand: string;  // Active brand from backend
}

/**
 * Fetch settings from backend
 */
export async function fetchSettings(): Promise<BackendSettings> {
  try {
    const response = await fetch(`${BACKEND_URL}/settings`);
    if (!response.ok) {
      throw new Error(`Failed to fetch settings: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching settings from backend:', error);
    // Return defaults if backend is unavailable
    return {
      values: {},
      masked: {},
      descriptions: {},
      theme: 'light',
      availableThemes: ['light', 'dark'],
      timeout: 120,
      activeBrand: 'WF',  // Default fallback
    };
  }
}

/**
 * Get active brand from backend settings
 * This is used by the branding system to dynamically load the correct brand
 */
export async function getActiveBrand(): Promise<string> {
  try {
    const settings = await fetchSettings();
    return settings.activeBrand || 'WF';
  } catch (error) {
    console.warn('Failed to get active brand from backend, using default WF');
    return 'WF';
  }
}
