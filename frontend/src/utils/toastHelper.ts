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
import React from 'react'

const TOAST_KEYWORDS = {
  TOASTINFO: 'info',
  TOASTSUCCESS: 'success',
  TOASTERROR: 'error',
  TOASTWARNING: 'warning',
  TOASTLOADING: 'loading',
} as const

/**
 * Parse message for toast commands and display if found (using static API)
 */
export function parseAndShowToast(messageText: string): boolean
/**
 * Parse message for toast commands and display if found (with message instance)
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
          // Show the appropriate toast type with larger styling and longer duration
          messageInstance[type]({
            content: React.createElement('div', { style: { fontSize: 16, minWidth: 480 } }, toastMessage),
            duration: 6,
            style: { minWidth: 480 },
          })
          console.log(`[Toast] ${type.toUpperCase()}: ${toastMessage}`)
          return true
        }
      }
    }
  }

  return false
}

/**
 * Extract toast command from message without displaying
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
 */
export function hasToastCommand(message: string): boolean {
  if (!message || typeof message !== 'string') {
    return false
  }

  return Object.keys(TOAST_KEYWORDS).some((keyword) => message.includes(keyword))
}
