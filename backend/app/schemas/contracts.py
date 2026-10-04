"""
Smart RMS Canonical Data Contracts
Defines typed domain models and source-of-truth contracts for the university environment.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Canonical Enums
# ============================================================================

class TicketStatus(str, Enum):
    """Canonical lifecycle status for RMS requests."""
    NEW = "NEW"
    INGESTED = "INGESTED"
    ANALYZED = "ANALYZED"
    ROUTED = "ROUTED"
    STAFF_REVIEW = "STAFF_REVIEW"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_STUDENT = "WAITING_FOR_STUDENT"
    WAITING_FOR_DEPARTMENT = "WAITING_FOR_DEPARTMENT"
    ESCALATED = "ESCALATED"
    APPROVED = "APPROVED"       # Staff approved resolution draft
    RESOLVED = "RESOLVED"       # Final resolution dispatched to student
    CLOSED = "CLOSED"           # Ticket closed after verification or student confirmation
    DRAFTED = "DRAFTED"         # Intermediate status for draft generation


class PriorityLevel(str, Enum):
    """Canonical priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_str(cls, val: str) -> "PriorityLevel":
        v = val.strip().upper()
        if v in cls.__members__:
            return cls[v]
        return cls.MEDIUM


class StaffRole(str, Enum):
    """Realistic synthetic university staff roles."""
    STAFF_OPERATOR = "STAFF_OPERATOR"
    DEPARTMENT_STAFF = "DEPARTMENT_STAFF"
    HOD = "HOD"
    DEPARTMENT_HOD = "DEPARTMENT_HOD"
    ADMIN = "ADMIN"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class SLAStatus(str, Enum):
    """SLA tracking status."""
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    BREACHED = "BREACHED"


class AuditEventType(str, Enum):
    """Audit event classifications."""
    CREATED = "CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    ASSIGNED = "ASSIGNED"
    REDIRECTED = "REDIRECTED"
    ESCALATED = "ESCALATED"
    DRAFT_GENERATED = "DRAFT_GENERATED"
    APPROVED = "APPROVED"
    RESPONSE_ADDED = "RESPONSE_ADDED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


# ============================================================================
# Domain Models
# ============================================================================

class StudentReference(BaseModel):
    """Synthetic student identity reference."""
    model_config = ConfigDict(extra="ignore")

    student_id: str = Field(..., description="Synthetic student identifier (e.g. STU-SYN-8492)")
    registration_number: Optional[str] = Field(None, description="Synthetic university registration number")
    name: Optional[str] = Field(None, description="Synthetic display name")
    program: Optional[str] = Field("B.Tech Computer Science & Engineering", description="Academic degree program")
    semester: Optional[int] = Field(5, description="Current enrolled term/semester")
    section: Optional[str] = Field(None, description="Class section")
    hostel_block: Optional[str] = Field(None, description="Hostel building if residential")
    room_number: Optional[str] = Field(None, description="Hostel room number")
    email: Optional[str] = Field(None, description="Synthetic university email")
    phone: Optional[str] = Field(None, description="Synthetic contact number")
    is_synthetic: bool = Field(True, description="Strict synthetic data flag")


class DepartmentSLAPolicy(BaseModel):
    """SLA configuration per priority level in hours."""
    model_config = ConfigDict(extra="ignore")

    LOW: int = Field(72, description="SLA hours for Low priority")
    MEDIUM: int = Field(48, description="SLA hours for Medium priority")
    HIGH: int = Field(24, description="SLA hours for High priority")
    CRITICAL: int = Field(12, description="SLA hours for Critical priority")

    def get_hours_for_priority(self, priority: Union[str, PriorityLevel]) -> int:
        p_str = priority.value if isinstance(priority, PriorityLevel) else str(priority).upper()
        if p_str in ["CRITICAL"]:
            return self.CRITICAL
        elif p_str in ["HIGH"]:
            return self.HIGH
        elif p_str in ["MEDIUM"]:
            return self.MEDIUM
        return self.LOW


class DepartmentEscalationPolicy(BaseModel):
    """Department escalation routing policy."""
    model_config = ConfigDict(extra="ignore")

    target_role: StaffRole = Field(StaffRole.HOD, description="Role to escalate unhandled tickets to")
    escalation_window_hours: int = Field(24, description="Hours before automatic escalation trigger")
    notification_channel: str = Field("email", description="Notification dispatch channel")


class Department(BaseModel):
    """University administrative department entity."""
    model_config = ConfigDict(extra="ignore")

    department_id: str = Field(..., description="Synthetic department identifier (e.g. DEPT-HOSTEL)")
    department_code: str = Field(..., description="Short departmental acronym (e.g. HA, AF)")
    name: str = Field(..., description="Official departmental title")
    description: str = Field(..., description="Scope of operations and handled matters")
    categories: List[str] = Field(default_factory=list, description="Taxonomy categories handled by department")
    sla_policy: DepartmentSLAPolicy = Field(default_factory=DepartmentSLAPolicy)
    escalation_policy: DepartmentEscalationPolicy = Field(default_factory=DepartmentEscalationPolicy)
    staff_ids: List[str] = Field(default_factory=list, description="IDs of staff members assigned to department")
    hod_reference: Optional[Dict[str, Any]] = Field(None, description="HOD contact information")
    active_status: bool = Field(True, description="Whether department is actively accepting RMS requests")


class WorkloadMetadata(BaseModel):
    """Staff operator workload tracking."""
    model_config = ConfigDict(extra="ignore")

    assigned_tickets_count: int = Field(0, description="Total active tickets currently assigned")
    open_tickets_count: int = Field(0, description="Tickets pending staff review or action")
    max_capacity: int = Field(20, description="Maximum concurrent ticket threshold")
    specialty_categories: List[str] = Field(default_factory=list, description="Domain specialty areas")


class StaffUser(BaseModel):
    """Synthetic university staff user."""
    model_config = ConfigDict(extra="ignore")

    user_id: str = Field(..., description="Synthetic staff ID (e.g. USR-STAFF-01)")
    display_name: str = Field(..., description="Full name and title")
    email: str = Field(..., description="Synthetic university email")
    role: StaffRole = Field(StaffRole.STAFF_OPERATOR, description="Operational role")
    department_id: str = Field(..., description="Department assigned to")
    department_name: Optional[str] = Field(None, description="Department name for display")
    permissions: List[str] = Field(default_factory=list, description="Granted operation permissions")
    active_status: bool = Field(True, description="Whether staff member is active")
    workload_metadata: WorkloadMetadata = Field(default_factory=WorkloadMetadata)
    avatar_url: Optional[str] = Field(None, description="Profile avatar URL")


class AttachmentMetadata(BaseModel):
    """File attachment metadata associated with RMS requests."""
    model_config = ConfigDict(extra="ignore")

    attachment_id: str = Field(..., description="Unique attachment ID")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(0, description="File size in bytes")
    content_type: str = Field("application/octet-stream", description="MIME content type")
    url: Optional[str] = Field(None, description="Storage or retrieval URL")
    uploaded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SLARecord(BaseModel):
    """Tracks Service Level Agreement timeline and status."""
    model_config = ConfigDict(extra="ignore")

    priority: str = Field("Medium", description="Ticket priority at SLA establishment")
    sla_hours: int = Field(48, description="Allowed resolution duration in hours")
    due_at: str = Field(..., description="ISO UTC timestamp when SLA expires")
    is_breached: bool = Field(False, description="Whether deadline has passed without resolution")
    remaining_hours: float = Field(48.0, description="Hours remaining until breach (negative if breached)")
    status: SLAStatus = Field(SLAStatus.ON_TRACK, description="SLA tracking state")


class AuditEvent(BaseModel):
    """Immutable audit trail record for compliance and history."""
    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(..., description="Unique audit event ID")
    ticket_id: str = Field(..., description="Associated RMS ticket ID")
    event_type: AuditEventType = Field(AuditEventType.STATUS_CHANGED, description="Event classification")
    actor_id: str = Field("SYSTEM", description="User ID or SYSTEM")
    actor_role: Optional[str] = Field(None, description="Role of the actor executing the action")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    from_state: Optional[str] = Field(None, description="State before transition")
    to_state: Optional[str] = Field(None, description="State after transition")
    notes: Optional[str] = Field(None, description="Staff notes, reason, or details")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context payload")


class RMSResponse(BaseModel):
    """Message or official response on an RMS ticket."""
    model_config = ConfigDict(extra="ignore")

    response_id: str = Field(..., description="Unique response ID")
    ticket_id: str = Field(..., description="Target RMS ticket ID")
    author_id: str = Field(..., description="Author user ID or STU-ID")
    author_name: str = Field("University Staff", description="Display name of author")
    author_role: str = Field("STAFF_OPERATOR", description="Role: STAFF_OPERATOR, HOD, STUDENT, AI")
    content: str = Field(..., description="Response body text")
    is_internal: bool = Field(False, description="Whether visible only to staff or also to student")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Assignment(BaseModel):
    """Ticket routing and staff assignment record."""
    model_config = ConfigDict(extra="ignore")

    assignment_id: str = Field(..., description="Unique assignment ID")
    ticket_id: str = Field(..., description="Target ticket ID")
    department_id: str = Field(..., description="Target department ID")
    staff_id: Optional[str] = Field(None, description="Assigned staff member ID")
    assigned_by: str = Field("SYSTEM", description="Actor who created assignment")
    assigned_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: Optional[str] = Field(None, description="Reason for assignment or reassignment")
    active: bool = Field(True, description="Whether this assignment is current")


class Escalation(BaseModel):
    """Departmental escalation record."""
    model_config = ConfigDict(extra="ignore")

    escalation_id: str = Field(..., description="Unique escalation ID")
    ticket_id: str = Field(..., description="Target ticket ID")
    escalated_by: str = Field(..., description="Staff member initiating escalation")
    target_role: str = Field("DEPARTMENT_HOD", description="Target escalation role")
    reason: str = Field(..., description="Justification for escalation")
    urgent: bool = Field(False, description="Emergency escalation flag")
    escalated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field("PENDING", description="Status of escalation: PENDING, ACKNOWLEDGED, RESOLVED")


class KnowledgeDocument(BaseModel):
    """Approved university policy document for RAG grounding."""
    model_config = ConfigDict(extra="ignore")

    document_id: str = Field(..., description="Document identifier (e.g. DOC-2024-HOSTEL-01)")
    title: str = Field(..., description="Document policy title")
    department: str = Field(..., description="Governing department name or code")
    clause: str = Field(..., description="Section or clause citation")
    content: str = Field(..., description="Full policy text or article content")
    effective_date: str = Field(..., description="Effective enforcement date")
    keywords: List[str] = Field(default_factory=list, description="Topic search tags")
    version: str = Field("1.0", description="Policy document version")
    is_active: bool = Field(True, description="Active enforcement status")


# ============================================================================
# Canonical RMS Request Contract
# ============================================================================

class RMSRequest(BaseModel):
    """
    Canonical RMS Request model.
    Acts as the source-of-truth data contract across the entire Smart RMS architecture.
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    ticket_id: str = Field(..., description="Unique ticket identifier (e.g. TKT-RMS-1001)")
    external_reference: Optional[str] = Field(None, description="University UMS reference ID")
    student_reference: str = Field(..., description="Student synthetic ID or reference code")
    student_details: Optional[StudentReference] = Field(None, description="Detailed student reference if available")
    
    # Title / Subject interoperability
    title: str = Field(..., alias="subject", description="Concise summary title of grievance")
    description: str = Field(..., description="Full text description submitted by student")
    redacted_description: Optional[str] = Field(None, description="PII-sanitized text description")
    
    category: str = Field(..., description="High-level category (e.g. Hostel, Finance, Academic)")
    subcategory: Optional[str] = Field(None, description="Granular issue classification")
    department: str = Field(..., description="Target or routed department name")
    assigned_department_id: Optional[str] = Field(None, description="Target department identifier (e.g. DEPT-HOSTEL)")
    assigned_staff_id: Optional[str] = Field(None, alias="assigned_staff", description="Assigned staff member ID")
    
    priority: str = Field("Medium", description="Priority level (Low, Medium, High, Critical)")
    status: str = Field("INGESTED", description="Workflow lifecycle state")
    escalation_level: int = Field(0, description="Escalation counter (0 = base, 1 = HOD, 2 = Dean)")
    source: str = Field("STUDENT_PORTAL", description="Origin: STUDENT_PORTAL, UMS_GATEWAY, EMAIL, HELPDESK")
    
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last modification timestamp")
    due_at: Optional[str] = Field(None, description="SLA deadline timestamp")
    resolved_at: Optional[str] = Field(None, description="Resolution timestamp")
    resolution_text: Optional[str] = Field(None, description="Final approved resolution narrative")
    
    sla_record: Optional[SLARecord] = Field(None, description="Computed SLA metrics and status")
    tags: List[str] = Field(default_factory=list, description="Categorical tags")
    attachments: List[Union[str, AttachmentMetadata]] = Field(default_factory=list, description="Attachment items")
    responses: List[RMSResponse] = Field(default_factory=list, description="Audit of staff and student communications")
    history: List[AuditEvent] = Field(default_factory=list, description="Chronological audit history")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata payload")
    
    # AI and evaluation metadata
    ai_analysis: Optional[Dict[str, Any]] = Field(None, description="Computed AI classification and analysis")
    confidence: float = Field(0.85, description="Composite model confidence score")
    requires_human_review: Optional[bool] = Field(None, description="Flag if review is demanded by guardrails")
    is_synthetic: bool = Field(True, description="Strict synthetic data flag")

    @property
    def subject(self) -> str:
        """Compatibility accessor for code expecting 'subject'."""
        return self.title


# ============================================================================
# API Request / Response Payloads for New Capabilities
# ============================================================================

class RMSCreateRequest(BaseModel):
    """Payload to create or ingest a new synthetic RMS ticket."""
    student_reference: str = Field(..., description="Student ID (e.g. STU-SYN-8492)")
    subject: str = Field(..., description="Brief grievance subject")
    description: str = Field(..., description="Grievance description")
    category: str = Field("General", description="Category")
    department: str = Field("Academic Affairs", description="Department name")
    priority: str = Field("Medium", description="Low, Medium, High, Critical")
    subcategory: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)
    source: str = Field("STUDENT_PORTAL")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssignmentRequest(BaseModel):
    """Payload to assign a ticket to department or staff."""
    department_id: Optional[str] = None
    staff_id: Optional[str] = None
    assigned_by: str = Field("STAFF_OPERATOR")
    reason: Optional[str] = None


class RMSResponseCreateRequest(BaseModel):
    """Payload to add a response to an RMS ticket."""
    author_id: str
    author_name: Optional[str] = "Staff Operator"
    author_role: str = "STAFF_OPERATOR"
    content: str
    is_internal: bool = False
