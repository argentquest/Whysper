/**
 * Wells Fargo Typography
 *
 * Font characteristics from brand guidelines:
 * - Logo: Custom serif font (bold, classic, authoritative)
 * - Body: Clean, readable sans-serif
 */

const wellsFargoSansStack = '"Wells Fargo Sans", "Wells Fargo Sans Regular", "Source Sans Pro", Arial, Helvetica, sans-serif';

export const WFTypography = {
  fontFamily: {
    primary: wellsFargoSansStack,
    heading: '"Wells Fargo Sans SemiBold", "Wells Fargo Sans", "Source Sans Pro", Arial, Helvetica, sans-serif',
    mono: '"IBM Plex Mono", "Roboto Mono", "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
  },

  fontSize: {
    xs: '12px',
    sm: '14px',
    base: '16px',
    lg: '18px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '32px',
    '4xl': '40px',
    '5xl': '56px',
  },

  fontWeight: {
    hairline: 200,
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeight: {
    tight: 1.15,
    comfy: 1.35,
    normal: 1.5,
    relaxed: 1.75,
  },

  letterSpacing: {
    condensed: '-0.01em',
    normal: '0',
    wide: '0.02em',
  },
} as const;

export type WFTypographyConfig = typeof WFTypography;
