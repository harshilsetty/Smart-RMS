"""
RAG Context Builder for Smart RMS.
Assembles, validates, and packages retrieved policy evidence into GroundedContext.
Enforces the core principle: NO-SOURCE -> NO-ANSWER.
"""

from typing import List, Optional
from app.schemas.rms import RAGSource, GroundedContext
from app.rag.retriever import PolicyRetriever

class RAGContextBuilder:
    """
    Dedicated component responsible for transforming retrieval evidence
    into grounded context for staff-copilot draft generation.
    Does NOT make autonomous resolution decisions.
    """

    def __init__(
        self,
        retriever: Optional[PolicyRetriever] = None,
        default_threshold: float = 0.65,
        default_top_k: int = 3
    ):
        self.retriever = retriever or PolicyRetriever()
        self.default_threshold = default_threshold
        self.default_top_k = default_top_k

    def build_context(
        self,
        query: str,
        department: Optional[str] = None,
        top_k: Optional[int] = None,
        min_threshold: Optional[float] = None
    ) -> GroundedContext:
        k = top_k if top_k is not None else self.default_top_k
        threshold = min_threshold if min_threshold is not None else self.default_threshold

        # 1. Retrieve candidates
        sources = self.retriever.retrieve(
            query=query,
            department=department,
            limit=k,
            min_threshold=0.0  # Retrieve all candidates to evaluate against threshold
        )

        # 2. Filter by relevance threshold
        authoritative_sources = [s for s in sources if s.relevance_score >= threshold]

        # 3. Check for sufficient evidence
        if not authoritative_sources:
            return GroundedContext(
                query=query,
                department=department,
                grounding_status="INSUFFICIENT_EVIDENCE",
                sources=sources,  # Preserve retrieved candidates for staff inspection
                context_text="",
                needs_human_review=True,
                refusal_reason=f"No approved policy crossed the confidence threshold ({threshold:.2f}). Human review required."
            )

        # 4. Format grounded context with explicit citations
        context_blocks = []
        for idx, src in enumerate(authoritative_sources, start=1):
            block = (
                f"[Source {idx}]: {src.title} (Doc ID: {src.document_id}, Version: {src.document_version})\n"
                f"Section/Clause: {src.clause}\n"
                f"Relevance Score: {src.relevance_score:.4f}\n"
                f"Authoritative Policy Excerpt:\n\"{src.excerpt}\""
            )
            context_blocks.append(block)

        context_text = "\n\n---\n\n".join(context_blocks)

        return GroundedContext(
            query=query,
            department=department,
            grounding_status="GROUNDED",
            sources=authoritative_sources,
            context_text=context_text,
            needs_human_review=False,
            refusal_reason=None
        )
