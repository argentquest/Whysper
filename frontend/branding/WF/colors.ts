/**
 * Wells Fargo Brand Colors
 * Based on official Wells Fargo brand guidelines
 *
 * Color Psychology:
 * - Deep Red (#b31e30): Passion, energy, power, commitment, dedication
 * - Golden Yellow (#ffcc02): Wealth, prosperity, optimism (gold rush heritage)
 */

export const WFColors = {
  // Brand-specific primary colors (internal use only)
  brand: {
    deepRed: '#b31e30',
    deepRedRGB: 'rgb(179, 30, 48)',
    goldenYellow: '#ffcc02',
    goldenYellowRGB: 'rgb(255, 204, 2)',
    white: '#ffffff',
    whiteRGB: 'rgb(255, 255, 255)',
  },

  // Generic Primary Colors (use these in components)
  primary: '#b31e30',           // Main brand color
  secondary: '#ffcc02',         // Secondary brand color
  tertiary: '#f5f5f5',          // Tertiary color for subtle backgrounds (status bars, etc.)
  accent: '#b31e30',            // Accent color for highlights
  background: '#ffffff',        // Background color

  // Gradients (generic names)
  gradients: {
    primary: 'linear-gradient(135deg, #b31e30 0%, #ffcc02 100%)',      // User messages
    secondary: 'linear-gradient(90deg, #0033a0 0%, #00a9ce 100%)',    // System messages
    header: 'linear-gradient(135deg, #b31e30 0%, #ffcc02 100%)',      // Header gradient
  },

  // Data Visualization Colors (from pie chart)
  dataViz: {
    studentLoans: '#E84E2A',      // 36% - Orange-Red
    dailyExpenses: '#F9A655',     // 18% - Orange
    nonStudentLoans: '#B8B8B8',   // 18% - Gray
    retirement: '#8B4F9F',        // 16% - Purple
    healthCare: '#C4B5E8',        // 8% - Lavender
    other: '#2C2968',             // 4% - Navy
  },

  // Semantic Colors (for UI states)
  semantic: {
    success: '#52c41a',
    warning: '#ffcc02',   // Using golden yellow
    error: '#b31e30',     // Using deep red
    info: '#1890ff',
  },

  // Neutral Colors
  neutral: {
    gray1: '#ffffff',
    gray2: '#fafafa',
    gray3: '#f5f5f5',
    gray4: '#f0f0f0',
    gray5: '#d9d9d9',
    gray6: '#bfbfbf',
    gray7: '#8c8c8c',
    gray8: '#595959',
    gray9: '#434343',
    gray10: '#262626',
    gray11: '#1f1f1f',
    gray12: '#141414',
    gray13: '#000000',
  },

  // Text Colors
  text: {
    primary: '#262626',
    secondary: '#595959',
    tertiary: '#8c8c8c',
    inverse: '#ffffff',
  },
} as const;

export type WFColorPalette = typeof WFColors;
