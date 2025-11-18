import { createContext } from 'react';
import { type ThemeKey } from './antd-themes';

// Define the contract for theme management with type safety
export interface ThemeContextType {
  theme: ThemeKey; // Current active theme identifier
  toggleTheme: () => void; // Method to switch between light/dark themes
  setTheme: (theme: ThemeKey) => void; // Method to explicitly set a specific theme
}

// Initialize a React context for theme management with optional undefined initial state
export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);
```

Key changes:
- Added concise inline comments explaining the purpose of each section
- Kept all original code structure and types intact
- Used // style comments
- Focused on explaining the logical intent of the code