export interface RAGSource {
  document_id: string;
  title: string;
  clause: string;
  excerpt: string;
  relevance_score: number;
}

export interface AIAnalysis {
  intent: string;
  suggested_department: string;
  priority_score: number;
  urgency_level: 'Low' | 'Medium' | 'High' | 'Critical';
  confidence: number;
  pii_detected: string[];
  entities: Record<string, any>;
  summary: string;
  suggested_action: string;
}

export interface Ticket {
  ticket_id: string;
  student_reference: string;
  subject: string;
  description: string;
  redacted_description?: string;
  category: string;
  department: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  status: 'INGESTED' | 'ANALYZED' | 'DRAFTED' | 'STAFF_REVIEW' | 'APPROVED' | 'ESCALATED' | 'RESOLVED';
  created_at: string;
  attachments: string[];
  ai_analysis?: AIAnalysis;
  confidence: number;
  assigned_staff?: string;
  resolution_text?: string;
  resolved_at?: string;
}

export interface DraftResponse {
  ticket_id: string;
  draft_response: string;
  sources: RAGSource[];
  confidence: number;
  requires_staff_edit: boolean;
  policy_compliance_passed: boolean;
  disclaimer: string;
}

export interface AnalyticsOverview {
  total_tickets: number;
  open_tickets: number;
  approved_today: number;
  escalated_tickets: number;
  avg_resolution_time_hours: number;
  ai_acceptance_rate: number;
  department_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
}
