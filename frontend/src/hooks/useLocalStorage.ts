/**
 * localStorage Hook
 * Provides persistent state with automatic synchronization across tabs
 *
 * Adapted from ArchitectureGenStudio
 */

import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // Initialize state with value from localStorage or fallback to initial value
  const [storedValue, setStoredValue] = useState<T>(() => {
    // Check if running in browser environment
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      // Attempt to retrieve existing value from localStorage
      const item = window.localStorage.getItem(key);
      // Parse stored value or use initial value if no item exists
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      // Log any parsing errors and return initial value
      console.error(`Error loading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Create a setter function that persists values to localStorage
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        // Support both direct values and function updates
        const valueToStore = value instanceof Function ? value(storedValue) : value;

        // Update local state
        setStoredValue(valueToStore);

        // Persist to localStorage if in browser environment
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        // Log any storage errors
        console.error(`Error saving localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Create a function to remove the value from localStorage
  const removeValue = useCallback(() => {
    try {
      // Reset to initial value
      setStoredValue(initialValue);
      // Remove item from localStorage if in browser environment
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      // Log any removal errors
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Sync state across different tabs/windows
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      return;
    }

    // Handle storage events from other tabs/windows
    const handleStorageChange = (e: StorageEvent) => {
      // Check if event is for this specific key
      if (e.key === key && e.newValue) {
        try {
          // Update local state with new value from storage event
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          // Log any parsing errors
          console.error(`Error parsing storage event for key "${key}":`, error);
        }
      }
    };

    // Add event listener for storage changes
    window.addEventListener('storage', handleStorageChange);
    // Cleanup listener on component unmount
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  // Return tuple with stored value, setter, and remove function
  return [storedValue, setValue, removeValue];
}