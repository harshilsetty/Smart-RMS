import React from 'react';
import { Search, Filter, Sparkles, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { Ticket } from '../types';

interface TicketQueueProps {
  tickets: Ticket[];
  selectedTicketId: string | null;
  onSelectTicket: (ticket: Ticket) => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  selectedDepartment: string;
  setSelectedDepartment: (dept: string) => void;
  selectedPriority: string;
  setSelectedPriority: (prio: string) => void;
}

const DEPARTMENTS = [
  'All Departments',
  'Hostel Affairs',
  'Accounts & Finance',
  'Academic Affairs',
  'Examination Branch',
  'Student Welfare',
  'Scholarship Section',
  'IT Services'
];

const PRIORITIES = ['All Priorities', 'Critical', 'High', 'Medium', 'Low'];

export const TicketQueue: React.FC<TicketQueueProps> = ({
  tickets,
  selectedTicketId,
  onSelectTicket,
  searchQuery,
  setSearchQuery,
  selectedDepartment,
  setSelectedDepartment,
  selectedPriority,
  setSelectedPriority
}) => {
  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'High':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Medium':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
      case 'RESOLVED':
        return <span className="inline-flex items-center text-[10px] text-emerald-400 font-semibold"><CheckCircle className="w-3 h-3 mr-1" /> Approved</span>;
      case 'ESCALATED':
        return <span className="inline-flex items-center text-[10px] text-purple-400 font-semibold"><AlertCircle className="w-3 h-3 mr-1" /> Escalated</span>;
      case 'DRAFTED':
        return <span className="inline-flex items-center text-[10px] text-teal-400 font-semibold"><Sparkles className="w-3 h-3 mr-1" /> Draft Ready</span>;
      default:
        return <span className="inline-flex items-center text-[10px] text-amber-400 font-semibold"><Clock className="w-3 h-3 mr-1" /> In Review</span>;
    }
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl flex flex-col h-full overflow-hidden">
      {/* Search & Filter Header */}
      <div className="p-3.5 border-b border-slate-800 space-y-2.5">
        <div className="relative">
          <Search className="h-4 w-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search tickets, subject, or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950/80 border border-slate-700/80 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="grid grid-cols-2 gap-2">
          <select
            value={selectedDepartment}
            onChange={(e) => setSelectedDepartment(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 rounded-md px-2 py-1 focus:outline-none focus:border-emerald-500"
          >
            {DEPARTMENTS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>

          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 rounded-md px-2 py-1 focus:outline-none focus:border-emerald-500"
          >
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Ticket List Items */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60">
        {tickets.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No tickets match your filters.
          </div>
        ) : (
          tickets.map((t) => {
            const isSelected = t.ticket_id === selectedTicketId;
            return (
              <div
                key={t.ticket_id}
                onClick={() => onSelectTicket(t)}
                className={`p-3.5 cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-slate-800/90 border-l-4 border-l-emerald-500'
                    : 'hover:bg-slate-800/40'
                }`}
              >
                {/* Meta row */}
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono text-slate-400 font-semibold">{t.ticket_id}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${getPriorityBadge(t.priority)}`}>
                      {t.priority}
                    </span>
                  </div>
                  {getStatusBadge(t.status)}
                </div>

                {/* Subject */}
                <h3 className="text-xs font-semibold text-slate-200 line-clamp-1 mb-1">
                  {t.subject}
                </h3>

                {/* Department & Student Ref */}
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[140px] text-slate-300 font-medium">{t.department}</span>
                  <span className="font-mono text-[10px] text-slate-500">{t.student_reference}</span>
                </div>

                {/* AI Triage Snippet */}
                {t.ai_analysis && (
                  <div className="mt-2 pt-1.5 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                    <span className="text-emerald-400 font-medium truncate max-w-[160px]">
                      ⚡ {t.ai_analysis.intent}
                    </span>
                    <span className="text-slate-400 font-semibold">
                      {Math.round(t.confidence * 100)}% conf
                    </span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
