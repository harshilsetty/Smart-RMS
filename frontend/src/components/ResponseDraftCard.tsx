import React, { useState, useEffect } from 'react';
import {
  Send,
  Edit3,
  ShieldAlert,
  CheckCircle,
  RefreshCw,
  AlertTriangle,
  XCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  SlidersHorizontal,
  FileText,
  AlertOctagon,
  Scale
} from 'lucide-react';
import { DraftResponse } from '../types';

interface ResponseDraftCardProps {
  draft: DraftResponse | null;
  isLoading: boolean;
  onApprove: (editedText: string) => void;
  onRegenerate?: () => Promise<void>;
  onOverrideGrounding?: (reason: string, action: string) => Promise<void>;
  isApproved: boolean;
}

export const ResponseDraftCard: React.FC<ResponseDraftCardProps> = ({
  draft,
  isLoading,
  onApprove,
  onRegenerate,
  onOverrideGrounding,
  isApproved
}) => {
  const [text, setText] = useState('');
  const [showClaims, setShowClaims] = useState(false);
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideAction, setOverrideAction] = useState('ACCEPT_DRAFT');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isOverriding, setIsOverriding] = useState(false);

  useEffect(() => {
    if (draft?.draft_response) {
      setText(draft.draft_response);
    }
  }, [draft]);

  const cv = draft?.claim_verification;
  const status = cv?.overall_status || draft?.grounding_status || 'REQUIRES_HUMAN_REVIEW';
  const isBlocked = cv?.is_blocked || draft?.requires_staff_edit || false;

  const handleRegenerate = async () => {
    if (!onRegenerate) return;
    setIsRegenerating(true);
    try {
      await onRegenerate();
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleConfirmOverride = async () => {
    if (!overrideReason.trim() || !onOverrideGrounding) return;
    setIsOverriding(true);
    try {
      await onOverrideGrounding(overrideReason, overrideAction);
      setShowOverrideModal(false);
      setOverrideReason('');
    } finally {
      setIsOverriding(false);
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case 'FULLY_GROUNDED':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1.5 shadow-sm shadow-emerald-950">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>✓ FULLY GROUNDED</span>
          </span>
        );
      case 'PARTIALLY_GROUNDED':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center space-x-1.5 shadow-sm shadow-amber-950">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>⚠ PARTIALLY GROUNDED</span>
          </span>
        );
      case 'CONTRADICTED':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center space-x-1.5 shadow-sm shadow-rose-950">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>✕ CONTRADICTED</span>
          </span>
        );
      case 'INSUFFICIENT_EVIDENCE':
      case 'UNSUPPORTED':
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-orange-500/10 text-orange-400 border border-orange-500/30 flex items-center space-x-1.5 shadow-sm shadow-orange-950">
            <ShieldAlert className="w-3.5 h-3.5 text-orange-400" />
            <span>⚠ INSUFFICIENT EVIDENCE</span>
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 flex items-center space-x-1.5 shadow-sm shadow-yellow-950">
            <AlertOctagon className="w-3.5 h-3.5 text-yellow-400" />
            <span>⚠ REQUIRES HUMAN REVIEW</span>
          </span>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-xs">
        <RefreshCw className="w-6 h-6 mx-auto mb-2 animate-spin text-emerald-400" />
        Verifying draft claims against authoritative university policy evidence...
      </div>
    );
  }

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col space-y-4 shadow-xl">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Edit3 className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            AI Suggested Response & Claim Grounding
          </h3>
        </div>

        <div className="flex items-center space-x-2">
          {getStatusBadge()}
          {cv && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              Score: {Math.round(cv.grounding_score * 100)}% ({cv.latency_ms} ms)
            </span>
          )}
        </div>
      </div>

      {/* Safety Policy Alert Banner */}
      {status === 'CONTRADICTED' ? (
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-lg p-3 text-xs text-rose-300 space-y-1">
          <div className="flex items-center space-x-2 font-bold text-rose-200">
            <XCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Policy Contradiction Detected — Response Blocked</span>
          </div>
          <p className="text-[11px] leading-relaxed text-rose-300/90 pl-6">
            {cv?.block_reason || 'Generated response conflicts directly with authoritative university policy evidence. Immediate staff intervention or override required.'}
          </p>
        </div>
      ) : status === 'REQUIRES_HUMAN_REVIEW' || status === 'UNSUPPORTED' || status === 'INSUFFICIENT_EVIDENCE' ? (
        <div className="bg-amber-950/40 border border-amber-800/60 rounded-lg p-3 text-xs text-amber-300 space-y-1">
          <div className="flex items-center space-x-2 font-bold text-amber-200">
            <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0" />
            <span>Grounding Guardrail Active — Human Review Mandatory</span>
          </div>
          <p className="text-[11px] leading-relaxed text-amber-300/90 pl-6">
            {cv?.block_reason || draft?.refusal_reason || 'Evidence does not fully substantiate all claims or high-impact policy clauses. Automated dispatch is prevented.'}
          </p>
        </div>
      ) : (
        <div className="bg-emerald-950/30 border border-emerald-800/40 rounded-lg p-3 text-xs text-emerald-300 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>
              <strong>Verified Against Policy:</strong> All atomic propositions are corroborated by authoritative evidence.
            </span>
          </div>
          <span className="text-[10px] text-emerald-400 font-mono">
            {cv?.supported_claims_count || 0}/{cv?.total_claims || 0} Claims Verified
          </span>
        </div>
      )}

      {/* Claim-Level Verification Inspection Toggle */}
      {cv && cv.claim_verifications.length > 0 && (
        <div className="border border-slate-800/80 rounded-lg bg-slate-950/50 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowClaims(!showClaims)}
            className="w-full px-3 py-2 text-xs flex items-center justify-between text-slate-300 hover:text-white hover:bg-slate-800/50 transition font-medium"
          >
            <div className="flex items-center space-x-2">
              <Scale className="w-3.5 h-3.5 text-cyan-400" />
              <span>Inspect Atomic Claim Verification ({cv.claim_verifications.length} Claims)</span>
            </div>
            {showClaims ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showClaims && (
            <div className="p-3 border-t border-slate-800/80 space-y-2.5">
              {cv.claim_verifications.map((item, i) => (
                <div
                  key={item.claim.claim_id || i}
                  className={`p-2.5 rounded-lg border text-xs space-y-1.5 transition ${
                    item.status === 'SUPPORTED'
                      ? 'bg-emerald-950/20 border-emerald-900/40'
                      : item.status === 'CONTRADICTED'
                      ? 'bg-rose-950/30 border-rose-800/50'
                      : 'bg-amber-950/20 border-amber-900/40'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-[10px] text-slate-400">{item.claim.claim_id}</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {item.claim.category}
                      </span>
                      {item.is_high_impact && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                          HIGH IMPACT
                        </span>
                      )}
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                        item.status === 'SUPPORTED'
                          ? 'text-emerald-400 bg-emerald-500/10'
                          : item.status === 'CONTRADICTED'
                          ? 'text-rose-400 bg-rose-500/10'
                          : 'text-amber-400 bg-amber-500/10'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <p className="text-slate-100 font-sans text-xs">
                    "{item.claim.text}"
                  </p>

                  {item.matched_evidence && (
                    <div className="text-[11px] text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800 flex items-start space-x-1.5">
                      <FileText className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="font-semibold text-slate-300">
                          {item.matched_evidence.title} ({item.matched_evidence.clause})
                        </span>
                        : <span className="italic">"{item.matched_evidence.excerpt}"</span>
                      </div>
                    </div>
                  )}

                  <p className="text-[10px] text-slate-400">
                    <span className="text-slate-500 font-mono">Verification: </span>
                    {item.verification_reason}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Editable Response Body */}
      <div className="space-y-1">
        <label className="text-[11px] text-slate-400 font-medium flex items-center justify-between">
          <span>Official Response Content (Editable by Staff):</span>
          <span className="text-[10px] font-mono text-slate-500">{text.length} chars</span>
        </label>
        <textarea
          rows={7}
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isApproved}
          placeholder="Response draft will appear here..."
          className="w-full bg-slate-950/90 border border-slate-700/80 rounded-lg p-3 text-xs text-slate-100 placeholder-slate-500 font-sans leading-relaxed focus:outline-none focus:border-emerald-500 transition disabled:opacity-80 disabled:cursor-not-allowed"
        />
      </div>

      {/* Action Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800">
        <div className="flex items-center space-x-2">
          {onRegenerate && (
            <button
              type="button"
              onClick={handleRegenerate}
              disabled={isRegenerating || isApproved}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition flex items-center space-x-1.5 disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating ? 'animate-spin' : ''}`} />
              <span>Regenerate & Verify</span>
            </button>
          )}

          {onOverrideGrounding && isBlocked && (
            <button
              type="button"
              onClick={() => setShowOverrideModal(true)}
              disabled={isApproved}
              className="px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30 hover:bg-amber-500/20 transition flex items-center space-x-1.5"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Override Grounding</span>
            </button>
          )}
        </div>

        <button
          type="button"
          onClick={() => onApprove(text)}
          disabled={isApproved || (isBlocked && status === 'CONTRADICTED')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-1.5 ${
            isApproved
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : isBlocked && status === 'CONTRADICTED'
              ? 'bg-rose-900/50 text-rose-300 border border-rose-700/50 cursor-not-allowed opacity-60'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950/50'
          }`}
        >
          {isApproved ? (
            <>
              <CheckCircle className="w-4 h-4 text-emerald-400" />
              <span>Approved & Sent</span>
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Approve & Send Resolution</span>
            </>
          )}
        </button>
      </div>

      {/* Grounding Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center space-x-2 text-amber-400">
              <SlidersHorizontal className="w-5 h-5" />
              <h3 className="font-bold text-sm text-white">Staff Operational Grounding Override</h3>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              By overriding this verification failure, <strong>you accept operational responsibility</strong> for
              dispatching an uncorroborated response. This event is recorded permanently in the ticket audit trail as{' '}
              <code className="bg-slate-800 text-amber-300 px-1 py-0.5 rounded text-[11px]">GROUNDING_OVERRIDE</code>.
            </p>

            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-400">Action Choice:</label>
              <select
                value={overrideAction}
                onChange={(e) => setOverrideAction(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-slate-200"
              >
                <option value="ACCEPT_DRAFT">Accept Draft With Staff Authority</option>
                <option value="MODIFY_CLAIMS">Modify Draft Claims Manually</option>
                <option value="REJECT_DRAFT">Reject AI Draft Permanently</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-semibold text-slate-400">
                Operational Rationale (Mandatory):
              </label>
              <textarea
                rows={3}
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="Explain why this response is approved despite verification failure..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setShowOverrideModal(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 text-slate-300 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmOverride}
                disabled={!overrideReason.trim() || isOverriding}
                className="px-4 py-1.5 rounded-lg text-xs font-bold bg-amber-600 hover:bg-amber-500 text-white disabled:opacity-50"
              >
                {isOverriding ? 'Logging Override...' : 'Confirm Responsibility & Override'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
