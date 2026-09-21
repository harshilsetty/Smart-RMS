import React from 'react';
import { Sparkles, Compass, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { AIAnalysis } from '../types';

interface AIAnalysisCardProps {
  analysis: AIAnalysis | undefined;
  confidence: number;
}

export const AIAnalysisCard: React.FC<AIAnalysisCardProps> = ({ analysis, confidence }) => {
  if (!analysis) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center text-slate-500 text-xs">
        <Sparkles className="w-5 h-5 mx-auto mb-1.5 text-slate-600" />
        No AI triage data yet. Click "Run Copilot Triage" to analyze.
      </div>
    );
  }

  const confidencePct = Math.round((analysis.confidence || confidence || 0.85) * 100);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
      {/* Header with confidence meter */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            AI Triage & Intelligence
          </h3>
        </div>
        
        {/* Confidence pill */}
        <div className="flex items-center space-x-1.5">
          <span className="text-[11px] text-slate-400">Confidence:</span>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {confidencePct}%
          </span>
        </div>
      </div>

      {/* Grid of Extracted Attributes */}
      <div className="grid grid-cols-2 gap-2.5 text-xs">
        {/* Intent */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block mb-0.5 font-semibold">DETECTED INTENT</span>
          <span className="font-mono text-emerald-300 font-bold text-xs truncate block">
            {analysis.intent}
          </span>
        </div>

        {/* Suggested Dept */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block mb-0.5 font-semibold">RECOMMENDED DEPT</span>
          <span className="text-slate-200 font-bold text-xs truncate block">
            {analysis.suggested_department}
          </span>
        </div>

        {/* Urgency */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block mb-0.5 font-semibold">URGENCY LEVEL</span>
          <span className={`font-bold text-xs ${analysis.urgency_level === 'Critical' ? 'text-rose-400' : 'text-amber-400'}`}>
            Level {analysis.priority_score} — {analysis.urgency_level}
          </span>
        </div>

        {/* Action Type */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <span className="text-[10px] text-slate-400 block mb-0.5 font-semibold">ACTION DIRECTIVE</span>
          <span className="text-teal-300 font-medium text-[11px] truncate block">
            {analysis.suggested_action}
          </span>
        </div>
      </div>

      {/* AI Summary */}
      <div className="bg-slate-950/40 border border-slate-800/60 rounded-lg p-2.5">
        <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider block mb-1">
          Context Summary
        </span>
        <p className="text-xs text-slate-300 leading-relaxed">
          {analysis.summary}
        </p>
      </div>
    </div>
  );
};
