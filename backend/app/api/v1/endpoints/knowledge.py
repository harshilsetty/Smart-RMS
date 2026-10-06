import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Path as FastPath
from app.rag.retriever import PolicyRetriever
from app.rag.context_builder import RAGContextBuilder
from app.rag.vector_store import LocalVectorStore
from app.schemas.rms import RAGSource, RAGQueryRequest, RAGQueryResponse, KnowledgeSearchResponse
from app.schemas.contracts import KnowledgeDocument
from app.config import settings

router = APIRouter()
vector_store = LocalVectorStore()
retriever = PolicyRetriever(vector_store=vector_store)
context_builder = RAGContextBuilder(retriever=retriever)

@router.get("/search", response_model=List[RAGSource], summary="Search university approved policies")
def search_knowledge(
    q: Optional[str] = Query(None, description="Search query string"),
    query: Optional[str] = Query(None, description="Search query string alias"),
    department: Optional[str] = Query(None, description="Filter by department"),
    document_type: Optional[str] = Query(None, description="Filter by document type (e.g., REGULATION, SOP, POLICY)"),
    version: Optional[str] = Query(None, description="Filter by specific policy version"),
    active_only: bool = Query(True, description="Only return active and currently effective policies"),
    top_k: int = Query(5, ge=1, le=20, description="Max results to return"),
    limit: Optional[int] = Query(None, ge=1, le=20, description="Max results alias"),
    min_threshold: float = Query(0.0, ge=0.0, le=1.0, description="Minimum relevance threshold")
):
    search_query = q or query or ""
    k = limit or top_k

    if not search_query.strip():
        return []

    # Dense retrieval with metadata constraints
    q_vec = vector_store.embedding_provider.embed_text(search_query)
    results = vector_store.search_by_vector(
        query_vector=q_vec,
        query_text=search_query,
        top_k=k,
        department=department,
        active_only=active_only,
        version=version,
        min_threshold=min_threshold
    )

    sources: List[RAGSource] = []
    for chunk, score in results:
        # Document type filter if specified
        if document_type and chunk.document_type.upper() != document_type.upper():
            continue
        sources.append(
            RAGSource(
                document_id=chunk.document_id,
                title=chunk.document_title,
                clause=chunk.clause,
                excerpt=chunk.content,
                relevance_score=score,
                document_version=chunk.document_version,
                chunk_id=chunk.chunk_id,
                department=chunk.department
            )
        )
    return sources

@router.post("/retrieve", response_model=RAGQueryResponse, summary="Retrieve grounded context with validation")
def retrieve_grounded_context(request: RAGQueryRequest):
    """
    RAG analysis endpoint returning validated grounded context,
    enforcing NO-SOURCE -> NO-ANSWER safety rule.
    """
    grounded = context_builder.build_context(
        query=request.query,
        department=request.department,
        top_k=request.top_k,
        min_threshold=request.min_threshold
    )
    return RAGQueryResponse(
        query=request.query,
        grounding_status=grounded.grounding_status,
        needs_human_review=grounded.needs_human_review,
        sources=grounded.sources,
        context_text=grounded.context_text,
        total_candidates=len(grounded.sources),
        refusal_reason=grounded.refusal_reason
    )

@router.get("/documents", response_model=List[KnowledgeDocument], summary="List all synthetic policy documents")
def list_documents(
    department: Optional[str] = Query(None, description="Filter by department"),
    active_only: bool = Query(False, description="Filter only active documents")
):
    doc_path = settings.MOCK_DATA_DIR / "knowledge_documents.json"
    if not doc_path.exists():
        return []
    with open(doc_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    out = []
    for d in docs:
        if active_only and not d.get("is_active", True):
            continue
        if department and department.lower() not in d.get("department", "").lower():
            continue
        out.append(KnowledgeDocument(**d))
    return out

@router.get("/documents/{document_id}", response_model=KnowledgeDocument, summary="Get single synthetic policy document")
def get_document(document_id: str = FastPath(..., description="Document identifier")):
    doc_path = settings.MOCK_DATA_DIR / "knowledge_documents.json"
    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="Knowledge base not initialized")
    with open(doc_path, "r", encoding="utf-8") as f:
        docs = json.load(f)
    for d in docs:
        if d.get("document_id") == document_id:
            return KnowledgeDocument(**d)
    raise HTTPException(status_code=404, detail=f"Knowledge document '{document_id}' not found")

