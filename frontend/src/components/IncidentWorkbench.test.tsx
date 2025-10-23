import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import IncidentWorkbench from './IncidentWorkbench';
import { incidentStore } from '../stores/incidentStore'; // Mock store

jest.mock('zustand'); // For store mocking

describe('IncidentWorkbench', () => {
  const props = { incidentId: '1', trigger: <button>Open</button> };

  beforeEach(() => {
    // Mock store with suggestedActions
    incidentStore.getState = jest.fn().mockReturnValue({
      incidents: [{ id: '1', action: 'Test Action', agentSupport: {}, suggestedActions: [{ playbookId: 'p-001', name: 'Test', successRate: '90%', confidence: 0.9 }] }],
    });
  });

  it('renders modal on trigger click', () => {
    render(<IncidentWorkbench {...props} />);
    fireEvent.click(screen.getByText('Open'));
    expect(screen.getByText('Incident Workbench: Test Action')).toBeInTheDocument();
  });

  it('displays raw payload and action buttons', () => {
    render(<IncidentWorkbench {...props} />);
    fireEvent.click(screen.getByText('Open'));
    expect(screen.getByLabelText('Raw payload')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('handles no incident gracefully', () => {
    const { container } = render(<IncidentWorkbench incidentId="invalid" trigger={<button>Open</button>} />);
    fireEvent.click(screen.getByText('Open'));
    expect(container).toBeEmptyDOMElement(); // Or fallback UI if added
  });

  it('has proper a11y attributes', () => {
    render(<IncidentWorkbench {...props} />);
    fireEvent.click(screen.getByText('Open'));
    expect(screen.getByRole('dialog', { name: 'Incident Workbench: Test Action' })).toHaveAttribute('aria-describedby', 'incident-details');
  });
});
