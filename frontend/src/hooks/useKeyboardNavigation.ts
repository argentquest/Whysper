/**
 * useKeyboardNavigation Hook
 *
 * Provides keyboard navigation support for the application.
 * Implements WCAG 2.1 AA keyboard accessibility requirements.
 *
 * Features:
 * - Tab navigation
 * - Escape key handling
 * - Arrow key navigation
 * - Enter/Space activation
 */

import { useEffect, useCallback } from 'react';

export interface KeyboardNavigationOptions {
  onEscape?: () => void;
  onEnter?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  enabled?: boolean;
}

export function useKeyboardNavigation(options: KeyboardNavigationOptions) {
  // Destructure options with default enabled state
  const {
    onEscape,
    onEnter,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    enabled = true,
  } = options;

  // Create a memoized key handler to prevent unnecessary re-renders
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Exit if keyboard navigation is disabled
      if (!enabled) return;

      // Switch statement to handle different keyboard events
      switch (event.key) {
        case 'Escape':
          // Prevent default and call Escape handler if provided
          if (onEscape) {
            event.preventDefault();
            onEscape();
          }
          break;

        case 'Enter':
          // Prevent default and call Enter handler if provided
          if (onEnter) {
            event.preventDefault();
            onEnter();
          }
          break;

        case 'ArrowUp':
          // Prevent default and call ArrowUp handler if provided
          if (onArrowUp) {
            event.preventDefault();
            onArrowUp();
          }
          break;

        case 'ArrowDown':
          // Prevent default and call ArrowDown handler if provided
          if (onArrowDown) {
            event.preventDefault();
            onArrowDown();
          }
          break;

        case 'ArrowLeft':
          // Prevent default and call ArrowLeft handler if provided
          if (onArrowLeft) {
            event.preventDefault();
            onArrowLeft();
          }
          break;

        case 'ArrowRight':
          // Prevent default and call ArrowRight handler if provided
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

  // Add and remove global keydown event listener based on enabled state
  useEffect(() => {
    // Exit if keyboard navigation is disabled
    if (!enabled) return;

    // Add global keydown listener
    window.addEventListener('keydown', handleKeyDown);
    // Clean up listener on unmount or state change
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [enabled, handleKeyDown]);
}

/**
 * Focus management utilities
 */
export const focusUtils = {
  /**
   * Focus the first focusable element in a container
   */
  focusFirst: (container: HTMLElement | null) => {
    // Exit if no container provided
    if (!container) return;

    // Select all focusable elements
    const focusable = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    // Focus the first focusable element if available
    if (focusable.length > 0) {
      focusable[0].focus();
    }
  },

  /**
   * Trap focus within a container (for modals, dialogs)
   */
  trapFocus: (container: HTMLElement, event: KeyboardEvent) => {
    // Only handle Tab key events
    if (event.key !== 'Tab') return;

    // Select all focusable and non-disabled elements
    const focusable = Array.from(
      container.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );

    // Exit if no focusable elements
    if (focusable.length === 0) return;

    // Get first and last focusable elements
    const firstFocusable = focusable[0];
    const lastFocusable = focusable[focusable.length - 1];

    // Handle circular focus navigation
    if (event.shiftKey) {
      // Shift + Tab: if on first element, wrap to last
      if (document.activeElement === firstFocusable) {
        event.preventDefault();
        lastFocusable.focus();
      }
    } else {
      // Tab: if on last element, wrap to first
      if (document.activeElement === lastFocusable) {
        event.preventDefault();
        firstFocusable.focus();
      }
    }
  },

  /**
   * Restore focus to previous element
   */
  restoreFocus: (element: HTMLElement | null) => {
    // Restore focus only if element exists in document
    if (element && document.body.contains(element)) {
      element.focus();
    }
  },
};