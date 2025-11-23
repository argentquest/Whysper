import { useEffect, useCallback } from 'react';

/**
 * KeyboardNavigationOptions interface
 *
 * Configuration options for the useKeyboardNavigation hook.
 * @interface KeyboardNavigationOptions
 * @property {Function} [onEscape] - Callback for Escape key press
 * @property {Function} [onEnter] - Callback for Enter key press
 * @property {Function} [onArrowUp] - Callback for ArrowUp key press
 * @property {Function} [onArrowDown] - Callback for ArrowDown key press
 * @property {Function} [onArrowLeft] - Callback for ArrowLeft key press
 * @property {Function} [onArrowRight] - Callback for ArrowRight key press
 * @property {boolean} [enabled] - Whether keyboard navigation is enabled (default: true)
 */
export interface KeyboardNavigationOptions {
  onEscape?: () => void;
  onEnter?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  enabled?: boolean;
}

/**
 * useKeyboardNavigation hook
 *
 * A custom hook to handle keyboard navigation events globally.
 *
 * @param {KeyboardNavigationOptions} options - Configuration options
 */
export function useKeyboardNavigation(options: KeyboardNavigationOptions) {
  // Destructure options with default settings to simplify configuration
  const {
    onEscape,
    onEnter,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    enabled = true,
  } = options;

  // Create a memoized key handler to optimize performance and prevent unnecessary re-renders
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Immediately exit if keyboard navigation is globally disabled
      if (!enabled) return;

      // Switch statement provides clean, centralized key event handling
      switch (event.key) {
        case 'Escape':
          // Prevent default browser behavior and call custom escape handler
          if (onEscape) {
            event.preventDefault();
            onEscape();
          }
          break;

        case 'Enter':
          // Prevent default and call enter handler if configured
          if (onEnter) {
            event.preventDefault();
            onEnter();
          }
          break;

        case 'ArrowUp':
          // Prevent default browser scroll and call up navigation handler
          if (onArrowUp) {
            event.preventDefault();
            onArrowUp();
          }
          break;

        case 'ArrowDown':
          // Prevent default browser scroll and call down navigation handler
          if (onArrowDown) {
            event.preventDefault();
            onArrowDown();
          }
          break;

        case 'ArrowLeft':
          // Prevent default browser scroll and call left navigation handler
          if (onArrowLeft) {
            event.preventDefault();
            onArrowLeft();
          }
          break;

        case 'ArrowRight':
          // Prevent default browser scroll and call right navigation handler
          if (onArrowRight) {
            event.preventDefault();
            onArrowRight();
          }
          break;

        default:
          break;
      }
    },
    [enabled, onEscape, onEnter, onArrowUp, onArrowDown, onArrowLeft, onArrowRight]
  );

  // Use effect to add/remove global keyboard event listener based on enabled state
  useEffect(() => {
    // Skip event listener if navigation is disabled
    if (!enabled) return;

    // Attach global keydown listener for entire application
    window.addEventListener('keydown', handleKeyDown);
    // Clean up listener to prevent memory leaks
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);
}

// Utility functions for managing focus in complex UI interactions
/**
 * Focus utilities for managing keyboard focus
 */
export const focusUtils = {
  // Find and focus the first interactive element in a given container
  /**
   * Focuses the first interactive element within a container.
   * @param {HTMLElement | null} container - The container element to search within
   */
  focusFirst: (container: HTMLElement | null) => {
    // Validate container exists before proceeding
    if (!container) return;

    // Select wide range of focusable elements using CSS selectors
    const focusable = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    // Focus first element if any are found
    if (focusable.length > 0) {
      focusable[0].focus();
    }
  },

  // Create circular focus navigation within a specific container
  /**
   * Traps focus within a container, cycling between first and last focusable elements.
   * @param {HTMLElement} container - The container element to trap focus within
   * @param {KeyboardEvent} event - The keyboard event triggering the focus trap
   */
  trapFocus: (container: HTMLElement, event: KeyboardEvent) => {
    // Only process Tab key events for focus trapping
    if (event.key !== 'Tab') return;

    // Find all focusable and non-disabled elements in container
    const focusable = Array.from(
      container.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );

    // Exit if no focusable elements are present
    if (focusable.length === 0) return;

    // Identify first and last focusable elements for circular navigation
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    // Implement circular focus navigation with Shift+Tab and Tab
    if (event.shiftKey) {
      // Wrap focus to last element when Shift+Tabbing from first element
      if (document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    } else {
      // Wrap focus to first element when Tabbing from last element
      if (document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  },

  // Safely restore focus to a previously stored element
  /**
   * Restores focus to a specific element if it still exists in the DOM.
   * @param {HTMLElement | null} element - The element to restore focus to
   */
  restoreFocus: (element: HTMLElement | null) => {
    // Ensure element exists and is still in the document before focusing
    if (element && document.body.contains(element)) {
      element.focus();
    }
  },
};
