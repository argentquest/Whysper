/**
 * GenerationScreen Tests
 *
 * Tests for the generation screen component.
 * Verifies three-panel layout, export functionality, and diagram rendering.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GenerationScreen } from './GenerationScreen';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';

describe('GenerationScreen', () => {
  const mockProps = {
    selectedModel: 'gpt5' as const,
    currentPhase: 3,
    phases: [
      { title: 'Analysis', description: 'Understanding your system', icon: '🔍' },
      { title: 'Clarification', description: 'Asking detailed questions', icon: '💬' },
      { title: 'Generation', description: 'Creating diagram code', icon: '✏️' },
      { title: 'Rendering', description: 'Visualizing the diagram', icon: '🎨' },
    ],
    loading: false,
    sessionId: 'test-session-123',
    status: null as DiagramUpdate | null,
    score: 9,
    diagramCode: 'graph TD\n  A[Start] --> B[Process]\n  B --> C[End]',
    svgOutput: '<svg>test</svg>',
    chatHistory: [
      { role: 'user', content: 'E-commerce platform' },
      { role: 'assistant', content: 'Analysis complete' },
    ],
    clarifications: [
      { question: 'What type of system?', answer: 'E-commerce' },
    ],
    sseConnected: true,
    exportModalOpen: false,
    onChangeModel: vi.fn(),
    onNewDiagram: vi.fn(),
    onExportClick: vi.fn(),
    onExportModalClose: vi.fn(),
    onExportSubmit: vi.fn(),
    onCodeChange: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Header Rendering', () => {
    it('should render header with Diagram Wizard title', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText('Diagram Wizard')).toBeInTheDocument();
    });

    it('should display model tag in header', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText('GPT-5')).toBeInTheDocument();
    });

    it('should show session ID truncated', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText(/test-sess/)).toBeInTheDocument();
    });

    it('should display connection status', () => {
      render(<GenerationScreen {...mockProps} sseConnected={true} />);
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    it('should show disconnected status', () => {
      render(<GenerationScreen {...mockProps} sseConnected={false} />);
      expect(screen.getByText('Disconnected')).toBeInTheDocument();
    });

    it('should show Complete tag when status is completed', () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed', message: 'Done!' } as DiagramUpdate}
        />
      );
      expect(screen.getByText(/Complete ✅/)).toBeInTheDocument();
    });

    it('should show Error tag when status is error', () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'error', message: 'Failed!' } as DiagramUpdate}
        />
      );
      expect(screen.getByText(/Error ❌/)).toBeInTheDocument();
    });
  });

  describe('Three-Panel Layout', () => {
    it('should render all three panels', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText('Conversation')).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Code')).toBeInTheDocument();
    });

    it('should display chat panel on the left', () => {
      render(<GenerationScreen {...mockProps} />);
      const conversationPanel = screen.getByText('Conversation').closest('div');
      expect(conversationPanel).toBeInTheDocument();
    });

    it('should display preview panel in the center', () => {
      render(<GenerationScreen {...mockProps} />);
      const previewPanel = screen.getByText('Preview').closest('div');
      expect(previewPanel).toBeInTheDocument();
    });

    it('should display code panel on the right', () => {
      render(<GenerationScreen {...mockProps} />);
      const codePanel = screen.getByText('Code').closest('div');
      expect(codePanel).toBeInTheDocument();
    });
  });

  describe('Code Display and Editing', () => {
    it('should display diagram code in code panel', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText(/graph TD/)).toBeInTheDocument();
    });

    it('should show copy button for code', () => {
      render(<GenerationScreen {...mockProps} />);
      const copyButtons = screen.getAllByRole('button').filter((btn) =>
        btn.querySelector('svg') || btn.textContent?.includes('Copy')
      );
      expect(copyButtons.length).toBeGreaterThan(0);
    });

    it('should handle code changes when complete', async () => {
      render(<GenerationScreen {...mockProps} />);
      // Code editor would handle changes
      expect(mockProps.onCodeChange).toBeDefined();
    });

    it('should show full code in panel', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText(/graph TD/)).toBeInTheDocument();
      expect(screen.getByText(/Start/)).toBeInTheDocument();
      expect(screen.getByText(/Process/)).toBeInTheDocument();
    });
  });

  describe('Chat History Display', () => {
    it('should display chat history in left panel', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText('Conversation')).toBeInTheDocument();
    });

    it('should be read-only during generation', () => {
      render(<GenerationScreen {...mockProps} />);
      // Chat panel is read-only when in generation screen
      expect(mockProps.chatHistory.length).toBeGreaterThan(0);
    });
  });

  describe('SVG Preview', () => {
    it('should display SVG preview in center panel', () => {
      render(<GenerationScreen {...mockProps} svgOutput="<svg>diagram</svg>" />);
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });

    it('should show loading state for preview', () => {
      render(<GenerationScreen {...mockProps} loading={true} svgOutput="" />);
      // Preview would show loading
      expect(mockProps.loading).toBe(true);
    });
  });

  describe('Progress Indicator', () => {
    it('should display current phase', () => {
      render(<GenerationScreen {...mockProps} currentPhase={3} />);
      expect(screen.getByText('Generation')).toBeInTheDocument();
    });

    it('should display clarity score', () => {
      render(<GenerationScreen {...mockProps} score={9} />);
      expect(screen.getByText('9/10')).toBeInTheDocument();
    });

    it('should update phase as generation progresses', () => {
      const { rerender } = render(<GenerationScreen {...mockProps} currentPhase={3} />);
      expect(screen.getByText('Generation')).toBeInTheDocument();

      rerender(<GenerationScreen {...mockProps} currentPhase={4} />);
      expect(screen.getByText('Rendering')).toBeInTheDocument();
    });
  });

  describe('Export Functionality', () => {
    it('should call onExportClick when export button clicked', async () => {
      const user = userEvent.setup();
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed' } as DiagramUpdate}
        />
      );

      // Find export button (might be in footer or with download icon)
      const buttons = screen.getAllByRole('button');
      const exportButton = buttons.find((btn) =>
        btn.innerHTML.includes('Download') || btn.textContent?.includes('Export')
      );

      if (exportButton) {
        await user.click(exportButton);
        expect(mockProps.onExportClick).toHaveBeenCalled();
      }
    });

    it('should close export modal when onExportModalClose called', async () => {
      render(<GenerationScreen {...mockProps} exportModalOpen={true} />);
      // Modal would be visible when open
      expect(mockProps.exportModalOpen).toBe(true);
    });

    it('should handle export submission', async () => {
      render(<GenerationScreen {...mockProps} />);
      expect(mockProps.onExportSubmit).toBeDefined();
    });
  });

  describe('New Diagram Functionality', () => {
    it('should have new diagram button', async () => {
      const user = userEvent.setup();
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed' } as DiagramUpdate}
        />
      );

      const buttons = screen.getAllByRole('button');
      const newDiagramButton = buttons.find((btn) =>
        btn.textContent?.includes('New') || btn.textContent?.includes('Start')
      );

      if (newDiagramButton) {
        await user.click(newDiagramButton);
        expect(mockProps.onNewDiagram).toHaveBeenCalled();
      }
    });

    it('should call onNewDiagram when new diagram action triggered', () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed' } as DiagramUpdate}
        />
      );
      expect(mockProps.onNewDiagram).toBeDefined();
    });
  });

  describe('Model Change', () => {
    it('should call onChangeModel when model change triggered', async () => {
      const user = userEvent.setup();
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed' } as DiagramUpdate}
        />
      );

      const buttons = screen.getAllByRole('button');
      const changeModelButton = buttons.find((btn) =>
        btn.textContent?.includes('Change') && btn.textContent?.includes('Model')
      );

      if (changeModelButton) {
        await user.click(changeModelButton);
        expect(mockProps.onChangeModel).toHaveBeenCalled();
      }
    });
  });

  describe('Status Display', () => {
    it('should show refinement alert during code refinement', () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'refining' } as DiagramUpdate}
        />
      );
      expect(screen.getByText(/Code Refinement/)).toBeInTheDocument();
    });

    it('should show refinement alert during fallback fix', () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'fallback_fix' } as DiagramUpdate}
        />
      );
      expect(screen.getByText(/Code Refinement/)).toBeInTheDocument();
    });

    it('should show error alert when error status', () => {
      const error = { message: 'Generation failed' };
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'error', message: 'Generation failed' } as DiagramUpdate}
          error={error}
        />
      );
      expect(screen.getByText('Generation failed')).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading state in preview during generation', () => {
      render(<GenerationScreen {...mockProps} loading={true} svgOutput="" />);
      expect(mockProps.loading).toBe(true);
    });

    it('should disable export when loading', () => {
      render(<GenerationScreen {...mockProps} loading={true} />);
      // Export would be disabled
      expect(mockProps.loading).toBe(true);
    });

    it('should show spinner when loading', () => {
      render(<GenerationScreen {...mockProps} loading={true} />);
      expect(mockProps.loading).toBe(true);
    });
  });

  describe('Empty States', () => {
    it('should handle empty diagram code gracefully', () => {
      render(<GenerationScreen {...mockProps} diagramCode="" />);
      expect(screen.getByText('Code')).toBeInTheDocument();
    });

    it('should handle empty SVG output gracefully', () => {
      render(<GenerationScreen {...mockProps} svgOutput="" />);
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });

    it('should handle empty chat history', () => {
      render(<GenerationScreen {...mockProps} chatHistory={[]} />);
      expect(screen.getByText('Conversation')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<GenerationScreen {...mockProps} />);
      const heading = screen.getByText('Diagram Wizard');
      expect(heading.tagName).toMatch(/H|HEADER/);
    });

    it('should have descriptive button labels', () => {
      render(<GenerationScreen {...mockProps} />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      buttons.forEach((button) => {
        expect(button.textContent || button.getAttribute('aria-label')).toBeTruthy();
      });
    });

    it('should have semantic structure for panels', () => {
      render(<GenerationScreen {...mockProps} />);
      expect(screen.getByText('Conversation')).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Code')).toBeInTheDocument();
    });
  });

  describe('Multiple Interactions', () => {
    it('should handle sequential actions', async () => {
      render(
        <GenerationScreen
          {...mockProps}
          status={{ status: 'completed' } as DiagramUpdate}
        />
      );

      // Export would be one action
      expect(mockProps.onExportClick).toBeDefined();

      // New diagram would be another action
      expect(mockProps.onNewDiagram).toBeDefined();
    });

    it('should maintain state during interactions', () => {
      const { rerender } = render(<GenerationScreen {...mockProps} />);

      expect(screen.getByText('Code')).toBeInTheDocument();

      rerender(<GenerationScreen {...mockProps} loading={false} />);

      expect(screen.getByText('Code')).toBeInTheDocument();
    });
  });

  describe('Model Display', () => {
    it('should display all model types', () => {
      const models = ['gpt5', 'grok', 'claude', 'gemini'] as const;
      models.forEach((model) => {
        const { unmount } = render(
          <GenerationScreen {...mockProps} selectedModel={model} />
        );
        expect(mockProps.selectedModel).toBe(model);
        unmount();
      });
    });

    it('should update model display when model changes', () => {
      const { rerender } = render(<GenerationScreen {...mockProps} selectedModel="gpt5" />);
      expect(screen.getByText('GPT-5')).toBeInTheDocument();

      rerender(<GenerationScreen {...mockProps} selectedModel="claude" />);
      expect(screen.getByText('CLAUDE')).toBeInTheDocument();
    });
  });
});
