import {
  Ticket,
  DraftResponse,
  AnalyticsOverview,
  Department,
  StaffUser,
  AuditEvent,
  RMSResponse,
  OperationsAnalytics
} from '../types';

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

export async function createTicket(payload: {
  student_reference: string;
  subject: string;
  description: string;
  category?: string;
  department?: string;
  priority?: string;
  subcategory?: string;
  attachments?: string[];
  source?: string;
}): Promise<Ticket> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to create ticket');
  return await res.json();
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

export async function regenerateDraftResponse(ticketId: string): Promise<DraftResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/draft/regenerate`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to regenerate draft');
  return await res.json();
}

export async function overrideGroundingStatus(
  ticketId: string,
  staffId: string,
  reason: string,
  actionTaken: string = 'ACCEPT_DRAFT',
  notes?: string
): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/grounding-override`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      staff_id: staffId,
      reason,
      action_taken: actionTaken,
      notes
    })
  });
  if (!res.ok) throw new Error('Grounding override failed');
  return await res.json();
}

export async function fetchTelemetryMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/telemetry`);
  if (!res.ok) throw new Error('Failed to fetch telemetry');
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

export async function assignTicket(
  ticketId: string,
  payload: { department_id?: string; staff_id?: string; assigned_by: string; reason?: string }
): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Assignment failed');
  return await res.json();
}

export async function addTicketResponse(
  ticketId: string,
  payload: { author_id: string; author_name?: string; author_role?: string; content: string; is_internal?: boolean }
): Promise<RMSResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/responses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to add response');
  return await res.json();
}

export async function fetchTicketHistory(ticketId: string): Promise<AuditEvent[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/history`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return await res.json();
}

export async function fetchDepartments(): Promise<Department[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/departments`);
    if (!res.ok) throw new Error('Failed to fetch departments');
    return await res.json();
  } catch (err) {
    console.error('Error fetching departments:', err);
    return [];
  }
}

export async function fetchDepartmentById(deptId: string): Promise<Department | null> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/departments/${deptId}`);
    if (!res.ok) throw new Error('Failed to fetch department');
    return await res.json();
  } catch (err) {
    console.error('Error fetching department details:', err);
    return null;
  }
}

export async function fetchUsers(filters?: { department_id?: string; role?: string }): Promise<StaffUser[]> {
  const params = new URLSearchParams();
  if (filters?.department_id) params.append('department_id', filters.department_id);
  if (filters?.role) params.append('role', filters.role);

  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/users?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch users');
    return await res.json();
  } catch (err) {
    console.error('Error fetching users:', err);
    return [];
  }
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

export async function fetchOperationsAnalytics(): Promise<OperationsAnalytics> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/operations`);
  if (!res.ok) throw new Error('Failed to fetch operations analytics');
  return await res.json();
}

export async function resolveTicket(
  ticketId: string,
  payload: { staff_id: string; resolution_text: string; notes?: string }
): Promise<Ticket> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Resolution failed' }));
    throw new Error(err.detail || 'Resolution failed');
  }
  return await res.json();
}

export async function closeTicket(
  ticketId: string,
  payload: { staff_id: string; notes?: string }
): Promise<Ticket> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}/close`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Closure failed' }));
    throw new Error(err.detail || 'Closure failed');
  }
  return await res.json();
}

export async function patchTicket(
  ticketId: string,
  payload: {
    status?: string;
    priority?: string;
    department?: string;
    assigned_staff_id?: string;
    assigned_department_id?: string;
    actor_id: string;
    reason?: string;
  }
): Promise<Ticket> {
  const res = await fetch(`${API_BASE_URL}/api/v1/rms/${ticketId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Update failed' }));
    throw new Error(err.detail || 'Update failed');
  }
  return await res.json();
}

export async function fetchEvaluationSummary(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/evaluation/summary`);
  if (!res.ok) throw new Error('Failed to fetch evaluation summary');
  return await res.json();
}

export async function fetchActiveLearningQueue(): Promise<any[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/active-learning/queue`);
  if (!res.ok) throw new Error('Failed to fetch active learning queue');
  return await res.json();
}

export async function fetchActiveLearningMetrics(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/active-learning/metrics`);
  if (!res.ok) throw new Error('Failed to fetch active learning metrics');
  return await res.json();
}

export async function validateFeedback(feedbackId: string, action: 'APPROVE' | 'REJECT', actorId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/active-learning/${feedbackId}/validate?action=${action}&actor_id=${actorId}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to validate feedback');
  return await res.json();
}

export async function fetchProductionModel(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/models/production`);
  if (!res.ok) throw new Error('Failed to fetch production model');
  return await res.json();
}

export async function fetchChallengerModels(): Promise<any[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/models/challengers`);
  if (!res.ok) throw new Error('Failed to fetch challenger models');
  return await res.json();
}

export async function promoteModel(version: string, reviewer: string, reason: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/models/${version}/promote?reviewer=${reviewer}&reason=${reason}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to promote model');
  return await res.json();
}

export async function rollbackModel(version: string, reviewer: string, reason: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/v1/models/${version}/rollback?reviewer=${reviewer}&reason=${reason}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to rollback model');
  return await res.json();
}
