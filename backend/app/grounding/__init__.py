"""
Smart RMS - Grounding and Verification Subsystem
Milestone 6: Automated Claim Extraction, Evidence Matching, and NLI Verification
"""

import time
from typing import List, Optional, Any
from app.schemas.grounding import (
    ClaimCategory,
    EntailmentLabel,
    ClaimVerificationStatus,
    DraftGroundingStatus,
    ExtractedClaim,
    EvidenceMatch,
    ClaimVerificationResult,
    DraftGroundingVerification,
    GroundingOverrideRequest,
    GroundingOverrideResponse
)
from app.grounding.claim_extractor import ClaimExtractor
from app.grounding.evidence_matcher import EvidenceMatcher
from app.grounding.verifier import (
    BaseClaimVerifier,
    DeterministicClaimVerifier,
    NLIClaimVerifier,
    get_claim_verifier
)
from app.grounding.decision_engine import GroundingDecisionEngine


class ClaimGroundingPipeline:
    """
    End-to-end verification pipeline:
    1. Extracts atomic claims from generated draft
    2. Matches claims against authoritative retrieved policy sources
    3. Verifies entailment / contradiction using configured verifier
    4. Evaluates safety guardrails and produces draft grounding verdict
    """

    def __init__(self, verifier_provider: Optional[str] = None):
        self.extractor = ClaimExtractor()
        self.matcher = EvidenceMatcher()
        self.verifier = get_claim_verifier(verifier_provider)
        self.decision_engine = GroundingDecisionEngine()

    def verify_draft(
        self,
        draft_text: str,
        sources: List[Any]
    ) -> DraftGroundingVerification:
        t0 = time.perf_counter()

        # 1. Claim Extraction
        claims = self.extractor.extract_claims(draft_text)
        t1 = time.perf_counter()

        # 2. Claim -> Evidence Matching (restricted to evidence already retrieved for this ticket)
        matches = [self.matcher.match_claim(c, sources) for c in claims]
        t2 = time.perf_counter()

        # 3. Verification
        claim_verifications = [self.verifier.verify_claim(c, m) for c, m in zip(claims, matches)]
        t3 = time.perf_counter()

        elapsed_ms = (t3 - t0) * 1000.0

        # 4. Grounding Decision
        verdict = self.decision_engine.evaluate(
            claim_verifications=claim_verifications,
            verifier_provider=self.verifier.provider_name,
            latency_ms=round(elapsed_ms, 3)
        )
        verdict.stage_latency_ms = {
            "claim_extraction": round((t1 - t0) * 1000.0, 4),
            "evidence_matching": round((t2 - t1) * 1000.0, 4),
            "verification": round((t3 - t2) * 1000.0, 4),
        }
        return verdict


# Singleton pipeline instance
_pipeline_instance = None


def get_grounding_pipeline(verifier_provider: Optional[str] = None) -> ClaimGroundingPipeline:
    global _pipeline_instance
    if _pipeline_instance is None or verifier_provider is not None:
        _pipeline_instance = ClaimGroundingPipeline(verifier_provider)
    return _pipeline_instance
