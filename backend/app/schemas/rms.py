from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RAGSource(BaseModel):
    document_id: str
    title: str
    clause: str
    excerpt: str
    relevance_score: float = 0.90

class AIAnalysis(BaseModel):
    intent: str
    suggested_department: str
    priority_score: int
    urgency_level: str
    confidence: float = 0.88
    pii_detected: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)
    summary: str
    suggested_action: str

class TicketBase(BaseModel):
    ticket_id: str
    student_reference: str
    subject: str
    description: str
    category: str
    department: str
    priority: str
    status: str
    created_at: str
    attachments: List[str] = Field(default_factory=list)

class Ticket(TicketBase):
    ai_analysis: Optional[AIAnalysis] = None
    confidence: float = 0.85
    redacted_description: Optional[str] = None
    assigned_staff: Optional[str] = None
    resolution_text: Optional[str] = None
    resolved_at: Optional[str] = None

class TicketListResponse(BaseModel):
    total: int
    count: int
    tickets: List[Ticket]

class DraftResponse(BaseModel):
    ticket_id: str
    draft_response: str
    sources: List[RAGSource] = Field(default_factory=list)
    confidence: float
    requires_staff_edit: bool = False
    policy_compliance_passed: bool = True
    disclaimer: str = "AI assists. Humans decide. Please review and verify before approving."

class AnalyzeRequest(BaseModel):
    override_text: Optional[str] = None

class AnalyzeResponse(BaseModel):
    ticket_id: str
    ai_analysis: AIAnalysis
    redacted_description: str
    sources: List[RAGSource] = Field(default_factory=list)

class ApprovalRequest(BaseModel):
    staff_id: str
    approved_text: str
    notes: Optional[str] = None

class ApprovalResponse(BaseModel):
    ticket_id: str
    status: str
    approved_by: str
    resolved_at: str
    message: str

class EscalateRequest(BaseModel):
    staff_id: str
    target_role: str = "DEPARTMENT_HOD"
    reason: str
    urgent: bool = False

class EscalateResponse(BaseModel):
    ticket_id: str
    status: str
    escalated_to: str
    message: str

class RedirectRequest(BaseModel):
    staff_id: str
    new_department: str
    reason: str

class RedirectResponse(BaseModel):
    ticket_id: str
    previous_department: str
    new_department: str
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str = "Smart RMS API"
    version: str = "1.0.0"
    environment: str
    ai_provider: str
    vector_store: str
    mock_mode: bool
    timestamp: str

class AnalyticsOverviewResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    approved_today: int
    escalated_tickets: int
    avg_resolution_time_hours: float
    ai_acceptance_rate: float
    department_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]

class KnowledgeDocResponse(BaseModel):
    document_id: str
    title: str
    department: str
    clause: str
    content: str
    effective_date: str
    keywords: List[str]
