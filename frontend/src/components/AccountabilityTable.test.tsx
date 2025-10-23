import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AccountabilityTable from './AccountabilityTable';
import { incidentStore } from '../stores/incidentStore'; // Mock store

jest.mock('zustand'); // For store mocking

describe('AccountabilityTable', () => {
  beforeEach(() => {
    // Mock store incidents
    incidentStore.getState = jest.fn().mockReturnValue({
      incidents: [ // Sample mock
        { id: '1', status: 'Attention Needed', agentName: 'Trader-7', action: 'Trade', owner: '@user1', time: '2025-10-23', agentSupport: {}, expanded: false },
      ],
      toggleExpand: jest.fn(),
      sortBy: jest.fn(),
    });
  });

  it('renders table headers and rows', () => {
    render(<AccountabilityTable />);
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Attention Needed')).toBeInTheDocument();
  });

  it('sorts columns on header click', () => {
    render(<AccountabilityTable />);
    fireEvent.click(screen.getByText('Status'));
    expect(incidentStore.getState.sortBy).toHaveBeenCalledWith('status', expect.any(String));
  });

  it('expands row on toggle', () => {
    render(<AccountabilityTable />);
    fireEvent.click(screen.getByLabelText('Toggle expand'));
    expect(incidentStore.getState.toggleExpand).toHaveBeenCalledWith('1');
    expect(screen.getByLabelText('Raw payload')).toBeInTheDocument(); // After expand
  });

  it('has proper a11y attributes', () => {
    render(<AccountabilityTable />);
    expect(screen.getByRole('table', { name: 'Accountability Table' })).toBeInTheDocument();
    expect(screen.getByLabelText('Toggle expand')).toBeInTheDocument();
  });
});
