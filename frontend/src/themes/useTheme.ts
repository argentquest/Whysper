import { useContext } from 'react';
import { ThemeContext } from './ThemeContext';

// Custom hook to access theme configuration from context
// Provides a standardized way to retrieve theme settings across the app
export const useTheme = () => {
  // Retrieve the current theme context using React's useContext hook
  // Allows components to access theme-related data without prop drilling
  const context = useContext(ThemeContext);

  // Validate that the hook is being used within a ThemeProvider
  // Prevents accidental usage outside of the theme context scope
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }

  // Return the theme context for use in components
  // Provides direct access to theme methods and properties
  return context;
};
