from typing import Dict, Any, Optional, List
from app.nlp.schemas import NLPResult, SemanticMatch, PriorityLevel
from app.nlp.preprocessing import clean_text
from app.nlp.entity_extractor import EntityExtractor
from app.nlp.intent_classifier import BaseIntentClassifier, RuleBasedIntentClassifier
from app.nlp.department_classifier import BaseDepartmentClassifier, RuleBasedDepartmentRouter
from app.nlp.urgency_classifier import BaseUrgencyClassifier, RuleBasedUrgencyClassifier
from app.nlp.semantic_similarity import SemanticSimilarityEngine
from app.nlp.confidence import ConfidenceEvaluator

class NLPPipeline:
    """
    Unified modular NLP pipeline for Smart RMS.
    Analyzes ticket subject and text to produce structured, measurable,
    explainable NLP analysis with confidence and human-review flags.
    """

    def __init__(
        self,
        intent_classifier: Optional[BaseIntentClassifier] = None,
        department_router: Optional[BaseDepartmentClassifier] = None,
        urgency_classifier: Optional[BaseUrgencyClassifier] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        similarity_engine: Optional[SemanticSimilarityEngine] = None,
        confidence_evaluator: Optional[ConfidenceEvaluator] = None
    ):
        self.intent_classifier = intent_classifier or RuleBasedIntentClassifier()
        self.department_router = department_router or RuleBasedDepartmentRouter()
        self.urgency_classifier = urgency_classifier or RuleBasedUrgencyClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.similarity_engine = similarity_engine or SemanticSimilarityEngine()
        self.confidence_evaluator = confidence_evaluator or ConfidenceEvaluator()

    def process(
        self,
        subject: str,
        description: str,
        candidate_docs: Optional[List[Dict[str, Any]]] = None
    ) -> NLPResult:
        """Executes full NLP pipeline on ticket subject and description."""
        combined_text = f"{clean_text(subject)} {clean_text(description)}".strip()

        # 1. Entity Extraction
        entities = self.entity_extractor.extract(combined_text)

        # 2. Intent Classification
        intent_res = self.intent_classifier.classify(combined_text)

        # 3. Department Routing
        dept_res = self.department_router.route(
            text=combined_text,
            intent=intent_res.intent,
            entities=entities
        )

        # 4. Urgency & Priority Classification
        urgency_res = self.urgency_classifier.classify(
            text=combined_text,
            intent=intent_res.intent,
            entities=entities
        )

        # 5. Semantic Similarity with candidate documents (if provided)
        semantic_matches: List[SemanticMatch] = []
        has_authoritative_match = True
        if candidate_docs:
            ranked = self.similarity_engine.find_similar(
                text=combined_text,
                candidate_documents=candidate_docs,
                top_k=2
            )
            for score, doc in ranked:
                semantic_matches.append(
                    SemanticMatch(
                        document_id=doc.get("document_id", "UNKNOWN"),
                        title=doc.get("title", "Policy Document"),
                        similarity_score=score,
                        excerpt=doc.get("content", "")[:160] + "..." if len(doc.get("content", "")) > 160 else doc.get("content", "")
                    )
                )
            # If top match similarity is very low (< 0.20), flag as lacking authoritative match
            if not ranked or ranked[0][0] < 0.20:
                has_authoritative_match = False

        # 6. Confidence & Human Review Assessment
        conf_level, requires_review, review_reasons = self.confidence_evaluator.evaluate(
            intent_conf=intent_res.confidence,
            dept_conf=dept_res.confidence,
            priority_conf=urgency_res.confidence,
            has_authoritative_source=has_authoritative_match
        )

        # 7. Summary & Suggested Action Synthesis
        summary = self._generate_summary(subject, intent_res.intent, dept_res.department, entities)
        suggested_action = self._suggest_action(dept_res.department, urgency_res.priority, intent_res.intent)

        return NLPResult(
            intent=intent_res.intent,
            intent_confidence=intent_res.confidence,
            department=dept_res.department,
            department_confidence=dept_res.confidence,
            priority=urgency_res.priority.value,
            priority_confidence=urgency_res.confidence,
            priority_score=urgency_res.priority_score,
            entities=entities,
            summary=summary,
            suggested_action=suggested_action,
            semantic_matches=semantic_matches,
            requires_human_review=requires_review,
            review_reasons=review_reasons,
            confidence_level=conf_level,
            classifier_mode="deterministic_baseline"
        )

    def _generate_summary(self, subject: str, intent: str, dept: str, entities: Dict[str, Any]) -> str:
        parts = [f"RMS ticket concerning '{subject}'."]
        parts.append(f"Classified as {intent} for {dept}.")
        if "hostel_block" in entities:
            parts.append(f"Located in {entities['hostel_block']}.")
        if "course_code" in entities:
            parts.append(f"Regarding course {entities['course_code']}.")
        if "currency_amount" in entities:
            parts.append(f"Involves disputed amount {entities['currency_amount']}.")
        return " ".join(parts)

    def _suggest_action(self, dept: str, priority: PriorityLevel, intent: str) -> str:
        if priority == PriorityLevel.CRITICAL:
            return f"Immediate expedited routing to {dept} supervisor; SLA response within 4 hours."
        elif priority == PriorityLevel.HIGH:
            return f"Route to {dept} operational desk; resolve within 24-hour SLA window."
        elif priority == PriorityLevel.MEDIUM:
            return f"Assign to {dept} review officer for verification within standard 48-hour SLA."
        else:
            return f"Process via standard {dept} self-service or standard administrative workflow."
