import React, { useEffect, useState } from 'react';
import { ConfigProvider } from 'antd';
import { getThemeConfig, type ThemeKey, themes } from './antd-themes';
import { ThemeContext, type ThemeContextType } from './ThemeContext';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default to light
  const [theme, setThemeState] = useState<ThemeKey>(() => {
    const savedTheme = localStorage.getItem('Whysper-theme');
    // Validate saved theme exists in our themes object
    if (savedTheme && savedTheme in themes) {
      console.log(`🎨 ThemeProvider: Loading saved theme "${savedTheme}"`);
      return savedTheme as ThemeKey;
    }
    console.log(`🎨 ThemeProvider: No valid saved theme found, defaulting to "modernGradient"`);
    return 'modernGradient';
  });

  // Update document data-theme attribute and localStorage when theme changes
  useEffect(() => {
    console.log(`🎨 ThemeProvider: Applying theme "${theme}"`);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('Whysper-theme', theme);

    // Log theme configuration for debugging
    const themeConfig = getThemeConfig(theme);
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