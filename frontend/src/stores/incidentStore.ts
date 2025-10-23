import { create } from 'zustand'; // Lightweight state mgmt per CTO rec

interface Incident {
  id: string;
  status: 'Attention Needed' | 'In Progress' | 'Resolved';
  agentName: string;
  action: string;
  owner: string;
  time: string;
  agentSupport: Record<string, unknown>; // JSONB payload
  expanded?: boolean; // For row toggle
}

interface IncidentState {
  incidents: Incident[];
  toggleExpand: (id: string) => void;
  sortBy: (key: keyof Incident, direction: 'asc' | 'desc') => void;
}

export const incidentStore = create<IncidentState>((set) => ({
  incidents: [ // Mock data reflecting statuses; prod: Fetch from /api/events
    { id: '1', status: 'Attention Needed', agentName: 'Trader-7', action: 'Trade Execution', owner: '@user1', time: '2025-10-23T12:00:00Z', agentSupport: { timestamp: '2025-10-23T12:00:00Z', error_log: 'Timeout on exchange API' } },
    { id: '2', status: 'In Progress', agentName: 'Analyzer-3', action: 'Data Aggregation', owner: '@user2', time: '2025-10-23T11:45:00Z', agentSupport: { timestamp: '2025-10-23T11:45:00Z', error_log: 'Partial data loss' } },
    { id: '3', status: 'Resolved', agentName: 'Recoverer-5', action: 'Rollback', owner: '@user3', time: '2025-10-23T11:30:00Z', agentSupport: { timestamp: '2025-10-23T11:30:00Z', error_log: 'Successful recovery' } },
  ],
  toggleExpand: (id) => set((state) => ({
    incidents: state.incidents.map((inc) => inc.id === id ? { ...inc, expanded: !inc.expanded } : inc),
  })),
  sortBy: (key, direction) => set((state) => ({
    incidents: [...state.incidents].sort((a, b) => {
      const valA = a[key], valB = b[key];
      return (valA < valB ? -1 : valA > valB ? 1 : 0) * (direction === 'asc' ? 1 : -1);
    }),
  })),
}));

// Mock SSE integration (prod: replace with actual /api/events listener)
// Why: Enables reactive triage; smallest safe with mock for isolated testing.
const mockSSE = () => {
  // Sim add/update incidents; prod: Parse SSE for real-time
  setInterval(() => {
    incidentStore.getState().incidents.push({ id: Date.now().toString(), status: 'Attention Needed', agentName: 'NewAgent', action: 'New Action', owner: '@new', time: new Date().toISOString(), agentSupport: {} });
  }, 10000); // Sim 10s updates
};

if (process.env.NODE_ENV !== 'test') mockSSE(); // Disable in tests
