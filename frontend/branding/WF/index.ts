/**
 * Wells Fargo Branding
 *
 * Main export for all Wells Fargo brand configuration
 */

import { WFColors } from './colors';
import { WFTypography } from './typography';
import { WFBrand } from './brand';
import { wfThemes } from './theme';

export { WFColors } from './colors';
export type { WFColorPalette } from './colors';

export { WFTypography } from './typography';
export type { WFTypographyConfig } from './typography';

export { WFBrand } from './brand';
export type { WFBrandConfig } from './brand';

export { wfThemes, wfLightTheme, wfDarkTheme } from './theme';
export type { WFThemeVariant } from './theme';

// Re-export everything as a single object for convenience
export const WellsFargoBranding = {
  colors: WFColors,
  typography: WFTypography,
  brand: WFBrand,
  themes: wfThemes,
} as const;
