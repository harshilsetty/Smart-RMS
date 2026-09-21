import React from 'react';
import { ShieldCheck, Bot, UserCheck, Bell, Activity } from 'lucide-react';

interface HeaderProps {
  activeTab: 'dashboard' | 'analytics' | 'settings';
  setActiveTab: (tab: 'dashboard' | 'analytics' | 'settings') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
      {/* Branding */}
      <div className="flex items-center space-x-3.5">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
          <Bot className="h-6 w-6 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-tight text-white">SMART RMS</h1>
            <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">
              Copilot v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">University RMS Resolution & Operations System</p>
        </div>
      </div>

      {/* Center Navigation Tabs */}
      <nav className="flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'dashboard'
              ? 'bg-slate-800 text-white shadow'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Staff Workstation
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'analytics'
              ? 'bg-slate-800 text-white shadow'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Operations Analytics
        </button>
      </nav>

      {/* Operator Status & Privacy Indicator */}
      <div className="flex items-center space-x-4">
        {/* PII Protection Shield */}
        <div className="flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 text-xs font-medium">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span>PII Redaction: Active</span>
        </div>

        {/* Mock Mode Status Indicator */}
        <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 text-xs">
          <Activity className="h-3.5 w-3.5 text-amber-400" />
          <span>Mock Adapter</span>
        </div>

        {/* Staff Profile Badge */}
        <div className="flex items-center space-x-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-300 border border-slate-700 font-medium text-xs">
            SO
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-xs font-semibold text-slate-200">Staff Operator</p>
            <p className="text-[10px] text-slate-400">Academic & Hostel Desk</p>
          </div>
        </div>
      </div>
    </header>
  );
};
