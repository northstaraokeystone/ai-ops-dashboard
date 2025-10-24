import { create } from 'zustand';

// Define all interfaces at the top for clarity
interface Playbook {
  playbookId: string;
  name: string;
  successRate: string;
  confidence: number;
}

interface Incident {
  id: string;
  status: 'Attention Needed' | 'In Progress' | 'Resolved';
  agentName: string;
  action: string;
  owner: string;
  time: string;
  agentSupport: Record<string, unknown>; // JSONB payload
  suggestedActions: Playbook[]; // This is now part of the core Incident interface
  expanded?: boolean; // Optional property for UI state
}

interface IncidentState {
  incidents: Incident[];
  toggleExpand: (id: string) => void;
  // Note: The sortBy function was causing issues with the complex object.
  // We will let the TanStack Table library handle sorting in the component itself.
  // This simplifies the store significantly.
}

export const incidentStore = create<IncidentState>((set) => ({
  // --- MOCK DATA ---
  // This is the single source of mock data for the store.
  incidents: [
    {
      id: '1',
      status: 'Attention Needed',
      agentName: 'Trader-7',
      action: 'Trade Execution',
      owner: '@user1',
      time: '2025-10-23T12:00:00Z',
      agentSupport: { timestamp: '2025-10-23T12:00:00Z', error_log: 'Timeout on exchange API' },
      suggestedActions: [
        { playbookId: 'p-001', name: 'Restart Container', successRate: '91% Success', confidence: 0.92 },
        { playbookId: 'p-002', name: 'Rollback Commit', successRate: '85% Success', confidence: 0.88 },
      ]
    },
    {
      id: '2',
      status: 'In Progress',
      agentName: 'Analyzer-3',
      action: 'Data Aggregation',
      owner: '@user2',
      time: '2025-10-23T11:45:00Z',
      agentSupport: { timestamp: '2025-10-23T11:45:00Z', error_log: 'Partial data loss' },
      suggestedActions: [
        { playbookId: 'p-003', name: 'Re-ingest Source', successRate: '75% Success', confidence: 0.80 },
      ]
    },
    {
      id: '3',
      status: 'Resolved',
      agentName: 'Recoverer-5',
      action: 'Rollback',
      owner: '@user3',
      time: '2025-10-23T11:30:00Z',
      agentSupport: { timestamp: '2025-10-23T11:30:00Z', error_log: 'Successful recovery' },
      suggestedActions: [] // Resolved incidents have no suggested actions
    },
  ],

  // --- ACTIONS ---
  toggleExpand: (id) => set((state) => ({
    incidents: state.incidents.map((inc) =>
      inc.id === id ? { ...inc, expanded: !inc.expanded } : { ...inc, expanded: false }
    ),
  })),
}));


// Mock real-time updates (for demo purposes)
const mockSSE = () => {
  setInterval(() => {
    // This is a simplified way to update state in Zustand without using the `set` from inside
    const currentState = incidentStore.getState();
    const newIncident: Incident = {
      id: Date.now().toString(),
      status: 'Attention Needed',
      agentName: `NewAgent-${Math.floor(Math.random()*100)}`,
      action: 'New Action',
      owner: 'unassigned',
      time: new Date().toISOString(),
      agentSupport: { error: 'A new simulated error' },
      suggestedActions: [
        { playbookId: 'p-999', name: 'Investigate', successRate: 'N/A', confidence: 0.99 },
      ]
    };
    incidentStore.setState({ incidents: [newIncident, ...currentState.incidents] });
  }, 15000); // Add a new incident every 15 seconds
};

if (process.env.NODE_ENV !== 'test') {
  //mockSSE(); // Disabling mock SSE for now to ensure a stable build
}
