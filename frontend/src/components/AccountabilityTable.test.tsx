import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useStore } from 'zustand';
import AccountabilityTable from './AccountabilityTable';
import { incidentStore } from '../stores/incidentStore';

// Mock the zustand library
jest.mock('zustand');

// Type assertion for the mocked useStore
const useStoreMock = useStore as jest.Mock;

describe('AccountabilityTable', () => {

  // A complete mock incident object
  const mockIncidents = [
    {
      id: '1',
      status: 'Attention Needed',
      agentName: 'Trader-7',
      action: 'Trade Execution',
      owner: '@user1',
      time: '2025-10-23T12:00:00Z',
      agentSupport: { error: 'API Timeout' },
      suggestedActions: [],
      expanded: false,
    },
  ];

  // A mock toggle function to track calls
  const mockToggleExpand = jest.fn();

  beforeEach(() => {
    // Reset mocks before each test
    mockToggleExpand.mockClear();
    useStoreMock.mockImplementation((selector) => selector({
      incidents: mockIncidents,
      toggleExpand: mockToggleExpand,
    }));
  });

  it('renders table headers and rows correctly', () => {
    render(<AccountabilityTable />);
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Trader-7')).toBeInTheDocument();
  });

  it('calls toggleExpand function on row expand click', () => {
    render(<AccountabilityTable />);
    // The button to expand the row has an aria-label
    const expandButton = screen.getByLabelText('Toggle expand');
    fireEvent.click(expandButton);
    // Verify our mock function was called with the correct incident ID
    expect(mockToggleExpand).toHaveBeenCalledWith('1');
  });

  it('renders the expanded content when a row is expanded', () => {
    // For this test, we'll set the mock state to be "already expanded"
    useStoreMock.mockImplementation((selector) => selector({
        incidents: [{ ...mockIncidents[0], expanded: true }], // Set expanded to true
        toggleExpand: mockToggleExpand,
    }));

    render(<AccountabilityTable />);

    // Check if the raw payload view is now visible
    const rawPayload = screen.getByLabelText('Raw payload');
    expect(rawPayload).toBeInTheDocument();
    expect(rawPayload).toHaveTextContent('"error": "API Timeout"');
  });
});
