/**
 * Wells Fargo Brand Colors (WF2)
 *
 * Tuned to match the current wellsfrago.com experience shown in the
 * supplied captures: high-contrast cardinal red paired with warm
 * neutrals and a hint of gold for accent rules.
 */

const cardinalRed = '#d71e28';
const cardinalRedDark = '#b81820';
const heritageGold = '#f7b500';
const footerLightGray = '#e3ded8'; // light gray used in footer dividers and cards
const sunsetPeach = '#fde5c8'; // 40% lighter mix between cardinal red and heritage gold
const warmBeige = '#f8f4f1';
const sand = '#e9dfd6';
const linkBlue = '#004c97';

export const WFColors = {
  brand: {
    cardinal: cardinalRed,
    cardinalDark: cardinalRedDark,
    heritageGold,
    lightGray: footerLightGray,
    warmBeige,
    sand,
    linkBlue,
    white: '#ffffff',
  },

  // Primary tokens used by Ant theme + components
  primary: cardinalRed,
  secondary: heritageGold,
  tertiary: footerLightGray,
  quaternary: sunsetPeach,
  accent: linkBlue,
  background: '#ffffff',
  backgroundMuted: warmBeige,
  ctaGradient: `linear-gradient(180deg, ${cardinalRed} 0%, ${cardinalRedDark} 100%)`,

  gradients: {
    primary: `linear-gradient(135deg, ${cardinalRed} 0%, ${heritageGold} 100%)`,
    secondary: `linear-gradient(135deg, ${linkBlue} 0%, #6aa8ff 100%)`,
    hero: `linear-gradient(125deg, ${cardinalRed} 0%, ${cardinalRedDark} 70%)`,
    badge: `linear-gradient(135deg, ${cardinalRed} 0%, #a7068a 100%)`,
    header: `linear-gradient(180deg, ${cardinalRed} 0%, ${cardinalRedDark} 100%)`,
  },

  dataViz: {
    deposits: '#d71e28',
    lending: '#f58634',
    investments: '#a7068a',
    savings: '#f7b500',
    insurance: '#8b4f9f',
    misc: '#004c97',
  },

  semantic: {
    success: '#3c803f',
    warning: '#f7b500',
    error: cardinalRed,
    info: '#4f6fbd',
  },

  neutral: {
    white: '#ffffff',
    warm1: warmBeige,
    warm2: sand,
    warm3: '#d4c8bc',
    stroke: footerLightGray,
    strokeMuted: '#c9bfb6',
    charcoal: '#231f20',
    graphite: '#5d5550',
    slate: '#7c756e',
    offBlack: '#161213',
  },

  text: {
    primary: '#231f20',
    secondary: '#5d5550',
    muted: '#7c756e',
    inverse: '#ffffff',
    link: linkBlue,
  },
} as const;

export type WFColorPalette = typeof WFColors;
