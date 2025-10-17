import React, { useState } from 'react';

function App() {
  // This is a "state hook". It creates a variable `activeTab` and a function
  // `setActiveTab` to update it. The default value is 'integrity'.
  const [activeTab, setActiveTab] = useState('integrity');

  const tabs = [
    { id: 'integrity', label: 'Data Integrity' },
    { id: 'gpu', label: 'GPU Efficiency' },
    { id: 'roi', label: 'ROI Monitor' },
  ];

  return (
    <div className="bg-brand-bg-primary text-brand-text-secondary min-h-screen">
      {/* Main Header */}
      <header className="bg-brand-bg-secondary border-b border-brand-border py-8 text-center">
        <h1 className="text-6xl font-bold text-brand-text-primary">AI Trust Fabric</h1>
        <p className="text-lg text-brand-text-secondary mt-2">Decision Integrity Platform</p>
      </header>

      {/* Tab Navigation */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="flex justify-center">
          <nav className="flex space-x-2 p-1 bg-brand-bg-secondary rounded-lg">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-md font-semibold text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-brand-accent text-brand-bg-primary'
                    : 'text-brand-text-secondary hover:bg-brand-bg-tertiary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content Area (where panels will go) */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'integrity' && <div>Integrity Panel Placeholder</div>}
        {activeTab === 'gpu' && <div>GPU Panel Placeholder</div>}
        {activeTab === 'roi' && <div>ROI Panel Placeholder</div>}
      </main>
    </div>
  );
}

export default App;
