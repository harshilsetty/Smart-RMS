import React from 'react';
import { Inbox, AlertTriangle, CheckCircle2, ShieldAlert, Clock, Sparkles, AlertOctagon, Archive } from 'lucide-react';
import { AnalyticsOverview, OperationsAnalytics } from '../types';

interface MetricsBarProps {
  analytics?: AnalyticsOverview | null;
  operationsAnalytics?: OperationsAnalytics | null;
}

export const MetricsBar: React.FC<MetricsBarProps> = ({ analytics, operationsAnalytics }) => {
  if (operationsAnalytics) {
    const total = operationsAnalytics.total_tickets;
    const backlog = operationsAnalytics.open_backlog;
    const escalated = operationsAnalytics.escalation_count;
    const atRisk = operationsAnalytics.tickets_by_sla_status?.['AT_RISK'] ?? 0;
    const breached = operationsAnalytics.tickets_by_sla_status?.['BREACHED'] ?? 0;
    const resolved = operationsAnalytics.resolved_count;
    const closed = operationsAnalytics.closed_count;

    const opMetrics = [
      {
        label: 'Total RMS',
        value: total,
        subtext: 'Synthetic registry',
        icon: Inbox,
        color: 'text-sky-400',
        bg: 'bg-sky-500/10 border-sky-500/20'
      },
      {
        label: 'Active Backlog',
        value: backlog,
        subtext: 'In progress & review',
        icon: Clock,
        color: 'text-amber-400',
        bg: 'bg-amber-500/10 border-amber-500/20'
      },
      {
        label: 'SLA At Risk',
        value: atRisk,
        subtext: '< 25% window remaining',
        icon: AlertTriangle,
        color: 'text-rose-400',
        bg: 'bg-rose-500/10 border-rose-500/20'
      },
      {
        label: 'SLA Breached',
        value: breached,
        subtext: 'Overdue resolution',
        icon: AlertOctagon,
        color: 'text-red-500',
        bg: 'bg-red-500/10 border-red-500/20'
      },
      {
        label: 'Escalated (HOD)',
        value: escalated,
        subtext: 'Tier 1 / Tier 2',
        icon: ShieldAlert,
        color: 'text-purple-400',
        bg: 'bg-purple-500/10 border-purple-500/20'
      },
      {
        label: 'Resolved',
        value: resolved,
        subtext: 'Awaiting closure',
        icon: CheckCircle2,
        color: 'text-emerald-400',
        bg: 'bg-emerald-500/10 border-emerald-500/20'
      },
      {
        label: 'Closed',
        value: closed,
        subtext: 'Completed lifecycle',
        icon: Archive,
        color: 'text-slate-400',
        bg: 'bg-slate-500/10 border-slate-500/20'
      }
    ];

    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3 mb-4">
        {opMetrics.map((m, idx) => {
          const IconComponent = m.icon;
          return (
            <div
              key={idx}
              className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-3 flex items-center space-x-2.5 transition hover:border-slate-700"
            >
              <div className={`p-2 rounded-lg border ${m.bg}`}>
                <IconComponent className={`h-4 w-4 ${m.color}`} />
              </div>
              <div className="min-w-0">
                <div className="text-lg font-bold text-white tracking-tight leading-none mb-0.5">
                  {m.value}
                </div>
                <div className="text-[11px] font-semibold text-slate-300 truncate">{m.label}</div>
                <div className="text-[9px] text-slate-500 truncate">{m.subtext}</div>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Fallback to overview analytics
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
