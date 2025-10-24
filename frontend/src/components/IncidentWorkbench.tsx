import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import ActionButton from './ActionButton';
import { useStore } from 'zustand';
import { incidentStore } from '../stores/incidentStore';

interface IncidentWorkbenchProps {
  incidentId: string;
  trigger: React.ReactNode;
}

const IncidentWorkbench: React.FC<IncidentWorkbenchProps> = ({ incidentId, trigger }) => {
  const [open, setOpen] = React.useState(false);
  const incidents = useStore(incidentStore, (state) => state.incidents);
  const incident = incidents.find((inc) => inc.id === incidentId);

  if (!incident) {
    // Return null or a fallback UI if the incident isn't found
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-4xl" aria-describedby="incident-details">
        <DialogHeader>
          <DialogTitle>Incident Workbench: {incident.action}</DialogTitle>
        </DialogHeader>
        <div id="incident-details" className="space-y-4 mt-4">
          <h3 className="text-lg font-semibold">Raw Payload</h3>
          <pre aria-label="Raw payload" className="text-xs p-4 bg-gray-800 text-white rounded-md overflow-auto max-h-60">{JSON.stringify(incident.agentSupport, null, 2)}</pre>

          <h3 className="text-lg font-semibold">Suggested Actions</h3>
          <div className="flex flex-wrap gap-4">
            {incident.suggestedActions.map((action) => (
              <ActionButton
                key={action.playbookId}
                playbookId={action.playbookId}
                // THIS IS THE FIX: Map 'playbookName' from our store to the prop the button expects
                playbookName={action.playbookName}
                successRate={action.successRate}
                confidence={action.confidence}
              />
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default IncidentWorkbench;
