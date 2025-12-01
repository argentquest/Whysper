/**
 * Wells Fargo Branding
 *
 * Main export for all Wells Fargo brand configuration
 */

import { WFBrand } from './brand';
import { WFColors } from './colors';
import { wfThemes } from './theme';
import { WFTypography } from './typography';

export type { WFBrandConfig } from './brand';
export { WFBrand } from './brand';
export type { WFColorPalette } from './colors';
export { WFColors } from './colors';
export type { WFThemeVariant } from './theme';
export { wfDarkTheme,wfLightTheme, wfThemes } from './theme';
export type { WFTypographyConfig } from './typography';
export { WFTypography } from './typography';

// Re-export everything as a single object for convenience
export const WellsFargoBranding = {
  colors: WFColors,
  typography: WFTypography,
  brand: WFBrand,
  themes: wfThemes,
} as const;
