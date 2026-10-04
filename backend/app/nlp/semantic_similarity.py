import math
from typing import List, Dict, Any, Tuple, Optional
from app.nlp.preprocessing import tokenize, clean_text

class SemanticSimilarityEngine:
    """
    Modular semantic similarity engine.
    Computes text-to-text similarity and ranks candidate documents using a hybrid
    token-weighted cosine & character 3-gram similarity metric with university domain
    synonym canonicalization.
    Designed to be easily subclassed or swapped with dense neural embedding models.
    """

    SYNONYM_MAP = {
        "hall ticket": "admit card",
        "hallticket": "admit card",
        "examination": "exam",
        "tuition fee": "fee",
        "tuition": "fee",
        "fees": "fee",
        "re-evaluation": "reevaluation",
        "wi-fi": "wifi",
        "continuous assessment": "ca marks",
        "marks discrepancy": "grade discrepancy",
        "marks": "grade"
    }

    def _normalize_text(self, text: str) -> str:
        norm = clean_text(text).lower()
        for syn, canonical in self.SYNONYM_MAP.items():
            norm = norm.replace(syn, canonical)
        return norm

    def _char_ngrams(self, text: str, n: int = 3) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for i in range(len(text) - n + 1):
            gram = text[i:i + n]
            counts[gram] = counts.get(gram, 0) + 1
        return counts

    def _cosine_similarity_dicts(self, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        if not vec1 or not vec2:
            return 0.0
        dot_product = sum(vec1[k] * vec2[k] for k in vec1 if k in vec2)
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot_product / (mag1 * mag2)

    def similarity(self, text_a: str, text_b: str) -> float:
        """
        Computes hybrid semantic similarity between two texts.
        Returns a float between 0.0 and 1.0.
        """
        if not text_a or not text_b:
            return 0.0
        norm_a = self._normalize_text(text_a)
        norm_b = self._normalize_text(text_b)

        if norm_a == norm_b:
            return 1.0

        # 1. Token-level Jaccard similarity
        tokens_a = set(tokenize(norm_a, remove_stopwords=True))
        tokens_b = set(tokenize(norm_b, remove_stopwords=True))
        token_sim = 0.0
        if tokens_a and tokens_b:
            intersection = tokens_a.intersection(tokens_b)
            union = tokens_a.union(tokens_b)
            token_sim = len(intersection) / len(union) if union else 0.0

        # 2. Character 3-gram cosine similarity
        grams_a = self._char_ngrams(norm_a, n=3)
        grams_b = self._char_ngrams(norm_b, n=3)
        char_sim = self._cosine_similarity_dicts(grams_a, grams_b)

        # Weighted combination
        combined = 0.4 * token_sim + 0.6 * char_sim
        return round(min(max(combined, 0.0), 1.0), 3)

    def find_similar(
        self,
        text: str,
        candidate_documents: List[Dict[str, Any]],
        top_k: int = 3,
        content_field: str = "content"
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Ranks candidate documents by semantic similarity to the input query text.
        Returns top_k items as (score, doc) tuples sorted descending by score.
        """
        scored_candidates: List[Tuple[float, Dict[str, Any]]] = []

        for doc in candidate_documents:
            candidate_text = doc.get(content_field, "")
            if "title" in doc:
                candidate_text = f"{doc['title']} {candidate_text}"
            elif "subject" in doc:
                candidate_text = f"{doc['subject']} {candidate_text}"

            score = self.similarity(text, candidate_text)
            scored_candidates.append((score, doc))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[:top_k]
