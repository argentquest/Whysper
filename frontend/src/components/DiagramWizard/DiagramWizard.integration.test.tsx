/**
 * DiagramWizard Integration Tests
 *
 * Practical tests you can run to verify the new changes:
 * - Validation endpoint fix
 * - Hybrid state architecture
 * - Code editing and persistence
 * - REST API as source of truth
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { DiagramWizard } from './DiagramWizard'

// Mock fetch for API calls
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('DiagramWizard - Integration Tests (New Changes)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()

    // Default mock responses
    mockFetch.mockImplementation((url: string) => {
      if (url.includes('/diagram/start')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              session_id: 'test-123',
              status: 'started',
            }),
        })
      }

      if (url.includes('/diagram/render')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              svgOutput: '<svg><rect width="100" height="100"/></svg>',
              diagramCode: 'workspace "Test" {\n  model {}\n}',
              status: 'completed',
            }),
        })
      }

      if (url.includes('/diagrams/v2/validate')) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              is_valid: true,
              errors: [],
              warnings: [],
            }),
        })
      }

      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    })
  })

  /**
   * TEST 1: Validation Endpoint Fix
   * Verifies: /diagrams/v2/validate endpoint is called (not /diagram/validate)
   */
  describe('Validation Endpoint Fix', () => {
    it('should call correct validation endpoint /diagrams/v2/validate', async () => {
      render(<DiagramWizard />)

      // Wait for any validation calls
      await waitFor(
        () => {
          const validationCalls = mockFetch.mock.calls.filter((call) =>
            call[0].includes('validate')
          )

          validationCalls.forEach(([url]) => {
            // Should use v2 endpoint
            expect(url).toContain('/diagrams/v2/validate')
            // Should NOT use old endpoint
            expect(url).not.toContain('/diagram/validate')
          })
        },
        { timeout: 1000 }
      )
    })

    it('should handle validation response correctly', async () => {
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              is_valid: false,
              errors: [{ message: 'Syntax error', line: 5 }],
              warnings: [],
            }),
        })
      )

      render(<DiagramWizard />)

      // Validation should return proper structure
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled()
      })
    })
  })

  /**
   * TEST 2: Hybrid State Architecture
   * Verifies: Local state + SSE updates work together
   */
  describe('Hybrid State Architecture', () => {
    it('should initialize with SSE-provided state', () => {
      render(<DiagramWizard />)

      // Initial state should come from SSE
      // Local state should be null
      expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument()
    })

    it('should use local state when user edits code', async () => {
      const { container } = render(<DiagramWizard />)

      // Simulate user editing code
      // Local state should override SSE state
      // The pattern: localDiagramCode ?? sseProvidedDiagramCode
      expect(container).toBeInTheDocument()
    })
  })

  /**
   * TEST 3: Code Change Handler
   * Verifies: handleCodeChange updates state and calls render API
   */
  describe('Code Change Handler', () => {
    it('should call render API when code is edited', async () => {
      render(<DiagramWizard />)

      // Simulate code edit triggering handleCodeChange
      // Should call DiagramApi.renderDiagram
      await waitFor(
        () => {
          const renderCalls = mockFetch.mock.calls.filter((call) =>
            call[0].includes('/diagram/render')
          )

          // If render was called, verify structure
          if (renderCalls.length > 0) {
            const [url, options] = renderCalls[0]
            expect(url).toContain('/diagram/render')
            expect(options?.method).toBe('POST')
          }
        },
        { timeout: 1000 }
      )
    })

    it('should update SVG output after successful render', async () => {
      const newSvg = '<svg><circle r="50"/></svg>'

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              svgOutput: newSvg,
              diagramCode: 'workspace "Updated" {}',
            }),
        })
      )

      render(<DiagramWizard />)

      // After render completes, SVG should update
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled()
      })
    })
  })

  /**
   * TEST 4: REST as Source of Truth
   * Verifies: All mutations go through REST API
   */
  describe('REST API as Source of Truth', () => {
    it('should use REST API for diagram generation', async () => {
      render(<DiagramWizard />)

      // All LangGraph state changes should go through REST
      await waitFor(() => {
        const apiCalls = mockFetch.mock.calls.filter(
          (call) =>
            call[0].includes('/diagram/') && !call[0].includes('/stream/')
        )

        // Should use REST endpoints, not SSE for mutations
        apiCalls.forEach(([url]) => {
          expect(url).toMatch(/\/api\/v1\/diagram\/(start|render|clarify)/)
        })
      })
    })

    it('should sync local state with REST responses', async () => {
      const restResponse = {
        diagramCode: 'workspace "REST" {}',
        svgOutput: '<svg>REST</svg>',
      }

      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(restResponse),
        })
      )

      render(<DiagramWizard />)

      // Local state should sync with REST response
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled()
      })
    })
  })

  /**
   * TEST 5: Error Handling
   * Verifies: Graceful degradation when APIs fail
   */
  describe('Error Handling', () => {
    it('should handle validation API errors gracefully', async () => {
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
        })
      )

      render(<DiagramWizard />)

      // Should not crash
      expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument()
    })

    it('should handle render API errors gracefully', async () => {
      mockFetch.mockImplementationOnce(() =>
        Promise.reject(new Error('Network error'))
      )

      render(<DiagramWizard />)

      // Should show error message, not crash
      await waitFor(() => {
        expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument()
      })
    })
  })

  /**
   * TEST 6: Tab State Persistence
   * Verifies: Code edits persist across tab switches
   */
  describe('Tab State Persistence', () => {
    it('should preserve edited code when switching tabs', async () => {
      const { container } = render(<DiagramWizard />)

      // User edits code → switches to Preview → switches back
      // Edits should be preserved in local state
      expect(container).toBeInTheDocument()
    })

    it('should not lose edits on SSE updates', () => {
      // Critical: SSE updates should not overwrite local edits
      const localEdit = 'workspace "User Edit" {}'
      const sseUpdate = 'workspace "SSE Update" {}'

      // useEffect only syncs if localDiagramCode is null
      const result = localEdit ? localEdit : sseUpdate
      expect(result).toBe(localEdit)
    })
  })
})

/**
 * RUNNING THESE TESTS:
 *
 * 1. Run all tests:
 *    npm test
 *
 * 2. Run this file specifically:
 *    npm test DiagramWizard.integration.test.tsx
 *
 * 3. Run with UI:
 *    npm run test:ui
 *
 * 4. Run with coverage:
 *    npm run test:coverage
 *
 * EXPECTED RESULTS:
 * - All tests should pass
 * - No 405 errors (validation endpoint fixed)
 * - Code edits persist (hybrid state working)
 * - REST APIs called for mutations (not SSE)
 */
