// frontend/src/App.jsx
import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import OverviewDashboard from './components/OverviewDashboard';
import Panel1 from './apps/augury-panel/Panel1';

export default function App() {
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen bg-background text-foreground p-4 sm:p-6 lg:p-8">
      <header className="mb-8">
        <div className="flex items-baseline justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">TruthRun</h1>
            <p className="text-secondary-foreground mt-1">The Trust Command Center</p>
          </div>
          <nav className="flex gap-2 text-sm">
            <Link
              to="/"
              className={`px-3 py-2 rounded-lg ${pathname === '/' ? 'bg-white/10' : 'hover:bg-white/5'} transition`}
            >
              Overview
            </Link>
            <Link
              to="/augury"
              className={`px-3 py-2 rounded-lg ${pathname.startsWith('/augury') ? 'bg-white/10' : 'hover:bg-white/5'} transition`}
            >
              Augury
            </Link>
          </nav>
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<OverviewDashboard />} />
          <Route path="/augury" element={<Panel1 />} />
        </Routes>
      </main>
    </div>
  );
}
