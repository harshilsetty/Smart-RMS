import React from 'react';
import { Sparkles, ShieldAlert, CheckCircle, AlertTriangle, Tag, BookOpen, Layers } from 'lucide-react';
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
  const intentConfPct = analysis.intent_confidence ? Math.round(analysis.intent_confidence * 100) : null;
  const deptConfPct = analysis.department_confidence ? Math.round(analysis.department_confidence * 100) : null;
  const prioConfPct = analysis.priority_confidence ? Math.round(analysis.priority_confidence * 100) : null;

  const requiresReview = analysis.requires_human_review || (analysis.confidence < 0.75);

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
      {/* Header with overall confidence and human review status */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            NLP Triage & Intelligence
          </h3>
        </div>
        
        <div className="flex items-center space-x-2">
          {requiresReview ? (
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-3 h-3" />
              <span>Review Recommended</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle className="w-3 h-3" />
              <span>High Confidence</span>
            </span>
          )}

          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-800 text-slate-200 border border-slate-700">
            {confidencePct}%
          </span>
        </div>
      </div>

      {/* Human Review Advisory if triggered */}
      {requiresReview && analysis.review_reasons && analysis.review_reasons.length > 0 && (
        <div className="bg-amber-950/30 border border-amber-800/40 rounded-lg p-2 text-[11px] text-amber-300 space-y-1">
          <div className="flex items-center space-x-1 font-semibold text-amber-400">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Human-in-the-Loop Flags:</span>
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-amber-200/90 text-[10px]">
            {analysis.review_reasons.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Grid of Extracted Attributes */}
      <div className="grid grid-cols-2 gap-2.5 text-xs">
        {/* Intent */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[10px] text-slate-400 font-semibold">DETECTED INTENT</span>
            {intentConfPct !== null && (
              <span className="text-[9px] text-emerald-400 font-mono">{intentConfPct}%</span>
            )}
          </div>
          <span className="font-mono text-emerald-300 font-bold text-xs truncate block">
            {analysis.intent}
          </span>
        </div>

        {/* Suggested Dept */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[10px] text-slate-400 font-semibold">ROUTED DEPT</span>
            {deptConfPct !== null && (
              <span className="text-[9px] text-slate-400 font-mono">{deptConfPct}%</span>
            )}
          </div>
          <span className="text-slate-200 font-bold text-xs truncate block">
            {analysis.suggested_department}
          </span>
        </div>

        {/* Priority Level */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[10px] text-slate-400 font-semibold">PRIORITY LEVEL</span>
            {prioConfPct !== null && (
              <span className="text-[9px] text-slate-400 font-mono">{prioConfPct}%</span>
            )}
          </div>
          <span className={`font-bold text-xs ${analysis.urgency_level === 'Critical' ? 'text-rose-400' : analysis.urgency_level === 'High' ? 'text-amber-400' : 'text-slate-200'}`}>
            Level {analysis.priority_score} — {analysis.urgency_level}
          </span>
        </div>

        {/* Urgency Level */}
        <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
          <div className="flex items-center justify-between mb-0.5">
            <span className="text-[10px] text-slate-400 font-semibold">URGENCY (TIME HORIZON)</span>
            {analysis.urgency_confidence && (
              <span className="text-[9px] text-purple-400 font-mono">{Math.round(analysis.urgency_confidence * 100)}%</span>
            )}
          </div>
          <span className={`font-bold text-xs ${analysis.urgency === 'IMMEDIATE' ? 'text-rose-400' : analysis.urgency === 'URGENT' ? 'text-amber-400' : 'text-teal-300'}`}>
            {analysis.urgency || analysis.urgency_level || 'NORMAL'}
          </span>
        </div>
      </div>

      {/* Clarification Alert if Ambiguity Detected */}
      {analysis.needs_clarification && (
        <div className="bg-indigo-950/30 border border-indigo-700/50 rounded-lg p-2.5 text-xs text-indigo-300 space-y-1">
          <div className="flex items-center space-x-1.5 font-bold text-indigo-400">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Clarification Required (Ambiguous Query)</span>
          </div>
          <p className="text-[11px] text-indigo-200/90 leading-relaxed">
            {analysis.clarification_reason || 'Query lacks specific domain identifiers. Staff confirmation or student clarification needed.'}
          </p>
        </div>
      )}

      {/* Action Directive */}
      <div className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
        <span className="text-[10px] text-slate-400 block mb-0.5 font-semibold">ACTION DIRECTIVE</span>
        <span className="text-teal-300 font-medium text-[11px] truncate block">
          {analysis.suggested_action}
        </span>
      </div>

      {/* Structured Domain Entities Chips */}
      {analysis.structured_entities && analysis.structured_entities.length > 0 ? (
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-lg p-2.5 space-y-1.5">
          <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
            <Tag className="w-3 h-3 text-teal-400" />
            <span>Structured Entities ({analysis.structured_entities.length})</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {analysis.structured_entities.map((se, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-700/80 text-slate-300 font-mono"
                title={`Confidence: ${Math.round((se.confidence || 0.9) * 100)}% | Span: ${se.source_span || se.value}`}
              >
                <span className="text-slate-400 font-sans mr-1">{se.entity_type}:</span>
                <span className="text-emerald-300 font-semibold">{se.value}</span>
              </span>
            ))}
          </div>
        </div>
      ) : analysis.entities && Object.keys(analysis.entities).length > 0 ? (
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-lg p-2.5 space-y-1.5">
          <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
            <Tag className="w-3 h-3 text-teal-400" />
            <span>Extracted Domain Entities</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(analysis.entities).map(([k, v]) => {
              const displayVal = Array.isArray(v) ? v.join(', ') : typeof v === 'object' ? JSON.stringify(v) : String(v);
              return (
                <span
                  key={k}
                  className="inline-flex items-center px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-700/80 text-slate-300 font-mono"
                >
                  <span className="text-slate-400 font-sans mr-1">{k}:</span>
                  <span className="text-emerald-300 font-semibold">{displayVal}</span>
                </span>
              );
            })}
          </div>
        </div>
      ) : null}

      {/* Machine-readable Explanations */}
      {analysis.explanation && Object.keys(analysis.explanation).length > 0 && (
        <div className="bg-slate-950/50 border border-slate-800/80 rounded-lg p-2.5 space-y-1 text-xs">
          <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block mb-1">
            Explainability & Decision Evidence
          </span>
          <div className="space-y-1 text-[11px] text-slate-300">
            {Object.entries(analysis.explanation).map(([key, val]) => (
              <div key={key} className="flex items-start space-x-1.5">
                <span className="text-slate-400 font-mono text-[10px] uppercase font-bold min-w-[70px] pt-0.5">{key}:</span>
                <span className="text-slate-200 leading-snug">{val}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Semantic Matches if available */}
      {analysis.semantic_matches && analysis.semantic_matches.length > 0 && (
        <div className="bg-slate-950/40 border border-slate-800/60 rounded-lg p-2.5 space-y-1">
          <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
            <Layers className="w-3 h-3 text-cyan-400" />
            <span>Semantic Policy Matches</span>
          </div>
          <div className="space-y-1">
            {analysis.semantic_matches.map((m, idx) => (
              <div key={idx} className="flex items-center justify-between text-[11px] text-slate-300">
                <span className="truncate pr-2">{m.title}</span>
                <span className="font-mono text-cyan-400 text-[10px] font-semibold">
                  {Math.round(m.similarity_score * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Summary */}
      <div className="bg-slate-950/40 border border-slate-800/60 rounded-lg p-2.5">
        <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block mb-1">
          Context Summary
        </span>
        <p className="text-xs text-slate-300 leading-relaxed">
          {analysis.summary}
        </p>
      </div>
    </div>
  );
};
