import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'; // shadcn for modal per design_system_v1.md
import ActionButton from './ActionButton'; // From T-2.11.1
import { useStore } from 'zustand';
import { incidentStore } from '../stores/incidentStore';

interface IncidentWorkbenchProps {
  incidentId: string; // Prop for fetch
  trigger: React.ReactNode; // e.g., Table row click trigger
}

const IncidentWorkbench: React.FC<IncidentWorkbenchProps> = ({ incidentId, trigger }) => {
  const [open, setOpen] = React.useState(false);
  const incidents = useStore(incidentStore, (state) => state.incidents);
  const incident = incidents.find((inc) => inc.id === incidentId);

  if (!incident) return null;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-4xl" aria-describedby="incident-details">
        <DialogHeader>
          <DialogTitle>Incident Workbench: {incident.action}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <pre aria-label="Raw payload" className="overflow-auto p-4 bg-gray-100 rounded">{JSON.stringify(incident.agentSupport, null, 2)}</pre>
          <div className="flex flex-wrap gap-4">
            {incident.suggestedActions.map((action) => (
              <ActionButton key={action.playbookId} {...action} />
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default IncidentWorkbench;
