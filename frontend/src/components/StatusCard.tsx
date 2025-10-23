import React from 'react';
import { useStore } from 'zustand'; // Zustand for efficient, reactive state mgmt per CTO rec
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'; // shadcn/UI from design_system_v1.md
import { Badge } from '@/components/ui/badge'; // For status badges
import { TrendingUp, TrendingDown } from 'lucide-react'; // Icons for trends, accessible SVGs
import { kpiStore } from '../stores/kpiStore'; // Assumed Zustand store for Trinity data (SSE-fed)

interface StatusCardProps {
  title: string; // e.g., 'Truth Score'
  kpiKey: keyof typeof kpiStore.getState; // Key to fetch from store (type-safe)
}

const StatusCard: React.FC<StatusCardProps> = ({ title, kpiKey }) => {
  const { value, color, trend, badge } = useStore(kpiStore, (state) => state[kpiKey]); // Reactive pull from Zustand

  const trendIcon = trend === 'up' ? (
    <TrendingUp className="h-4 w-4 text-green-500" aria-hidden="true" />
  ) : trend === 'down' ? (
    <TrendingDown className="h-4 w-4 text-red-500" aria-hidden="true" />
  ) : null;

  return (
    <Card className={`border-${color}-500 bg-background shadow-md hover:shadow-lg transition-shadow`} aria-labelledby={`${title}-title`.replace(/\s/g, '-').toLowerCase()}>
      <CardHeader className="pb-2">
        <CardTitle id={`${title}-title`.replace(/\s/g, '-').toLowerCase()} className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between">
        <div className="text-3xl font-bold">{value}</div>
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
