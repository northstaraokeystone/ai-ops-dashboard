import React from 'react';
import { useStore } from 'zustand';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge'; // <-- CORRECTED IMPORT PATH
import { TrendingUp, TrendingDown } from 'lucide-react';
import { kpiStore, Kpi } from '../stores/kpiStore'; // Import the Kpi type

// Define a type for the keys of the KPI store for type safety
type KpiKey = 'truthScore' | 'resilience' | 'agentHealth';

interface StatusCardProps {
  title: string;
  kpiKey: KpiKey;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, kpiKey }) => {
  // Use a selector to get the specific KPI data.
  // This is more efficient as it only re-renders when this specific part of the store changes.
  const kpiData = useStore(kpiStore, (state) => state[kpiKey]);

  if (!kpiData) {
    return null; // Handle case where data might not be ready
  }

  const { value, color, trend, badge } = kpiData;

  const trendIcon = trend === 'up' ? (
    <TrendingUp className="h-4 w-4 text-green-500" aria-hidden="true" />
  ) : trend === 'down' ? (
    <TrendingDown className="h-4 w-4 text-red-500" aria-hidden="true" />
  ) : null;

  // Dynamically create class names for Tailwind CSS
  const colorClass = {
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    red: 'border-red-500',
  }[color];

  return (
    <Card className={`${colorClass} bg-card shadow-md hover:shadow-lg transition-shadow`} aria-labelledby={`${title.replace(/\s/g, '-').toLowerCase()}-title`}>
      <CardHeader className="pb-2">
        <CardTitle id={`${title.replace(/\s/g, '-').toLowerCase()}-title`} className="text-lg font-semibold text-primary-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between">
        <div className="text-3xl font-bold text-primary-foreground">{value}</div>
        <div className="flex items-center space-x-2">
          {trendIcon && <span className="sr-only">Trend: {trend}</span>}
          {trendIcon}
          {badge && <Badge variant="outline" aria-label={`Badge: ${badge}`}>{badge}</Badge>}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatusCard;
