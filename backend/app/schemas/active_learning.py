from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import uuid

class FeedbackType(str, Enum):
    INTENT_CORRECTION = "INTENT_CORRECTION"
    DEPARTMENT_CORRECTION = "DEPARTMENT_CORRECTION"
    PRIORITY_CORRECTION = "PRIORITY_CORRECTION"
    URGENCY_CORRECTION = "URGENCY_CORRECTION"
    ENTITY_CORRECTION = "ENTITY_CORRECTION"
    GROUNDING_CORRECTION = "GROUNDING_CORRECTION"
    DRAFT_REJECTION = "DRAFT_REJECTION"
    DRAFT_EDIT = "DRAFT_EDIT"
    DRAFT_APPROVAL = "DRAFT_APPROVAL"
    REGENERATION = "REGENERATION"
    ESCALATION = "ESCALATION"
    REDIRECT = "REDIRECT"

class FeedbackQualityState(str, Enum):
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    USED_FOR_TRAINING = "USED_FOR_TRAINING"

class FeedbackEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    feedback_id: str = Field(default_factory=lambda: f"FB-{uuid.uuid4().hex[:8].upper()}")
    ticket_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    feedback_type: FeedbackType
    
    # Non-destructive storage
    original_prediction: Optional[str] = None
    corrected_value: Optional[str] = None
    
    # Model provenance
    model_provider: Optional[str] = None
    model_version: Optional[str] = None
    confidence: Optional[float] = None
    
    # Grounding context
    grounding_status: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    
    # Audit & Action
    human_action: str
    reason: Optional[str] = None
    actor_id: str = "SYSTEM"
    synthetic_context_id: Optional[str] = None

    # Quality state
    status: FeedbackQualityState = FeedbackQualityState.CANDIDATE
    
    # Active learning prioritization score
    al_priority_score: float = 0.0
    
    # Disagreement logging
    model_disagreement: Optional[dict] = None
