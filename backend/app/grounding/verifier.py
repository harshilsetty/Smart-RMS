"""
Smart RMS - Claim Verification Architecture (Milestone 6)

    BaseClaimVerifier            (abstract interface - model-agnostic)
        ├── DeterministicClaimVerifier   (explainable rules; default + guaranteed fallback)
        └── NLIClaimVerifier             (local cross-encoder NLI; hybrid with deterministic rules)

Premise    = authoritative policy evidence (best-matching evidence sentence)
Hypothesis = extracted draft claim

Scores
------
* Deterministic SUPPORTED     -> entailment_score = lexical containment of the matched sentence.
* Deterministic CONTRADICTED  -> entailment_score = 1.0 meaning "a contradiction rule fired".
* Deterministic NEUTRAL       -> entailment_score = lexical containment.
* NLI                          -> softmax probability of the predicted label (uncalibrated).
None of these scores are calibrated probabilities.
"""

import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from app.schemas.grounding import (
    ExtractedClaim, EvidenceMatch, ClaimVerificationResult,
    ClaimVerificationStatus, EntailmentLabel,
)
from app.grounding.text_utils import (
    containment, extract_durations_hours, extract_currency, extract_percentages,
    extract_numbers, has_negation,
)

logger = logging.getLogger(__name__)

# Containment needed for SUPPORTED. High-impact claims get a stricter threshold (Part 8).
SUPPORT_THRESHOLD = 0.60
HIGH_IMPACT_SUPPORT_THRESHOLD = 0.75
# Minimum topical overlap before polarity / generic-number contradiction rules may fire.
CONTRADICTION_OVERLAP = 0.50

RESTRICTIVE_TERMS = ("only", "exclusively", "restricted to", "reserved", "and above",
                     "or above", "minimum", "at least", "solely", "subject to")

POLARITY_PAIRS = (
    # (evidence phrase, claim phrase) - claim asserts the opposite of evidence
    ("non-refundable", "refund"),
    ("not refundable", "refund"),
    ("no refund", "refund"),
    ("no grace marks", "grace marks"),
    ("no physical", "hard copy"),
    ("strictly barred", "can freely"),
    ("barred", "can freely"),
    ("without exception", "remain open"),
    ("prohibited", "can swap"),
    ("in person", "whatsapp"),
    ("original", "photocop"),
    ("mandatory", "optional"),
    ("compulsory", "optional"),
)


class BaseClaimVerifier(ABC):
    """Model-agnostic interface. Any future verifier (other NLI models, LLM judges) plugs in here."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    def verify_claim(self, claim: ExtractedClaim, evidence: Optional[EvidenceMatch]) -> ClaimVerificationResult:
        ...

    def verify_claims(self, claims: List[ExtractedClaim],
                      evidence_matches: List[Optional[EvidenceMatch]]) -> List[ClaimVerificationResult]:
        return [self.verify_claim(c, e) for c, e in zip(claims, evidence_matches)]


def _result(claim, status, label, score, evidence, reason) -> ClaimVerificationResult:
    return ClaimVerificationResult(
        claim=claim, status=status, entailment_label=label,
        entailment_score=round(float(score), 4), matched_evidence=evidence,
        verification_reason=reason, is_high_impact=claim.is_high_impact,
    )


class DeterministicClaimVerifier(BaseClaimVerifier):
    """Explainable rule engine: numeric constraints, scope, polarity, lexical containment."""

    @property
    def provider_name(self) -> str:
        return "deterministic"

    def verify_claim(self, claim: ExtractedClaim, evidence: Optional[EvidenceMatch]) -> ClaimVerificationResult:
        if not claim.is_policy_claim:
            return _result(claim, ClaimVerificationStatus.UNVERIFIED, EntailmentLabel.NEUTRAL, 0.0, evidence,
                           "Operational/communication statement (acknowledgement or routing). "
                           "Not a policy assertion; not verified against policy.")

        if not evidence or not (evidence.excerpt or "").strip():
            return _result(claim, ClaimVerificationStatus.INSUFFICIENT_EVIDENCE, EntailmentLabel.NEUTRAL, 0.0, None,
                           "No retrieved policy evidence addresses this claim.")

        premise = evidence.matched_sentence or evidence.excerpt
        reason = self.detect_contradiction(claim, premise, evidence.excerpt, evidence.lexical_similarity)
        if reason:
            return _result(claim, ClaimVerificationStatus.CONTRADICTED, EntailmentLabel.CONTRADICTION, 1.0,
                           evidence, reason)

        ok, reason = self.detect_support(claim, premise, evidence.lexical_similarity)
        if ok:
            return _result(claim, ClaimVerificationStatus.SUPPORTED, EntailmentLabel.ENTAILMENT,
                           evidence.lexical_similarity, evidence,
                           f"{reason} Source: {evidence.title} → {evidence.clause}.")

        return _result(claim, ClaimVerificationStatus.INSUFFICIENT_EVIDENCE, EntailmentLabel.NEUTRAL,
                       evidence.lexical_similarity, evidence, reason)

    # ------------------------------------------------------------------ rules

    def detect_contradiction(self, claim: ExtractedClaim, premise: str, full_excerpt: str,
                             overlap: float) -> Optional[str]:
        c_txt, p_low = claim.text, premise.lower()
        c_low = c_txt.lower()
        ents = claim.entities_detected or {}

        def _mismatch(claim_vals, prem_vals, full_vals) -> bool:
            # Contradiction only if the premise states a value of the same type, the claim's
            # value is absent from the premise AND absent from the whole retrieved chunk.
            return bool(prem_vals) and not (set(claim_vals) & prem_vals) and not (set(claim_vals) & full_vals)

        if "duration_hours" in ents:
            pv, fv = extract_durations_hours(premise), extract_durations_hours(full_excerpt)
            if _mismatch(ents["duration_hours"], pv, fv):
                return (f"Deadline conflict: claim states {self._fmt_hours(ents['duration_hours'])}, "
                        f"policy states {self._fmt_hours(sorted(pv))}.")
        if "amount" in ents:
            pv, fv = extract_currency(premise), extract_currency(full_excerpt)
            if _mismatch(ents["amount"], pv, fv):
                return (f"Fee conflict: claim states ₹{', ₹'.join(f'{a:,.0f}' for a in ents['amount'])}, "
                        f"policy states ₹{', ₹'.join(f'{a:,.0f}' for a in sorted(pv))}.")
        if "percent" in ents:
            pv, fv = extract_percentages(premise), extract_percentages(full_excerpt)
            if _mismatch(ents["percent"], pv, fv):
                return (f"Threshold conflict: claim states {ents['percent']}%, "
                        f"policy states {sorted(pv)}%.")
        if "semester" in ents:
            m = re.search(r"semester\s*(\d+)", p_low)
            if m and int(m.group(1)) != ents["semester"]:
                return f"Eligibility conflict: claim states semester {ents['semester']}, policy states semester {m.group(1)}."
        if "cgpa" in ents:
            m = re.search(r"cgpa\s*(?:\([a-z]+\)\s*)?(?:of|above|>=|>|at least)?\s*(\d+(?:\.\d+)?)", p_low)
            if m and float(m.group(1)) != ents["cgpa"]:
                return f"Eligibility conflict: claim states CGPA {ents['cgpa']}, policy states CGPA {m.group(1)}."

        if ents.get("scope") == "UNIVERSAL" and any(t in p_low for t in RESTRICTIVE_TERMS):
            return "Scope conflict: claim asserts universal eligibility, but policy restricts eligibility."

        for ev_p, cl_p in POLARITY_PAIRS:
            if ev_p in p_low and cl_p in c_low and ev_p not in c_low:
                return f"Polarity conflict: policy states '{ev_p}', claim asserts '{cl_p}'."

        if overlap >= CONTRADICTION_OVERLAP:
            if has_negation(c_txt) != has_negation(premise):
                return "Polarity conflict: claim and policy evidence differ in negation on the same subject."
            c_nums, p_nums = extract_numbers(c_txt), extract_numbers(premise)
            if c_nums and p_nums and not (c_nums <= extract_numbers(full_excerpt)):
                return (f"Numeric conflict: claim states {sorted(c_nums - p_nums)}, "
                        f"policy sentence states {sorted(p_nums)}.")
        return None

    def detect_support(self, claim: ExtractedClaim, premise: str, overlap: float) -> Tuple[bool, str]:
        ents = claim.entities_detected or {}
        # Every numeric fact in the claim must be present in the premise sentence.
        if "duration_hours" in ents and not set(ents["duration_hours"]) <= extract_durations_hours(premise):
            return False, "Deadline in claim is not stated in the matched policy sentence."
        if "amount" in ents and not set(ents["amount"]) <= extract_currency(premise):
            return False, "Amount in claim is not stated in the matched policy sentence."
        if "percent" in ents and not set(ents["percent"]) <= extract_percentages(premise):
            return False, "Percentage in claim is not stated in the matched policy sentence."
        if ents.get("scope") == "UNIVERSAL" and not any(
                t in premise.lower() for t in ("all students", "any student", "every student", "regardless")):
            return False, "Universal-scope claim is not established by the policy sentence."

        if ents.get("subclaim_type"):
            # Atomic deadline/amount sub-claim: value verified above against the base sentence's evidence.
            if overlap >= SUPPORT_THRESHOLD:
                return True, "Numeric value verified verbatim in the matched policy sentence."
            return False, "Base sentence for this numeric sub-claim is not adequately matched to policy."

        threshold = HIGH_IMPACT_SUPPORT_THRESHOLD if claim.is_high_impact else SUPPORT_THRESHOLD
        if overlap >= threshold:
            return True, f"Claim content is stated in the policy sentence (containment {overlap:.2f} ≥ {threshold})."
        return False, (f"Policy evidence does not establish this claim "
                       f"(containment {overlap:.2f} < {threshold}{' high-impact' if claim.is_high_impact else ''}).")

    @staticmethod
    def _fmt_hours(vals) -> str:
        out = []
        for h in vals:
            out.append(f"{h/24:g} days" if h >= 24 and h % 24 == 0 else f"{h:g} hours")
        return " / ".join(out)


class NLIClaimVerifier(BaseClaimVerifier):
    """
    Local cross-encoder NLI verifier (default: cross-encoder/nli-deberta-v3-xsmall).

    * Loads ONLY from local files (local_files_only=True) - never downloads at app startup.
      Use scripts/download_nli_model.py to fetch weights explicitly.
    * If loading fails, every call is delegated to DeterministicClaimVerifier and
      provider_name reports 'deterministic_fallback' - the system never claims NLI is active when it is not.
    * Hybrid safety: deterministic contradiction rules run first and override the model;
      the model may only upgrade a claim to SUPPORTED if deterministic numeric checks also pass.
    """

    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-xsmall",
                 entail_threshold: float = 0.70, contra_threshold: float = 0.60):
        self.model_name = model_name
        self.entail_threshold = entail_threshold
        self.contra_threshold = contra_threshold
        self.deterministic = DeterministicClaimVerifier()
        self._model = None
        self._tokenizer = None
        self._id2label = {}
        self.is_loaded = False
        self.load_error: Optional[str] = None
        self.load_time_ms: Optional[float] = None
        self._load()

    @property
    def provider_name(self) -> str:
        return "nli" if self.is_loaded else "deterministic_fallback"

    def _load(self):
        t0 = time.perf_counter()
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=True)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name, local_files_only=True)
            self._model.eval()
            self._id2label = {int(k): str(v).upper() for k, v in self._model.config.id2label.items()}
            self.is_loaded = True
            self.load_time_ms = round((time.perf_counter() - t0) * 1000, 1)
            logger.info("NLI model loaded locally: %s", self.model_name)
        except Exception as e:  # weights absent / transformers missing / corrupt cache
            self.is_loaded = False
            self.load_error = f"{type(e).__name__}: {str(e)[:200]}"
            logger.warning("NLI model unavailable (%s). Using deterministic fallback.", self.load_error)

    def predict(self, premise: str, hypothesis: str) -> dict:
        """Raw NLI probabilities {'ENTAILMENT':p, 'NEUTRAL':p, 'CONTRADICTION':p}."""
        import torch
        inputs = self._tokenizer(premise, hypothesis, truncation=True, max_length=256, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(self._model(**inputs).logits, dim=-1)[0].tolist()
        return {self._id2label[i]: p for i, p in enumerate(probs)}

    def verify_claim(self, claim: ExtractedClaim, evidence: Optional[EvidenceMatch]) -> ClaimVerificationResult:
        det = self.deterministic.verify_claim(claim, evidence)
        if not self.is_loaded:
            return det
        if det.status in (ClaimVerificationStatus.CONTRADICTED, ClaimVerificationStatus.UNVERIFIED) \
                or evidence is None:
            return det

        premise = evidence.matched_sentence or evidence.excerpt
        try:
            probs = self.predict(premise, claim.text)
        except Exception as ex:
            logger.warning("NLI inference failed (%s); using deterministic result.", ex)
            return det

        p_c, p_e, p_n = probs.get("CONTRADICTION", 0), probs.get("ENTAILMENT", 0), probs.get("NEUTRAL", 0)
        if p_c >= self.contra_threshold:
            return _result(claim, ClaimVerificationStatus.CONTRADICTED, EntailmentLabel.CONTRADICTION, p_c,
                           evidence, f"NLI: policy evidence contradicts claim (p={p_c:.2f}).")
        # Numeric facts must still be verbatim-verifiable: NLI cannot upgrade a numeric mismatch.
        numeric_ok, _ = self.deterministic.detect_support(claim, premise, 1.0)
        if p_e >= self.entail_threshold and numeric_ok:
            return _result(claim, ClaimVerificationStatus.SUPPORTED, EntailmentLabel.ENTAILMENT, p_e,
                           evidence, f"NLI: policy evidence entails claim (p={p_e:.2f}). "
                                     f"Source: {evidence.title} → {evidence.clause}.")
        return _result(claim, ClaimVerificationStatus.INSUFFICIENT_EVIDENCE, EntailmentLabel.NEUTRAL, p_n,
                       evidence, f"NLI: evidence does not entail claim (entail p={p_e:.2f}, neutral p={p_n:.2f}).")


_instances = {}


def get_claim_verifier(provider_type: Optional[str] = None) -> BaseClaimVerifier:
    """Factory honouring CLAIM_VERIFIER_PROVIDER ('deterministic' | 'nli')."""
    from app.config import settings
    provider = (provider_type or getattr(settings, "CLAIM_VERIFIER_PROVIDER", "deterministic")).lower()
    if provider not in _instances:
        if provider == "nli":
            _instances[provider] = NLIClaimVerifier(getattr(settings, "NLI_MODEL_NAME",
                                                            "cross-encoder/nli-deberta-v3-xsmall"))
        else:
            _instances[provider] = DeterministicClaimVerifier()
    return _instances[provider]
