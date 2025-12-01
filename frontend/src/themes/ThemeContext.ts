/**
 * ThemeContext Theme Configuration
 *
 * Theme-related configuration and utilities for the application.
 */
import { createContext } from 'react'

import { type ThemeKey } from './antd-themes'

/**
 * ThemeContextType type definition
 *
 * Describes the structure and properties of ThemeContextType
 */
export interface ThemeContextType {
  theme: ThemeKey
  toggleTheme: () => void
  setTheme: (theme: ThemeKey) => void
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined)
