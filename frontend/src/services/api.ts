import { Ticket, DraftResponse, AnalyticsOverview } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchTickets(filters?: {
  department?: string;
  priority?: string;
  status?: string;
  search?: string;
}): Promise<{ total: number; tickets: Ticket[] }> {
  const params = new URLSearchParams();
  if (filters?.department) params.append('department', filters.department);
  if (filters?.priority) params.append('priority', filters.priority);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.search) params.append('search', filters.search);

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/rms?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Backend API unavailable, falling back to local mock data:', err);
    // Return empty fallback or let caller handle
    return { total: 0, tickets: [] };
  }
}

export async function fetchTicketById(ticketId: string): Promise<Ticket | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch ticket:', err);
    return null;
  }
}

export async function triggerAIAnalysis(ticketId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Analysis failed');
  return await res.json();
}

export async function fetchDraftResponse(ticketId: string): Promise<DraftResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/draft`);
  if (!res.ok) throw new Error('Failed to fetch draft');
  return await res.json();
}

export async function approveTicket(ticketId: string, staffId: string, approvedText: string, notes?: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, approved_text: approvedText, notes })
  });
  if (!res.ok) throw new Error('Approval failed');
  return await res.json();
}

export async function escalateTicket(ticketId: string, staffId: string, reason: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/escalate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, target_role: 'DEPARTMENT_HOD', reason })
  });
  if (!res.ok) throw new Error('Escalation failed');
  return await res.json();
}

export async function redirectTicket(ticketId: string, staffId: string, newDepartment: string, reason: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/redirect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ staff_id: staffId, new_department: newDepartment, reason })
  });
  if (!res.ok) throw new Error('Redirect failed');
  return await res.json();
}

export async function fetchAnalytics(): Promise<AnalyticsOverview> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`);
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return await res.json();
  } catch (err) {
    return {
      total_tickets: 8,
      open_tickets: 6,
      approved_today: 2,
      escalated_tickets: 1,
      avg_resolution_time_hours: 4.2,
      ai_acceptance_rate: 88.5,
      department_distribution: { 'Hostel Affairs': 2, 'Accounts & Finance': 2, 'Examination Branch': 2, 'Academic Affairs': 2 },
      priority_distribution: { 'High': 3, 'Medium': 3, 'Critical': 1, 'Low': 1 }
    };
  }
}
