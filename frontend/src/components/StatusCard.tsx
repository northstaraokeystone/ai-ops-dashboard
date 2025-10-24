import React from 'react';
import { useStore } from 'zustand';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { kpiStore, Kpi } from '../stores/kpiStore';

type KpiKey = 'truthScore' | 'resilience' | 'agentHealth';

interface StatusCardProps {
  title: string;
  kpiKey: KpiKey;
}

const StatusCard: React.FC<StatusCardProps> = ({ title, kpiKey }) => {
  const kpiData = useStore(kpiStore, (state) => state[kpiKey]);

  if (!kpiData) return null;

  const { value, color, trend, badge } = kpiData;

  const trendIcon = trend === 'up' ? (
    <TrendingUp className="h-4 w-4 text-green-500" aria-hidden="true" />
  ) : trend === 'down' ? (
    <TrendingDown className="h-4 w-4 text-red-500" aria-hidden="true" />
  ) : null;

  const colorClass = {
    green: 'border-green-500',
    yellow: 'border-yellow-500',
    red: 'border-red-500',
  }[color];

  return (
    <Card
      className={`${colorClass} bg-card shadow-md transition-all duration-200 ease-in-out transform hover:scale-[1.03] hover:shadow-xl hover:border-accent`}
      aria-labelledby={`${title.replace(/\s/g, '-').toLowerCase()}-title`}
    >
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
