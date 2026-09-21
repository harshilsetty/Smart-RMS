from typing import List, Optional
from app.rag.vector_store import VectorStore, MockVectorStore
from app.schemas.rms import RAGSource

class PolicyRetriever:
    """Retrieves relevant university policies and formats them as RAGSource items."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or MockVectorStore()

    def retrieve(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[RAGSource]:
        raw_results = self.vector_store.search(query, department=department, limit=limit)
        sources: List[RAGSource] = []
        for r in raw_results:
            sources.append(
                RAGSource(
                    document_id=r["document_id"],
                    title=r["title"],
                    clause=r["clause"],
                    excerpt=r["excerpt"],
                    relevance_score=r["relevance_score"]
                )
            )
        return sources
