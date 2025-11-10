/**
 * Dynamic Branding Configuration
 *
 * This module dynamically loads the active brand based on the VITE_BRAND environment variable.
 * The brand folder name is set in the .env file.
 *
 * To switch brands:
 * 1. Create a new brand folder in frontend/branding/ (e.g., branding/MyBrand/)
 * 2. Copy the structure from an existing brand folder (e.g., WF/)
 * 3. Update the brand configuration files
 * 4. Set VITE_BRAND=MyBrand in your .env file
 * 5. Restart the dev server
 */

// Get the active brand from environment variable, default to 'WF'
const activeBrand = import.meta.env.VITE_BRAND || 'WF';

// Import all available brands
import * as WFBranding from './WF';
// Import other brands here as they are created
// import * as ACMEBranding from './ACME';

// Select the active brand based on environment variable
let selectedBrand: typeof WFBranding;

switch (activeBrand) {
  case 'WF':
    selectedBrand = WFBranding;
    break;
  // Add more brands here as needed
  // case 'ACME':
  //   selectedBrand = ACMEBranding;
  //   break;
  default:
    console.warn(`Brand "${activeBrand}" not found, falling back to WF`);
    selectedBrand = WFBranding;
}

// Export brand-agnostic names
export const BrandColors = selectedBrand.WFColors;
export const BrandTypography = selectedBrand.WFTypography;
export const Brand = selectedBrand.WFBrand;
export const BrandThemes = selectedBrand.wfThemes;
export const DefaultLightTheme = selectedBrand.wfLightTheme;
export const DefaultDarkTheme = selectedBrand.wfDarkTheme;

// Export as a single object for convenience
export const ActiveBranding = {
  colors: BrandColors,
  typography: BrandTypography,
  brand: Brand,
  themes: BrandThemes,
};

// Type exports - these are brand-agnostic
export type BrandColorPalette = typeof BrandColors;
export type BrandTypographyConfig = typeof BrandTypography;
export type BrandConfig = typeof Brand;
export type BrandThemeVariant = keyof typeof BrandThemes;

// Export the active brand name for debugging
export const ACTIVE_BRAND = activeBrand;

// Log the active brand on module load (only in development)
if (import.meta.env.DEV) {
  console.log(`🎨 Active Brand: ${activeBrand}`);
  console.log(`🎨 Brand Colors:`, BrandColors);
  console.log(`🎨 Default Light Theme Primary:`, DefaultLightTheme.token.colorPrimary);
  console.log(`🎨 Default Dark Theme Primary:`, DefaultDarkTheme.token.colorPrimary);
}
