from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IntentType(str, Enum):
    HOSTEL_MAINTENANCE = "HOSTEL_MAINTENANCE"
    FEE_PAYMENT = "FEE_PAYMENT"
    EXAMINATION = "EXAMINATION"
    ATTENDANCE = "ATTENDANCE"
    SCHOLARSHIP = "SCHOLARSHIP"
    IT_SUPPORT = "IT_SUPPORT"
    ACADEMIC = "ACADEMIC"
    STUDENT_SERVICES = "STUDENT_SERVICES"
    GENERAL_INQUIRY = "GENERAL_INQUIRY"
    UNKNOWN = "UNKNOWN"
    OTHER = "OTHER"

class DepartmentType(str, Enum):
    HOSTEL_AFFAIRS = "Hostel Affairs"
    ACCOUNTS_FINANCE = "Accounts & Finance"
    ACADEMIC_AFFAIRS = "Academic Affairs"
    EXAMINATION_BRANCH = "Examination Branch"
    STUDENT_WELFARE = "Student Welfare"
    SCHOLARSHIP_SECTION = "Scholarship Section"
    IT_SERVICES = "IT Services"
    GENERAL_ADMIN = "General Administration"

class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class UrgencyLevel(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    URGENT = "URGENT"
    IMMEDIATE = "IMMEDIATE"

class StructuredEntity(BaseModel):
    entity_type: str
    value: str
    confidence: float = 1.0
    source_span: Optional[str] = None

class ExtractedEntity(BaseModel):
    entity_type: str
    value: str
    confidence: float = 1.0

class SemanticMatch(BaseModel):
    document_id: str
    title: str
    similarity_score: float
    excerpt: str

class IntentClassificationResult(BaseModel):
    intent: str
    confidence: float
    secondary_intent: Optional[str] = None
    margin: float = 0.0
    matched_keywords: List[str] = Field(default_factory=list)
    reason: Optional[str] = None
    is_ambiguous: bool = False

class DepartmentRoutingResult(BaseModel):
    department: str
    confidence: float
    reason: str
    secondary_department: Optional[str] = None

class UrgencyClassificationResult(BaseModel):
    priority: PriorityLevel
    confidence: float
    priority_score: int
    signals_detected: List[str] = Field(default_factory=list)
    reason: str
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    urgency_confidence: float = 0.85
    temporal_expressions: List[str] = Field(default_factory=list)

class NLPResult(BaseModel):
    intent: str
    intent_confidence: float
    department: str
    department_confidence: float
    priority: str
    priority_confidence: float
    priority_score: int
    urgency: str = "NORMAL"
    urgency_confidence: float = 0.85
    entities: Dict[str, Any] = Field(default_factory=dict)
    structured_entities: List[StructuredEntity] = Field(default_factory=list)
    summary: str
    suggested_action: str
    semantic_matches: List[SemanticMatch] = Field(default_factory=list)
    requires_human_review: bool
    review_reasons: List[str] = Field(default_factory=list)
    needs_clarification: bool = False
    clarification_reason: Optional[str] = None
    confidence_level: ConfidenceLevel
    overall_confidence: float = 0.85
    explanation: Dict[str, str] = Field(default_factory=dict)
    classifier_mode: str = "deterministic_baseline"
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
