/**
 * useTheme Theme Configuration
 * 
 * Theme-related configuration and utilities for the application.
 */
import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

/**
 * Custom React hook for theme functionality
 */
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};