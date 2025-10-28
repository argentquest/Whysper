/**
 * Wells Fargo Ant Design Theme Configuration
 *
 * Applies Wells Fargo brand colors to Ant Design components
 */

import type { ThemeConfig } from 'antd';
import { WFColors } from './colors';

/**
 * Light Theme - Wells Fargo Branding
 */
export const wfLightTheme: ThemeConfig = {
  token: {
    // Brand Colors
    colorPrimary: WFColors.primary,
    colorSuccess: WFColors.semantic.success,
    colorWarning: WFColors.secondary,
    colorError: WFColors.primary,
    colorInfo: WFColors.semantic.info,

    // Background Colors
    colorBgContainer: WFColors.neutral.gray1,
    colorBgElevated: WFColors.neutral.gray1,
    colorBgLayout: WFColors.neutral.gray2,

    // Text Colors
    colorText: WFColors.text.primary,
    colorTextSecondary: WFColors.text.secondary,
    colorTextTertiary: WFColors.text.tertiary,

    // Border
    colorBorder: WFColors.neutral.gray5,
    colorBorderSecondary: WFColors.neutral.gray4,

    // Border Radius
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    // Font
    fontSize: 14,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',

    // Spacing
    padding: 16,
    margin: 16,

    // Component specific
    controlHeight: 36,
    controlHeightLG: 44,
    controlHeightSM: 28,
  },

  components: {
    Button: {
      primaryShadow: '0 2px 8px rgba(179, 30, 48, 0.15)',
      dangerShadow: '0 2px 8px rgba(179, 30, 48, 0.15)',
      controlHeight: 36,
      controlHeightLG: 44,
      borderRadius: 8,
      fontWeight: 500,
    },

    Layout: {
      headerBg: WFColors.neutral.gray1,
      headerPadding: '0 24px',
      bodyBg: WFColors.neutral.gray2,
      footerBg: WFColors.neutral.gray1,
    },

    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: WFColors.primary + '10', // 10% opacity
      itemSelectedColor: WFColors.primary,
      itemHoverBg: WFColors.neutral.gray3,
    },

    Card: {
      borderRadiusLG: 12,
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)',
    },

    Input: {
      borderRadius: 8,
      controlHeight: 36,
    },

    Select: {
      borderRadius: 8,
      controlHeight: 36,
    },

    Modal: {
      borderRadiusLG: 12,
      boxShadow: '0 6px 16px rgba(0, 0, 0, 0.12)',
    },

    Tabs: {
      itemSelectedColor: WFColors.primary,
      itemHoverColor: WFColors.primary,
      inkBarColor: WFColors.primary,
    },

    Badge: {
      colorError: WFColors.primary,
    },

    Tag: {
      defaultBg: WFColors.neutral.gray3,
      defaultColor: WFColors.text.primary,
    },
  },
};

/**
 * Dark Theme - Wells Fargo Branding
 */
export const wfDarkTheme: ThemeConfig = {
  token: {
    // Brand Colors
    colorPrimary: WFColors.secondary,
    colorSuccess: WFColors.semantic.success,
    colorWarning: WFColors.secondary,
    colorError: '#ff4d4f',
    colorInfo: '#1890ff',

    // Background Colors
    colorBgContainer: WFColors.neutral.gray11,
    colorBgElevated: WFColors.neutral.gray10,
    colorBgLayout: WFColors.neutral.gray12,

    // Text Colors
    colorText: WFColors.neutral.gray3,
    colorTextSecondary: WFColors.neutral.gray5,
    colorTextTertiary: WFColors.neutral.gray6,

    // Border
    colorBorder: WFColors.neutral.gray8,
    colorBorderSecondary: WFColors.neutral.gray9,

    // Border Radius
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 6,

    // Font
    fontSize: 14,
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',

    // Spacing
    padding: 16,
    margin: 16,

    // Component specific
    controlHeight: 36,
    controlHeightLG: 44,
    controlHeightSM: 28,
  },

  components: {
    Button: {
      primaryShadow: '0 2px 8px rgba(255, 204, 2, 0.15)',
      controlHeight: 36,
      controlHeightLG: 44,
      borderRadius: 8,
      fontWeight: 500,
    },

    Layout: {
      headerBg: WFColors.neutral.gray11,
      headerPadding: '0 24px',
      bodyBg: WFColors.neutral.gray12,
      footerBg: WFColors.neutral.gray11,
    },

    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: WFColors.secondary + '20', // 20% opacity
      itemSelectedColor: WFColors.secondary,
      itemHoverBg: WFColors.neutral.gray10,
    },

    Card: {
      borderRadiusLG: 12,
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.45)',
    },

    Input: {
      borderRadius: 8,
      controlHeight: 36,
    },

    Select: {
      borderRadius: 8,
      controlHeight: 36,
    },

    Modal: {
      borderRadiusLG: 12,
      boxShadow: '0 6px 16px rgba(0, 0, 0, 0.45)',
    },

    Tabs: {
      itemSelectedColor: WFColors.secondary,
      itemHoverColor: WFColors.secondary,
      inkBarColor: WFColors.secondary,
    },

    Badge: {
      colorError: '#ff4d4f',
    },

    Tag: {
      defaultBg: WFColors.neutral.gray10,
      defaultColor: WFColors.neutral.gray3,
    },
  },
};

/**
 * All Wells Fargo themed variants
 */
export const wfThemes = {
  light: wfLightTheme,
  dark: wfDarkTheme,
} as const;

export type WFThemeVariant = keyof typeof wfThemes;
