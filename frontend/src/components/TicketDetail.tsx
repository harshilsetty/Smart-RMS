import React, { useState } from 'react';
import { ShieldCheck, Eye, EyeOff, Paperclip, ArrowUpRight, Shuffle, Bot, AlertCircle } from 'lucide-react';
import { Ticket } from '../types';

interface TicketDetailProps {
  ticket: Ticket;
  onAnalyze: () => void;
  onEscalate: () => void;
  onRedirect: () => void;
  isAnalyzing: boolean;
}

export const TicketDetail: React.FC<TicketDetailProps> = ({
  ticket,
  onAnalyze,
  onEscalate,
  onRedirect,
  isAnalyzing
}) => {
  const [showRedactedOnly, setShowRedactedOnly] = useState(true);

  const displayDescription = showRedactedOnly && ticket.redacted_description
    ? ticket.redacted_description
    : ticket.description;

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3.5">
      {/* Ticket Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {ticket.ticket_id}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Student Ref: {ticket.student_reference}
            </span>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs text-slate-400">{ticket.category}</span>
          </div>
          <h2 className="text-base font-bold text-white tracking-tight">
            {ticket.subject}
          </h2>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition disabled:opacity-50"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>{isAnalyzing ? 'Analyzing...' : 'Run Copilot Triage'}</span>
          </button>

          <button
            onClick={onEscalate}
            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-500/30 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
          >
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Escalate HOD</span>
          </button>

          <button
            onClick={onRedirect}
            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
          >
            <Shuffle className="w-3.5 h-3.5" />
            <span>Redirect</span>
          </button>
        </div>
      </div>

      {/* Student Description & PII Controls */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Student Submission
          </label>
          <button
            onClick={() => setShowRedactedOnly(!showRedactedOnly)}
            className="text-[11px] text-emerald-400 hover:text-emerald-300 flex items-center space-x-1 font-medium"
          >
            {showRedactedOnly ? (
              <>
                <Eye className="w-3.5 h-3.5" />
                <span>Show Original (Staff Vault)</span>
              </>
            ) : (
              <>
                <EyeOff className="w-3.5 h-3.5" />
                <span>Mask PII Tokens</span>
              </>
            )}
          </button>
        </div>

        <div className="bg-slate-950/80 border border-slate-800/90 rounded-lg p-3 text-xs text-slate-300 leading-relaxed font-sans whitespace-pre-wrap">
          {displayDescription}
        </div>
      </div>

      {/* PII Protection Notice */}
      {ticket.ai_analysis?.pii_detected && ticket.ai_analysis.pii_detected.length > 0 && (
        <div className="flex items-center space-x-2 bg-emerald-950/20 border border-emerald-800/30 rounded-lg px-3 py-1.5 text-xs text-emerald-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span className="font-semibold">Sanitized Tokens:</span>
          <div className="flex items-center space-x-1.5 flex-wrap">
            {ticket.ai_analysis.pii_detected.map((token, i) => (
              <span key={i} className="font-mono text-[10px] bg-emerald-900/40 px-1.5 py-0.5 rounded text-emerald-300 border border-emerald-700/50">
                {token}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Attachments list */}
      {ticket.attachments && ticket.attachments.length > 0 && (
        <div className="flex items-center space-x-2 text-xs text-slate-400 pt-1">
          <Paperclip className="w-3.5 h-3.5 text-slate-500" />
          <span className="font-semibold text-slate-300">Attachments:</span>
          {ticket.attachments.map((att, idx) => (
            <span key={idx} className="bg-slate-800 px-2 py-0.5 rounded text-[11px] text-slate-300 border border-slate-700">
              {att}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
