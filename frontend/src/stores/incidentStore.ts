import { create } from 'zustand';

// Define all interfaces at the top for clarity
export interface Playbook {
  playbookId: string;
  playbookName: string; // <-- Corrected from 'name' to 'playbookName' for clarity
  successRate: string;
  confidence: number;
}

export interface Incident {
  id: string;
  status: 'Attention Needed' | 'In Progress' | 'Resolved';
  agentName: string;
  action: string;
  owner: string;
  time: string;
  agentSupport: Record<string, unknown>;
  suggestedActions: Playbook[];
  expanded?: boolean;
}

interface IncidentState {
  incidents: Incident[];
  toggleExpand: (id: string) => void;
}

export const incidentStore = create<IncidentState>((set) => ({
  // --- MOCK DATA ---
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
        { playbookId: 'p-001', playbookName: 'Restart Container', successRate: '91% Success', confidence: 0.92 },
        { playbookId: 'p-002', playbookName: 'Rollback Commit', successRate: '85% Success', confidence: 0.88 },
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
        { playbookId: 'p-003', playbookName: 'Re-ingest Source', successRate: '75% Success', confidence: 0.80 },
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
      suggestedActions: []
    },
  ],

  // --- ACTIONS ---
  toggleExpand: (id) => set((state) => ({
    incidents: state.incidents.map((inc) =>
      inc.id === id ? { ...inc, expanded: !inc.expanded } : { ...inc, expanded: false }
    ),
  })),
}));
