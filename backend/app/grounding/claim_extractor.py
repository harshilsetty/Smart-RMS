"""
Smart RMS - Claim Extraction Engine
Milestone 6: Deterministic, explainable claim extraction from AI-generated draft responses.

Design:
1. Sentence segmentation (shared rules in text_utils).
2. Boilerplate removal (greetings, sign-offs, refusal notices) - not claims.
3. Operational statements (acknowledgement / routing / "keep documents ready")
   are kept but flagged is_policy_claim=False. They are displayed to staff as
   UNVERIFIED; they never count as policy support.
4. Sentences containing a numeric deadline or an explicit currency amount are
   decomposed into atomic sub-claims (base rule + deadline + fee), following the
   Milestone 6 spec example.
5. Category + high-impact tagging via keyword heuristics.
"""

import re
import uuid
from typing import List, Dict, Any

from app.schemas.grounding import ClaimCategory, ExtractedClaim
from app.grounding.text_utils import (
    split_sentences, DURATION_RE, CURRENCY_RE,
    extract_durations_hours, extract_currency, extract_percentages,
)

# Numeric deadline phrase, e.g. "within 7 calendar days", "within 7 to 10 working days"
DEADLINE_PHRASE_RE = re.compile(
    r"\b(?:within|in|after|before|up to|no later than)\s+" + DURATION_RE.pattern,
    re.IGNORECASE,
)

ELIGIBILITY_RE = re.compile(
    r"\b(eligible|eligibility|ineligible|qualify|minimum\s+(?:cgpa|attendance|marks)|"
    r"semester\s+\d+|cgpa|attendance|all students|only students|debarred|permitted to|allowed to)\b",
    re.IGNORECASE,
)
DOCUMENT_RE = re.compile(
    r"\b(documents?|certificates?|id card|hall ticket|admit card|receipts?|affidavits?|"
    r"fir|undertaking|transcripts?|marksheet|proof)\b",
    re.IGNORECASE,
)
EXCEPTION_RE = re.compile(
    r"\b(except|unless|exemption|waiver|waived|special case|medical emergency|"
    r"relaxation|concession|condonation)\b",
    re.IGNORECASE,
)
CONTACT_RE = re.compile(r"\b(contact|email|helpdesk|helpline|room\s+\d+|block\s+\d+|office)\b", re.IGNORECASE)
PROCESS_RE = re.compile(r"\b(apply|submit|upload|portal|procedure|form|register|request)\b", re.IGNORECASE)
POLICY_RE = re.compile(r"\b(policy|rule|mandatory|regulation|must|shall|required|prohibited)\b", re.IGNORECASE)
FEE_WORD_RE = re.compile(r"\b(fee|fees|fine|penalty|refund|refundable|non-refundable|charge|dues)\b", re.IGNORECASE)

HIGH_IMPACT_KEYWORDS = (
    "refund", "fee", "fine", "penalty", "cgpa", "grade", "marks", "re-evaluation",
    "attendance", "hall ticket", "admit card", "examination", "exam", "debarred",
    "disciplinary", "suspension", "rustication", "scholarship", "eligib", "deadline",
    "backlog", "aadhaar", "bank account", "personal record",
)

BOILERPLATE_PREFIXES = (
    "dear student", "hello", "hi ", "greetings", "warm regards", "best regards",
    "regards", "sincerely", "thank you", "ai assists", "please review and verify",
)
BOILERPLATE_CONTAINS = (
    "insufficient authoritative information",
    "human review required",
    "our system determined that there is insufficient",
    "has been routed to the",
)
OPERATIONAL_PATTERNS = (
    r"\bwe acknowledge your\b",
    r"\byour request has been (logged|received|registered)\b",
    r"\bassigned to the designated\b",
    r"\bplease ensure all required supporting documents are kept ready\b",
    r"\bwe anticipate resolution\b",
    r"\bstaff (officer|member) will (review|contact)\b",
)


class ClaimExtractor:
    """Extracts atomic, verifiable claims from AI-generated draft responses."""

    def extract_claims(self, draft_text: str) -> List[ExtractedClaim]:
        if not draft_text or not draft_text.strip():
            return []

        claims: List[ExtractedClaim] = []
        for sentence in split_sentences(draft_text):
            if self._is_boilerplate(sentence):
                continue

            # Strip a leading "Policy Guidance Note:" label and surrounding quotes
            clean = re.sub(r"^policy guidance note:\s*", "", sentence, flags=re.IGNORECASE)
            clean = clean.strip(" \"“”'")
            if len(clean.split()) < 3:
                continue

            operational = self._is_operational(clean)
            props = [clean] if operational else self._decompose(clean)

            for prop in props:
                entities = self._extract_entities(prop)
                if prop.startswith("The deadline is "):
                    entities["subclaim_type"] = "DEADLINE"
                elif prop.startswith("The applicable amount is "):
                    entities["subclaim_type"] = "AMOUNT"
                category = ClaimCategory.GENERAL_INFORMATION if operational else self._categorize(prop, entities)
                claims.append(ExtractedClaim(
                    claim_id=f"CLM-{uuid.uuid4().hex[:8].upper()}",
                    text=prop,
                    category=category,
                    source_sentence=sentence,
                    confidence=1.0,
                    is_high_impact=False if operational else self._is_high_impact(category, prop, entities),
                    is_policy_claim=not operational,
                    entities_detected=entities,
                ))
        return claims

    # ------------------------------------------------------------------ helpers

    def _decompose(self, sentence: str) -> List[str]:
        """
        Splits a sentence with a numeric deadline and/or explicit currency amount into
        atomic propositions. Only explicit numeric facts trigger decomposition; vague
        phrases ("prior to", "in a timely manner") never create sub-claims.
        """
        deadline = DEADLINE_PHRASE_RE.search(sentence)
        fee = CURRENCY_RE.search(sentence)
        if not deadline and not fee:
            return [sentence]

        props: List[str] = []
        base = sentence
        for m in sorted([x for x in (deadline, fee) if x], key=lambda x: x.start(), reverse=True):
            base = base[:m.start()] + " " + base[m.end():]
        base = re.sub(r"\b(of|is|with|at|for|subject to|a fee of|fee of)\s*([.,;]|$)", r"\2", base, flags=re.IGNORECASE)
        base = re.sub(r"\s+", " ", base).strip(" ,;.-")
        if len(base.split()) >= 4:
            props.append(base + ".")
        if deadline:
            props.append(f"The deadline is {deadline.group(0).strip()}.")
        if fee:
            props.append(f"The applicable amount is {fee.group(0).strip()}.")
        return props

    def _categorize(self, text: str, entities: Dict[str, Any]) -> ClaimCategory:
        if "duration_hours" in entities and DEADLINE_PHRASE_RE.search(text):
            return ClaimCategory.DEADLINE
        if "amount" in entities or FEE_WORD_RE.search(text):
            return ClaimCategory.FEE
        if ELIGIBILITY_RE.search(text):
            return ClaimCategory.ELIGIBILITY
        if EXCEPTION_RE.search(text):
            return ClaimCategory.EXCEPTION
        if DOCUMENT_RE.search(text):
            return ClaimCategory.DOCUMENT_REQUIREMENT
        if CONTACT_RE.search(text):
            return ClaimCategory.CONTACT
        if PROCESS_RE.search(text):
            return ClaimCategory.PROCESS
        if POLICY_RE.search(text):
            return ClaimCategory.POLICY_RULE
        return ClaimCategory.GENERAL_INFORMATION

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Entities parsed with the same rules applied to evidence (see text_utils)."""
        entities: Dict[str, Any] = {}
        durations = sorted(extract_durations_hours(text))
        if durations:
            entities["duration_hours"] = durations
        amounts = sorted(extract_currency(text))
        if amounts:
            entities["amount"] = amounts
        pcts = sorted(extract_percentages(text))
        if pcts:
            entities["percent"] = pcts
        sem = re.search(r"\bsemester\s*(\d+)", text, re.IGNORECASE)
        if sem:
            entities["semester"] = int(sem.group(1))
        cgpa = re.search(r"\bcgpa\s*(?:of|above|>=|>|at least)?\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if cgpa:
            entities["cgpa"] = float(cgpa.group(1))
        low = text.lower()
        if any(t in low for t in ("all students", "any student", "every student", "all semesters", "regardless of")):
            entities["scope"] = "UNIVERSAL"
        return entities

    def _is_high_impact(self, category: ClaimCategory, text: str, entities: Dict[str, Any]) -> bool:
        if category in (ClaimCategory.ELIGIBILITY, ClaimCategory.FEE, ClaimCategory.DEADLINE):
            return True
        low = text.lower()
        if any(k in low for k in HIGH_IMPACT_KEYWORDS):
            return True
        return any(k in entities for k in ("amount", "duration_hours", "cgpa", "percent"))

    def _is_operational(self, sentence: str) -> bool:
        low = sentence.lower()
        # A sentence carrying explicit numeric policy facts is never treated as operational.
        if extract_currency(sentence) or extract_durations_hours(sentence):
            return False
        return any(re.search(p, low) for p in OPERATIONAL_PATTERNS)

    def _is_boilerplate(self, sentence: str) -> bool:
        low = sentence.lower().strip(" ,.-!")
        if any(low.startswith(p) for p in BOILERPLATE_PREFIXES):
            return True
        if any(p in low for p in BOILERPLATE_CONTAINS):
            return True
        # Signature lines: short, no terminal punctuation (e.g. "Hostel Affairs Redressal Desk")
        if not re.search(r"[.!?\"”]$", sentence.strip()) and len(sentence.split()) <= 6:
            return True
        return False
