from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict, model_validator

# Re-export canonical domain contracts
from app.schemas.contracts import (
    InvalidStateTransitionError,
    TicketStatus,
    PriorityLevel,
    StaffRole,
    SLAStatus,
    ResponseType,
    ResponseStatus,
    EscalationLevel,
    AuditEventType,
    StudentReference,
    DepartmentSLAPolicy,
    DepartmentEscalationPolicy,
    Department,
    StaffUser,
    WorkloadMetadata,
    AttachmentMetadata,
    SLARecord,
    AuditEvent,
    RMSResponse,
    Assignment,
    Escalation,
    KnowledgeDocument,
    RMSRequest,
    RMSCreateRequest,
    AssignmentRequest,
    RMSResponseCreateRequest,
    ResolveRequest,
    CloseRequest,
    TicketPatchRequest,
    OperationsAnalytics
)


class RAGSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str
    title: str
    clause: str
    excerpt: str
    relevance_score: float = 0.90
    source_id: Optional[str] = None
    document_name: Optional[str] = None
    section: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.source_id:
            self.source_id = self.document_id
        if not self.document_name:
            self.document_name = self.title
        if not self.section:
            self.section = self.clause


class AIAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    intent: str
    suggested_department: str
    priority_score: int
    urgency_level: str
    confidence: float = 0.88
    intent_confidence: Optional[float] = None
    department_confidence: Optional[float] = None
    priority_confidence: Optional[float] = None
    requires_human_review: bool = False
    review_reasons: List[str] = Field(default_factory=list)
    semantic_matches: List[Dict[str, Any]] = Field(default_factory=list)
    pii_detected: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)
    summary: str
    suggested_action: str


class TicketBase(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    ticket_id: str
    student_reference: str
    subject: str
    description: str
    category: str
    department: str
    priority: str
    status: str
    created_at: str
    attachments: List[Any] = Field(default_factory=list)


class Ticket(TicketBase):
    """
    Core Ticket model.
    Maintains 100% backward compatibility with Phase 1 frontend/tests,
    while embodying the full Milestone 1 & 2 canonical data contract.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    title: Optional[str] = None
    external_reference: Optional[str] = None
    subcategory: Optional[str] = None
    assigned_department_id: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    assigned_staff: Optional[str] = None
    escalation_level: int = 0
    source: str = "STUDENT_PORTAL"
    due_at: Optional[str] = None
    updated_at: Optional[str] = None
    resolved_at: Optional[str] = None
    closed_at: Optional[str] = None
    resolution_text: Optional[str] = None
    resolving_actor: Optional[str] = None
    closing_actor: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    sla_record: Optional[SLARecord] = None
    responses: List[RMSResponse] = Field(default_factory=list)
    assignments: List[Assignment] = Field(default_factory=list)
    escalations: List[Escalation] = Field(default_factory=list)
    history: List[Union[AuditEvent, Dict[str, Any]]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_synthetic: bool = True

    # AI & Review extensions
    ai_analysis: Optional[AIAnalysis] = None
    confidence: float = 0.85
    redacted_description: Optional[str] = None
    requires_human_review: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def sync_subject_and_title(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Sync title and subject
            if "subject" in data and "title" not in data:
                data["title"] = data["subject"]
            elif "title" in data and "subject" not in data:
                data["subject"] = data["title"]
            # Sync assigned_staff and assigned_staff_id
            if "assigned_staff" in data and not data.get("assigned_staff_id"):
                data["assigned_staff_id"] = data["assigned_staff"]
            elif "assigned_staff_id" in data and not data.get("assigned_staff"):
                data["assigned_staff"] = data["assigned_staff_id"]
        return data


class TicketListResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int
    count: int
    tickets: List[Ticket]


class DraftResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    draft_response: str
    sources: List[RAGSource] = Field(default_factory=list)
    confidence: float
    requires_staff_edit: bool = False
    policy_compliance_passed: bool = True
    disclaimer: str = "AI assists. Humans decide. Please review and verify before approving."


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    override_text: Optional[str] = None


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    ai_analysis: AIAnalysis
    redacted_description: str
    sources: List[RAGSource] = Field(default_factory=list)
    nlp_result: Optional[Dict[str, Any]] = None


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    staff_id: str
    approved_text: str
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    status: str
    approved_by: str
    resolved_at: str
    message: str


class EscalateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    staff_id: str
    target_role: str = "DEPARTMENT_HOD"
    reason: str
    urgent: bool = False


class EscalateResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    status: str
    escalated_to: str
    message: str


class RedirectRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    staff_id: str
    new_department: str
    reason: str


class RedirectResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    previous_department: str
    new_department: str
    status: str
    message: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    service: str = "Smart RMS API"
    version: str = "1.0.0"
    environment: str
    ai_provider: str
    vector_store: str
    mock_mode: bool
    timestamp: str


class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total_tickets: int
    open_tickets: int
    approved_today: int
    escalated_tickets: int
    avg_resolution_time_hours: float
    ai_acceptance_rate: float
    department_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]


class KnowledgeDocResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str
    title: str
    department: str
    clause: str
    content: str
    effective_date: str
    keywords: List[str]
