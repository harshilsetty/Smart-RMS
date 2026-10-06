import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Eye,
  EyeOff,
  Paperclip,
  ArrowUpRight,
  Shuffle,
  Bot,
  UserCheck,
  MessageSquare,
  History,
  CheckCircle,
  Archive,
  AlertTriangle,
  Clock,
  Send,
  Lock,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Ticket, Department, StaffUser, AuditEvent, RMSResponse } from '../types';
import {
  assignTicket,
  redirectTicket,
  addTicketResponse,
  escalateTicket,
  resolveTicket,
  closeTicket,
  fetchDepartments,
  fetchUsers
} from '../services/api';

interface TicketDetailProps {
  ticket: Ticket;
  onAnalyze: () => void;
  onRefresh?: () => void;
  isAnalyzing: boolean;
}

export const TicketDetail: React.FC<TicketDetailProps> = ({
  ticket,
  onAnalyze,
  onRefresh,
  isAnalyzing
}) => {
  const [showRedactedOnly, setShowRedactedOnly] = useState(true);
  const [activeTab, setActiveTab] = useState<'details' | 'communication' | 'audit'>('details');
  const [departments, setDepartments] = useState<Department[]>([]);
  const [staffUsers, setStaffUsers] = useState<StaffUser[]>([]);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showRedirectModal, setShowRedirectModal] = useState(false);
  const [showResponseModal, setShowResponseModal] = useState(false);
  const [showEscalateModal, setShowEscalateModal] = useState(false);
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [showHistoryAccordion, setShowHistoryAccordion] = useState(false);

  // Form states
  const [selectedDeptId, setSelectedDeptId] = useState('');
  const [selectedStaffId, setSelectedStaffId] = useState('');
  const [actionReason, setActionReason] = useState('');
  const [responseContent, setResponseContent] = useState('');
  const [isInternalNote, setIsInternalNote] = useState(false);
  const [resolutionNarrative, setResolutionNarrative] = useState('');
  const [escalationLevel, setEscalationLevel] = useState('LEVEL_1');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusFeedback, setStatusFeedback] = useState<string | null>(null);

  useEffect(() => {
    fetchDepartments().then(setDepartments).catch(console.error);
    fetchUsers().then(setStaffUsers).catch(console.error);
  }, []);

  const displayDescription = showRedactedOnly && ticket.redacted_description
    ? ticket.redacted_description
    : ticket.description;

  const triggerToast = (msg: string) => {
    setStatusFeedback(msg);
    setTimeout(() => setStatusFeedback(null), 3000);
  };

  // Handlers
  const handleAssignSubmit = async () => {
    if (!selectedDeptId) return;
    setIsSubmitting(true);
    try {
      await assignTicket(ticket.ticket_id, {
        department_id: selectedDeptId,
        staff_id: selectedStaffId || undefined,
        assigned_by: 'USR-STAFF-01',
        reason: actionReason || 'Operational staff assignment'
      });
      setShowAssignModal(false);
      setActionReason('');
      triggerToast('Assignment saved and recorded in audit trail.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Assignment failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRedirectSubmit = async () => {
    if (!selectedDeptId || !actionReason) return;
    setIsSubmitting(true);
    try {
      await redirectTicket(ticket.ticket_id, 'USR-STAFF-01', selectedDeptId, actionReason);
      setShowRedirectModal(false);
      setActionReason('');
      triggerToast('Ticket successfully redirected to new department.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Redirection failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResponseSubmit = async () => {
    if (!responseContent.trim()) return;
    setIsSubmitting(true);
    try {
      await addTicketResponse(ticket.ticket_id, {
        author_id: 'USR-STAFF-01',
        author_name: 'Staff Operator',
        author_role: 'STAFF_OPERATOR',
        content: responseContent,
        is_internal: isInternalNote
      });
      setResponseContent('');
      setShowResponseModal(false);
      triggerToast(isInternalNote ? 'Internal note added.' : 'Official response sent.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Failed to add communication: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEscalateSubmit = async () => {
    if (!actionReason.trim()) return;
    setIsSubmitting(true);
    try {
      await escalateTicket(ticket.ticket_id, 'USR-STAFF-01', actionReason);
      setShowEscalateModal(false);
      setActionReason('');
      triggerToast('Ticket escalated to Department HOD.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Escalation failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResolveSubmit = async () => {
    if (!resolutionNarrative.trim() || resolutionNarrative.trim().length < 5) {
      alert('Official resolution narrative must be at least 5 characters.');
      return;
    }
    setIsSubmitting(true);
    try {
      await resolveTicket(ticket.ticket_id, {
        staff_id: 'USR-STAFF-01',
        resolution_text: resolutionNarrative,
        notes: actionReason || 'Official resolution by staff operator'
      });
      setShowResolveModal(false);
      setResolutionNarrative('');
      setActionReason('');
      triggerToast('Ticket officially resolved.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCloseSubmit = async () => {
    setIsSubmitting(true);
    try {
      await closeTicket(ticket.ticket_id, {
        staff_id: 'USR-STAFF-01',
        notes: actionReason || 'Ticket verified and permanently closed.'
      });
      setShowCloseModal(false);
      setActionReason('');
      triggerToast('Ticket closed.');
      if (onRefresh) onRefresh();
    } catch (err: any) {
      alert(`Closure failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const sla = ticket.sla_record;
  const isResolvedOrClosed = ticket.status === 'RESOLVED' || ticket.status === 'CLOSED';

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col space-y-4">
      {/* Toast Feedback */}
      {statusFeedback && (
        <div className="bg-emerald-950/80 border border-emerald-500/50 text-emerald-300 text-xs px-3 py-1.5 rounded-lg">
          {statusFeedback}
        </div>
      )}

      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {ticket.ticket_id}
            </span>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              State: {ticket.status}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Student Ref: {ticket.student_reference}
            </span>
            <span className="text-xs text-slate-500">•</span>
            <span className="text-xs text-slate-400">{ticket.category}</span>
          </div>
          <h2 className="text-base font-bold text-white tracking-tight">
            {ticket.subject || ticket.title}
          </h2>
        </div>

        {/* Operational Action Controls */}
        <div className="flex items-center flex-wrap gap-1.5">
          <button
            onClick={onAnalyze}
            disabled={isAnalyzing}
            className="px-2.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition disabled:opacity-50"
            title="Run AI Triage & Copilot"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>{isAnalyzing ? 'Analyzing...' : 'Copilot Triage'}</span>
          </button>

          <button
            onClick={() => setShowAssignModal(true)}
            className="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-sky-300 border border-sky-500/30 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
          >
            <UserCheck className="w-3.5 h-3.5" />
            <span>Assign</span>
          </button>

          <button
            onClick={() => setShowRedirectModal(true)}
            className="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
          >
            <Shuffle className="w-3.5 h-3.5" />
            <span>Redirect</span>
          </button>

          <button
            onClick={() => setShowResponseModal(true)}
            className="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/30 rounded-lg text-xs font-medium flex items-center space-x-1 transition"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Add Note / Reply</span>
          </button>

          <button
            onClick={() => setShowEscalateModal(true)}
            disabled={ticket.status === 'CLOSED'}
            className="px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-500/30 rounded-lg text-xs font-medium flex items-center space-x-1 transition disabled:opacity-40"
          >
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Escalate</span>
          </button>

          {ticket.status !== 'RESOLVED' && ticket.status !== 'CLOSED' && (
            <button
              onClick={() => setShowResolveModal(true)}
              className="px-2.5 py-1.5 bg-emerald-700/80 hover:bg-emerald-600 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Resolve</span>
            </button>
          )}

          {ticket.status === 'RESOLVED' && (
            <button
              onClick={() => setShowCloseModal(true)}
              className="px-2.5 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
            >
              <Archive className="w-3.5 h-3.5" />
              <span>Close Ticket</span>
            </button>
          )}
        </div>
      </div>

      {/* SLA & Ownership Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
        <div>
          <span className="text-slate-400 font-semibold">Department: </span>
          <span className="text-white font-medium">{ticket.department}</span>
          <span className="text-slate-500 mx-2">|</span>
          <span className="text-slate-400 font-semibold">Assigned Staff: </span>
          <span className="text-emerald-400 font-mono font-medium">
            {ticket.assigned_staff || ticket.assigned_staff_id || 'Unassigned'}
          </span>
        </div>
        <div className="flex items-center md:justify-end space-x-3">
          {sla && (
            <>
              <div className="flex items-center space-x-1 text-slate-300">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Due: {new Date(sla.due_at).toLocaleDateString()}</span>
                <span className="text-slate-500">({Math.round(sla.remaining_hours)}h remaining)</span>
              </div>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  sla.status === 'BREACHED'
                    ? 'bg-red-500/20 text-red-400 border-red-500/30'
                    : sla.status === 'AT_RISK'
                    ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                }`}
              >
                SLA: {sla.status}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Tabs: Details / Communication / Audit Trail */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-1 text-xs">
        <button
          onClick={() => setActiveTab('details')}
          className={`px-3 py-1 rounded-t font-semibold transition ${
            activeTab === 'details'
              ? 'text-emerald-400 border-b-2 border-emerald-400 bg-slate-800/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Submission & Triage
        </button>
        <button
          onClick={() => setActiveTab('communication')}
          className={`px-3 py-1 rounded-t font-semibold transition ${
            activeTab === 'communication'
              ? 'text-emerald-400 border-b-2 border-emerald-400 bg-slate-800/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Communication Thread ({ticket.responses?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`px-3 py-1 rounded-t font-semibold transition ${
            activeTab === 'audit'
              ? 'text-emerald-400 border-b-2 border-emerald-400 bg-slate-800/40'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Audit History ({ticket.history?.length || 0})
        </button>
      </div>

      {/* Tab 1: Details */}
      {activeTab === 'details' && (
        <div className="space-y-3.5">
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

            <div className="bg-slate-950/80 border border-slate-800/90 rounded-lg p-3 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans">
              {displayDescription}
            </div>
          </div>

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

          {ticket.resolution_text && (
            <div className="p-3 bg-emerald-950/20 border border-emerald-700/40 rounded-lg space-y-1">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                Official Resolution
              </span>
              <p className="text-xs text-emerald-200">{ticket.resolution_text}</p>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Communication Thread */}
      {activeTab === 'communication' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Staff notes, AI drafts, and official responses dispatched to the student:
            </span>
            <button
              onClick={() => setShowResponseModal(true)}
              className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold"
            >
              + Add Response / Note
            </button>
          </div>

          <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
            {!ticket.responses || ticket.responses.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-xs bg-slate-950/40 rounded-lg">
                No communications recorded yet.
              </div>
            ) : (
              ticket.responses.map((resp, idx) => {
                const isInternal = resp.is_internal;
                const isAIDraft = (resp as any).response_type === 'AI_DRAFT' || resp.author_role === 'AI';
                return (
                  <div
                    key={resp.response_id || idx}
                    className={`p-3 rounded-lg border text-xs space-y-1 ${
                      isInternal
                        ? 'bg-amber-950/15 border-amber-800/40 text-amber-200'
                        : isAIDraft
                        ? 'bg-purple-950/20 border-purple-800/40 text-purple-200'
                        : 'bg-emerald-950/15 border-emerald-800/40 text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white">{resp.author_name || resp.author_id}</span>
                        <span className="text-[10px] text-slate-400 font-mono">({resp.author_role})</span>
                        {isInternal && (
                          <span className="px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 text-[9px] font-bold border border-amber-500/30">
                            INTERNAL NOTE
                          </span>
                        )}
                        {isAIDraft && (
                          <span className="px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 text-[9px] font-bold border border-purple-500/30">
                            AI DRAFT (NOT SENT)
                          </span>
                        )}
                        {!isInternal && !isAIDraft && (
                          <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[9px] font-bold border border-emerald-500/30">
                            OFFICIAL RESPONSE
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono">
                        {new Date(resp.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed whitespace-pre-wrap">{resp.content}</p>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Audit Trail */}
      {activeTab === 'audit' && (
        <div className="space-y-3">
          <div className="text-xs text-slate-400">
            Append-only, tamper-evident chronological audit events for governance:
          </div>

          <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
            {!ticket.history || ticket.history.length === 0 ? (
              <div className="p-6 text-center text-slate-500 text-xs bg-slate-950/40 rounded-lg">
                No audit events recorded yet.
              </div>
            ) : (
              ticket.history.map((evt, idx) => (
                <div
                  key={evt.event_id || idx}
                  className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-emerald-400 font-semibold">{evt.event_type}</span>
                      <span className="text-slate-400">by</span>
                      <span className="font-mono text-slate-300 font-medium">{evt.actor_id}</span>
                      {evt.actor_role && (
                        <span className="text-slate-500 text-[10px]">({evt.actor_role})</span>
                      )}
                    </div>
                    <span className="text-slate-500 font-mono text-[10px]">
                      {new Date(evt.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {evt.from_state && evt.to_state && (
                    <div className="text-[10px] text-slate-400 font-mono">
                      Transition: {evt.from_state} &rarr; {evt.to_state}
                    </div>
                  )}
                  {evt.notes && (
                    <div className="text-slate-300 text-[11px] font-sans pt-0.5">{evt.notes}</div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* ========================================================
          MODALS FOR ACTION CONFIRMATION & UX (Section 22)
         ======================================================== */}

      {/* Modal: Assignment / Reassignment */}
      {showAssignModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Assign / Reassign Ticket</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Department:</label>
                <select
                  value={selectedDeptId}
                  onChange={(e) => setSelectedDeptId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                >
                  <option value="">Select Department...</option>
                  {departments.map((d) => (
                    <option key={d.department_id} value={d.department_id}>
                      {d.name} ({d.department_code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Staff Member (Optional):</label>
                <select
                  value={selectedStaffId}
                  onChange={(e) => setSelectedStaffId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                >
                  <option value="">Auto-assign / Department Queue</option>
                  {staffUsers
                    .filter((u) => !selectedDeptId || u.department_id === selectedDeptId)
                    .map((u) => (
                      <option key={u.user_id} value={u.user_id}>
                        {u.display_name} ({u.role})
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Operational Reason:</label>
                <input
                  type="text"
                  placeholder="e.g. Assigned to senior officer for verification"
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowAssignModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleAssignSubmit}
                disabled={isSubmitting || !selectedDeptId}
                className="px-3 py-1.5 rounded bg-sky-600 text-white text-xs font-semibold hover:bg-sky-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Assigning...' : 'Confirm Assignment'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Redirection */}
      {showRedirectModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Redirect Ticket to Another Department</h3>
            <p className="text-xs text-slate-400">
              Redirection will deactivate previous staff assignments, update department ownership, and record full audit traceability.
            </p>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Destination Department:</label>
                <select
                  value={selectedDeptId}
                  onChange={(e) => setSelectedDeptId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                >
                  <option value="">Select Destination Department...</option>
                  {departments.map((d) => (
                    <option key={d.department_id} value={d.name}>
                      {d.name} ({d.department_code})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Mandatory Redirection Reason:</label>
                <input
                  type="text"
                  placeholder="e.g. Student grievance concerns fee adjustment handled by Accounts"
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowRedirectModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleRedirectSubmit}
                disabled={isSubmitting || !selectedDeptId || !actionReason}
                className="px-3 py-1.5 rounded bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Redirecting...' : 'Confirm Redirection'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Add Response / Note */}
      {showResponseModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-lg w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Add Staff Communication</h3>
            
            <div className="flex items-center space-x-4 text-xs">
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="radio"
                  checked={!isInternalNote}
                  onChange={() => setIsInternalNote(false)}
                  className="accent-emerald-500"
                />
                <span className="text-slate-200 font-medium">Official Student Response</span>
              </label>

              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="radio"
                  checked={isInternalNote}
                  onChange={() => setIsInternalNote(true)}
                  className="accent-amber-500"
                />
                <span className="text-amber-300 font-medium">Internal Staff Note</span>
              </label>
            </div>

            <div>
              <textarea
                rows={4}
                placeholder={isInternalNote ? 'Enter internal review notes visible only to university staff...' : 'Enter official resolution text dispatched to student...'}
                value={responseContent}
                onChange={(e) => setResponseContent(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="flex justify-end space-x-2 pt-1">
              <button
                onClick={() => setShowResponseModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleResponseSubmit}
                disabled={isSubmitting || !responseContent.trim()}
                className="px-3 py-1.5 rounded bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Posting...' : isInternalNote ? 'Save Note' : 'Send Official Response'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Escalate */}
      {showEscalateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Escalate Ticket to Higher Authority</h3>
            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Target Authority:</label>
                <select
                  value={escalationLevel}
                  onChange={(e) => setEscalationLevel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                >
                  <option value="LEVEL_1">Tier 1 Senior Officer</option>
                  <option value="LEVEL_2">Tier 2 Grievance Cell</option>
                  <option value="HOD">Department Head (HOD)</option>
                </select>
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Escalation Reason:</label>
                <input
                  type="text"
                  placeholder="e.g. Special dean waiver required for attendance shortage"
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowEscalateModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleEscalateSubmit}
                disabled={isSubmitting || !actionReason.trim()}
                className="px-3 py-1.5 rounded bg-purple-600 text-white text-xs font-semibold hover:bg-purple-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Escalating...' : 'Confirm Escalation'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Resolve */}
      {showResolveModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-lg w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Officially Resolve Ticket</h3>
            <p className="text-xs text-slate-400">
              Provide the verified official resolution narrative. This will be published into the communication thread and mark the ticket as RESOLVED.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Official Resolution Narrative:</label>
                <textarea
                  rows={4}
                  placeholder="Enter the official university resolution delivered to the student..."
                  value={resolutionNarrative}
                  onChange={(e) => setResolutionNarrative(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-slate-400 font-semibold block mb-1">Internal Resolution Notes (Optional):</label>
                <input
                  type="text"
                  placeholder="e.g. Verified with Exam Cell records"
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowResolveModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleResolveSubmit}
                disabled={isSubmitting || !resolutionNarrative.trim()}
                className="px-3 py-1.5 rounded bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Resolving...' : 'Confirm Resolution'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Close Ticket */}
      {showCloseModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white">Permanently Close Ticket</h3>
            <p className="text-xs text-slate-400">
              Closure marks the ticket as officially completed. Ensure all administrative steps and communications are concluded.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <label className="text-slate-400 font-semibold block mb-1">Closing Verification Notes:</label>
                <input
                  type="text"
                  placeholder="e.g. Student accepted resolution without appeal"
                  value={actionReason}
                  onChange={(e) => setActionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-2">
              <button
                onClick={() => setShowCloseModal(false)}
                className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 text-xs hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCloseSubmit}
                disabled={isSubmitting}
                className="px-3 py-1.5 rounded bg-slate-700 text-white text-xs font-semibold hover:bg-slate-600 disabled:opacity-50"
              >
                {isSubmitting ? 'Closing...' : 'Confirm Closure'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
