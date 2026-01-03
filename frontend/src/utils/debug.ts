/**
 * Debug Utility Module
 *
 * Provides conditional logging that can be disabled in production.
 * All console.log statements should be replaced with debug() calls.
 */

// Enable debug logging based on environment
const DEBUG_ENABLED = import.meta.env.DEV || import.meta.env.VITE_DEBUG === 'true'

/**
 * Conditional debug logger
 * Only logs in development mode or when VITE_DEBUG=true
 *
 * @param args - Arguments to log
 */
export const debug = (...args: any[]) => {
  if (DEBUG_ENABLED) {
    console.log(...args)
  }
}

/**
 * Debug info logger (always shows in dev)
 */
export const debugInfo = (...args: any[]) => {
  if (DEBUG_ENABLED) {
    console.info(...args)
  }
}

/**
 * Debug warning logger (always shows in dev)
 */
export const debugWarn = (...args: any[]) => {
  if (DEBUG_ENABLED) {
    console.warn(...args)
  }
}

/**
 * Debug error logger (always shows, even in production)
 */
export const debugError = (...args: any[]) => {
  console.error(...args)
}

/**
 * Debug group logger
 */
export const debugGroup = (label: string) => {
  if (DEBUG_ENABLED) {
    console.group(label)
  }
}

/**
 * Debug group end
 */
export const debugGroupEnd = () => {
  if (DEBUG_ENABLED) {
    console.groupEnd()
  }
}

/**
 * Expose debug helpers to window for debugging in browser console
 * Only in development mode
 */
if (DEBUG_ENABLED && typeof window !== 'undefined') {
  (window as any).__DEBUG__ = {
    enable: () => sessionStorage.setItem('debug', 'true'),
    disable: () => sessionStorage.removeItem('debug'),
    isEnabled: () => DEBUG_ENABLED,
  }
}
