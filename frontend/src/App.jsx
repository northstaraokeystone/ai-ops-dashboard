import React from 'react';
import OverviewDashboard from './components/OverviewDashboard';

function App() {
  return (
    <div className="min-h-screen bg-background text-foreground p-4 sm:p-6 lg:p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">TruthRun</h1>
        <p className="text-secondary-foreground mt-1">
          The Trust Command Center
        </p>
      </header>
      <main>
        <OverviewDashboard />
      </main>
    </div>
  );
}

export default App;
