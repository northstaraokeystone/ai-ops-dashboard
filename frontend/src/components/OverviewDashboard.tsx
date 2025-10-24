import React from 'react';
import StatusCard from './StatusCard'; // The component we just fixed

const OverviewDashboard: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" role="region" aria-label="Overview Dashboard">
      <StatusCard title="Truth Score" kpiKey="truthScore" />
      <StatusCard title="Resilience (MTTR)" kpiKey="resilience" />
      <StatusCard title="Agent Health" kpiKey="agentHealth" />
    </div>
  );
};

export default OverviewDashboard;
