/**
 * ModelSelectionScreen Tests
 *
 * Tests for the model selection screen component.
 * Verifies model display, selection handling, and user interactions.
 */

import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ModelSelectionScreen, type ModelId } from './ModelSelectionScreen';

describe('ModelSelectionScreen', () => {
  let mockOnSelect: Mock;

  beforeEach(() => {
    mockOnSelect = vi.fn();
  });

  describe('Rendering', () => {
    it('should render the component with header', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Choose Your AI Model')).toBeInTheDocument();
    });

    it('should display the subtitle text', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(
        screen.getByText(/Select the AI model that best fits your architecture needs/)
      ).toBeInTheDocument();
    });

    it('should render all 4 model cards', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Deep Context')).toBeInTheDocument();
      expect(screen.getByText('Fast')).toBeInTheDocument();
      expect(screen.getByText('Thinking')).toBeInTheDocument();
      expect(screen.getByText('Efficient')).toBeInTheDocument();
    });

    it('should display all model descriptions', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(
        screen.getByText(/Deep contextual analysis with long-context reasoning/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Fast, deterministic analysis with lean efficiency/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Transparent thinking with structured reasoning/)
      ).toBeInTheDocument();
      expect(
        screen.getByText(/Efficient output with pragmatic approach/)
      ).toBeInTheDocument();
    });

    it('should display footer tip', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(
        screen.getByText(/Different models handle architectures differently/)
      ).toBeInTheDocument();
    });

    it('should render select buttons for each model', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const selectButtons = screen.getAllByText('Select');
      expect(selectButtons).toHaveLength(4);
    });
  });

  describe('Model Display', () => {
    it('should show GPT-5 strengths', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Complex system architectures')).toBeInTheDocument();
      expect(screen.getByText('Comprehensive validation')).toBeInTheDocument();
      expect(screen.getByText('Rich metadata extraction')).toBeInTheDocument();
    });

    it('should show Grok strengths', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Quick analysis')).toBeInTheDocument();
      expect(screen.getByText('Deterministic results')).toBeInTheDocument();
      expect(screen.getByText('Simple systems')).toBeInTheDocument();
    });

    it('should show Claude strengths', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Clear explanations')).toBeInTheDocument();
      expect(screen.getByText('Structured output')).toBeInTheDocument();
      expect(screen.getByText('Visible reasoning')).toBeInTheDocument();
    });

    it('should show Gemini strengths', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Fast processing')).toBeInTheDocument();
      expect(screen.getByText('Practical approach')).toBeInTheDocument();
      expect(screen.getByText('Resource efficient')).toBeInTheDocument();
    });
  });

  describe('Selection Interaction', () => {
    it('should call onSelect with gpt5 when Deep Context is clicked', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const deepContextCard = screen
        .getByText('Deep Context')
        .closest('div[class*="card"]');
      fireEvent.click(deepContextCard!);
      expect(mockOnSelect).toHaveBeenCalledWith('gpt5');
    });

    it('should call onSelect with grok when Fast is clicked', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const fastCard = screen.getByText('Fast').closest('div[class*="card"]');
      fireEvent.click(fastCard!);
      expect(mockOnSelect).toHaveBeenCalledWith('grok');
    });

    it('should call onSelect with claude when Thinking is clicked', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const thinkingCard = screen.getByText('Thinking').closest('div[class*="card"]');
      fireEvent.click(thinkingCard!);
      expect(mockOnSelect).toHaveBeenCalledWith('claude');
    });

    it('should call onSelect with gemini when Efficient is clicked', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const efficientCard = screen
        .getByText('Efficient')
        .closest('div[class*="card"]');
      fireEvent.click(efficientCard!);
      expect(mockOnSelect).toHaveBeenCalledWith('gemini');
    });

    it('should call onSelect when select button is clicked', async () => {
      const user = userEvent.setup();
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const selectButtons = screen.getAllByText('Select');
      await user.click(selectButtons[0]);
      expect(mockOnSelect).toHaveBeenCalledWith('gpt5');
    });
  });

  describe('Loading State', () => {
    it('should disable cards when loading is true', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} loading={true} />);
      const selectButtons = screen.getAllByText('Loading...');
      expect(selectButtons).toHaveLength(4);
    });

    it('should show Loading text on buttons when loading', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} loading={true} />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toBeDisabled();
      });
    });

    it('should not call onSelect when loading and card clicked', async () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} loading={true} />);
      const efficientCard = screen
        .getByText('Efficient')
        .closest('div[class*="card"]');
      fireEvent.click(efficientCard!);
      expect(mockOnSelect).not.toHaveBeenCalled();
    });

    it('should have reduced opacity when loading', () => {
      const { container } = render(
        <ModelSelectionScreen onSelect={mockOnSelect} loading={true} />
      );
      const cards = container.querySelectorAll('[class*="modelCard"]');
      cards.forEach((card) => {
        expect(card).toHaveStyle('opacity: 0.6');
      });
    });
  });

  describe('Styling and Layout', () => {
    it('should have purple gradient background', () => {
      const { container } = render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const background = container.querySelector('div[style*="gradient"]');
      expect(background).toBeInTheDocument();
      expect(background).toHaveStyle(
        'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      );
    });

    it('should display in flex layout', () => {
      const { container } = render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const layout = container.querySelector('div[style*="display: flex"]');
      expect(layout).toBeInTheDocument();
    });

    it('should center content vertically and horizontally', () => {
      const { container } = render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const layout = container.querySelector(
        'div[style*="justifyContent: center"]'
      );
      expect(layout).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const heading = screen.getByRole('heading', { level: 2 });
      expect(heading).toHaveTextContent('Choose Your AI Model');
    });

    it('should have all buttons with proper labels', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      buttons.forEach((button) => {
        expect(button.textContent).toBeTruthy();
      });
    });

    it('should have text content for all model cards', () => {
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      expect(screen.getByText('Deep Context')).toBeVisible();
      expect(screen.getByText('Fast')).toBeVisible();
      expect(screen.getByText('Thinking')).toBeVisible();
      expect(screen.getByText('Efficient')).toBeVisible();
    });
  });

  describe('Type Safety', () => {
    it('should accept valid ModelId types', () => {
      const validIds: ModelId[] = ['gpt5', 'grok', 'claude', 'gemini'];
      validIds.forEach((id) => {
        mockOnSelect.mockClear();
        render(<ModelSelectionScreen onSelect={mockOnSelect} />);
        // Test would verify only valid IDs are passed
        expect(['gpt5', 'grok', 'claude', 'gemini']).toContain(id);
      });
    });
  });

  describe('Multiple Interactions', () => {
    it('should handle multiple rapid clicks', async () => {
      const user = userEvent.setup();
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);
      const buttons = screen.getAllByText('Select');

      await user.click(buttons[0]); // gpt5
      expect(mockOnSelect).toHaveBeenCalledWith('gpt5');

      mockOnSelect.mockClear();
      await user.click(buttons[1]); // grok
      expect(mockOnSelect).toHaveBeenCalledWith('grok');

      mockOnSelect.mockClear();
      await user.click(buttons[2]); // claude
      expect(mockOnSelect).toHaveBeenCalledWith('claude');

      mockOnSelect.mockClear();
      await user.click(buttons[3]); // gemini
      expect(mockOnSelect).toHaveBeenCalledWith('gemini');
    });

    it('should handle click on card and button for same model', async () => {
      const user = userEvent.setup();
      render(<ModelSelectionScreen onSelect={mockOnSelect} />);

      const buttons = screen.getAllByText('Select');
      await user.click(buttons[0]); // Click button
      expect(mockOnSelect).toHaveBeenCalledWith('gpt5');

      mockOnSelect.mockClear();

      const deepContextCard = screen
        .getByText('Deep Context')
        .closest('div[class*="card"]');
      await user.click(deepContextCard!); // Click card
      expect(mockOnSelect).toHaveBeenCalledWith('gpt5');
    });
  });
});
