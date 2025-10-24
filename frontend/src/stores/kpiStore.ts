import { create } from 'zustand';

// Define the shape of a single KPI object
interface Kpi {
  value: string;
  color: 'green' | 'red' | 'yellow';
  trend: 'up' | 'down' | 'stable';
  badge?: string;
}

// Define the overall state of the store
interface KpiState {
  truthScore: Kpi;
  resilience: Kpi;
  agentHealth: Kpi;
  // We will let components update the store directly for simplicity,
  // removing the complex updateKPI function.
}

export const kpiStore = create<KpiState>(() => ({
  // --- MOCK DATA ---
  // Clean, initial state for our three KPIs.
  truthScore: {
    value: '99.8%',
    color: 'green',
    trend: 'stable'
  },
  resilience: {
    value: '<2 min',
    color: 'green',
    trend: 'up',
    badge: '0 open'
  },
  agentHealth: {
    value: '98%',
    color: 'yellow',
    trend: 'stable',
    badge: '1 at-risk'
  },
}));


// Mock real-time updates (for demo purposes)
const mockKpiUpdates = () => {
  setInterval(() => {
    // This is a safer way to update a specific part of the state
    const newColor = Math.random() > 0.5 ? 'green' : 'yellow';
    kpiStore.setState(state => ({
      ...state,
      agentHealth: {
        ...state.agentHealth,
        color: newColor,
        badge: newColor === 'green' ? 'All healthy' : '1 at-risk'
      }
    }));
  }, 7000); // Update agent health every 7 seconds
};

// We will keep this disabled for the initial build to ensure stability.
if (process.env.NODE_ENV === 'development-live-demo') {
  // mockKpiUpdates();
}
