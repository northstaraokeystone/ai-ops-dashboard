import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import StatusCard from './StatusCard';
import { kpiStore } from '../stores/kpiStore'; // Mock store

jest.mock('zustand'); // For store mocking

describe('StatusCard', () => {
  beforeEach(() => {
    kpiStore.getState = jest.fn().mockReturnValue({
      value: '99.999%',
      color: 'green',
      trend: 'up',
      badge: '2 incidents'
    });
  });

  it('renders title and value correctly', () => {
    render(<StatusCard title="Truth Score" kpiKey="truthScore" />);
    expect(screen.getByText('Truth Score')).toBeInTheDocument();
    expect(screen.getByText('99.999%')).toBeInTheDocument();
  });

  it('applies correct color class', () => {
    const { container } = render(<StatusCard title="Truth Score" kpiKey="truthScore" />);
    expect(container.firstChild).toHaveClass('border-green-500');
  });

  it('renders trend icon and badge', () => {
    render(<StatusCard title="Truth Score" kpiKey="truthScore" />);
    expect(screen.getByLabelText('Badge: 2 incidents')).toBeInTheDocument();
    expect(screen.getByRole('img', { hidden: true })).toHaveClass('text-green-500'); // Trend up
  });

  it('has proper a11y attributes', () => {
    render(<StatusCard title="Truth Score" kpiKey="truthScore" />);
    expect(screen.getByLabelText('Badge: 2 incidents')).toBeInTheDocument();
    expect(screen.getByText('Truth Score')).toHaveAttribute('id', 'truth-score-title');
  });
});
