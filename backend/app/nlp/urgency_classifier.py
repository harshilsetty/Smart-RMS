import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.nlp.schemas import PriorityLevel, UrgencyClassificationResult, UrgencyLevel

class BaseUrgencyClassifier(ABC):
    """Abstract interface for Urgency & Priority Classifiers."""

    @abstractmethod
    def classify(
        self,
        text: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> UrgencyClassificationResult:
        """Evaluates text and metadata to classify recommended ticket priority."""
        pass

class RuleBasedUrgencyClassifier(BaseUrgencyClassifier):
    """
    Explainable, rule-based urgency classifier for University RMS.
    Analyzes hazard language, imminent exam deadlines, duplicate payment amounts,
    and repeated grievance indicators.
    """

    CRITICAL_SIGNALS = [
        (r"exam.*(?:48\s*hours?|tomorrow|today|commencing)", "Exam commencing in <=48 hours with clearance obstacle"),
        (r"(?:admit card|hall ticket).*blocked", "Immediate hall ticket blockage preventing exam participation"),
        (r"(?:leak|water).*(?:switchboard|electric|short circuit|hazard|shock)", "Physical safety hazard: water proximity to electrical fixtures"),
        (r"(?:emergency|immediate medical|hospitalized critically)", "Acute health emergency requirement")
    ]

    HIGH_SIGNALS = [
        (r"(?:deducted twice|debited twice|double deduction)", "Duplicate fee debit requiring urgent financial ledger reconciliation"),
        (r"(?:deadline\s+is\s+30th|closing date|portal closing|due date\s+approaching)", "Strict institutional/portal submission deadline approaching"),
        (r"(?:pending.*(?:3 weeks|month|repeatedly|no response|reminder))", "Prolonged unresolved delay exceeding university standard SLA"),
        (r"(?:leak|leaking|ac unit|spark|geyser|broken)", "Active residential infrastructure malfunction requiring supervisor dispatch"),
        (r"(?:datesheet clash|timetable clash|exam center|spelling error.*transcript|re-eval)", "Examination schedule or official transcript requirement"),
        (r"(?:fee|tuition|refund|payment|challan|scholarship|pms|nsp)", "Financial reconciliation or statutory scholarship verification requirement")
    ]

    MEDIUM_SIGNALS = [
        (r"(?:ca\s*marks|continuous assessment|grade|rubric|inconsistency)", "Academic evaluation record adjustment within standard appeal window"),
        (r"(?:medical leave|attendance condonation|duty leave|hospitalization|surgery recovery)", "Attendance condonation request supported by medical certification"),
        (r"(?:biometric|punch machine|mentor|credit transfer|elective)", "Routine academic administration or attendance biometric discrepancy")
    ]

    TEMPORAL_PATTERNS = [
        (r"\b(?:starts?\s+in\s+24\s*hours?|within\s+24\s*hours?|today|tonight)\b", "Immediate time-window (within 24 hours)"),
        (r"\b(?:tomorrow|in\s+48\s*hours?|within\s+2\s*days?)\b", "Near-term time-window (24-48 hours)"),
        (r"\b(?:this\s+week|by\s+friday|in\s+3\s*days?|3rd\s+day)\b", "Weekly operational window"),
        (r"\b(?:deadline\s+is\s+\d{1,2}(?:st|nd|rd|th)?|closing\s+date|due\s+date)\b", "Explicit calendar deadline constraint"),
        (r"\b(?:pending.*(?:3\s*weeks|month|repeatedly|no\s+response|reminder))\b", "Long-standing delay backlog")
    ]

    def classify(
        self,
        text: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, Any]] = None
    ) -> UrgencyClassificationResult:
        entities = entities or {}
        lower = text.lower()
        signals: List[str] = []
        temporal_exprs: List[str] = []

        # Extract temporal cues
        for pat, desc in self.TEMPORAL_PATTERNS:
            matches = re.findall(pat, lower)
            if matches:
                temporal_exprs.append(desc)

        # 1. Evaluate Critical Signals
        for pattern, reason in self.CRITICAL_SIGNALS:
            if re.search(pattern, lower):
                signals.append(reason)
        if signals:
            return UrgencyClassificationResult(
                priority=PriorityLevel.CRITICAL,
                confidence=0.95,
                priority_score=4,
                signals_detected=signals,
                reason="; ".join(signals),
                urgency=UrgencyLevel.IMMEDIATE,
                urgency_confidence=0.95,
                temporal_expressions=temporal_exprs
            )

        # 2. Evaluate High Signals
        for pattern, reason in self.HIGH_SIGNALS:
            if re.search(pattern, lower):
                signals.append(reason)
        # Check intent cues
        if intent in ["HOSTEL_MAINTENANCE", "FEE_PAYMENT", "SCHOLARSHIP"]:
            signals.append(f"Standard operational triage for high-impact {intent} domain")

        if signals:
            is_immediate_urgency = any("Immediate" in t or "Near-term" in t for t in temporal_exprs)
            urgency_val = UrgencyLevel.IMMEDIATE if is_immediate_urgency else UrgencyLevel.URGENT
            return UrgencyClassificationResult(
                priority=PriorityLevel.HIGH,
                confidence=0.90,
                priority_score=3,
                signals_detected=signals,
                reason="; ".join(signals),
                urgency=urgency_val,
                urgency_confidence=0.90,
                temporal_expressions=temporal_exprs
            )

        # 3. Evaluate Medium Signals
        for pattern, reason in self.MEDIUM_SIGNALS:
            if re.search(pattern, lower):
                signals.append(reason)
        if intent in ["ACADEMIC", "ATTENDANCE"]:
            signals.append("Standard academic/attendance review timeline")

        if signals:
            urgency_val = UrgencyLevel.URGENT if temporal_exprs else UrgencyLevel.NORMAL
            return UrgencyClassificationResult(
                priority=PriorityLevel.MEDIUM,
                confidence=0.88,
                priority_score=2,
                signals_detected=signals,
                reason="; ".join(signals),
                urgency=urgency_val,
                urgency_confidence=0.88,
                temporal_expressions=temporal_exprs
            )

        # 4. Default: Low Priority
        return UrgencyClassificationResult(
            priority=PriorityLevel.LOW,
            confidence=0.85,
            priority_score=1,
            signals_detected=["Routine administrative inquiry without acute time constraint"],
            reason="Routine request subject to standard departmental turnaround.",
            urgency=UrgencyLevel.LOW,
            urgency_confidence=0.85,
            temporal_expressions=temporal_exprs
        )
