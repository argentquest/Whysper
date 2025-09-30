import { createContext } from 'react';
import { type ThemeKey } from './antd-themes';

export interface ThemeContextType {
  theme: ThemeKey;
  toggleTheme: () => void;
  setTheme: (theme: ThemeKey) => void;
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);