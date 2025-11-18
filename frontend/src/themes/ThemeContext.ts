/**
 * ThemeContext Theme Configuration
 * 
 * Theme-related configuration and utilities for the application.
 */
import { createContext } from 'react';
import { type ThemeKey } from './antd-themes';

/**
 * ThemeContextType defines the shape of theme management context
 * Provides type safety and ensures consistent theme interaction methods
 */
export interface ThemeContextType {
  theme: ThemeKey; // Current active theme identifier
  toggleTheme: () => void; // Method to switch between light/dark themes
  setTheme: (theme: ThemeKey) => void; // Method to explicitly set a specific theme
}

// Create a context for theme management with optional initial value
export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);