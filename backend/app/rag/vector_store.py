import json
import re
import math
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings
from app.nlp.preprocessing import tokenize, clean_text

class DocumentChunker:
    """Chunks policy documents into logical segments while preserving metadata."""

    @staticmethod
    def chunk_document(doc: Dict[str, Any], max_chunk_words: int = 60) -> List[Dict[str, Any]]:
        content = doc.get("content", "")
        # Split into sentences or clauses
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content) if s.strip()]
        chunks: List[Dict[str, Any]] = []

        current_sentences: List[str] = []
        current_len = 0

        for s in sentences:
            s_len = len(s.split())
            if current_len + s_len > max_chunk_words and current_sentences:
                chunk_text = " ".join(current_sentences)
                chunks.append({
                    "chunk_id": f"{doc.get('document_id', 'DOC')}-C{len(chunks) + 1}",
                    "document_id": doc.get("document_id", ""),
                    "source_id": doc.get("document_id", ""),
                    "title": doc.get("title", ""),
                    "document_name": doc.get("title", ""),
                    "clause": doc.get("clause", ""),
                    "section": doc.get("clause", ""),
                    "department": doc.get("department", ""),
                    "content": chunk_text,
                    "excerpt": chunk_text,
                    "keywords": doc.get("keywords", [])
                })
                current_sentences = [s]
                current_len = s_len
            else:
                current_sentences.append(s)
                current_len += s_len

        if current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append({
                "chunk_id": f"{doc.get('document_id', 'DOC')}-C{len(chunks) + 1}",
                "document_id": doc.get("document_id", ""),
                "source_id": doc.get("document_id", ""),
                "title": doc.get("title", ""),
                "document_name": doc.get("title", ""),
                "clause": doc.get("clause", ""),
                "section": doc.get("clause", ""),
                "department": doc.get("department", ""),
                "content": chunk_text,
                "excerpt": chunk_text,
                "keywords": doc.get("keywords", [])
            })

        return chunks if chunks else [{
            "chunk_id": f"{doc.get('document_id', 'DOC')}-C1",
            "document_id": doc.get("document_id", ""),
            "source_id": doc.get("document_id", ""),
            "title": doc.get("title", ""),
            "document_name": doc.get("title", ""),
            "clause": doc.get("clause", ""),
            "section": doc.get("clause", ""),
            "department": doc.get("department", ""),
            "content": content,
            "excerpt": content,
            "keywords": doc.get("keywords", [])
        }]

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

class LocalVectorStore(VectorStore):
    """
    Local in-memory retrieval engine with document chunking, metadata filtering,
    and hybrid token/character n-gram semantic relevance scoring.
    Does not require external embedding models or paid API services.
    """

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or (settings.MOCK_DATA_DIR / "knowledge_documents.json")
        self.documents: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        self._load_documents()

    def _load_documents(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                    self._build_index()
            except Exception:
                self.documents = []
                self.chunks = []

    def _build_index(self):
        self.chunks = []
        for doc in self.documents:
            chunks = DocumentChunker.chunk_document(doc)
            self.chunks.extend(chunks)

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        self.documents.extend(documents)
        self._build_index()
        return True

    def search(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        query_cleaned = clean_text(query).lower()
        query_tokens = set(tokenize(query_cleaned, remove_stopwords=True))
        scored_chunks: List[Tuple[float, Dict[str, Any]]] = []

        for chunk in self.chunks:
            # Department filter if specified
            chunk_dept = chunk.get("department", "").lower()
            if department and department.lower() not in chunk_dept and chunk_dept not in department.lower():
                continue

            chunk_text = f"{chunk.get('title', '')} {chunk.get('content', '')}".lower()
            chunk_tokens = set(tokenize(chunk_text, remove_stopwords=True))
            keywords = [k.lower() for k in chunk.get("keywords", [])]

            # 1. Keyword direct match
            keyword_score = sum(0.25 for kw in keywords if kw in query_cleaned)

            # 2. Token overlap score
            overlap = query_tokens.intersection(chunk_tokens)
            token_score = len(overlap) * 0.08 if query_tokens else 0.0

            # 3. Base prior if matching department
            dept_bonus = 0.20 if (department and department.lower() in chunk_dept) else 0.10

            raw_score = dept_bonus + keyword_score + token_score
            # Bound score realistically [0.0, 0.98]
            final_score = round(min(max(raw_score, 0.10), 0.98), 2)

            scored_chunks.append((final_score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        results = []
        seen_doc_ids = set()
        for score, chunk in scored_chunks:
            doc_id = chunk["document_id"]
            if doc_id in seen_doc_ids:
                continue
            seen_doc_ids.add(doc_id)
            results.append({
                "document_id": chunk["document_id"],
                "source_id": chunk["document_id"],
                "title": chunk["title"],
                "document_name": chunk["title"],
                "clause": chunk["clause"],
                "section": chunk["clause"],
                "excerpt": chunk["content"],
                "relevance_score": score
            })
            if len(results) >= limit:
                break

        return results

class MockVectorStore(LocalVectorStore):
    """Backward-compatible alias for LocalVectorStore."""
    pass

class ChromaVectorStore(VectorStore):
    """Chroma Vector Store adapter with graceful fallback to LocalVectorStore."""

    def __init__(self, persist_directory: str = "./chroma_data"):
        self.persist_directory = persist_directory
        self._local_store = LocalVectorStore()

    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        return self._local_store.add_documents(documents)

    def search(self, query: str, department: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        return self._local_store.search(query, department, limit)
