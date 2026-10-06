"""
Knowledge ingestion pipeline for Smart RMS.
Validates synthetic documents, performs semantic chunking, computes embeddings,
and builds the local vector index.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings
from app.schemas.contracts import KnowledgeDocument, KnowledgeChunk
from app.rag.chunker import SemanticDocumentChunker
from app.rag.embeddings import EmbeddingProvider, get_embedding_provider
from app.rag.vector_store import LocalVectorStore

class KnowledgeIngestionPipeline:
    """
    Automated pipeline transforming raw synthetic policies into an indexed vector database.
    """

    def __init__(
        self,
        docs_path: Optional[Path] = None,
        index_path: Optional[Path] = None,
        embedding_provider: Optional[EmbeddingProvider] = None
    ):
        self.docs_path = docs_path or (settings.MOCK_DATA_DIR / "knowledge_documents.json")
        self.index_path = index_path or (settings.MOCK_DATA_DIR / "knowledge_index.json")
        self.embedding_provider = embedding_provider or get_embedding_provider()

    def run(self, filter_approved_only: bool = True) -> Dict[str, Any]:
        """
        Executes complete ingestion pipeline and returns exact measured counts.
        """
        if not self.docs_path.exists():
            raise FileNotFoundError(f"Knowledge documents file not found at {self.docs_path}")

        # 1. Load documents
        with open(self.docs_path, "r", encoding="utf-8") as f:
            raw_docs = json.load(f)

        validated_docs: List[KnowledgeDocument] = []
        for raw in raw_docs:
            doc = KnowledgeDocument(**raw)
            validated_docs.append(doc)

        total_sections = sum(len(d.sections) for d in validated_docs)

        # 2. Filter active/approved if requested
        if filter_approved_only:
            docs_to_chunk = [d for d in validated_docs if d.approval_status == "APPROVED" and d.is_active]
        else:
            docs_to_chunk = validated_docs

        # 3. Semantic Chunking
        all_chunks: List[KnowledgeChunk] = []
        for doc in docs_to_chunk:
            chunks = SemanticDocumentChunker.chunk_document(doc)
            all_chunks.extend(chunks)

        # 4. Generate Embeddings
        texts_to_embed = [
            f"{c.document_title} {c.heading} {c.clause} {c.content}"
            for c in all_chunks
        ]
        embeddings = self.embedding_provider.embed_batch(texts_to_embed)

        # 5. Build and persist index
        store = LocalVectorStore(
            embedding_provider=self.embedding_provider,
            index_file=self.index_path
        )
        # Reset current chunks to freshly ingested ones
        store.chunks = []
        store.embeddings = store.embeddings[:0]
        store.add_chunks(all_chunks, embeddings)
        store.save(self.index_path)

        stats = {
            "total_documents_loaded": len(validated_docs),
            "approved_documents_indexed": len(docs_to_chunk),
            "total_sections": total_sections,
            "total_chunks_created": len(all_chunks),
            "total_embeddings_generated": len(embeddings),
            "total_indexed": len(store.chunks),
            "embedding_provider": self.embedding_provider.name,
            "embedding_dimension": self.embedding_provider.dimension,
            "index_path": str(self.index_path)
        }
        return stats
