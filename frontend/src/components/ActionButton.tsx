import React, { useState } from 'react';
import { Button } from '@/components/ui/button'; // shadcn/UI from design_system_v1.md
import { Loader2, Check, AlertCircle } from 'lucide-react'; // Icons for states

interface ActionButtonProps {
  playbookId: string; // For API call
  playbookName: string; // e.g., "Restart Container"
  successRate: string; // e.g., "91% Success"
  confidence: number; // e.g., 0.92 (display as %)
}

const ActionButton: React.FC<ActionButtonProps> = ({ playbookId, playbookName, successRate, confidence }) => {
  const [state, setState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleClick = async () => {
    setState('loading');
    try {
      // Mock API call (prod: fetch POST /api/playbook/{id}/execute)
      await new Promise((resolve) => setTimeout(resolve, 1500)); // Sim 1.5s exec
      // Assume success; prod: handle response
      setState('success');
    } catch (error) {
      setState('error');
    }
  };

  const buttonContent = {
    idle: playbookName,
    loading: <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Executing...</>,
    success: <><Check className="mr-2 h-4 w-4" />Success</>,
    error: <><AlertCircle className="mr-2 h-4 w-4" />Error</>,
  }[state];

  return (
    <div className="flex flex-col items-start space-y-1">
      <Button
        onClick={handleClick}
        disabled={state !== 'idle'}
        className={`bg-blue-500 hover:bg-blue-600 text-white ${state === 'success' ? 'bg-green-500' : state === 'error' ? 'bg-red-500' : ''}`}
        aria-label={`${playbookName} with ${successRate} and ${Math.round(confidence * 100)}% confidence`}
      >
        {buttonContent}
      </Button>
      <div className="text-sm text-gray-500">{successRate} • {Math.round(confidence * 100)}% Confidence</div>
    </div>
  );
};

export default ActionButton;
