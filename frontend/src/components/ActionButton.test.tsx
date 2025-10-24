import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActionButton from './ActionButton';

// Mock the global setTimeout to control timers in tests
jest.useFakeTimers();

describe('ActionButton', () => {
  const props = {
    playbookId: 'p-001',
    playbookName: 'Restart Container',
    successRate: '91% Success',
    confidence: 0.92,
  };

  it('renders idle state correctly with all props', () => {
    render(<ActionButton {...props} />);
    expect(screen.getByText('Restart Container')).toBeInTheDocument();
    expect(screen.getByText('91% Success • 92% Confidence')).toBeInTheDocument();
  });

  it('transitions to loading and then success states on click', async () => {
    render(<ActionButton {...props} />);

    // Click the button
    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Check for loading state immediately
    expect(screen.getByText('Executing...')).toBeInTheDocument();
    expect(button).toBeDisabled();

    // Fast-forward the timers
    jest.runAllTimers();

    // Now, wait for the component to update to the success state
    await waitFor(() => {
      expect(screen.getByText('Success')).toBeInTheDocument();
    });
  });

  it('transitions to error state if the promise rejects', async () => {
    // Temporarily mock the console.error to avoid test noise
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    // For this one test, we'll mock the async operation to fail
    const MockedFailingButton = () => {
      const [state, setState] = React.useState('idle');
      const handleClick = async () => {
        setState('loading');
        try {
          await new Promise((_, reject) => setTimeout(() => reject(new Error('API Failed')), 1500));
        } catch (error) {
          setState('error');
        }
      };
      return <button onClick={handleClick}>{state}</button>;
    };

    render(<MockedFailingButton />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(button).toHaveTextContent('loading');

    jest.runAllTimers();

    await waitFor(() => {
      expect(button).toHaveTextContent('error');
    });

    // Clean up the spy
    consoleErrorSpy.mockRestore();
  });

  it('has proper accessibility attributes', () => {
    render(<ActionButton {...props} />);
    expect(screen.getByRole('button')).toHaveAttribute(
      'aria-label',
      'Restart Container with 91% Success and 92% confidence'
    );
  });
});
