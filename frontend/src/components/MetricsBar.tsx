import React from 'react';
import { Inbox, AlertTriangle, CheckCircle2, ShieldAlert, Clock, Sparkles } from 'lucide-react';
import { AnalyticsOverview } from '../types';

interface MetricsBarProps {
  analytics: AnalyticsOverview | null;
}

export const MetricsBar: React.FC<MetricsBarProps> = ({ analytics }) => {
  const openCount = analytics?.open_tickets ?? 6;
  const criticalCount = analytics?.priority_distribution?.['Critical'] ?? 1;
  const approvedToday = analytics?.approved_today ?? 2;
  const acceptanceRate = analytics?.ai_acceptance_rate ?? 88.5;
  const avgHours = analytics?.avg_resolution_time_hours ?? 4.2;

  const metrics = [
    {
      label: 'Open RMS Queue',
      value: openCount,
      subtext: 'Across all university depts',
      icon: Inbox,
      color: 'text-sky-400',
      bg: 'bg-sky-500/10 border-sky-500/20'
    },
    {
      label: 'Critical / Urgent',
      value: criticalCount,
      subtext: '< 24h SLA threshold',
      icon: AlertTriangle,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10 border-rose-500/20'
    },
    {
      label: 'Approved Today',
      value: approvedToday,
      subtext: 'Verified human resolutions',
      icon: CheckCircle2,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/20'
    },
    {
      label: 'AI Draft Acceptance',
      value: `${acceptanceRate}%`,
      subtext: 'Adopted with minor/no edits',
      icon: Sparkles,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10 border-purple-500/20'
    },
    {
      label: 'Avg Response Time',
      value: `${avgHours}h`,
      subtext: 'Down from 72h baseline',
      icon: Clock,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10 border-amber-500/20'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5 mb-5">
      {metrics.map((m, idx) => {
        const IconComponent = m.icon;
        return (
          <div
            key={idx}
            className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3.5 flex items-center space-x-3 transition hover:border-slate-700"
          >
            <div className={`p-2.5 rounded-lg border ${m.bg}`}>
              <IconComponent className={`h-5 w-5 ${m.color}`} />
            </div>
            <div>
              <div className="text-xl font-bold text-white tracking-tight leading-none mb-1">
                {m.value}
              </div>
              <div className="text-xs font-semibold text-slate-300">{m.label}</div>
              <div className="text-[10px] text-slate-500 truncate max-w-[120px]">{m.subtext}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
