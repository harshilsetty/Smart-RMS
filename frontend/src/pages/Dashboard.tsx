import React, { useState, useEffect } from 'react';
import { MetricsBar } from '../components/MetricsBar';
import { TicketQueue } from '../components/TicketQueue';
import { TicketDetail } from '../components/TicketDetail';
import { AIAnalysisCard } from '../components/AIAnalysisCard';
import { RAGSourcesCard } from '../components/RAGSourcesCard';
import { ResponseDraftCard } from '../components/ResponseDraftCard';
import { Ticket, DraftResponse, AnalyticsOverview } from '../types';
import {
  fetchTickets,
  fetchDraftResponse,
  triggerAIAnalysis,
  approveTicket,
  escalateTicket,
  redirectTicket,
  fetchAnalytics
} from '../services/api';

export const Dashboard: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [draft, setDraft] = useState<DraftResponse | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('All Departments');
  const [selectedPriority, setSelectedPriority] = useState('All Priorities');

  const [isLoadingDraft, setIsLoadingDraft] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Initial load
  useEffect(() => {
    loadTickets();
    loadAnalytics();
  }, [selectedDepartment, selectedPriority, searchQuery]);

  const loadTickets = async () => {
    const filters: any = {};
    if (selectedDepartment !== 'All Departments') filters.department = selectedDepartment;
    if (selectedPriority !== 'All Priorities') filters.priority = selectedPriority;
    if (searchQuery.trim()) filters.search = searchQuery.trim();

    const data = await fetchTickets(filters);
    setTickets(data.tickets);
    if (data.tickets.length > 0 && !selectedTicket) {
      handleSelectTicket(data.tickets[0]);
    } else if (selectedTicket) {
      const refreshed = data.tickets.find((t) => t.ticket_id === selectedTicket.ticket_id);
      if (refreshed) setSelectedTicket(refreshed);
    }
  };

  const loadAnalytics = async () => {
    const data = await fetchAnalytics();
    setAnalytics(data);
  };

  const handleSelectTicket = async (ticket: Ticket) => {
    setSelectedTicket(ticket);
    setIsLoadingDraft(true);
    try {
      const draftData = await fetchDraftResponse(ticket.ticket_id);
      setDraft(draftData);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoadingDraft(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedTicket) return;
    setIsAnalyzing(true);
    try {
      await triggerAIAnalysis(selectedTicket.ticket_id);
      showToast('AI analysis & RAG policy check completed.');
      await loadTickets();
      // Reload draft
      const draftData = await fetchDraftResponse(selectedTicket.ticket_id);
      setDraft(draftData);
    } catch (err) {
      showToast('AI analysis failed.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleApprove = async (editedText: string) => {
    if (!selectedTicket) return;
    try {
      await approveTicket(selectedTicket.ticket_id, 'STAFF-OP-01', editedText);
      showToast(`Ticket ${selectedTicket.ticket_id} approved and resolved.`);
      await loadTickets();
      await loadAnalytics();
    } catch (err) {
      showToast('Approval submission failed.');
    }
  };

  const handleEscalate = async () => {
    if (!selectedTicket) return;
    const reason = prompt('Enter escalation note for Department HOD:', 'Requires administrative exception approval.');
    if (!reason) return;
    try {
      await escalateTicket(selectedTicket.ticket_id, 'STAFF-OP-01', reason);
      showToast(`Ticket escalated to HOD.`);
      await loadTickets();
    } catch (err) {
      showToast('Escalation failed.');
    }
  };

  const handleRedirect = async () => {
    if (!selectedTicket) return;
    const newDept = prompt('Enter new department name (e.g. Accounts & Finance, Hostel Affairs):', 'Accounts & Finance');
    if (!newDept) return;
    try {
      await redirectTicket(selectedTicket.ticket_id, 'STAFF-OP-01', newDept, 'Misrouted by student.');
      showToast(`Ticket redirected to ${newDept}.`);
      await loadTickets();
    } catch (err) {
      showToast('Redirection failed.');
    }
  };

  const isApproved = selectedTicket?.status === 'APPROVED' || selectedTicket?.status === 'RESOLVED';

  return (
    <div className="p-5 max-w-[1600px] mx-auto space-y-4">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 bg-slate-800 border border-emerald-500 text-emerald-300 px-4 py-2.5 rounded-xl shadow-2xl text-xs font-semibold z-50 animate-bounce">
          {toastMessage}
        </div>
      )}

      {/* Top Operations KPI Metrics */}
      <MetricsBar analytics={analytics} />

      {/* Workstation 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-230px)] min-h-[680px]">
        {/* Left Column: Filterable Queue (4 cols) */}
        <div className="lg:col-span-4 h-full">
          <TicketQueue
            tickets={tickets}
            selectedTicketId={selectedTicket?.ticket_id || null}
            onSelectTicket={handleSelectTicket}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            selectedDepartment={selectedDepartment}
            setSelectedDepartment={setSelectedDepartment}
            selectedPriority={selectedPriority}
            setSelectedPriority={setSelectedPriority}
          />
        </div>

        {/* Right Column: Active Ticket Workstation (8 cols) */}
        <div className="lg:col-span-8 h-full overflow-y-auto space-y-4 pr-1">
          {selectedTicket ? (
            <>
              {/* Ticket Raw/Redacted Details */}
              <TicketDetail
                ticket={selectedTicket}
                onAnalyze={handleRunAnalysis}
                onEscalate={handleEscalate}
                onRedirect={handleRedirect}
                isAnalyzing={isAnalyzing}
              />

              {/* AI Triage & Evidence Side-by-Side or Stacked */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AIAnalysisCard
                  analysis={selectedTicket.ai_analysis}
                  confidence={selectedTicket.confidence}
                />
                <RAGSourcesCard
                  sources={draft?.sources || []}
                />
              </div>

              {/* Grounded Draft & Human-in-the-Loop Review */}
              <ResponseDraftCard
                draft={draft}
                isLoading={isLoadingDraft}
                onApprove={handleApprove}
                isApproved={isApproved}
              />
            </>
          ) : (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center text-slate-500 text-sm flex items-center justify-center h-full">
              Select a ticket from the queue to start review.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
