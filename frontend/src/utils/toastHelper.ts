/**
 * Toast Helper - Extract and display toast notifications from SSE messages
 *
 * Allows backend to trigger toasts by including special keywords in messages:
 * - TOASTINFO: message text
 * - TOASTSUCCESS: message text
 * - TOASTERROR: message text
 * - TOASTWARNING: message text
 * - TOASTLOADING: message text
 *
 * This helper works globally across the entire application by using Ant Design's
 * static message API, so no message instance needs to be passed.
 */

import { message as antdMessage } from 'antd'
import type { MessageInstance } from 'antd/es/message/interface'

const TOAST_KEYWORDS = {
  TOASTINFO: 'info',
  TOASTSUCCESS: 'success',
  TOASTERROR: 'error',
  TOASTWARNING: 'warning',
  TOASTLOADING: 'loading',
} as const

/**
 * Parse message for toast commands and display if found (using static API)
 *
 * @param messageText - The message text to parse
 * @returns true if a toast command was found and displayed, false otherwise
 *
 * @example
 * parseAndShowToast("TOASTINFO: Analyzing diagram...")
 * // Shows info toast: "Analyzing diagram..."
 *
 * parseAndShowToast("TOASTERROR: Validation failed!")
 * // Shows error toast: "Validation failed!"
 *
 * parseAndShowToast("Regular message without toast")
 * // Returns false, no toast shown
 */
export function parseAndShowToast(messageText: string): boolean
/**
 * Parse message for toast commands and display if found (with message instance)
 *
 * @param messageText - The message text to parse
 * @param messageApi - Ant Design message API instance (optional)
 * @returns true if a toast command was found and displayed, false otherwise
 */
export function parseAndShowToast(messageText: string, messageApi?: MessageInstance): boolean
export function parseAndShowToast(messageText: string, messageApi?: MessageInstance): boolean {
  if (!messageText || typeof messageText !== 'string') {
    return false
  }

  // Use provided message API or fall back to static API
  const messageInstance = messageApi || antdMessage

  // Check for each toast keyword
  for (const [keyword, type] of Object.entries(TOAST_KEYWORDS)) {
    if (messageText.includes(keyword)) {
      // Extract the message after the keyword
      const parts = messageText.split(keyword)
      if (parts.length > 1) {
        // Get text after keyword, removing leading colon/whitespace
        const toastMessage = parts[1].replace(/^[:\s]+/, '').trim()

        if (toastMessage) {
          // Show the appropriate toast type
          messageInstance[type](toastMessage)
          console.log(`🍞 [Toast] ${type.toUpperCase()}: ${toastMessage}`)
          return true
        }
      }
    }
  }

  return false
}

/**
 * Extract toast command from message without displaying
 * Useful for logging or conditional display
 *
 * @param message - The message text to parse
 * @returns Object with toast type and message, or null if no toast command found
 */
export function extractToastCommand(message: string): { type: string; message: string } | null {
  if (!message || typeof message !== 'string') {
    return null
  }

  for (const [keyword, type] of Object.entries(TOAST_KEYWORDS)) {
    if (message.includes(keyword)) {
      const parts = message.split(keyword)
      if (parts.length > 1) {
        const toastMessage = parts[1].replace(/^[:\s]+/, '').trim()
        if (toastMessage) {
          return { type, message: toastMessage }
        }
      }
    }
  }

  return null
}

/**
 * Check if a message contains a toast command
 *
 * @param message - The message text to check
 * @returns true if message contains a toast keyword
 */
export function hasToastCommand(message: string): boolean {
  if (!message || typeof message !== 'string') {
    return false
  }

  return Object.keys(TOAST_KEYWORDS).some((keyword) => message.includes(keyword))
}
