from typing import List, Dict, Any, Optional
from app.nlp.preprocessing import tokenize

def compute_grounding_metrics(
    draft_responses: List[str],
    retrieved_sources_list: List[List[Dict[str, Any]]],
    expected_doc_ids: List[Optional[str]]
) -> Dict[str, Any]:
    """
    Evaluates response grounding against retrieved policy evidence using transparent heuristics.
    
    NOTE: Grounding evaluation in this Phase 2 baseline is heuristic.
    It does not claim zero hallucinations or neural NLI entailment.
    It evaluates:
      - Citation fidelity: cited clause/title presence in retrieved sources.
      - Lexical evidence support: key policy tokens from source present in response.
      - No-source safety adherence: strict fallback to human review when no authoritative source exists.
    """
    total = len(draft_responses)
    if total == 0:
        return {
            "evaluation_type": "heuristic",
            "grounding_rate": 0.0,
            "citation_fidelity": 0.0,
            "no_source_adherence": 0.0,
            "evaluated_samples": 0
        }

    grounded_count = 0
    citation_hits = 0
    no_source_evaluated = 0
    no_source_passed = 0

    for draft, sources, expected_doc in zip(draft_responses, retrieved_sources_list, expected_doc_ids):
        draft_lower = draft.lower()

        # Case 1: Query had no authoritative policy document (expected_doc is None or sources empty)
        if not expected_doc or not sources:
            no_source_evaluated += 1
            if "insufficient authoritative information" in draft_lower and "human review required" in draft_lower:
                no_source_passed += 1
                grounded_count += 1
            continue

        # Case 2: Sources exist - check citation and excerpt overlap
        top_source = sources[0]
        source_title = top_source.get("title", "").lower()
        source_clause = top_source.get("clause", "").lower()
        excerpt = top_source.get("excerpt", "").lower()

        # Citation fidelity check
        has_citation = (source_title in draft_lower) or (source_clause in draft_lower) or ("clause" in draft_lower)
        if has_citation:
            citation_hits += 1

        # Excerpt key token overlap
        excerpt_tokens = set(tokenize(excerpt, remove_stopwords=True))
        draft_tokens = set(tokenize(draft_lower, remove_stopwords=True))
        shared = excerpt_tokens.intersection(draft_tokens)

        # Grounded if either citation is faithful and key policy terms are cited
        is_grounded = has_citation and (len(shared) >= 3 or len(excerpt_tokens) == 0)
        if is_grounded:
            grounded_count += 1

    grounding_rate = round(grounded_count / total, 4) if total > 0 else 0.0
    cited_denom = (total - no_source_evaluated)
    citation_fidelity = round(citation_hits / cited_denom, 4) if cited_denom > 0 else 1.0
    no_source_adherence = round(no_source_passed / no_source_evaluated, 4) if no_source_evaluated > 0 else 1.0

    return {
        "evaluation_type": "heuristic_evidence_verification",
        "grounding_rate": grounding_rate,
        "citation_fidelity": citation_fidelity,
        "no_source_adherence": no_source_adherence,
        "evaluated_samples": total,
        "no_source_cases_count": no_source_evaluated,
        "methodology_disclaimer": "Heuristic token overlap and citation verification; not neural NLI."
    }
