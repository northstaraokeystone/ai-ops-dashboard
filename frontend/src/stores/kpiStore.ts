import { create } from 'zustand'; // Lightweight state mgmt per CTO rec

interface KPIState {
  truthScore: { value: string; color: 'green' | 'red' | 'yellow'; trend: 'up' | 'down' | 'stable'; badge?: string };
  resilience: { value: string; color: 'green' | 'red' | 'yellow'; trend: 'up' | 'down' | 'stable'; badge?: string };
  agentHealth: { value: string; color: 'green' | 'red' | 'yellow'; trend: 'up' | 'down' | 'stable'; badge?: string };
  updateKPI: (kpiKey: keyof Omit<KPIState, 'updateKPI'>, data: Partial<KPIState[keyof KPIState]>) => void;
}

export const kpiStore = create<KPIState>((set) => ({
  truthScore: { value: '99.999%', color: 'green', trend: 'stable' },
  resilience: { value: '<5min', color: 'green', trend: 'up', badge: '0 open' },
  agentHealth: { value: '98%', color: 'green', trend: 'stable', badge: '45/46' },
  updateKPI: (kpiKey, data) => set((state) => ({ [kpiKey]: { ...state[kpiKey], ...data } })),
}));

// Mock SSE integration (prod: replace with actual /api/events listener)
// Why: Enables reactive updates for "3-second truth" aha; smallest safe with mock for isolated testing.
const mockSSE = () => {
  setInterval(() => {
    kpiStore.getState().updateKPI('truthScore', { value: `${Math.random() > 0.5 ? 99.999 : 99.99}%`, color: Math.random() > 0.5 ? 'green' : 'yellow' });
    // Similar for others; prod: Parse SSE JSONB payloads
  }, 5000); // Sim 5s updates
};

if (process.env.NODE_ENV !== 'test') mockSSE(); // Disable in tests
