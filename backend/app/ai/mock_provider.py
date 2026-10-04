from typing import List, Dict, Any, Optional
from app.ai.provider import AIProvider
from app.schemas.rms import AIAnalysis, DraftResponse, RAGSource
from app.privacy.pii_detector import PIIDetector
from app.nlp.pipeline import NLPPipeline

class MockAIProvider(AIProvider):
    """Deterministic Mock AI Provider backed by the modular NLP pipeline."""

    def __init__(self, nlp_pipeline: Optional[NLPPipeline] = None):
        self.pii_detector = PIIDetector()
        self.nlp_pipeline = nlp_pipeline or NLPPipeline()

    async def analyze_ticket(self, ticket_subject: str, ticket_description: str) -> AIAnalysis:
        pii_tokens = self.pii_detector.get_detected_tokens(ticket_description)
        nlp_res = self.nlp_pipeline.process(ticket_subject, ticket_description)

        entities = dict(nlp_res.entities)

        avg_confidence = round(
            (nlp_res.intent_confidence + nlp_res.department_confidence + nlp_res.priority_confidence) / 3.0,
            2
        )

        return AIAnalysis(
            intent=nlp_res.intent,
            suggested_department=nlp_res.department,
            priority_score=nlp_res.priority_score,
            urgency_level=nlp_res.priority,
            confidence=avg_confidence,
            intent_confidence=nlp_res.intent_confidence,
            department_confidence=nlp_res.department_confidence,
            priority_confidence=nlp_res.priority_confidence,
            requires_human_review=nlp_res.requires_human_review,
            review_reasons=nlp_res.review_reasons,
            semantic_matches=[m.model_dump() for m in nlp_res.semantic_matches],
            pii_detected=pii_tokens,
            entities=entities,
            summary=nlp_res.summary,
            suggested_action=nlp_res.suggested_action
        )

    async def generate_draft(
        self,
        ticket_subject: str,
        ticket_description: str,
        sources: List[RAGSource],
        department: str
    ) -> DraftResponse:
        # Check for authoritative RAG sources (Relevance threshold >= 0.65)
        valid_sources = [s for s in sources if s.relevance_score >= 0.65]

        if valid_sources:
            primary_source = valid_sources[0]
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
                sources=valid_sources,
                confidence=primary_source.relevance_score,
                requires_staff_edit=False,
                policy_compliance_passed=True
            )

        # Strict No-Source-No-Answer Fallback
        no_source_body = (
            f"Dear Student,\n\n"
            f"Regarding your inquiry on '{ticket_subject}', our system determined that there is insufficient "
            f"authoritative information in current university policy records to safely generate an automated resolution draft.\n\n"
            f"Insufficient authoritative information. Human review required.\n\n"
            f"This request has been routed to the {department} operational desk for manual review by a staff officer.\n\n"
            f"Warm regards,\n"
            f"{department} Operations\n"
            f"Smart University RMS"
        )
        return DraftResponse(
            ticket_id="",
            draft_response=no_source_body,
            sources=[],
            confidence=0.0,
            requires_staff_edit=True,
            policy_compliance_passed=True
        )
