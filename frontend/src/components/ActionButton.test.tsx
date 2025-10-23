import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActionButton from './ActionButton';

describe('ActionButton', () => {
  const props = { playbookId: '1', playbookName: 'Restart Container', successRate: '91% Success', confidence: 0.92 };

  it('renders idle state correctly', () => {
    render(<ActionButton {...props} />);
    expect(screen.getByText('Restart Container')).toBeInTheDocument();
    expect(screen.getByText('91% Success • 92% Confidence')).toBeInTheDocument();
  });

  it('transitions to loading on click and success after mock', async () => {
    render(<ActionButton {...props} />);
    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('Executing...')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText('Success')).toBeInTheDocument(), { timeout: 2000 });
  });

  it('handles error state', async () => {
    // Mock error (override Promise to reject)
    jest.spyOn(global, 'setTimeout').mockImplementation((cb) => cb()); // Fast sim
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {}); // Suppress logs
    render(<ActionButton {...props} />);
    fireEvent.click(screen.getByRole('button'));
    await waitFor(() => expect(screen.getByText('Error')).toBeInTheDocument());
    consoleSpy.mockRestore();
  });

  it('has proper a11y attributes', () => {
    render(<ActionButton {...props} />);
    expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Restart Container with 91% Success and 92% confidence');
  });
});
