"""
Smart RMS - Evidence Matcher
Milestone 6: Maps each extracted claim to the best sentence inside the evidence
chunks ALREADY retrieved for the ticket. It never queries the vector store, so a
claim cannot be "rescued" by fetching an unrelated document.

Matching is sentence-level: each retrieved chunk is split into sentences and the
claim is compared to every sentence. Whole-chunk comparison was found during the
audit to under-score verbatim claims taken from long chunks.

Score (used only for ranking candidate sentences, not as a probability):
    match_score = 0.60 * containment + 0.25 * entity_alignment + 0.15 * min(rag_relevance, 1)
where containment = |claim tokens ∩ sentence tokens| / |claim tokens|.
"""

from typing import List, Optional, Any, Tuple

from app.schemas.grounding import ExtractedClaim, EvidenceMatch
from app.grounding.text_utils import (
    split_sentences, containment, extract_durations_hours, extract_currency,
    extract_percentages,
)


class EvidenceMatcher:
    def __init__(self, min_containment: float = 0.20):
        self.min_containment = min_containment

    def match_claim(self, claim: ExtractedClaim, sources: List[Any]) -> Optional[EvidenceMatch]:
        if not sources:
            return None

        best: Optional[Tuple[float, float, str, tuple]] = None
        # Decomposed deadline/amount sub-claims ("The deadline is within 7 days.") are matched
        # using their original sentence so they land on the same evidence as their base claim.
        match_text = claim.source_sentence if (claim.entities_detected or {}).get("subclaim_type") else claim.text
        for src in sources:
            fields = self._extract_source_fields(src)
            excerpt = fields[3]
            if not excerpt or not excerpt.strip():
                continue
            for sent in split_sentences(excerpt) or [excerpt]:
                cont = containment(match_text, sent)
                ent = self._entity_alignment(claim, sent)
                score = 0.60 * cont + 0.25 * ent + 0.15 * min(fields[4], 1.0)
                if best is None or score > best[0]:
                    best = (score, cont, sent, fields)

        if best is None:
            return None
        score, cont, sent, (doc_id, title, clause, excerpt, rel) = best
        if cont < self.min_containment:
            return None  # Retrieved evidence does not address this claim at all

        return EvidenceMatch(
            document_id=str(doc_id),
            title=str(title),
            clause=str(clause),
            excerpt=excerpt,
            relevance_score=round(float(rel), 4),
            lexical_similarity=round(cont, 4),
            semantic_similarity=None,
            matched_sentence=sent,
        )

    @staticmethod
    def _extract_source_fields(src: Any) -> tuple:
        if isinstance(src, dict):
            return (
                src.get("document_id") or src.get("id", "UNKNOWN_DOC"),
                src.get("title", "Policy Document"),
                src.get("clause") or src.get("section", "General"),
                src.get("excerpt") or src.get("content", ""),
                float(src.get("relevance_score", src.get("score", 0.0)) or 0.0),
            )
        return (
            getattr(src, "document_id", None) or getattr(src, "id", "UNKNOWN_DOC"),
            getattr(src, "title", "Policy Document"),
            getattr(src, "clause", None) or getattr(src, "section", "General"),
            getattr(src, "excerpt", None) or getattr(src, "content", ""),
            float(getattr(src, "relevance_score", None) or getattr(src, "score", 0.0) or 0.0),
        )

    @staticmethod
    def _entity_alignment(claim: ExtractedClaim, sentence: str) -> float:
        """1.0 if every numeric entity type in the claim also appears (same type) in the sentence."""
        ents = claim.entities_detected or {}
        checks = []
        if "duration_hours" in ents:
            checks.append(bool(extract_durations_hours(sentence)))
        if "amount" in ents:
            checks.append(bool(extract_currency(sentence)))
        if "percent" in ents:
            checks.append(bool(extract_percentages(sentence)))
        if not checks:
            return 0.0
        return sum(checks) / len(checks)
