export interface RAGSource {
  document_id: string;
  source_id?: string;
  title: string;
  document_name?: string;
  clause: string;
  section?: string;
  excerpt: string;
  relevance_score: number;
}

export interface SemanticMatch {
  document_id: string;
  title: string;
  similarity_score: number;
  excerpt: string;
}

export interface AIAnalysis {
  intent: string;
  suggested_department: string;
  priority_score: number;
  urgency_level: 'Low' | 'Medium' | 'High' | 'Critical';
  confidence: number;
  intent_confidence?: number;
  department_confidence?: number;
  priority_confidence?: number;
  requires_human_review?: boolean;
  review_reasons?: string[];
  semantic_matches?: SemanticMatch[];
  pii_detected: string[];
  entities: Record<string, any>;
  summary: string;
  suggested_action: string;
}

export interface SLARecord {
  priority: string;
  sla_hours: number;
  due_at: string;
  is_breached: boolean;
  remaining_hours: number;
  status: 'ON_TRACK' | 'AT_RISK' | 'BREACHED';
}

export interface RMSResponse {
  response_id: string;
  ticket_id: string;
  author_id: string;
  author_name: string;
  author_role: string;
  content: string;
  is_internal: boolean;
  created_at: string;
}

export interface AuditEvent {
  event_id: string;
  ticket_id: string;
  event_type: string;
  actor_id: string;
  actor_role?: string;
  timestamp: string;
  from_state?: string;
  to_state?: string;
  notes?: string;
  details?: Record<string, any>;
}

export interface DepartmentSLAPolicy {
  LOW: number;
  MEDIUM: number;
  HIGH: number;
  CRITICAL: number;
}

export interface DepartmentEscalationPolicy {
  target_role: string;
  escalation_window_hours: number;
  notification_channel: string;
}

export interface Department {
  department_id: string;
  department_code: string;
  name: string;
  description: string;
  categories: string[];
  sla_policy: DepartmentSLAPolicy;
  escalation_policy: DepartmentEscalationPolicy;
  staff_ids: string[];
  hod_reference?: {
    name: string;
    email: string;
    role?: string;
  };
  active_status: boolean;
}

export interface WorkloadMetadata {
  assigned_tickets_count: number;
  open_tickets_count: number;
  max_capacity: number;
  specialty_categories: string[];
}

export interface StaffUser {
  user_id: string;
  display_name: string;
  email: string;
  role: 'STAFF_OPERATOR' | 'DEPARTMENT_STAFF' | 'HOD' | 'DEPARTMENT_HOD' | 'ADMIN' | 'SYSTEM_ADMIN';
  department_id: string;
  department?: string;
  permissions: string[];
  active_status: boolean;
  workload_metadata?: WorkloadMetadata;
  avatar?: string;
}

export interface Assignment {
  assignment_id: string;
  ticket_id: string;
  department_id: string;
  staff_id?: string;
  assigned_by: string;
  assigned_at: string;
  reason?: string;
  active: boolean;
}

export interface Ticket {
  ticket_id: string;
  student_reference: string;
  subject: string;
  title?: string;
  external_reference?: string;
  description: string;
  redacted_description?: string;
  category: string;
  subcategory?: string;
  department: string;
  assigned_department_id?: string;
  assigned_staff_id?: string;
  assigned_staff?: string;
  priority: 'Low' | 'Medium' | 'High' | 'Critical';
  status:
    | 'NEW'
    | 'INGESTED'
    | 'ANALYZED'
    | 'ROUTED'
    | 'STAFF_REVIEW'
    | 'IN_PROGRESS'
    | 'WAITING_FOR_STUDENT'
    | 'WAITING_FOR_DEPARTMENT'
    | 'ESCALATED'
    | 'APPROVED'
    | 'RESOLVED'
    | 'CLOSED'
    | 'DRAFTED';
  created_at: string;
  updated_at?: string;
  due_at?: string;
  attachments: (string | any)[];
  ai_analysis?: AIAnalysis;
  confidence: number;
  resolution_text?: string;
  resolved_at?: string;
  requires_human_review?: boolean;
  sla_record?: SLARecord;
  tags?: string[];
  responses?: RMSResponse[];
  history?: AuditEvent[];
  metadata?: Record<string, any>;
  is_synthetic?: boolean;
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

export interface EvaluationSummary {
  dataset_size: number;
  intent_accuracy: number;
  intent_macro_f1: number;
  intent_weighted_f1?: number;
  department_accuracy: number;
  department_macro_f1: number;
  priority_accuracy: number;
  retrieval_precision_at_1: number;
  retrieval_precision_at_3: number;
  retrieval_recall_at_3: number;
  retrieval_mrr: number;
  grounding_rate: number;
  citation_fidelity: number;
  no_source_adherence: number;
  grounding_evaluation_type: string;
  human_review_rate: number;
  error_case_count: number;
  error_cases?: Array<{
    ticket_id: string;
    subject: string;
    intent: { expected: string; predicted: string };
    department: { expected: string; predicted: string };
    priority: { expected: string; predicted: string };
  }>;
  intent_per_class?: Record<string, any>;
  department_per_class?: Record<string, any>;
}
