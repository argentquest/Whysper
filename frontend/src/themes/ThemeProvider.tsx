import React, { useEffect, useState } from 'react';
import { ConfigProvider } from 'antd';
import { getThemeConfig, type ThemeMode } from './antd-themes';
import { ThemeContext, type ThemeContextType } from './ThemeContext';

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage or default to light
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const savedTheme = localStorage.getItem('whyspercode-theme');
    return (savedTheme as ThemeMode) || 'light';
  });

  // Update document data-theme attribute and localStorage when theme changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('whyspercode-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (newTheme: ThemeMode) => {
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