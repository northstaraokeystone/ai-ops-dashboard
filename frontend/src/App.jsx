import React from 'react';
import OverviewDashboard from './components/OverviewDashboard';
// Note: We are no longer importing IntegrityPanel. It has been deprecated.

function App() {
  return (
    <div className="min-h-screen bg-brand-bg-primary text-brand-text-primary p-4 sm:p-6 lg:p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">TruthRun</h1>
        <p className="text-brand-text-secondary mt-1">
          The Trust Command Center
        </p>
      </header>

      <main>
        {/*
          This is the entry point for the Trust Command Center.
          For now, we are only rendering the Level 1 Overview Dashboard.
          In the future, a router will be added here to navigate between
          the Overview, Triage, and Workbench levels.
        */}
        <OverviewDashboard />
      </main>

      <footer className="text-center mt-12 text-brand-text-tertiary text-xs">
        <p>TruthRun v27.1 - The Irrefutable Blueprint</p>
      </footer>
    </div>
  );
}

// ... existing code ...

export default App;

// Forcing a new Cloudflare build - 2025-10-23
