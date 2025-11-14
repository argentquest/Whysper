/**
 * Wells Fargo Ant Design Theme Configuration
 *
 * Applies Wells Fargo brand colors to Ant Design components
 */

import type { ThemeConfig } from 'antd';
import { WFColors } from './colors';
import wfSansRegularWoff2 from './assets/fonts/wellsfargosans-rg.woff2';
import wfSansRegularWoff from './assets/fonts/wellsfargosans-rg.woff';
import wfSansLightWoff2 from './assets/fonts/wellsfargosans-lt.woff2';
import wfSansLightWoff from './assets/fonts/wellsfargosans-lt.woff';
import wfSansSemiBoldWoff2 from './assets/fonts/wellsfargosans-sbd.woff2';
import wfSansSemiBoldWoff from './assets/fonts/wellsfargosans-sbd.woff';
import wfSansBoldWoff2 from './assets/fonts/wellsfargosans-bd.woff2';
import wfSansBoldWoff from './assets/fonts/wellsfargosans-bd.woff';
import wfSourceSansItalicWoff2 from './assets/fonts/wellsfargosourcesans-it.woff2';
import wfSourceSansItalicWoff from './assets/fonts/wellsfargosourcesans-it.woff';

type BrandTokenOverrides = NonNullable<ThemeConfig['token']> & Record<string, string | number>;

const BRAND_BODY_FONT = '"Wells Fargo Sans", "Wells Fargo Sans Regular", "Source Sans Pro", Arial, Helvetica, sans-serif';
const BRAND_HEADING_FONT = '"Wells Fargo Sans SemiBold", "Wells Fargo Sans", "Source Sans Pro", Arial, Helvetica, sans-serif';

const WF2_FONT_FACE_CSS = `
@font-face {
  font-display: swap;
  font-family: "Wells Fargo Sans";
  font-weight: 400;
  src: url(${wfSansRegularWoff2}) format("woff2"),
       url(${wfSansRegularWoff}) format("woff");
}
@font-face {
  font-display: swap;
  font-family: "Wells Fargo Sans";
  font-weight: 300;
  src: url(${wfSansLightWoff2}) format("woff2"),
       url(${wfSansLightWoff}) format("woff");
}
@font-face {
  font-display: swap;
  font-family: "Wells Fargo Sans";
  font-weight: 600;
  src: url(${wfSansSemiBoldWoff2}) format("woff2"),
       url(${wfSansSemiBoldWoff}) format("woff");
}
@font-face {
  font-display: swap;
  font-family: "Wells Fargo Sans";
  font-weight: 700;
  src: url(${wfSansBoldWoff2}) format("woff2"),
       url(${wfSansBoldWoff}) format("woff");
}
@font-face {
  font-display: swap;
  font-family: "Source Sans Pro";
  font-style: italic;
  src: url(${wfSourceSansItalicWoff2}) format("woff2"),
       url(${wfSourceSansItalicWoff}) format("woff");
}
`;

const injectWF2Fonts = () => {
  if (typeof document === 'undefined') return;
  if (document.head.querySelector('[data-wf2-fonts]')) return;
  const style = document.createElement('style');
  style.setAttribute('data-wf2-fonts', 'true');
  style.textContent = WF2_FONT_FACE_CSS;
  document.head.appendChild(style);
};

injectWF2Fonts();

const lightTokens: BrandTokenOverrides = {
  colorPrimary: WFColors.primary,
  colorInfo: WFColors.primary,
  colorSuccess: WFColors.semantic.success,
  colorWarning: WFColors.semantic.warning,
  colorError: WFColors.semantic.error,
  colorBgContainer: WFColors.brand.white,
  colorBgElevated: WFColors.brand.white,
  colorBgLayout: WFColors.backgroundMuted,
  colorText: WFColors.text.primary,
  colorTextSecondary: WFColors.text.secondary,
  colorTextTertiary: WFColors.text.muted,
  colorBorder: WFColors.neutral.stroke,
  colorBorderSecondary: WFColors.neutral.strokeMuted,
  colorLink: WFColors.text.link,
  colorBrandLink: WFColors.text.link,
  colorBrandHeaderBg: WFColors.brand.cardinal,
  colorBrandHeaderBorder: WFColors.brand.heritageGold,
  colorBrandHeaderText: '#ffffff',
  colorBrandTertiary: WFColors.tertiary,
  colorBrandQuaternary: WFColors.quaternary,
  colorBrandFooterBg: WFColors.backgroundMuted,
  colorBrandFooterBorder: WFColors.brand.heritageGold,
  colorBrandFooterCardBg: WFColors.brand.white,
  colorBrandFooterText: WFColors.text.primary,
  colorBrandMutedText: WFColors.text.secondary,
  colorBrandBadgeBg: WFColors.primary,
  colorBrandBadgeText: '#ffffff',
  colorBrandStatusProcessingBg: '#fff3cf',
  colorBrandStatusProcessingBorder: WFColors.brand.heritageGold,
  colorBrandStatusProcessingText: '#7a5600',
  colorBrandStatusSuccessBg: '#e6f3ec',
  colorBrandStatusSuccessBorder: '#8abf9b',
  colorBrandStatusSuccessText: '#1f4f2f',
  colorBrandStatusErrorBg: '#fbeaea',
  colorBrandStatusErrorBorder: WFColors.primary,
  colorBrandStatusErrorText: '#8b0d16',
  borderRadius: 12,
  borderRadiusLG: 20,
  borderRadiusSM: 8,
  controlHeight: 44,
  controlHeightLG: 52,
  controlHeightSM: 32,
  fontSize: 15,
  fontFamily: BRAND_BODY_FONT,
  fontFamilyHeading: BRAND_HEADING_FONT,
  padding: 16,
  margin: 16,
};

export const wfLightTheme: ThemeConfig = {
  token: lightTokens,
  components: {
    Layout: {
      headerBg: WFColors.brand.cardinal,
      headerPadding: '0 48px',
      bodyBg: WFColors.brand.white,
      footerBg: WFColors.backgroundMuted,
    },
    Menu: {
      itemBg: 'transparent',
      horizontalItemSelectedColor: '#ffffff',
      horizontalItemHoverColor: '#ffffff',
      itemSelectedBg: 'transparent',
      itemSelectedColor: '#ffffff',
      itemHoverColor: '#ffffff',
      itemColor: '#fdf2f3',
    },
    Button: {
      borderRadius: 999,
      controlHeight: 44,
      controlHeightLG: 52,
      fontWeight: 600,
      paddingContentHorizontal: 28,
      primaryShadow: '0 12px 24px rgba(215, 30, 40, 0.25)',
    },
    Card: {
      borderRadiusLG: 20,
      paddingLG: 24,
      boxShadow: '0 30px 60px rgba(35, 31, 32, 0.08)',
    },
    Input: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Select: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Modal: {
      borderRadiusLG: 20,
      boxShadow: '0 30px 60px rgba(35, 31, 32, 0.2)',
    },
    Tabs: {
      itemSelectedColor: WFColors.text.primary,
      itemHoverColor: WFColors.text.primary,
      inkBarColor: WFColors.primary,
      lineWidthBold: 3,
    },
    Badge: {
      colorError: WFColors.primary,
    },
    Tag: {
      defaultBg: WFColors.backgroundMuted,
      defaultColor: WFColors.text.primary,
    },
  },
};

const darkTokens: BrandTokenOverrides = {
  colorPrimary: WFColors.secondary,
  colorInfo: WFColors.secondary,
  colorSuccess: WFColors.semantic.success,
  colorWarning: WFColors.secondary,
  colorError: '#ff4d4f',
  colorBgContainer: WFColors.neutral.offBlack,
  colorBgElevated: WFColors.neutral.charcoal,
  colorBgLayout: WFColors.neutral.offBlack,
  colorText: WFColors.neutral.warm1,
  colorTextSecondary: WFColors.neutral.warm3,
  colorTextTertiary: '#999999',
  colorBorder: '#3a3a3a',
  colorBorderSecondary: '#4a4a4a',
  colorLink: WFColors.text.link,
  colorBrandLink: WFColors.text.link,
  colorBrandHeaderBg: WFColors.neutral.offBlack,
  colorBrandHeaderBorder: '#8a6b00',
  colorBrandHeaderText: '#ffffff',
  colorBrandTertiary: WFColors.tertiary,
  colorBrandQuaternary: WFColors.quaternary,
  colorBrandFooterBg: '#1c191a',
  colorBrandFooterBorder: '#8a6b00',
  colorBrandFooterCardBg: '#262122',
  colorBrandFooterText: '#f3f1ef',
  colorBrandMutedText: '#bcb4af',
  colorBrandBadgeBg: WFColors.secondary,
  colorBrandBadgeText: '#1c191a',
  colorBrandStatusProcessingBg: '#5f4a00',
  colorBrandStatusProcessingBorder: '#f7b500',
  colorBrandStatusProcessingText: '#ffdf8a',
  colorBrandStatusSuccessBg: '#1d3324',
  colorBrandStatusSuccessBorder: '#3b8c5d',
  colorBrandStatusSuccessText: '#c6f0d2',
  colorBrandStatusErrorBg: '#3a0a0f',
  colorBrandStatusErrorBorder: '#ff5c6b',
  colorBrandStatusErrorText: '#ffb3ba',
  borderRadius: 12,
  borderRadiusLG: 20,
  borderRadiusSM: 8,
  controlHeight: 44,
  controlHeightLG: 52,
  controlHeightSM: 32,
  fontSize: 15,
  fontFamily: BRAND_BODY_FONT,
  fontFamilyHeading: BRAND_HEADING_FONT,
  padding: 16,
  margin: 16,
};

export const wfDarkTheme: ThemeConfig = {
  token: darkTokens,
  components: {
    Layout: {
      headerBg: WFColors.neutral.offBlack,
      bodyBg: WFColors.neutral.offBlack,
      footerBg: '#1c191a',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#2a2223',
      itemSelectedColor: WFColors.secondary,
      itemHoverBg: '#1f1a1a',
    },
    Button: {
      borderRadius: 999,
      controlHeight: 44,
      controlHeightLG: 52,
      fontWeight: 600,
      paddingContentHorizontal: 28,
      primaryShadow: '0 12px 24px rgba(247, 181, 0, 0.25)',
    },
    Card: {
      borderRadiusLG: 20,
      paddingLG: 24,
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)',
    },
    Input: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Select: {
      borderRadius: 12,
      controlHeight: 44,
    },
    Modal: {
      borderRadiusLG: 20,
      boxShadow: '0 30px 60px rgba(0, 0, 0, 0.6)',
    },
    Tabs: {
      itemSelectedColor: WFColors.secondary,
      itemHoverColor: WFColors.secondary,
      inkBarColor: WFColors.secondary,
    },
    Badge: {
      colorError: WFColors.secondary,
    },
    Tag: {
      defaultBg: '#2d2627',
      defaultColor: WFColors.secondary,
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
