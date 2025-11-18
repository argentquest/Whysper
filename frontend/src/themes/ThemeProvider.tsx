/**
 * ThemeProvider Theme Configuration
 * 
 * Theme-related configuration and utilities for the application.
 */
import React, { useEffect, useState } from 'react';
import { ConfigProvider } from 'antd';
import { getThemeConfig, type ThemeKey, themes } from './antd-themes';
import { ThemeContext, type ThemeContextType } from './ThemeContext';

/**
 * ThemeProviderProps type definition
 * 
 * Describes the structure and properties of ThemeProviderProps
 */
interface ThemeProviderProps {
  children: React.ReactNode;
}

const DEFAULT_THEME: ThemeKey = 'light';
const CSS_BRAND_VARS = [
  '--wf-header-bg',
  '--wf-header-border',
  '--wf-header-text',
  '--wf-footer-bg',
  '--wf-footer-border',
  '--wf-footer-card-bg',
  '--wf-footer-text',
  '--wf-footer-muted',
  '--wf-link-color',
  '--wf-font-body',
  '--wf-font-heading',
  '--wf-app-bg',
  '--wf-column-bg',
  '--wf-column-border',
] as const;

const applyCssVariables = (token: Record<string, unknown>) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const cssValues: Record<(typeof CSS_BRAND_VARS)[number], string> = {
    '--wf-header-bg': String(token.colorBrandHeaderBg ?? token.colorBrandHeader ?? token.colorPrimary ?? '#d71e28'),
    '--wf-header-border': String(token.colorBrandHeaderBorder ?? token.colorPrimary ?? '#f7b500'),
    '--wf-header-text': String(token.colorBrandHeaderText ?? '#ffffff'),
    '--wf-footer-bg': String(token.colorBrandFooterBg ?? token.colorBgLayout ?? '#f8f4f1'),
    '--wf-footer-border': String(token.colorBrandFooterBorder ?? token.colorBorder ?? '#f7b500'),
    '--wf-footer-card-bg': String(token.colorBrandFooterCardBg ?? token.colorBgContainer ?? '#ffffff'),
    '--wf-footer-text': String(token.colorBrandFooterText ?? token.colorText ?? '#231f20'),
    '--wf-footer-muted': String(token.colorBrandMutedText ?? token.colorTextSecondary ?? '#5d5550'),
    '--wf-link-color': String(token.colorBrandLink ?? token.colorLink ?? token.colorPrimary ?? '#004c97'),
    '--wf-font-body': String(token.fontFamily ?? '"Wells Fargo Sans", Arial, sans-serif'),
    '--wf-font-heading': String(token.fontFamilyHeading ?? token.fontFamily ?? '"Wells Fargo Sans", Arial, sans-serif'),
    '--wf-app-bg': String(token.colorBgLayout ?? '#f5f5f5'),
    '--wf-column-bg': String(token.colorBgContainer ?? '#fafafa'),
    '--wf-column-border': String(token.colorBorder ?? '#e8e8e8'),
  };

  CSS_BRAND_VARS.forEach((cssVar) => {
    root.style.setProperty(cssVar, cssValues[cssVar]);
  });
};

/**
 * ThemeProvider function
 */
export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default
  const [theme, setThemeState] = useState<ThemeKey>(() => {
    const savedTheme = localStorage.getItem('Whysper-theme');
    if (savedTheme && savedTheme in themes) {
      console.log(`🎨 ThemeProvider: Loading saved theme "${savedTheme}"`);
      return savedTheme as ThemeKey;
    }
    console.log(`🎨 ThemeProvider: No valid saved theme found, defaulting to "${DEFAULT_THEME}"`);
    return DEFAULT_THEME;
  });

  // Update document data-theme attribute and localStorage when theme changes
  useEffect(() => {
    console.log(`🎨 ThemeProvider: Applying theme "${theme}"`);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('Whysper-theme', theme);

    const themeConfig = getThemeConfig(theme);
    applyCssVariables(themeConfig.token as Record<string, unknown>);
    console.log(`🎨 ThemeProvider: Theme config applied:`, {
      algorithm: themeConfig.algorithm,
      primaryColor: themeConfig.token.colorPrimary,
      bgColor: themeConfig.token.colorBgContainer,
    });
  }, [theme]);

  const toggleTheme = () => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (newTheme: ThemeKey) => {
    setThemeState(newTheme);
  };

  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <ConfigProvider theme={getThemeConfig(theme)}>
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  );
};
