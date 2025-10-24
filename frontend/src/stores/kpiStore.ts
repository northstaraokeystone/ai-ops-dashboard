import { create } from 'zustand';

// Define the shape of a single KPI object
export interface Kpi {
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

// Mock real-time updates for demo purposes, but controlled
const mockKpiUpdates = () => {
  setInterval(() => {
    const newColor = Math.random() > 0.5 ? 'green' : 'yellow';
    kpiStore.setState(state => ({
      ...state,
      agentHealth: {
        ...state.agentHealth,
        color: newColor,
        badge: newColor === 'green' ? 'All healthy' : '1 at-risk'
      }
    }));
  }, 7000);
};

// Use Vite's special import.meta.env object to check the mode
// This replaces the problematic `process.env.NODE_ENV`
if (import.meta.env.MODE === 'development') {
  // We can enable this for live local demos if we want, but it's
  // disabled by default to ensure a stable, predictable UI for builds.
  // mockKpiUpdates();
}
