from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, ConfigDict

from app.nlp.pipeline import NLPPipeline
from app.nlp.schemas import NLPResult
from app.services.rms_service import RMSService

router = APIRouter()
nlp_pipeline = NLPPipeline()
rms_service = RMSService()

class DirectAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    ticket_id: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

@router.post("/analyze", response_model=NLPResult, summary="Execute modular NLP intelligence pipeline")
def analyze_text(request: DirectAnalyzeRequest):
    """
    Executes intent classification, entity extraction, department routing,
    priority scoring, urgency classification, and confidence calculation.
    Supports either ticket_id or raw subject/description input.
    """
    subject = request.subject or request.title or ""
    description = request.description or ""

    if request.ticket_id:
        ticket = rms_service.adapter.get_ticket_by_id(request.ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket '{request.ticket_id}' not found")
        subject = subject or ticket.get("subject", ticket.get("title", ""))
        description = description or ticket.get("description", "")

    if not subject.strip() and not description.strip():
        raise HTTPException(status_code=400, detail="Either ticket_id or subject/description must be provided")

    result = nlp_pipeline.process(subject=subject, description=description)
    return result
