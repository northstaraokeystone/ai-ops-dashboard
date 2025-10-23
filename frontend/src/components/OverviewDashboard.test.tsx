import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import OverviewDashboard from './OverviewDashboard';
import { kpiStore } from '../stores/kpiStore'; // Mock store

jest.mock('zustand'); // For store mocking

describe('OverviewDashboard', () => {
  beforeEach(() => {
    // Mock store state for consistent tests
    kpiStore.getState = jest.fn().mockReturnValue({
      truthScore: { value: '99.999%', color: 'green', trend: 'stable' },
      resilience: { value: '<5min', color: 'green', trend: 'up' },
      agentHealth: { value: '98%', color: 'green', trend: 'stable' },
    });
  });

  it('renders three StatusCards with correct titles', () => {
    render(<OverviewDashboard />);
    expect(screen.getByText('Truth Score')).toBeInTheDocument();
    expect(screen.getByText('Resilience (MTTR)')).toBeInTheDocument();
    expect(screen.getByText('Agent Health')).toBeInTheDocument();
  });

  it('applies responsive grid classes', () => {
    const { container } = render(<OverviewDashboard />);
    expect(container.firstChild).toHaveClass('grid grid-cols-1 md:grid-cols-3 gap-4');
  });

  it('has proper a11y attributes', () => {
    render(<OverviewDashboard />);
    expect(screen.getByRole('region', { name: 'Overview Dashboard' })).toBeInTheDocument();
  });
});
