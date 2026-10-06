"""
Smart RMS - Grounding Decision Engine (Milestone 6)

Turns claim-level verification results into a draft-level grounding verdict and
enforces the strict safety policy. Only POLICY claims determine grounding;
operational statements (acknowledgements / routing notes) are reported as
UNVERIFIED and never count as support.

Decision order (first match wins):
  1. No policy claims                        -> UNSUPPORTED            (blocked)
  2. Any policy claim CONTRADICTED            -> CONTRADICTED           (blocked)
  3. Any HIGH-IMPACT policy claim unsupported -> REQUIRES_HUMAN_REVIEW  (blocked)
  4. All policy claims SUPPORTED              -> FULLY_GROUNDED         (still needs staff approval)
  5. Some policy claims SUPPORTED             -> PARTIALLY_GROUNDED     (staff review)
  6. No policy claim SUPPORTED                -> UNSUPPORTED            (blocked)

Grounding score (interpretable heuristic, NOT a calibrated probability):
  0                                                         if any contradiction
  supported_ratio × mean_evidence_relevance × mean_support_strength   otherwise
where the means are taken over SUPPORTED policy claims, relevance is the RAG
relevance of the source chunk and strength is the verifier's entailment_score
(lexical containment for the deterministic verifier, softmax p for NLI).
"""

from typing import List
from app.schemas.grounding import (
    ClaimVerificationResult, ClaimVerificationStatus, DraftGroundingStatus, DraftGroundingVerification,
)


class GroundingDecisionEngine:

    def evaluate(self, claim_verifications: List[ClaimVerificationResult],
                 verifier_provider: str = "deterministic", latency_ms: float = 0.0) -> DraftGroundingVerification:
        policy = [cv for cv in claim_verifications if cv.claim.is_policy_claim]
        operational = len(claim_verifications) - len(policy)

        supported = [cv for cv in policy if cv.status == ClaimVerificationStatus.SUPPORTED]
        contradicted = [cv for cv in policy if cv.status == ClaimVerificationStatus.CONTRADICTED]
        unsupported = [cv for cv in policy if cv.status in (ClaimVerificationStatus.INSUFFICIENT_EVIDENCE,
                                                            ClaimVerificationStatus.UNVERIFIED)]
        hi_unsupported = [cv for cv in unsupported if cv.is_high_impact]
        hi_violations = len(hi_unsupported) + sum(1 for cv in contradicted if cv.is_high_impact)

        if contradicted or not policy:
            score = 0.0
        else:
            ratio = len(supported) / len(policy)
            if supported:
                rel = sum(cv.matched_evidence.relevance_score for cv in supported if cv.matched_evidence) / len(supported)
                strength = sum(cv.entailment_score for cv in supported) / len(supported)
            else:
                rel = strength = 0.0
            score = round(ratio * min(rel, 1.0) * min(strength, 1.0), 4)

        if not policy:
            status, blocked = DraftGroundingStatus.UNSUPPORTED, True
            reason = "Draft contains no verifiable policy claims."
        elif contradicted:
            status, blocked = DraftGroundingStatus.CONTRADICTED, True
            reason = (f"Grounding verification identified {len(contradicted)} claim(s) that conflict with "
                      f"authoritative policy: " + " | ".join(cv.verification_reason for cv in contradicted[:2]))
        elif hi_unsupported:
            status, blocked = DraftGroundingStatus.REQUIRES_HUMAN_REVIEW, True
            reason = (f"Grounding verification identified {len(hi_unsupported)} high-impact claim(s) not "
                      f"established by retrieved policy evidence. Automated policy response blocked.")
        elif len(supported) == len(policy):
            status, blocked, reason = DraftGroundingStatus.FULLY_GROUNDED, False, None
        elif supported:
            status, blocked = DraftGroundingStatus.PARTIALLY_GROUNDED, False
            reason = f"{len(unsupported)} low-impact claim(s) lack policy support. Staff review required."
        else:
            status, blocked = DraftGroundingStatus.UNSUPPORTED, True
            reason = "No policy claim in the draft is supported by retrieved evidence."

        return DraftGroundingVerification(
            overall_status=status,
            grounding_score=score,
            total_claims=len(claim_verifications),
            supported_claims_count=len(supported),
            contradicted_claims_count=len(contradicted),
            unsupported_claims_count=len(unsupported),
            high_impact_violations_count=hi_violations,
            operational_statements_count=operational,
            claim_verifications=claim_verifications,
            is_blocked=blocked,
            block_reason=reason,
            verifier_provider=verifier_provider,
            latency_ms=latency_ms,
        )
