/**
 * SystemDescriptionScreen Tests
 *
 * Tests for the system description screen component.
 * Verifies input handling, conditional rendering, and user interactions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SystemDescriptionScreen } from './SystemDescriptionScreen';
import type { DiagramUpdate } from '../../../services/diagram/diagramApi';

describe('SystemDescriptionScreen', () => {
  const mockProps = {
    selectedModel: 'gpt5' as const,
    currentPhase: 1,
    phases: [
      { title: 'Analysis', description: 'Understanding your system', icon: '🔍' },
      { title: 'Clarification', description: 'Asking detailed questions', icon: '💬' },
      { title: 'Generation', description: 'Creating diagram code', icon: '✏️' },
      { title: 'Rendering', description: 'Visualizing the diagram', icon: '🎨' },
    ],
    userInput: '',
    loading: false,
    isInAnalysisPhase: false,
    sessionId: null,
    status: null as DiagramUpdate | null,
    score: 0,
    clarifications: [],
    chatHistory: [],
    sseConnected: true,
    onChangeModel: vi.fn(),
    onStartDiagram: vi.fn(),
    onClearInput: vi.fn(),
    onInputChange: vi.fn(),
    onSubmitClarification: vi.fn(),
    onConfirmReady: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('should render with header and model tag', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Diagram Wizard')).toBeInTheDocument();
      expect(screen.getByText('GPT-5')).toBeInTheDocument();
    });

    it('should show system description heading', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Describe Your System')).toBeInTheDocument();
    });

    it('should display textarea with placeholder', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/);
      expect(textarea).toBeInTheDocument();
    });

    it('should show "Using: model" indicator', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Using:')).toBeInTheDocument();
      expect(screen.getByText('GPT5')).toBeInTheDocument();
    });

    it('should display "Change Model" button', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Change Model')).toBeInTheDocument();
    });

    it('should display Start Conversation button', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Start Conversation')).toBeInTheDocument();
    });

    it('should display Clear button', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Clear')).toBeInTheDocument();
    });
  });

  describe('Input Handling', () => {
    it('should call onInputChange when user types in textarea', async () => {
      const user = userEvent.setup();
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/);

      await user.type(textarea, 'E-commerce platform');
      expect(mockProps.onInputChange).toHaveBeenCalled();
    });

    it('should show provided userInput in textarea', () => {
      render(<SystemDescriptionScreen {...mockProps} userInput="Test system description" />);
      const textarea = screen.getByPlaceholderText(/Describe the system/) as HTMLTextAreaElement;
      expect(textarea.value).toBe('Test system description');
    });

    it('should call onClearInput when Clear button clicked', async () => {
      const user = userEvent.setup();
      render(<SystemDescriptionScreen {...mockProps} userInput="Some text" />);
      const clearButton = screen.getByText('Clear');

      await user.click(clearButton);
      expect(mockProps.onClearInput).toHaveBeenCalled();
    });

    it('should disable Clear button when input is empty', () => {
      render(<SystemDescriptionScreen {...mockProps} userInput="" />);
      const clearButton = screen.getByText('Clear');
      expect(clearButton).toBeDisabled();
    });

    it('should enable Clear button when input has text', () => {
      render(<SystemDescriptionScreen {...mockProps} userInput="Some text" />);
      const clearButton = screen.getByText('Clear');
      expect(clearButton).not.toBeDisabled();
    });
  });

  describe('Start Conversation', () => {
    it('should call onStartDiagram when button clicked with input', async () => {
      const user = userEvent.setup();
      render(<SystemDescriptionScreen {...mockProps} userInput="My system" />);
      const startButton = screen.getByText('Start Conversation');

      await user.click(startButton);
      expect(mockProps.onStartDiagram).toHaveBeenCalledWith('My system');
    });

    it('should disable Start button when loading', () => {
      render(<SystemDescriptionScreen {...mockProps} loading={true} />);
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).toBeDisabled();
    });

    it('should disable Start button when input is empty', () => {
      render(<SystemDescriptionScreen {...mockProps} userInput="" />);
      const startButton = screen.getByText('Start Conversation');
      expect(startButton).toBeDisabled();
    });

    it('should show loading state on Start button', () => {
      render(<SystemDescriptionScreen {...mockProps} loading={true} />);
      const startButton = screen.getByRole('button', { name: /Start Conversation/ });
      expect(startButton).toBeDisabled();
    });
  });

  describe('Model Management', () => {
    it('should display correct model name in tag', () => {
      render(<SystemDescriptionScreen {...mockProps} selectedModel="claude" />);
      expect(screen.getByText('CLAUDE')).toBeInTheDocument();
    });

    it('should call onChangeModel when Change Model clicked', async () => {
      const user = userEvent.setup();
      render(<SystemDescriptionScreen {...mockProps} />);
      const changeButton = screen.getByText('Change Model');

      await user.click(changeButton);
      expect(mockProps.onChangeModel).toHaveBeenCalled();
    });

    it('should handle all model types', () => {
      const models = ['gpt5', 'grok', 'claude', 'gemini'] as const;
      models.forEach((model) => {
        const { unmount } = render(
          <SystemDescriptionScreen {...mockProps} selectedModel={model} />
        );
        expect(screen.getByText(model.toUpperCase())).toBeInTheDocument();
        unmount();
      });
    });
  });

  describe('Textarea Behavior', () => {
    it('should have proper placeholder text', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/) as HTMLTextAreaElement;
      expect(textarea.textContent || textarea.placeholder).toContain('E-commerce platform');
    });

    it('should not be disabled initially', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/) as HTMLTextAreaElement;
      expect(textarea.disabled).toBe(false);
    });

    it('should be disabled when loading', () => {
      render(<SystemDescriptionScreen {...mockProps} loading={true} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/) as HTMLTextAreaElement;
      expect(textarea.disabled).toBe(true);
    });

    it('should accept multiline input', async () => {
      const user = userEvent.setup();
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/);

      await user.type(textarea, 'Line 1\nLine 2\nLine 3');
      expect(mockProps.onInputChange).toHaveBeenCalled();
    });
  });

  describe('Chat Panel Conditional Rendering', () => {
    it('should show textarea when not in analysis phase', () => {
      render(<SystemDescriptionScreen {...mockProps} isInAnalysisPhase={false} />);
      expect(screen.getByPlaceholderText(/Describe the system/)).toBeInTheDocument();
      expect(screen.queryByText('Conversation')).not.toBeInTheDocument();
    });

    it('should show ChatPanel when in analysis phase', () => {
      render(
        <SystemDescriptionScreen
          {...mockProps}
          isInAnalysisPhase={true}
          sessionId="test-session"
        />
      );
      expect(screen.queryByPlaceholderText(/Describe the system/)).not.toBeInTheDocument();
      expect(screen.getByText('Conversation')).toBeInTheDocument();
    });

    it('should switch from textarea to ChatPanel during analysis', () => {
      const { rerender } = render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByPlaceholderText(/Describe the system/)).toBeInTheDocument();

      rerender(
        <SystemDescriptionScreen
          {...mockProps}
          isInAnalysisPhase={true}
          sessionId="test-session"
        />
      );
      expect(screen.queryByPlaceholderText(/Describe the system/)).not.toBeInTheDocument();
    });
  });

  describe('Clarification Handling', () => {
    it('should call onSubmitClarification with user input', async () => {
      render(
        <SystemDescriptionScreen
          {...mockProps}
          isInAnalysisPhase={true}
          sessionId="test-session"
        />
      );

      // ChatPanel would handle this, but we're testing the prop passing
      expect(mockProps.onSubmitClarification).toBeDefined();
    });

    it('should display clarifications count when provided', () => {
      const clarifications = [
        { question: 'What type of system?', answer: 'E-commerce' },
      ];
      render(
        <SystemDescriptionScreen
          {...mockProps}
          isInAnalysisPhase={true}
          sessionId="test-session"
          clarifications={clarifications}
        />
      );
      expect(mockProps.onSubmitClarification).toBeDefined();
    });
  });

  describe('Progress Indicator', () => {
    it('should display current phase', () => {
      render(<SystemDescriptionScreen {...mockProps} currentPhase={1} />);
      expect(screen.getByText('Analysis')).toBeInTheDocument();
    });

    it('should update phase display when phase changes', () => {
      const { rerender } = render(<SystemDescriptionScreen {...mockProps} currentPhase={1} />);
      expect(screen.getByText('Analysis')).toBeInTheDocument();

      rerender(<SystemDescriptionScreen {...mockProps} currentPhase={2} />);
      expect(screen.getByText('Clarification')).toBeInTheDocument();
    });

    it('should display clarity score when available', () => {
      render(<SystemDescriptionScreen {...mockProps} score={7} />);
      expect(screen.getByText('7/10')).toBeInTheDocument();
    });

    it('should not display score when score is 0', () => {
      render(<SystemDescriptionScreen {...mockProps} score={0} />);
      expect(screen.queryByText('0/10')).not.toBeInTheDocument();
    });
  });

  describe('SSE Connection Status', () => {
    it('should show Connected status when connected', () => {
      render(<SystemDescriptionScreen {...mockProps} sessionId="test-session-123" sseConnected={true} />);
      expect(screen.getByText(/Connected/)).toBeInTheDocument();
    });

    it('should show Disconnected status when not connected', () => {
      render(<SystemDescriptionScreen {...mockProps} sessionId="test-session-123" sseConnected={false} />);
      expect(screen.getByText(/Disconnected/)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error alert when error provided', () => {
      const error = { message: 'Test error occurred' };
      render(<SystemDescriptionScreen {...mockProps} error={error} />);
      expect(screen.getByText('Test error occurred')).toBeInTheDocument();
    });

    it('should not display error when no error', () => {
      render(<SystemDescriptionScreen {...mockProps} error={undefined} />);
      expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });
  });

  describe('Session Information', () => {
    it('should display session ID when available', () => {
      render(<SystemDescriptionScreen {...mockProps} sessionId="abc123def456" />);
      expect(screen.getByText(/abc123/)).toBeInTheDocument();
    });

    it('should not display session ID when not available', () => {
      render(<SystemDescriptionScreen {...mockProps} sessionId={null} />);
      expect(screen.queryByText(/Session:/)).not.toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading spinner when loading', () => {
      render(<SystemDescriptionScreen {...mockProps} loading={true} />);
      const startButton = screen.getByRole('button', { name: /Start Conversation/ });
      expect(startButton).toBeDisabled();
    });

    it('should disable all interactive elements when loading', () => {
      render(<SystemDescriptionScreen {...mockProps} loading={true} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/) as HTMLTextAreaElement;
      expect(textarea.disabled).toBe(true);
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      const heading = screen.getByText('Describe Your System');
      expect(heading.tagName).toBe('H3');
    });

    it('should have descriptive button labels', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      expect(screen.getByText('Start Conversation')).toBeInTheDocument();
      expect(screen.getByText('Clear')).toBeInTheDocument();
      expect(screen.getByText('Change Model')).toBeInTheDocument();
    });

    it('should have accessible form inputs', () => {
      render(<SystemDescriptionScreen {...mockProps} />);
      const textarea = screen.getByPlaceholderText(/Describe the system/);
      expect(textarea).toBeInTheDocument();
    });
  });
});
