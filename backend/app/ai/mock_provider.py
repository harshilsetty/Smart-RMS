from typing import List, Dict, Any
from app.ai.provider import AIProvider
from app.schemas.rms import AIAnalysis, DraftResponse, RAGSource
from app.privacy.pii_detector import PIIDetector

class MockAIProvider(AIProvider):
    """Deterministic Mock AI Provider for local development without external API keys."""

    def __init__(self):
        self.pii_detector = PIIDetector()

    async def analyze_ticket(self, ticket_subject: str, ticket_description: str) -> AIAnalysis:
        combined = (ticket_subject + " " + ticket_description).lower()
        pii_tokens = self.pii_detector.get_detected_tokens(ticket_description)

        # Keyword-based deterministic classification
        if "leak" in combined or "ac unit" in combined or "hostel" in combined or "room" in combined:
            return AIAnalysis(
                intent="HOSTEL_MAINTENANCE",
                suggested_department="Hostel Affairs",
                priority_score=3,
                urgency_level="High",
                confidence=0.95,
                pii_detected=pii_tokens,
                entities={"hostel_block": "BH/GH", "issue_type": "Facility Maintenance"},
                summary="Hostel room maintenance query concerning appliance malfunction or water leakage.",
                suggested_action="Dispatch maintenance supervisor within 24-hour standard SLA."
            )
        elif "fee" in combined or "refund" in combined or "deducted twice" in combined or "bank" in combined:
            return AIAnalysis(
                intent="FEE_PAYMENT_RECONCILIATION",
                suggested_department="Accounts & Finance",
                priority_score=3,
                urgency_level="High",
                confidence=0.94,
                pii_detected=pii_tokens,
                entities={"financial_issue": "Duplicate transaction or ledger reconciliation"},
                summary="Tuition fee deduction issue requiring ledger reconciliation and potential refund.",
                suggested_action="Verify transaction reference in settlement ledger and process refund within 7-10 days."
            )
        elif "admit card" in combined or "hall ticket" in combined or "exam" in combined:
            return AIAnalysis(
                intent="EXAM_HALL_TICKET_HOLD",
                suggested_department="Examination Branch",
                priority_score=4,
                urgency_level="Critical",
                confidence=0.96,
                pii_detected=pii_tokens,
                entities={"urgency": "Immediate / Exam in <48 hrs", "barrier": "Clearance Hold"},
                summary="Admit card clearance hold restricting student from downloading exam hall ticket.",
                suggested_action="Expedited clearance verification and emergency admit card release within 4 hours."
            )
        elif "ca" in combined or "marks" in combined or "grade" in combined:
            return AIAnalysis(
                intent="ACADEMIC_MARKS_DISCREPANCY",
                suggested_department="Academic Affairs",
                priority_score=2,
                urgency_level="Medium",
                confidence=0.91,
                pii_detected=pii_tokens,
                entities={"evaluation_type": "Continuous Assessment Rubric Verification"},
                summary="Discrepancy reported between instructor rubric marks and portal grade record.",
                suggested_action="Forward to course coordinator and department HOD for grade ledger rectification."
            )
        elif "attendance" in combined or "medical" in combined or "dengue" in combined or "leave" in combined:
            return AIAnalysis(
                intent="ATTENDANCE_MEDICAL_CONDONATION",
                suggested_department="Student Welfare",
                priority_score=2,
                urgency_level="Medium",
                confidence=0.93,
                pii_detected=pii_tokens,
                entities={"cause": "Hospitalization / Severe Illness"},
                summary="Medical leave duty adjustment application for hospitalization period.",
                suggested_action="Validate hospital discharge summary with Health Center and grant attendance duty."
            )
        else:
            return AIAnalysis(
                intent="GENERAL_UNIVERSITY_INQUIRY",
                suggested_department="Academic Affairs",
                priority_score=1,
                urgency_level="Low",
                confidence=0.85,
                pii_detected=pii_tokens,
                entities={"type": "General Service Request"},
                summary="Standard student administrative query regarding university procedures.",
                suggested_action="Provide policy guidance or issue relevant digitally signed e-document."
            )

    async def generate_draft(
        self,
        ticket_subject: str,
        ticket_description: str,
        sources: List[RAGSource],
        department: str
    ) -> DraftResponse:
        combined = (ticket_subject + " " + ticket_description).lower()

        if sources:
            primary_source = sources[0]
            citation = f"{primary_source.title} ({primary_source.clause})"
            body = (
                f"Dear Student,\n\n"
                f"We acknowledge your grievance regarding '{ticket_subject}'.\n\n"
                f"In accordance with official university policy—specifically {citation}—your request has been logged "
                f"and assigned to the designated {department} operational supervisor.\n\n"
                f"Policy Guidance Note: \"{primary_source.excerpt}\"\n\n"
                f"Please ensure all required supporting documents are kept ready if further verification is needed. "
                f"We anticipate resolution within the standard departmental SLA window.\n\n"
                f"Warm regards,\n"
                f"{department} Redressal Desk\n"
                f"Smart University RMS"
            )
            return DraftResponse(
                ticket_id="",
                draft_response=body,
                sources=sources,
                confidence=primary_source.relevance_score,
                requires_staff_edit=False,
                policy_compliance_passed=True
            )

        # Fallback if no sources found
        fallback_body = (
            f"Dear Student,\n\n"
            f"Thank you for contacting the {department} Redressal Desk regarding your inquiry: '{ticket_subject}'.\n\n"
            f"Your request has been placed in our review queue. A department officer will verify the relevant academic statutes "
            f"and update your ticket status within 24–48 hours.\n\n"
            f"Warm regards,\n"
            f"{department} Operations"
        )
        return DraftResponse(
            ticket_id="",
            draft_response=fallback_body,
            sources=[],
            confidence=0.70,
            requires_staff_edit=True,
            policy_compliance_passed=True
        )
