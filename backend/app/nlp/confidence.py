from typing import List, Tuple
from app.nlp.schemas import ConfidenceLevel

class ConfidenceEvaluator:
    """
    Evaluates multi-component confidence scores (intent, routing, priority)
    and enforces human-in-the-loop review thresholds.
    """

    HIGH_THRESHOLD: float = 0.85
    MEDIUM_THRESHOLD: float = 0.70

    def evaluate(
        self,
        intent_conf: float,
        dept_conf: float,
        priority_conf: float,
        has_authoritative_source: bool = True
    ) -> Tuple[ConfidenceLevel, bool, List[str]]:
        """
        Determines the overall confidence level and whether human review is mandated.
        Returns:
            - confidence_level: HIGH, MEDIUM, or LOW
            - requires_human_review: boolean
            - review_reasons: list of explainable review trigger reasons
        """
        reasons: List[str] = []

        # Weighted aggregate confidence
        aggregate = (0.45 * intent_conf) + (0.35 * dept_conf) + (0.20 * priority_conf)

        if not has_authoritative_source:
            reasons.append("No authoritative university policy document verified for query.")

        if intent_conf < self.MEDIUM_THRESHOLD:
            reasons.append(f"Intent classification confidence ({intent_conf:.2f}) below medium threshold.")
        elif intent_conf < self.HIGH_THRESHOLD:
            reasons.append(f"Intent classification confidence ({intent_conf:.2f}) requires staff confirmation.")

        if dept_conf < self.MEDIUM_THRESHOLD:
            reasons.append(f"Department routing confidence ({dept_conf:.2f}) below medium threshold.")

        if priority_conf < self.MEDIUM_THRESHOLD:
            reasons.append(f"Urgency assessment confidence ({priority_conf:.2f}) indicates potential ambiguous priority.")

        # Classify Level
        if aggregate >= self.HIGH_THRESHOLD and has_authoritative_source and not reasons:
            return ConfidenceLevel.HIGH, False, []
        elif aggregate >= self.MEDIUM_THRESHOLD and has_authoritative_source:
            return ConfidenceLevel.MEDIUM, True, reasons
        else:
            return ConfidenceLevel.LOW, True, reasons
