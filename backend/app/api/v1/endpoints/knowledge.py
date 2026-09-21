from typing import List, Optional
from fastapi import APIRouter, Query
from app.rag.retriever import PolicyRetriever
from app.schemas.rms import RAGSource

router = APIRouter()
retriever = PolicyRetriever()

@router.get("/search", response_model=List[RAGSource], summary="Search university approved policies")
def search_knowledge(
    q: str = Query(..., description="Search query string"),
    department: Optional[str] = Query(None, description="Filter by department"),
    limit: int = Query(5, ge=1, le=10)
):
    return retriever.retrieve(query=q, department=department, limit=limit)
