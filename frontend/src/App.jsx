import { useState, useEffect } from 'react';
import IntegrityPanel from './components/IntegrityPanel';

function App() {
  // State for the active UI tab
  const [activeTab, setActiveTab] = useState('integrity');

  // State for holding the array of interaction data fetched from the API
  const [interactions, setInteractions] = useState([]);

  // The definition for our navigation tabs
  const tabs = [
    { id: 'integrity', label: 'Data Integrity' },
    // { id: 'gpu', label: 'GPU Efficiency' },  // Placeholders for future work
    // { id: 'roi', label: 'ROI Monitor' },    // Placeholders for future work
  ];

  // Effect hook to fetch data from the backend API only once when the component mounts
  useEffect(() => {
    const fetchInteractions = async () => {
      try {
        // We call our local backend server, which is running on port 8000
        const response = await fetch('http://localhost:8000/api/interaction/');
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setInteractions(data); // Update our state with the fetched data
        console.log('Fetched interactions:', data); // Log for debugging
      } catch (error) {
        console.error('Error fetching interactions:', error);
      }
    };

    fetchInteractions();
  }, []); // The empty array [] means this effect runs only once

  // The main render function for the component
  return (
    <div className="bg-brand-bg-primary text-brand-text-secondary min-h-screen">
      {/* Main Header */}
      <header className="bg-brand-bg-secondary border-b border-brand-border py-8 text-center">
        <h1 className="text-6xl font-bold text-brand-text-primary">Fulcrum Ledger</h1>
        <p className="text-lg text-brand-text-secondary mt-2">Agentic Operations & Resilience Dashboard</p>
      </header>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="flex justify-center">
          <nav className="flex space-x-2 p-1 bg-brand-bg-secondary rounded-lg">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-md font-semibold text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-brand-accent text-brand-bg-primary'
                    // The classes below are from your MVP's styling
                    : 'text-brand-text-secondary hover:bg-brand-bg-tertiary'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Conditionally render the correct panel based on the active tab */}
        {activeTab === 'integrity' && <IntegrityPanel interactions={interactions} />}

        {/* These are placeholders for when we build the other panels */}
        {/* {activeTab === 'gpu' && <div>GPU Panel Placeholder</div>} */}
        {/* {activeTab === 'roi' && <div>ROI Panel Placeholder</div>} */}
      </main>
    </div>
  );
}

export default App;
