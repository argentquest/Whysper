/**
 * localStorage Hook
 * Provides persistent state with automatic synchronization across tabs
 *
 * Adapted from ArchitectureGenStudio
 */

import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((val: T) => T)) => void, () => void] {
  // Initialize state with safe value retrieval from localStorage
  const [storedValue, setStoredValue] = useState<T>(() => {
    // Prevent localStorage access during server-side rendering
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      // Retrieve and parse existing value or use initial value
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      // Handle parsing errors gracefully
      console.error(`Error loading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Create a setter function that safely stores values in localStorage
  const setValue = useCallback(
    (value: T | ((val: T) => T)) => {
      try {
        // Support functional and direct value updates
        const valueToStore = value instanceof Function ? value(storedValue) : value;

        // Update local state immediately
        setStoredValue(valueToStore);

        // Persist to localStorage only in browser environment
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        // Log any storage-related errors
        console.error(`Error saving localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Create a function to remove the value from localStorage
  const removeValue = useCallback(() => {
    try {
      // Reset to initial state
      setStoredValue(initialValue);
      // Remove item from localStorage if possible
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      // Log any removal errors
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Implement cross-tab/window state synchronization
  useEffect(() => {
    // Skip synchronization during server-side rendering
    if (typeof window === 'undefined') {
      return;
    }

    // Listen for storage changes from other tabs/windows
    const handleStorageChange = (e: StorageEvent) => {
      // Ensure event is for this specific key
      if (e.key === key && e.newValue) {
        try {
          // Update local state with new value from storage event
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          // Log parsing errors for storage events
          console.error(`Error parsing storage event for key "${key}":`, error);
        }
      }
    };

    // Add and cleanup storage event listener
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  // Return tuple with stored value, setter, and removal function
  return [storedValue, setValue, removeValue];
}
