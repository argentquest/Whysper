/**
 * setup Tests
 * 
 * Test suite for setup functionality.
 */
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup React testing library after each test to prevent state leakage between tests
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia to simulate media query behavior in tests without a real browser environment
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Create a mock IntersectionObserver to simulate browser intersection detection without actual DOM rendering
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

// Create a mock ResizeObserver to simulate browser resize detection without actual DOM rendering
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any;

// Create a mock localStorage implementation to simulate browser storage interactions during testing
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    // Retrieve an item from the mock storage
    getItem: (key: string) => store[key] || null,
    // Set an item in the mock storage
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    // Remove an item from the mock storage
    removeItem: (key: string) => {
      delete store[key];
    },
    // Clear entire mock storage
    clear: () => {
      store = {};
    },
  };
})();

// Replace browser's localStorage with mock implementation for consistent testing
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Add scrollIntoView mock if not natively supported to prevent test errors when scrolling is called
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = vi.fn();
}

// Mock EventSource to simulate Server-Sent Events (SSE) interactions during testing
global.EventSource = class EventSource {
  url: string;
  onopen: ((this: EventSource, ev: Event) => any) | null = null;
  onmessage: ((this: EventSource, ev: MessageEvent) => any) | null = null;
  onerror: ((this: EventSource, ev: Event) => any) | null = null;
  readyState: number = 0;

  constructor(url: string) {
    this.url = url;
  }

  close() {}
  addEventListener() {}
  removeEventListener() {}
  dispatchEvent() {
    return true;
  }
} as any;

// Optional: Suppress console errors during testing to reduce noise in test output
// vi.spyOn(console, 'error').mockImplementation(() => {});
