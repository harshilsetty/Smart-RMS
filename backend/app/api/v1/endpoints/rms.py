from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from app.services.rms_service import RMSService
from app.schemas.rms import (
    Ticket,
    TicketListResponse,
    DraftResponse,
    AnalyzeResponse,
    AnalyzeRequest,
    ApprovalRequest,
    ApprovalResponse,
    EscalateRequest,
    EscalateResponse,
    RedirectRequest,
    RedirectResponse,
    RMSCreateRequest,
    AssignmentRequest,
    RMSResponseCreateRequest,
    RMSResponse
)

router = APIRouter()
rms_service = RMSService()

@router.get("", response_model=TicketListResponse, summary="List RMS tickets with filters")
def list_tickets(
    department: Optional[str] = Query(None, description="Filter by department name or ID"),
    priority: Optional[str] = Query(None, description="Filter by priority (Low, Medium, High, Critical)"),
    status: Optional[str] = Query(None, description="Filter by ticket status"),
    search: Optional[str] = Query(None, description="Search keyword in subject or description")
):
    return rms_service.get_tickets(
        department=department,
        priority=priority,
        status=status,
        search=search
    )

@router.post("", response_model=Ticket, status_code=status.HTTP_201_CREATED, summary="Create or ingest a new synthetic RMS ticket")
def create_ticket(request: RMSCreateRequest):
    try:
        return rms_service.create_ticket(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ticket creation failed: {str(e)}")

@router.get("/{ticket_id}", response_model=Ticket, summary="Get single ticket details")
def get_ticket(ticket_id: str):
    ticket = rms_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket

@router.post("/{ticket_id}/analyze", response_model=AnalyzeResponse, summary="Trigger AI NLP analysis on ticket")
async def analyze_ticket(ticket_id: str, request: Optional[AnalyzeRequest] = None):
    try:
        override_text = request.override_text if request else None
        return await rms_service.analyze_ticket(ticket_id, override_text=override_text)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.get("/{ticket_id}/draft", response_model=DraftResponse, summary="Get grounded response draft with citations")
async def get_draft(ticket_id: str):
    try:
        return await rms_service.get_draft_response(ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Draft generation failed: {str(e)}")

@router.post("/{ticket_id}/approve", response_model=ApprovalResponse, summary="Staff approve and finalize ticket")
def approve_ticket(ticket_id: str, request: ApprovalRequest):
    try:
        return rms_service.approve_ticket(
            ticket_id=ticket_id,
            staff_id=request.staff_id,
            approved_text=request.approved_text,
            notes=request.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

@router.post("/{ticket_id}/escalate", response_model=EscalateResponse, summary="Escalate ticket to Department HOD")
def escalate_ticket(ticket_id: str, request: EscalateRequest):
    try:
        return rms_service.escalate_ticket(
            ticket_id=ticket_id,
            staff_id=request.staff_id,
            target_role=request.target_role,
            reason=request.reason
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{ticket_id}/redirect", response_model=RedirectResponse, summary="Redirect ticket to another department")
def redirect_ticket(ticket_id: str, request: RedirectRequest):
    try:
        return rms_service.redirect_ticket(
            ticket_id=ticket_id,
            staff_id=request.staff_id,
            new_department=request.new_department,
            reason=request.reason
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{ticket_id}/assign", summary="Assign ticket to department or staff member")
def assign_ticket(ticket_id: str, request: AssignmentRequest):
    try:
        return rms_service.assign_ticket(ticket_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment failed: {str(e)}")

@router.post("/{ticket_id}/responses", response_model=RMSResponse, status_code=status.HTTP_201_CREATED, summary="Add staff or student communication response")
def add_response(ticket_id: str, request: RMSResponseCreateRequest):
    try:
        return rms_service.add_response(ticket_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add response: {str(e)}")

@router.get("/{ticket_id}/history", response_model=List[Dict[str, Any]], summary="Get chronological audit history")
def get_ticket_history(ticket_id: str):
    try:
        return rms_service.get_ticket_history(ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
