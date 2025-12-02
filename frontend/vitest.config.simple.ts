import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      // Exclude tests that import monaco-editor
      '**/DiagramWizard.e2e.test.tsx',
      '**/DiagramWizard.stateManagement.test.tsx',
      '**/DiagramWizard.integration.test.tsx',
    ],
  },
  resolve: {
    alias: {
      'monaco-editor': 'monaco-editor/esm/vs/editor/editor.api',
    },
  },
})
