"""
Smart RMS - Claim Grounding and NLI Verification Schemas
Milestone 6: Automated Verification Layer for AI-Generated RMS Drafts
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ClaimCategory(str, Enum):
    POLICY_RULE = "POLICY_RULE"
    DEADLINE = "DEADLINE"
    ELIGIBILITY = "ELIGIBILITY"
    PROCESS = "PROCESS"
    FEE = "FEE"
    CONTACT = "CONTACT"
    DOCUMENT_REQUIREMENT = "DOCUMENT_REQUIREMENT"
    EXCEPTION = "EXCEPTION"
    GENERAL_INFORMATION = "GENERAL_INFORMATION"


class EntailmentLabel(str, Enum):
    ENTAILMENT = "ENTAILMENT"
    CONTRADICTION = "CONTRADICTION"
    NEUTRAL = "NEUTRAL"


class ClaimVerificationStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNVERIFIED = "UNVERIFIED"


class DraftGroundingStatus(str, Enum):
    FULLY_GROUNDED = "FULLY_GROUNDED"
    PARTIALLY_GROUNDED = "PARTIALLY_GROUNDED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class ExtractedClaim(BaseModel):
    model_config = ConfigDict(extra="ignore")

    claim_id: str
    text: str
    category: ClaimCategory
    source_sentence: str
    confidence: float = 1.0
    is_high_impact: bool = False
    # False for operational/communication statements (acknowledgements, routing notes).
    # These are shown to staff as UNVERIFIED but are not policy assertions.
    is_policy_claim: bool = True
    entities_detected: Dict[str, Any] = Field(default_factory=dict)


class EvidenceMatch(BaseModel):
    model_config = ConfigDict(extra="ignore")

    document_id: str
    title: str
    clause: str
    excerpt: str
    relevance_score: float
    # Deterministic matcher: fraction of claim content tokens found in the best evidence sentence.
    lexical_similarity: float = 0.0
    # Embedding similarity. None = not computed (deterministic matcher does not compute it).
    semantic_similarity: Optional[float] = None
    matched_sentence: Optional[str] = None


class ClaimVerificationResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    claim: ExtractedClaim
    status: ClaimVerificationStatus
    entailment_label: EntailmentLabel
    entailment_score: float
    matched_evidence: Optional[EvidenceMatch] = None
    verification_reason: str
    is_high_impact: bool = False


class DraftGroundingVerification(BaseModel):
    model_config = ConfigDict(extra="ignore")

    overall_status: DraftGroundingStatus
    grounding_score: float = 0.0
    total_claims: int = 0
    supported_claims_count: int = 0
    contradicted_claims_count: int = 0
    unsupported_claims_count: int = 0
    high_impact_violations_count: int = 0
    operational_statements_count: int = 0
    claim_verifications: List[ClaimVerificationResult] = Field(default_factory=list)
    is_blocked: bool = False
    block_reason: Optional[str] = None
    verifier_provider: str = "deterministic"
    latency_ms: float = 0.0
    stage_latency_ms: Dict[str, float] = Field(default_factory=dict)


class GroundingOverrideRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    staff_id: str
    reason: str = Field(..., min_length=5, description="Staff operational rationale for overriding grounding status")
    notes: Optional[str] = None
    action_taken: str = "ACCEPT_DRAFT"  # "ACCEPT_DRAFT", "REJECT_DRAFT", "MODIFY_CLAIMS"


class GroundingOverrideResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ticket_id: str
    previous_grounding_status: str
    updated_grounding_status: str
    overridden_by: str
    timestamp: str
    audit_event_id: str
    message: str
