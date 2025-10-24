import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useStore } from 'zustand';
import StatusCard from './StatusCard';
import { kpiStore } from '../stores/kpiStore';

// Mock the zustand library
jest.mock('zustand');

// Type assertion for the mocked useStore
const useStoreMock = useStore as jest.Mock;

describe('StatusCard', () => {

  // Define a complete, valid mock state that our tests can use
  const mockState = {
    truthScore: { value: '99.9%', color: 'green', trend: 'up', badge: 'Verified' },
    resilience: { value: '<1m', color: 'red', trend: 'down', badge: '3 open' },
    agentHealth: { value: '95%', color: 'yellow', trend: 'stable' },
  };

  beforeEach(() => {
    // Before each test, reset the mock to return a clean state
    useStoreMock.mockImplementation((selector) => selector(mockState));
  });

  it('renders title, value, and badge correctly', () => {
    render(<StatusCard title="Truth Score" kpiKey="truthScore" />);
    expect(screen.getByText('Truth Score')).toBeInTheDocument();
    expect(screen.getByText('99.9%')).toBeInTheDocument();
    expect(screen.getByText('Verified')).toBeInTheDocument();
  });

  it('applies the correct border color class based on state', () => {
    const { container } = render(<StatusCard title="Resilience (MTTR)" kpiKey="resilience" />);
    // The component adds 'border-red-500', so we check for that class
    expect(container.firstChild).toHaveClass('border-red-500');
  });

  it('renders the correct trend icon', () => {
    render(<StatusCard title="Resilience (MTTR)" kpiKey="resilience" />);
    // Check for the accessible "sr-only" text for the trend
    expect(screen.getByText('Trend: down')).toBeInTheDocument();
  });

  it('renders correctly without an optional badge', () => {
    render(<StatusCard title="Agent Health" kpiKey="agentHealth" />);
    expect(screen.getByText('Agent Health')).toBeInTheDocument();
    // Ensure no "Badge:" aria-label exists when no badge is provided
    expect(screen.queryByLabelText(/Badge:/)).not.toBeInTheDocument();
  });
});
