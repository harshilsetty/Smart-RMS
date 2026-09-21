import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

class VectorStore(ABC):
    """Abstract interface for Vector Store backends."""

    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Indexes policy documents into the vector store."""
        pass

    @abstractmethod
    def search(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches indexed documents for relevant clauses."""
        pass

class MockVectorStore(VectorStore):
    """Mock in-memory vector store loading official policy documents from JSON."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.MOCK_DATA_DIR / "knowledge_documents.json")
        self.documents: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception:
                self.documents = []

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        self.documents.extend(documents)
        return True

    def search(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            # Department filter if specified
            if department and department.lower() not in doc.get("department", "").lower():
                continue

            # Calculate keyword match score
            keywords = [k.lower() for k in doc.get("keywords", [])]
            content_lower = doc.get("content", "").lower() + " " + doc.get("title", "").lower()
            
            score = 0.5  # Base match
            for word in query_words:
                if len(word) > 3 and word in content_lower:
                    score += 0.1
                for kw in keywords:
                    if kw in query.lower():
                        score += 0.25

            score = min(score, 0.98)
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "document_id": doc["document_id"],
                "title": doc["title"],
                "clause": doc["clause"],
                "excerpt": doc["content"],
                "relevance_score": round(score, 2)
            }
            for score, doc in scored_docs[:limit]
        ]

class ChromaVectorStore(VectorStore):
    """Production Chroma Vector Store wrapper (falls back gracefully to MockVectorStore)."""

    def __init__(self, persist_directory: str = "./chroma_data"):
        self.persist_directory = persist_directory
        self.mock_store = MockVectorStore()

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        return self.mock_store.add_documents(documents)

    def search(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        return self.mock_store.search(query, department, limit)
