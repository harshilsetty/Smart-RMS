import React, { useState, useEffect } from 'react';
import { Send, Edit3, ShieldAlert, CheckCircle, RefreshCw } from 'lucide-react';
import { DraftResponse } from '../types';

interface ResponseDraftCardProps {
  draft: DraftResponse | null;
  isLoading: boolean;
  onApprove: (editedText: string) => void;
  isApproved: boolean;
}

export const ResponseDraftCard: React.FC<ResponseDraftCardProps> = ({
  draft,
  isLoading,
  onApprove,
  isApproved
}) => {
  const [text, setText] = useState('');

  useEffect(() => {
    if (draft?.draft_response) {
      setText(draft.draft_response);
    }
  }, [draft]);

  if (isLoading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-xs">
        <RefreshCw className="w-5 h-5 mx-auto mb-2 animate-spin text-emerald-400" />
        Generating grounded draft based on university policies...
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Edit3 className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            AI Suggested Response Draft
          </h3>
        </div>

        {isApproved ? (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Resolution Approved</span>
          </span>
        ) : (
          <span className="text-[11px] text-amber-400 font-medium bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
            Pending Staff Approval
          </span>
        )}
      </div>

      {/* Human in the loop banner */}
      <div className="bg-emerald-950/30 border border-emerald-800/40 rounded-lg p-2.5 flex items-start space-x-2 text-xs text-emerald-300">
        <ShieldAlert className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Human-in-the-Loop Safeguard: </span>
          AI assists with verified draft generation. Staff review and final approval is mandatory before any resolution is dispatched.
        </div>
      </div>

      {/* Editable Text Area */}
      <div className="relative">
        <textarea
          rows={7}
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isApproved}
          placeholder="Response draft will appear here..."
          className="w-full bg-slate-950/90 border border-slate-700/80 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 font-sans leading-relaxed focus:outline-none focus:border-emerald-500 transition disabled:opacity-80 disabled:cursor-not-allowed"
        />
      </div>

      {/* Footer / Submit Button */}
      <div className="flex items-center justify-between pt-1">
        <span className="text-[11px] text-slate-500">
          Operator signature will be appended to audit log upon approval.
        </span>

        <button
          onClick={() => onApprove(text)}
          disabled={isApproved || !text.trim()}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center space-x-1.5 transition shadow-lg shadow-emerald-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-3.5 h-3.5" />
          <span>{isApproved ? 'Resolution Sent' : 'Approve & Dispatch Resolution'}</span>
        </button>
      </div>
    </div>
  );
};
