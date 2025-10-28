/**
 * Wells Fargo Typography
 *
 * Font characteristics from brand guidelines:
 * - Logo: Custom serif font (bold, classic, authoritative)
 * - Body: Clean, readable sans-serif
 */

export const WFTypography = {
  // Font Families
  fontFamily: {
    // Primary font stack (sans-serif for better web readability)
    primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',

    // For headings/brand elements (serif option)
    heading: 'Georgia, "Times New Roman", Times, serif',

    // Monospace for code
    mono: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
  },

  // Font Sizes
  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
    '5xl': '48px',
  },

  // Font Weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // Line Heights
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2,
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
} as const;

export type WFTypographyConfig = typeof WFTypography;
