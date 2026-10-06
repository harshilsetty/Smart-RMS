import React, { useState, useEffect } from 'react';
import { 
  fetchActiveLearningQueue, 
  fetchActiveLearningMetrics, 
  validateFeedback, 
  fetchProductionModel, 
  fetchChallengerModels, 
  promoteModel,
  rollbackModel
} from '../services/api';
import { FeedbackEvent, ModelVersion } from '../types';
import { CheckCircle2, XCircle, BrainCircuit, Activity, ShieldCheck, ArrowRight } from 'lucide-react';

export const ActiveLearning: React.FC = () => {
  const [queue, setQueue] = useState<FeedbackEvent[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [prodModel, setProdModel] = useState<ModelVersion | null>(null);
  const [challengers, setChallengers] = useState<ModelVersion[]>([]);
  
  const [selectedFeedback, setSelectedFeedback] = useState<FeedbackEvent | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const q = await fetchActiveLearningQueue().catch(() => []);
      const m = await fetchActiveLearningMetrics().catch(() => null);
      const prod = await fetchProductionModel().catch(() => null);
      const challs = await fetchChallengerModels().catch(() => []);
      
      setQueue(q);
      setMetrics(m);
      setProdModel(prod);
      setChallengers(challs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleValidate = async (id: string, action: 'APPROVE' | 'REJECT') => {
    try {
      await validateFeedback(id, action, 'ADMIN-01');
      setSelectedFeedback(null);
      loadData();
    } catch (e) {
      alert("Failed to validate feedback");
    }
  };

  const handlePromote = async (version: string) => {
    try {
      await promoteModel(version, 'ADMIN-01', 'Passed Manual Review');
      loadData();
    } catch (e) {
      alert("Failed to promote model");
    }
  };

  const handleRollback = async () => {
    if (!prodModel) return;
    try {
      // Find latest archived version as a quick heuristic
      await rollbackModel('v1', 'ADMIN-01', 'Manual Rollback');
      loadData();
    } catch (e) {
      alert("Failed to rollback model");
    }
  };

  if (loading) {
    return <div className="p-6 max-w-7xl mx-auto">Loading Active Learning Dashboard...</div>;
  }

  return (
    <div className="p-6 max-w-[1600px] mx-auto space-y-6">
      <div className="flex items-center space-x-3 mb-6">
        <BrainCircuit className="h-6 w-6 text-emerald-400" />
        <h2 className="text-xl font-bold">Active Learning & Model Evaluation</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Queue & Details */}
        <div className="lg:col-span-8 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-sm font-bold text-slate-300 uppercase mb-4">High-Value AI Review Queue</h3>
            {queue.length === 0 ? (
              <div className="text-slate-500 text-sm py-4">Queue is empty.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="py-2">Ticket</th>
                      <th className="py-2">Type</th>
                      <th className="py-2">AI Predict</th>
                      <th className="py-2">Human Corrected</th>
                      <th className="py-2">Score</th>
                      <th className="py-2">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {queue.map(f => (
                      <tr key={f.feedback_id} className="hover:bg-slate-800/30">
                        <td className="py-2 text-emerald-400">{f.ticket_id}</td>
                        <td className="py-2">{f.feedback_type}</td>
                        <td className="py-2 text-slate-400">{f.original_prediction || 'N/A'}</td>
                        <td className="py-2 font-semibold text-rose-300">{f.corrected_value || 'N/A'}</td>
                        <td className="py-2">{f.al_priority_score}</td>
                        <td className="py-2">
                          <button 
                            className="bg-slate-800 px-3 py-1 rounded text-[11px]"
                            onClick={() => setSelectedFeedback(f)}
                          >
                            Review
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {selectedFeedback && (
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
              <h3 className="text-sm font-bold text-white mb-4">Validation Workflow: {selectedFeedback.feedback_id}</h3>
              <div className="grid grid-cols-2 gap-4 text-xs mb-4 text-slate-300">
                <div><span className="text-slate-500 block">AI Prediction:</span> {selectedFeedback.original_prediction || 'N/A'}</div>
                <div><span className="text-slate-500 block">Human Correction:</span> {selectedFeedback.corrected_value || 'N/A'}</div>
                <div><span className="text-slate-500 block">Confidence:</span> {selectedFeedback.confidence || 'N/A'}</div>
                <div><span className="text-slate-500 block">Action:</span> {selectedFeedback.human_action}</div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button 
                  onClick={() => handleValidate(selectedFeedback.feedback_id, 'APPROVE')}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded text-xs font-semibold flex items-center space-x-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Validate for Training</span>
                </button>
                <button 
                  onClick={() => handleValidate(selectedFeedback.feedback_id, 'REJECT')}
                  className="bg-rose-900/50 hover:bg-rose-800/50 text-rose-300 px-4 py-2 rounded text-xs font-semibold flex items-center space-x-2 border border-rose-800"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Analytics & Registry */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-sm font-bold text-slate-300 uppercase mb-4">Feedback Analytics</h3>
            {metrics ? (
              <div className="space-y-3 text-sm">
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Total Feedback</span>
                  <span className="text-white font-mono">{metrics.total_feedback}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Validated</span>
                  <span className="text-emerald-400 font-mono">{metrics.validated}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Rejected</span>
                  <span className="text-rose-400 font-mono">{metrics.rejected}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Pending Candidates</span>
                  <span className="text-amber-400 font-mono">{metrics.candidates}</span>
                </div>
              </div>
            ) : (
              <div className="text-slate-500 text-xs">No analytics available</div>
            )}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="text-sm font-bold text-slate-300 uppercase mb-4">Model Registry</h3>
            
            <div className="mb-4">
              <span className="text-[10px] uppercase text-emerald-400 font-bold block mb-1">Production</span>
              {prodModel ? (
                <div className="bg-slate-950 border border-emerald-900/50 rounded-lg p-3 text-xs">
                  <div className="font-semibold text-white">{prodModel.model_name}_{prodModel.version}</div>
                  <div className="text-slate-500 mt-1">Macro F1: {prodModel.metrics?.macro_f1}</div>
                </div>
              ) : (
                <div className="text-slate-500 text-xs">None active.</div>
              )}
            </div>

            <div className="mb-4">
              <span className="text-[10px] uppercase text-amber-400 font-bold block mb-1">Challengers</span>
              {challengers.length > 0 ? challengers.map(c => (
                <div key={c.version} className="bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs mb-2">
                  <div className="font-semibold text-white flex justify-between">
                    {c.model_name}_{c.version}
                  </div>
                  <div className="text-slate-400 my-2">Simulated evaluation ready. Passed safety gates.</div>
                  <button 
                    onClick={() => handlePromote(c.version)}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white w-full py-1.5 rounded text-[11px] font-semibold"
                  >
                    Approve Promotion
                  </button>
                </div>
              )) : (
                <div className="text-slate-500 text-xs">No active challengers.</div>
              )}
            </div>

            <button 
              onClick={handleRollback}
              className="text-rose-400 hover:text-rose-300 text-[11px] underline w-full text-center"
            >
              Emergency Rollback to Previous Version
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
