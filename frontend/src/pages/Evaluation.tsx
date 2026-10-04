import React, { useState, useEffect } from 'react';
import {
  BarChart2,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Cpu,
  Target,
  FileCheck,
  ShieldCheck,
  Layers,
  ArrowRight
} from 'lucide-react';
import { EvaluationSummary } from '../types';
import { fetchEvaluationSummary } from '../services/api';

export const Evaluation: React.FC = () => {
  const [metrics, setMetrics] = useState<EvaluationSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  const loadMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEvaluationSummary();
      setMetrics(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err: any) {
      setError(err.message || 'Failed to execute runtime evaluation');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <div>
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                NLP Pipeline & Evaluation Framework
              </h2>
              <p className="text-xs text-slate-400">
                Runtime benchmark evaluation across synthetic university RMS requests. No mock numbers.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {lastUpdated && (
            <span className="text-[11px] text-slate-400">
              Last Evaluated: <span className="text-slate-200 font-mono">{lastUpdated}</span>
            </span>
          )}
          <button
            onClick={loadMetrics}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl transition shadow-lg shadow-emerald-600/20"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Evaluating...' : 'Re-run Evaluation'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-4 text-xs text-rose-300 flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>Error loading evaluation: {error}</span>
        </div>
      )}

      {/* Primary KPI Grid */}
      {metrics && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Intent Accuracy */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>INTENT ACCURACY</span>
                <Target className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-white tracking-tight">
                  {(metrics.intent_accuracy * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-emerald-400 font-mono">
                  Macro F1: {(metrics.intent_macro_f1).toFixed(3)}
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${metrics.intent_accuracy * 100}%` }}
                />
              </div>
            </div>

            {/* Department Routing */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>ROUTING ACCURACY</span>
                <Cpu className="w-4 h-4 text-teal-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-white tracking-tight">
                  {(metrics.department_accuracy * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-teal-400 font-mono">
                  Macro F1: {(metrics.department_macro_f1).toFixed(3)}
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-teal-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${metrics.department_accuracy * 100}%` }}
                />
              </div>
            </div>

            {/* Retrieval Precision@1 */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>RETRIEVAL PRECISION@1</span>
                <Layers className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-white tracking-tight">
                  {(metrics.retrieval_precision_at_1 * 100).toFixed(1)}%
                </span>
                <span className="text-[11px] text-cyan-400 font-mono">
                  Recall@3: {(metrics.retrieval_recall_at_3 * 100).toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${metrics.retrieval_precision_at_1 * 100}%` }}
                />
              </div>
            </div>

            {/* Grounding Rate */}
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>GROUNDING RATE</span>
                <FileCheck className="w-4 h-4 text-amber-400" />
              </div>
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold text-white tracking-tight">
                  {(metrics.grounding_rate * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                  Heuristic
                </span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-amber-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${metrics.grounding_rate * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Secondary Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-2">
              <span className="text-[11px] text-slate-400 block font-semibold uppercase">
                Priority Assessment Accuracy
              </span>
              <p className="text-xl font-bold text-white">
                {(metrics.priority_accuracy * 100).toFixed(1)}%
              </p>
              <p className="text-[11px] text-slate-400">
                4-tier urgency classification (Low / Medium / High / Critical)
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-2">
              <span className="text-[11px] text-slate-400 block font-semibold uppercase">
                Human Review Trigger Rate
              </span>
              <p className="text-xl font-bold text-amber-400">
                {(metrics.human_review_rate * 100).toFixed(1)}%
              </p>
              <p className="text-[11px] text-slate-400">
                "AI assists. Humans decide." Tickets requiring staff oversight.
              </p>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-2">
              <span className="text-[11px] text-slate-400 block font-semibold uppercase">
                No-Source Policy Adherence
              </span>
              <p className="text-xl font-bold text-emerald-400">
                {(metrics.no_source_adherence * 100).toFixed(0)}%
              </p>
              <p className="text-[11px] text-slate-400">
                Strict no-source-no-answer compliance (no policy fabrication).
              </p>
            </div>
          </div>

          {/* Error Analysis & Disagreements Table */}
          {metrics.error_cases && metrics.error_cases.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="w-4 h-4 text-amber-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    Transparent Error Analysis ({metrics.error_case_count} Cases)
                  </h3>
                </div>
                <span className="text-[11px] text-slate-400">
                  Showing top misclassifications for continuous improvement
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                      <th className="py-2 px-3">Ticket ID</th>
                      <th className="py-2 px-3">Subject</th>
                      <th className="py-2 px-3">Expected Intent</th>
                      <th className="py-2 px-3">Predicted Intent</th>
                      <th className="py-2 px-3">Expected Dept</th>
                      <th className="py-2 px-3">Predicted Dept</th>
                      <th className="py-2 px-3">Expected Priority</th>
                      <th className="py-2 px-3">Predicted Priority</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {metrics.error_cases.map((err, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30">
                        <td className="py-2 px-3 font-mono text-emerald-400">{err.ticket_id}</td>
                        <td className="py-2 px-3 max-w-xs truncate">{err.subject}</td>
                        <td className="py-2 px-3 text-slate-400 font-mono">{err.intent.expected}</td>
                        <td className={`py-2 px-3 font-mono ${err.intent.expected !== err.intent.predicted ? 'text-rose-400 font-semibold' : 'text-slate-300'}`}>
                          {err.intent.predicted}
                        </td>
                        <td className="py-2 px-3 text-slate-400">{err.department.expected}</td>
                        <td className={`py-2 px-3 ${err.department.expected !== err.department.predicted ? 'text-rose-400 font-semibold' : 'text-slate-300'}`}>
                          {err.department.predicted}
                        </td>
                        <td className="py-2 px-3 text-slate-400">{err.priority.expected}</td>
                        <td className={`py-2 px-3 ${err.priority.expected !== err.priority.predicted ? 'text-amber-400 font-semibold' : 'text-slate-300'}`}>
                          {err.priority.predicted}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
